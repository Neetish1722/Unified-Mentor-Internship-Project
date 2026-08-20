import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

class EduProEngine:
    def __init__(self, excel_path, k=None):
        self.users = pd.read_excel(excel_path, sheet_name="Users")
        self.courses = pd.read_excel(excel_path, sheet_name="Courses")
        self.transactions = pd.read_excel(excel_path, sheet_name="Transactions")
        self.transactions["TransactionDate"] = pd.to_datetime(self.transactions["TransactionDate"])
        self._prepare()
        self.k = k or self._select_k()
        self._cluster()
        self._recommendation_index()
        self._evaluate()

    def _prepare(self):
        m = self.transactions.merge(self.users, on="UserID", how="left").merge(self.courses, on="CourseID", how="left")
        self.enriched = m
        g = m.groupby("UserID")
        p = self.users[["UserID","Age","Gender"]].copy().set_index("UserID")
        p["TotalCoursesEnrolled"] = g["CourseID"].nunique()
        p["EnrollmentFrequency"] = g["CourseID"].count() / ((m.TransactionDate.max()-m.TransactionDate.min()).days/30.44)
        p["AverageCourseRating"] = g["CourseRating"].mean()
        p["AverageSpending"] = g["Amount"].mean()
        p["TotalSpending"] = g["Amount"].sum()
        p["DiversityScore"] = g["CourseCategory"].nunique()
        p["PaidEnrollmentRatio"] = g["CourseType"].apply(lambda s: (s=="Paid").mean())
        p["AverageCourseDuration"] = g["CourseDuration"].mean()
        cat_counts = m.pivot_table(index="UserID",columns="CourseCategory",values="CourseID",aggfunc="count",fill_value=0)
        p["AvgCoursesPerCategory"] = p["TotalCoursesEnrolled"] / p["DiversityScore"].replace(0,1)
        level_counts = m.pivot_table(index="UserID",columns="CourseLevel",values="CourseID",aggfunc="count",fill_value=0)
        for level in ["Beginner","Intermediate","Advanced"]:
            if level not in level_counts: level_counts[level]=0
        p["LearningDepthIndex"] = level_counts["Advanced"] / p["TotalCoursesEnrolled"].replace(0,1)
        p["BeginnerRatio"] = level_counts["Beginner"] / p["TotalCoursesEnrolled"].replace(0,1)
        p["PreferredCourseCategory"] = cat_counts.idxmax(axis=1)
        p["PreferredCourseLevel"] = level_counts[["Beginner","Intermediate","Advanced"]].idxmax(axis=1)
        self.profiles=p.reset_index()

        num=["Age","TotalCoursesEnrolled","EnrollmentFrequency","AverageCourseRating","AverageSpending",
             "DiversityScore","PaidEnrollmentRatio","AverageCourseDuration","AvgCoursesPerCategory",
             "LearningDepthIndex","BeginnerRatio"]
        cat=["Gender","PreferredCourseCategory","PreferredCourseLevel"]
        self.num_features=num; self.cat_features=cat
        ct=ColumnTransformer([("num",StandardScaler(),num),
                              ("cat",OneHotEncoder(handle_unknown="ignore",sparse_output=False),cat)])
        self.X=ct.fit_transform(self.profiles[num+cat])
        self.preprocessor=ct

    def _select_k(self):
        vals=[]
        for k in range(2,9):
            km=KMeans(n_clusters=k,n_init=20,random_state=42).fit(self.X)
            vals.append((k,silhouette_score(self.X,km.labels_),km.inertia_))
        return max(vals,key=lambda x:x[1])[0]

    def _cluster(self):
        self.kmeans=KMeans(n_clusters=self.k,n_init=30,random_state=42)
        self.labels=self.kmeans.fit_predict(self.X)
        self.profiles["Cluster"]=self.labels
        hier=AgglomerativeClustering(n_clusters=self.k,linkage="ward").fit(self.X)
        self.hier_labels=hier.labels_
        self.silhouette=silhouette_score(self.X,self.labels)
        self.ari=adjusted_rand_score(self.labels,self.hier_labels)

    def _recommendation_index(self):
        enriched_clustered = self.enriched.merge(
            self.clustered_profiles[["UserID","Cluster"]], on="UserID", how="left"
        )
        self.enriched_clustered = enriched_clustered
        self.cluster_course = (enriched_clustered.groupby(["Cluster","CourseID"])
                               .size().rename("ClusterEnrollments").reset_index())
        cluster_size=self.clustered_profiles.groupby("Cluster").size().rename("ClusterLearners")
        self.cluster_course=self.cluster_course.merge(cluster_size,on="Cluster")
        self.cluster_course["ClusterPopularity"]=self.cluster_course["ClusterEnrollments"]/self.cluster_course["ClusterLearners"]

    def segment_name(self, cluster):
        s=self.clustered_profiles[self.clustered_profiles.Cluster==cluster]
        courses=s.TotalCoursesEnrolled.mean()
        spend=s.AverageSpending.mean()
        diversity=s.DiversityScore.mean()
        if courses >= self.clustered_profiles.TotalCoursesEnrolled.quantile(.75):
            return "Deep Specialists"
        if diversity >= self.clustered_profiles.DiversityScore.quantile(.66):
            return "Exploratory Learners"
        if spend >= self.clustered_profiles.AverageSpending.quantile(.66):
            return "Career-Focused / High-Value"
        return "Emerging Learners"

    def recommend(self,user_id,category=None,level=None,topn=10,ignore_seen_ids=None):
        p=self.clustered_profiles[self.clustered_profiles.UserID.eq(user_id)].iloc[0]
        seen=set(self.enriched.loc[self.enriched.UserID.eq(user_id),"CourseID"])
        if ignore_seen_ids:
            seen -= set(ignore_seen_ids)
        c=self.courses[~self.courses.CourseID.isin(seen)].copy()
        idx=self.cluster_course[self.cluster_course.Cluster.eq(p.Cluster)].copy()
        c=c.merge(idx[["CourseID","ClusterPopularity"]],on="CourseID",how="left").fillna({"ClusterPopularity":0})
        c["CategoryMatch"]=(c.CourseCategory==p.PreferredCourseCategory).astype(float)
        c["LevelMatch"]=(c.CourseLevel==p.PreferredCourseLevel).astype(float)
        c["RatingNorm"]=c.CourseRating/5
        c["PopularityNorm"]=c.ClusterPopularity/(c.ClusterPopularity.max() if c.ClusterPopularity.max()>0 else 1)
        c["RecommendationScore"]=(0.40*c.CategoryMatch+0.25*c.LevelMatch+
                                  0.20*c.PopularityNorm+0.15*c.RatingNorm)
        if category: c=c[c.CourseCategory.eq(category)]
        if level: c=c[c.CourseLevel.eq(level)]
        c=c.sort_values(["RecommendationScore","CourseRating"],ascending=False).head(topn).copy()
        c["Reason"]=np.select([
            c.CategoryMatch.eq(1)&c.LevelMatch.eq(1),
            c.CategoryMatch.eq(1),
            c.LevelMatch.eq(1)],
            ["Matches preferred category and level","Matches preferred category","Matches preferred learning level"],
            default="Popular and highly rated within learner segment")
        return c

    def _evaluate(self):
        hits=0; total=0
        for uid,g in self.transactions.sort_values("TransactionDate").groupby("UserID"):
            if len(g)<2: continue
            held=g.iloc[-1].CourseID
            rec=self.recommend(uid,topn=5,ignore_seen_ids={held})
            if held in set(rec.CourseID): hits+=1
            total+=1
        self.precision_at_5=hits/total if total else 0.0

    def elbow_data(self):
        rows=[]
        for k in range(2,9):
            km=KMeans(n_clusters=k,n_init=15,random_state=42).fit(self.X)
            rows.append({"K":k,"Inertia":km.inertia_})
        return pd.DataFrame(rows)

    def segment_summary(self):
        s=self.clustered_profiles.groupby("Cluster").agg(
            Learners=("UserID","count"),AvgAge=("Age","mean"),
            AvgCourses=("TotalCoursesEnrolled","mean"),AvgSpending=("AverageSpending","mean"),
            AvgDiversity=("DiversityScore","mean"),AvgRating=("AverageCourseRating","mean"),
            AvgDepth=("LearningDepthIndex","mean")).reset_index()
        s["Segment"]=s.Cluster.map(lambda x:self.segment_name(int(x)))
        return s.round(2)

    def category_summary(self):
        x=self.enriched.groupby("CourseCategory").agg(
            Enrollments=("CourseID","count"),UniqueLearners=("UserID","nunique"),
            AvgRating=("CourseRating","mean"),Revenue=("Amount","sum")).reset_index()
        return x.sort_values("Enrollments",ascending=False).round(2)

    def level_summary(self):
        return self.enriched.groupby("CourseLevel").size().rename("Enrollments").reset_index()

    def course_summary(self):
        x=self.enriched.groupby(["CourseID","CourseName","CourseCategory","CourseLevel"]).agg(
            Enrollments=("UserID","count"),UniqueLearners=("UserID","nunique"),
            Rating=("CourseRating","mean"),Revenue=("Amount","sum")).reset_index()
        return x.sort_values("Enrollments",ascending=False).round(2)

    def business_insights(self):
        s=self.segment_summary()
        top_cat=self.category_summary().iloc[0]
        top_seg=s.sort_values("Learners",ascending=False).iloc[0]
        return [
            f"The platform contains {len(self.users):,} learners, {len(self.courses):,} courses and {len(self.transactions):,} enrollment transactions.",
            f"The most enrolled category is {top_cat.CourseCategory} with {int(top_cat.Enrollments):,} enrollments.",
            f"The largest learner segment is {top_seg.Segment}, representing {int(top_seg.Learners):,} learners.",
            "Cluster-aware recommendations prioritize the learner's preferred category and level, then use segment popularity and course rating.",
            "Engagement Lift is treated as a proxy metric because the supplied dataset does not contain post-recommendation completion or retention outcomes."
        ]
    @property
    def clustered_profiles(self):
        return self.profiles
