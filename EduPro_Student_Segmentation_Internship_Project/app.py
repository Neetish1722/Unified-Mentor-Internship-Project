import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_engine import EduProEngine
st.set_page_config(page_title="EduPro Personalization Engine", page_icon="🎓", layout="wide")
@st.cache_resource
def load_engine():
    return EduProEngine("EduPro Online Platform.xlsx")

engine = load_engine()
users, courses, transactions = engine.users, engine.courses, engine.transactions
profiles = engine.profiles
clustered = engine.clustered_profiles

st.sidebar.title("🎓 EduPro")
st.sidebar.caption("Student Segmentation & Personalized Course Recommendation System")
page = st.sidebar.radio("Navigation", [
    "Executive Dashboard", "Learner Explorer", "Recommendations",
    "Segment Analytics", "Course Analytics", "Methodology & Validation"
])

if page == "Executive Dashboard":
    st.title("🎓 EduPro Personalization Intelligence")
    st.markdown("A data-driven learner segmentation and course recommendation engine built from EduPro's user, course and transaction data.")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Learners", f"{len(users):,}")
    c2.metric("Courses", f"{len(courses):,}")
    c3.metric("Enrollments", f"{len(transactions):,}")
    c4.metric("Learner Segments", f"{clustered['Cluster'].nunique()}")

    st.subheader("Learner Segment Distribution")
    seg_counts = clustered["Cluster"].value_counts().sort_index().reset_index()
    seg_counts.columns=["Segment","Learners"]
    st.plotly_chart(px.bar(seg_counts,x="Segment",y="Learners",text="Learners",
                            title="Learners by K-Means Segment"), use_container_width=True)

    left,right=st.columns(2)
    with left:
        st.subheader("Category Demand")
        cat = engine.category_summary()
        st.plotly_chart(px.bar(cat.head(12),x="CourseCategory",y="Enrollments",
                                title="Top Course Categories"),use_container_width=True)
    with right:
        st.subheader("Learning Level Mix")
        lvl = engine.level_summary()
        st.plotly_chart(px.pie(lvl,names="CourseLevel",values="Enrollments",
                               title="Enrollment Distribution by Course Level"),use_container_width=True)

    st.subheader("Business Insights")
    insights = engine.business_insights()
    for x in insights:
        st.write("•", x)

elif page == "Learner Explorer":
    st.title("👤 Learner Profile Explorer")
    selected = st.selectbox("Select learner", users["UserID"].tolist(),
                            format_func=lambda x: f"{x} — {users.loc[users.UserID.eq(x),'UserName'].iloc[0]}")
    p = clustered[clustered.UserID.eq(selected)].iloc[0]
    user = users[users.UserID.eq(selected)].iloc[0]
    seg = engine.segment_name(int(p.Cluster))

    a,b,c,d = st.columns(4)
    a.metric("Assigned Segment", seg)
    b.metric("Courses Enrolled", int(p.TotalCoursesEnrolled))
    c.metric("Category Diversity", int(p.DiversityScore))
    d.metric("Average Spend", f"${p.AverageSpending:,.2f}")

    left,right=st.columns(2)
    with left:
        st.subheader("Demographics")
        st.dataframe(pd.DataFrame({
            "Field":["User ID","Name","Age","Gender"],
            "Value":[user.UserID,user.UserName,user.Age,user.Gender]
        }),hide_index=True,use_container_width=True)
    with right:
        st.subheader("Behavior Profile")
        cols=["PreferredCourseCategory","PreferredCourseLevel","AverageCourseRating",
              "EnrollmentFrequency","LearningDepthIndex","PaidEnrollmentRatio"]
        st.dataframe(p[cols].to_frame("Value"),use_container_width=True)

    st.subheader("Learner Segment Position")
    scatter = clustered.copy()
    scatter["SegmentName"]=scatter.Cluster.map(lambda z: engine.segment_name(int(z)))
    fig=px.scatter(scatter,x="TotalCoursesEnrolled",y="AverageSpending",color="SegmentName",
                   hover_data=["UserID","PreferredCourseCategory","PreferredCourseLevel"],
                   title="Learners by Engagement and Spending")
    fig.add_scatter(x=[p.TotalCoursesEnrolled],y=[p.AverageSpending],mode="markers",
                    marker={"size": 18, "symbol": "star"},name="Selected learner")
    st.plotly_chart(fig,use_container_width=True)

elif page == "Recommendations":
    st.title("🎯 Personalized Course Recommendations")
    selected = st.selectbox("Select learner", users["UserID"].tolist(),
                            format_func=lambda x: f"{x} — {users.loc[users.UserID.eq(x),'UserName'].iloc[0]}")
    p = clustered[clustered.UserID.eq(selected)].iloc[0]
    st.info(f"Segment: **{engine.segment_name(int(p.Cluster))}** | Preferred category: **{p.PreferredCourseCategory}** | Preferred level: **{p.PreferredCourseLevel}**")
    col1,col2,col3=st.columns(3)
    category=col1.selectbox("Category",["All"]+sorted(courses.CourseCategory.unique().tolist()))
    level=col2.selectbox("Level",["All"]+sorted(courses.CourseLevel.unique().tolist()))
    topn=col3.slider("Number of recommendations",5,20,10)
    recs=engine.recommend(selected,category if category!="All" else None,level if level!="All" else None,topn)
    st.dataframe(recs[["CourseID","CourseName","CourseCategory","CourseType","CourseLevel",
                       "CourseRating","CoursePrice","RecommendationScore","Reason"]],
                 hide_index=True,use_container_width=True)

    st.subheader("Recommended Learning Path")
    for _,r in recs.head(5).iterrows():
        st.markdown(f"**{r.CourseName}** — {r.CourseCategory} • {r.CourseLevel} • ⭐ {r.CourseRating:.2f}  \n{r.Reason}")

elif page == "Segment Analytics":
    st.title("📊 Segment Comparison")
    summary=engine.segment_summary()
    st.dataframe(summary,hide_index=True,use_container_width=True)
    metric=st.selectbox("Visualize metric",["TotalCoursesEnrolled","AverageSpending","DiversityScore","AverageCourseRating","LearningDepthIndex"])
    chart=px.box(clustered,x="Cluster",y=metric,color="Cluster",points=False,title=f"{metric} by Segment")
    st.plotly_chart(chart,use_container_width=True)

    st.subheader("2D Cluster Visualization")
    x=st.selectbox("X axis",["TotalCoursesEnrolled","AverageSpending","DiversityScore","AverageCourseRating","Age"])
    y=st.selectbox("Y axis",["AverageSpending","TotalCoursesEnrolled","DiversityScore","LearningDepthIndex","Age"])
    fig=px.scatter(clustered,x=x,y=y,color="Cluster",hover_data=["UserID","PreferredCourseCategory","PreferredCourseLevel"])
    st.plotly_chart(fig,use_container_width=True)

elif page == "Course Analytics":
    st.title("📚 Course Analytics")
    cat=engine.category_summary()
    st.dataframe(cat,hide_index=True,use_container_width=True)
    st.plotly_chart(px.bar(cat,x="CourseCategory",y="Enrollments",color="AvgRating",
                            title="Category Enrollments and Rating"),use_container_width=True)
    st.subheader("Top Courses")
    top=engine.course_summary().head(15)
    st.dataframe(top,hide_index=True,use_container_width=True)

else:
    st.title("🧪 Methodology & Validation")
    st.markdown("""
### Data Science Pipeline
1. **Learner-level aggregation:** transaction history is joined with user and course attributes and aggregated by `UserID`.
2. **Feature engineering:** engagement, preference, spending, diversity and learning-depth features are generated.
3. **Preprocessing:** numerical features are standardized and categorical preferences are one-hot encoded.
4. **Segmentation:** K-Means is the production clustering method; hierarchical clustering is used as validation.
5. **Recommendation:** unseen courses are scored using cluster popularity, learner preference match and course rating.
6. **Validation:** Elbow/SSE, Silhouette Score, hierarchical agreement and a leave-last-enrollment Precision@K proxy are reported.
    """)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Selected K", engine.k)
    c2.metric("Silhouette", f"{engine.silhouette:.3f}")
    c3.metric("Hierarchical Agreement", f"{engine.ari:.3f}")
    c4.metric("Precision@5 Proxy", f"{engine.precision_at_5:.3f}")

    st.subheader("Elbow Analysis")
    elbow=engine.elbow_data()
    st.plotly_chart(px.line(elbow,x="K",y="Inertia",markers=True,title="K-Means Elbow Curve"),use_container_width=True)

    st.subheader("Segment Names")
    st.dataframe(pd.DataFrame({
        "Cluster":list(range(engine.k)),
        "Business Segment":[engine.segment_name(i) for i in range(engine.k)]
    }),hide_index=True,use_container_width=True)
