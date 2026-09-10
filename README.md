# EduPathAI: AI-Powered Student Learning, Employability & Career Recommendation System

An end-to-end machine learning platform that analyzes student academic histories and LMS behavioral logs, matches them against live real-world job postings, predicts career pathways across 16 modern domains, and prescribes personalized, explainable course bridges to close detected skill gaps.

---

## 🌟 Key Features & Capabilities
* **Tri-Partite Integration**: Dynamically links **176 live scraped jobs** (Arbeitnow API), **480 real student profiles & LMS logs** (xAPI-Edu-Data benchmark), and **28 curated online courses**.
* **16 Modern Career Pathways**: Predicts student alignment across 16 specialized industry tracks including AI Engineer, Cloud DevOps, Cybersecurity Analyst, Data Scientist, Full-Stack Developer, and UI/UX Designer.
* **Behavioral Persona Clustering**: Uses unsupervised **K-Means Clustering ($K=3$)** on LMS logs (logins, submissions, completion %) to identify High Achievers, Steady Learners, and At-Risk Learners.
* **Multi-Model Supervised Classification**: Compares **Random Forest, XGBoost, Logistic Regression, and Decision Trees**, with ensemble tree models achieving **100% test accuracy** and **1.0000 ROC-AUC** across 16 classes.
* **High-Impact Skill-Gap Recommender**: Recommends top-1 to top-3 focused bridge courses, recovering up to **76.6%** of missing job skills.
* **Explainable AI (XAI)**: Generates human-readable natural language justifications explaining why recommendations were generated.

---

## 📁 Repository Structure
```
├── data/
│   ├── jobs.csv                              # 176 live scraped job postings
│   ├── courses.csv                           # 28 curated industry courses
│   ├── students_employability.csv            # 480 student academic records
│   ├── learning_engagement.csv               # 480 LMS behavioral logs
│   ├── model_comparison_metrics.csv          # Multi-model classification metrics
│   └── phase7_complete_evaluation_report.csv # Complete Phase 7 evaluation numbers
├── plots/
│   ├── classification_model_comparison.png   # 4-model comparison & feature importances
│   ├── clustering_evaluation.png             # Elbow curve & 2D PCA cluster map
│   ├── phase7_confusion_and_roc.png          # 16x16 Confusion Matrix & ROC curves
│   └── phase7_recommendation_metrics.png     # Precision@K & Recall@K curves
├── scrape_jobs.py                            # Job market scraper (Arbeitnow API)
├── scrape_courses.py                         # Course catalog compiler (28 courses)
├── fetch_real_students.py                    # Student dataset mapper (16 career paths)
├── recommendation_engine.py                  # Core recommendation & XAI engine
├── run_engine_demo.py                        # Prototype runner across student profiles
├── model_comparison.py                       # Supervised & unsupervised benchmarking
├── phase7_model_evaluation.py                # Phase 7 evaluation suite & plot generator
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.9+ installed
* Install required libraries:
```bash
pip install pandas numpy scikit-learn xgboost matplotlib beautifulsoup4
```

### 2. Running the Recommendation Engine Demo
```bash
python run_engine_demo.py
```

### 3. Running Multi-Model Benchmarking (Phase 6)
```bash
python model_comparison.py
```

### 4. Running the Complete Model Evaluation Suite (Phase 7)
```bash
python phase7_model_evaluation.py
```
All evaluation tables will be exported to `data/` and all visual graphs will be saved to `plots/`.
