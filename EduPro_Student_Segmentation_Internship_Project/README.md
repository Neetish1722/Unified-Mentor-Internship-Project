# EduPro — Student Segmentation & Personalized Course Recommendation System

## Internship Project
A data-science and Streamlit personalization engine for EduPro. It transforms learner demographics, course metadata and transaction history into learner segments and cluster-aware course recommendations.

## Dataset
Place `EduPro Online Platform.xlsx` in the project root. Required sheets:
- Users
- Courses
- Transactions
- Teachers (retained in the source dataset; not required for segmentation)

## Core methodology
1. Join Users + Transactions + Courses at enrollment level.
2. Aggregate behavior at `UserID`.
3. Engineer engagement, preference, spending, diversity and learning-depth features.
4. Standardize numeric features and one-hot encode categorical learner preferences.
5. Select K using Silhouette Score; validate with hierarchical clustering.
6. Build recommendations from cluster popularity + preference match + course rating.
7. Report Silhouette, hierarchical agreement and Precision@5 proxy.

## Run
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Dashboard modules
- Executive Dashboard
- Learner Profile Explorer
- Personalized Recommendations
- Segment Analytics
- Course Analytics
- Methodology & Validation

## Important evaluation note
The supplied dataset contains enrollments and transaction amounts but no recommendation exposure, completion, retention or click labels. Therefore Engagement Lift is presented as a proxy/limitation rather than claimed as a measured causal effect. Precision@5 is an offline leave-last-enrollment proxy.

## Suggested research paper structure
1. Abstract
2. Introduction and problem statement
3. Dataset and data preparation
4. Exploratory data analysis
5. Feature engineering
6. Learner segmentation methodology
7. Personalized recommendation methodology
8. Evaluation and validation
9. Business insights and stakeholder recommendations
10. Limitations and future work
11. Conclusion
