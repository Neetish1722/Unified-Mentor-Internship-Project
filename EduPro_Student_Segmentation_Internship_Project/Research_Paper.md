# Research Paper / Technical Report
## Student Segmentation and Personalized Course Recommendation System for EduPro

### Abstract
This project develops a student-centric personalization engine for EduPro using unsupervised learning and cluster-aware recommendation logic. Learner demographics, course metadata and transaction history are transformed into learner-level behavioral profiles. K-Means clustering identifies learner segments, while hierarchical clustering provides an independent validation view. Recommendations combine preferred category, preferred level, cluster popularity and course rating. The system is deployed as an interactive Streamlit dashboard for learner exploration, segment analytics and personalized learning paths.

### 1. Problem Statement
Generic course recommendations treat learners as a homogeneous population. EduPro needs a structured framework to understand learner behavior, discover distinct learning patterns and recommend relevant courses.

### 2. Dataset
The supplied workbook contains:
- Users: learner identity, age and gender.
- Courses: category, type, level, price, duration and rating.
- Transactions: learner-course enrollment history, date, amount, payment method and teacher.
- Teachers: teacher metadata retained for future instructor analytics.

The project uses Users, Courses and Transactions for the personalization engine.

### 3. Feature Engineering
Learner-level features include total courses enrolled, average courses per category, enrollment frequency, preferred category, preferred level, average course rating, average spending, total spending, diversity score, paid enrollment ratio, average course duration and learning depth index.

Learning Depth Index is defined as advanced-level enrollments divided by total enrollments. Diversity Score is the number of unique course categories explored.

### 4. Preprocessing
Numerical variables are standardized using StandardScaler. Gender, preferred course category and preferred course level are one-hot encoded. This creates a common numerical feature space for clustering.

### 5. Learner Segmentation
K-Means is the production clustering algorithm. Candidate values of K from 2 to 8 are evaluated using the Silhouette Score and the elbow/inertia curve. Hierarchical clustering with Ward linkage is used as a validation method. The final dashboard reports both Silhouette and Adjusted Rand Agreement between the two clustering approaches.

### 6. Personalized Recommendation Logic
Previously enrolled courses are removed from the candidate pool. Each unseen course receives a score based on:
- 40% preferred category match
- 25% preferred level match
- 20% popularity within the learner's segment
- 15% course rating

The score is then used to rank personalized recommendations. Users can filter by category and level.

### 7. Evaluation
Silhouette Score measures separation and compactness of the clusters. Hierarchical agreement checks whether a second clustering method produces similar learner assignments. Precision@5 is calculated as an offline leave-last-enrollment proxy.

Engagement Lift cannot be directly measured from the supplied workbook because it contains no recommendation exposure, click, completion or retention outcome. A production deployment should add these event fields and conduct an A/B test.

### 8. Stakeholder Recommendations
1. Use different learning journeys for exploratory, specialist and high-value learners.
2. Promote category continuity for specialists while exposing adjacent categories to explorers.
3. Use level-aware recommendations to prevent beginner learners from receiving overly advanced courses.
4. Monitor recommendation precision and downstream completion after deployment.
5. Add recommendation impressions, clicks, completion, time spent and retention fields to enable causal evaluation.

### 9. Limitations
The dataset represents transactions rather than explicit preferences or outcomes. A transaction is therefore treated as an enrollment signal. The recommendation model is not a collaborative filtering model based on explicit ratings; course ratings are used as content quality signals.

### 10. Conclusion
The proposed EduPro system shifts personalization from one-size-fits-all recommendations to learner-centric intelligence. By combining behavioral segmentation with cluster-aware recommendations, EduPro can organize learners into actionable groups and provide more relevant course discovery. The Streamlit implementation makes the analytical outputs accessible to non-technical stakeholders and provides a foundation for future production experimentation.
