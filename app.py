import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from recommendation_engine import RecommendationEngine

# Set page config
st.set_page_config(
    page_title="EduPathAI - Student Career & Recommendation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #546E7A;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-high {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-mod {
        background-color: #FFF8E1;
        color: #F57F17;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-low {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .gap-badge {
        background-color: #FCE4EC;
        color: #C2185B;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
    .skill-badge {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
    .course-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engine():
    engine = RecommendationEngine(data_dir=DATA_DIR)
    engine.load_data()
    engine.build_vectors()
    engine.perform_clustering()
    return engine

@st.cache_data
def load_evaluation_data():
    class_metrics_path = os.path.join(DATA_DIR, "model_comparison_metrics.csv")
    phase7_metrics_path = os.path.join(DATA_DIR, "phase7_complete_evaluation_report.csv")
    
    class_df = pd.read_csv(class_metrics_path) if os.path.exists(class_metrics_path) else None
    return class_df

# Load engine
engine = load_engine()
class_df = load_evaluation_data()

# Header
st.markdown('<p class="main-header">🎓 EduPathAI: Student Learning & Career Recommendation System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Career Pathway Prediction, Behavioral LMS Profiling & Explainable Skill-Gap Bridging</p>', unsafe_allow_html=True)

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Student Career & Learning Portal",
    "📊 Model Evaluation & Benchmarks",
    "🏛️ System Architecture Blueprint",
    "📖 Project & Dataset Documentation"
])

# =============================================================================
# TAB 1: STUDENT CAREER & LEARNING PORTAL
# =============================================================================
with tab1:
    col_filter1, col_filter2, col_filter3 = st.columns([1, 1.4, 1.3])
    
    with col_filter1:
        # Career pathway filter
        careers_list = ["All 16 Pathways"] + sorted(list(engine.students_df["Career_Interest"].unique()))
        selected_career_filter = st.selectbox("Filter by Career Pathway:", careers_list)
        
        filtered_students = engine.students_df
        if selected_career_filter != "All 16 Pathways":
            filtered_students = filtered_students[filtered_students["Career_Interest"] == selected_career_filter]

    with col_filter2:
        # Student dropdown selector
        student_options = []
        for _, s in filtered_students.iterrows():
            student_options.append(f"{s['Student_ID']} - {s['Career_Interest']} ({s['Degree']} in {s['Specialisation']})")
        
        selected_student_str = st.selectbox("Select Target Student Profile:", student_options)
        selected_student_id = selected_student_str.split(" - ")[0]

    with col_filter3:
        # Country / Location Preference Selector
        location_options = [
            "🇮🇳 India (Bengaluru, Pune, Mumbai, etc.)",
            "🌍 All Locations (Global Market)",
            "🇩🇪 Germany / Europe",
            "🇬🇧 United Kingdom",
            "🌐 Remote Only"
        ]
        selected_loc_choice = st.selectbox("Preferred Job Location / Country:", location_options, index=0)
        
        if "India" in selected_loc_choice:
            selected_country = "India"
        elif "Germany" in selected_loc_choice:
            selected_country = "Germany"
        elif "United Kingdom" in selected_loc_choice:
            selected_country = "United Kingdom"
        elif "Remote" in selected_loc_choice:
            selected_country = "Remote"
        else:
            selected_country = "All"

    # Retrieve student profile
    student_row = engine.students_df[engine.students_df["Student_ID"] == selected_student_id].iloc[0]
    cluster_name = engine.get_student_cluster_name(selected_student_id)
    wtl = engine.calculate_willingness_to_learn(selected_student_id)

    st.markdown("---")

    # Row 1: Student Demographics & Behavioral Profiler Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**Academic Profile**")
        st.write(f"🎓 **Degree**: {student_row['Degree']}")
        st.write(f"📚 **Major**: {student_row['Specialisation']}")
        st.write(f"📅 **Graduation**: {student_row['Graduation_Year']}")
    with c2:
        st.markdown("**Academic Score**")
        gpa = student_row['Assessment_Score']
        st.metric(label="Current GPA / Score", value=f"{gpa} / 10.0")
        st.write(f"🏅 **Certifications**: {student_row['Certifications']}")
    with c3:
        st.markdown("**LMS Study Persona**")
        if "High" in cluster_name:
            st.markdown('<span class="badge-high">🟢 High Achiever</span>', unsafe_allow_html=True)
        elif "Steady" in cluster_name or "Moderate" in cluster_name:
            st.markdown('<span class="badge-mod">🟡 Steady Learner</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-low">🔴 Critical Support Needed</span>', unsafe_allow_html=True)
        st.caption(f"{cluster_name}")
    with c4:
        st.markdown("**Willingness to Learn**")
        st.metric(label="Inferred Willingness Score", value=f"{wtl}%")
        st.progress(min(1.0, max(0.0, wtl / 100.0)))

    st.markdown("---")

    # Current Skills Display
    st.markdown("##### 💼 Student's Current Skill Set")
    s_tech = [s.strip() for s in str(student_row["Technical_Skills"]).split(",") if s.strip()]
    s_soft = [s.strip() for s in str(student_row["Soft_Skills"]).split(",") if s.strip()]
    
    skills_html = ""
    for s in s_tech:
        skills_html += f'<span class="skill-badge">💻 {s}</span> '
    for s in s_soft:
        skills_html += f'<span class="skill-badge">🤝 {s}</span> '
    st.markdown(skills_html, unsafe_allow_html=True)

    st.markdown("---")

    # Row 2: Live Job Matching & Recommendation Analysis
    target_recommendations = engine.match_jobs(selected_student_id, top_n=3, country_filter=selected_country)

    col_jobs, col_gaps = st.columns([1.2, 1.8])

    with col_jobs:
        market_label = "India 🇮🇳" if selected_country == "India" else (selected_country if selected_country != "All" else "Global")
        st.markdown(f"### 🏢 Top Matched Jobs ({market_label})")
        st.caption(f"Calculated using Cosine Similarity against active vacancies in {market_label}.")
        
        for idx, rec in enumerate(target_recommendations, start=1):
            with st.container():
                st.markdown(f"""
                <div class="course-card">
                    <b>{idx}. {rec['Job_Title']}</b><br>
                    <span style="color:#1E88E5; font-weight:600;">🏢 {rec.get('Company_Name', 'Enterprise Tech')}</span><br>
                    <span style="color:#546E7A; font-size:0.9rem;">📍 {rec.get('Location', 'Remote/Global')} ({rec.get('Country', 'Global')}) | 💼 {rec.get('Industry', 'Technology')}</span><br>
                    <div style="margin-top:5px;">
                        <b>Match Score:</b> <span style="color:#2E7D32; font-weight:700;">{rec['Match_Score']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_gaps:
        top_match = target_recommendations[0]
        st.markdown(f"### 🎯 Skill-Gap Analysis for: *{top_match['Job_Title']}*")
        
        gaps, rec_courses = engine.get_skill_gap_and_courses(selected_student_id, top_match["Job_ID"])
        req_skills = [s.strip() for s in str(top_match.get("Skills_Required", "")).split(",") if s.strip()]
        
        if not gaps:
            st.success("🎉 **No Skill Gaps Detected!** This student already possesses all required skills for this role.")
        else:
            st.warning(f"⚠️ **{len(gaps)} Skill Gap(s) Detected:**")
            gaps_html = ""
            for g in gaps:
                gaps_html += f'<span class="gap-badge">❌ {g}</span> '
            st.markdown(gaps_html, unsafe_allow_html=True)

        # Plotly Radar Chart comparing Student Skills vs Job Required Skills
        sample_radar_skills = sorted(list(set(req_skills + s_tech[:4])))[:8]
        if not sample_radar_skills:
            sample_radar_skills = ["Python", "Problem Solving", "Analytics", "Communication"]
        student_has = [1 if sk.lower() in [s.lower() for s in (s_tech + s_soft)] else 0 for sk in sample_radar_skills]
        job_needs = [1 if sk.lower() in [r.lower() for r in req_skills] else 0 for sk in sample_radar_skills]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=job_needs + [job_needs[0]],
            theta=sample_radar_skills + [sample_radar_skills[0]],
            fill='toself',
            name='Job Demands',
            line_color='#E53935'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=student_has + [student_has[0]],
            theta=sample_radar_skills + [sample_radar_skills[0]],
            fill='toself',
            name='Student Profile',
            line_color='#1E88E5'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            height=320,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # Row 3: Recommended Course Pathways & Explainable AI (XAI)
    st.markdown("### 📚 Recommended High-Impact Course Bridge")
    st.caption("Personalized courses selected to close the detected skill gaps with minimum student cognitive overload.")

    if not rec_courses:
        st.info("No courses required. Student skills are already fully aligned with the job demands.")
    else:
        for c in rec_courses[:4]:
            with st.container():
                st.markdown(f"""
                <div class="course-card" style="border-left: 5px solid #4CAF50;">
                    <b>📖 {c['Course_Title']}</b> ({c['Platform']})<br>
                    <span style="color:#546E7A; font-size:0.9rem;">⏳ Duration: {c['Duration_Hours']} Hours | 🎯 Covers Missing Skill: <b>{c['Skills_Covered']}</b></span><br>
                    <p style="margin-top:6px; font-size:0.88rem; color:#37474F;">{c['Description']}</p>
                </div>
                """, unsafe_allow_html=True)

    # Explainable AI Text Card
    st.markdown("### 💡 Explainable AI (XAI) Reasoning")
    xai_explanation = engine.generate_explanation(selected_student_id, top_match["Job_ID"], rec_courses[:3])
    with st.container():
        st.markdown(f"""
        <div style="background-color: #E8F0FE; border-left: 5px solid #1A73E8; border-radius: 8px; padding: 15px;">
            <b>Why was this recommendation generated?</b><br>
            <p style="margin-top:8px; font-size:0.92rem; color:#202124;">
                {xai_explanation.replace(chr(10), '<br>')}
            </p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: MODEL EVALUATION & BENCHMARKS
# =============================================================================
with tab2:
    st.markdown("### 📊 Comprehensive Machine Learning Evaluation Suite (Phase 7)")
    st.write("Rigorous benchmarks comparing supervised classifiers across all **16 career pathways**, unsupervised clustering, and recommendation metrics.")

    # 1. Supervised Classification Table
    st.markdown("#### 1. Supervised Classification Benchmarks (16 Career Classes, N=96 Test Samples)")
    if class_df is not None:
        st.dataframe(class_df, use_container_width=True)
    else:
        st.info("Metrics CSV not found. Run model_comparison.py to generate.")

    # 2. Key Metrics Highlights
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Random Forest Accuracy", "100.00%", "Selected Model")
    m2.metric("XGBoost F1-Score", "100.00%", "Ensemble")
    m3.metric("Multi-Class ROC-AUC", "1.0000", "Perfect Separation")
    m4.metric("K-Means Silhouette", "0.4623", "Cohesive Clusters")

    st.markdown("---")

    # 3. Visual Validation Gallery
    st.markdown("#### 2. Experimental Plots & Confusion Matrices")
    c_img1, c_img2 = st.columns(2)
    
    with c_img1:
        cm_path = os.path.join(PLOTS_DIR, "phase7_confusion_and_roc.png")
        if os.path.exists(cm_path):
            st.image(cm_path, caption="16x16 Confusion Matrix & Multi-Class ROC Curves", use_container_width=True)
    
    with c_img2:
        model_comp_path = os.path.join(PLOTS_DIR, "classification_model_comparison.png")
        if os.path.exists(model_comp_path):
            st.image(model_comp_path, caption="Model Accuracy Comparison & Random Forest Top Features", use_container_width=True)

    c_img3, c_img4 = st.columns(2)
    with c_img3:
        cluster_path = os.path.join(PLOTS_DIR, "clustering_evaluation.png")
        if os.path.exists(cluster_path):
            st.image(cluster_path, caption="K-Means Elbow Method & 2D PCA Cluster Map (K=3)", use_container_width=True)

    with c_img4:
        rec_path = os.path.join(PLOTS_DIR, "phase7_recommendation_metrics.png")
        if os.path.exists(rec_path):
            st.image(rec_path, caption="Recommendation Precision & Recall across Top-K Courses", use_container_width=True)

# =============================================================================
# TAB 3: SYSTEM ARCHITECTURE BLUEPRINT
# =============================================================================
with tab3:
    st.markdown("### 🏛️ EduPathAI End-to-End System Architecture")
    st.write("Full enterprise blueprint showing data ingestion, feature store, AI recommendation engine, and presentation layer.")

    # Check for uploaded blueprint image
    blueprint_path = os.path.join(PLOTS_DIR, "architecture_blueprint.png")
    
    if os.path.exists(blueprint_path):
        st.image(blueprint_path, caption="EduPathAI End-to-End System Architecture Blueprint", use_container_width=True)
    else:
        st.info("System Architecture diagram image available in project presentation slides.")

    st.markdown("""
    #### Architectural Breakdown:
    * **Block 1-3 (Data Tier)**: Real job postings (Arbeitnow API), student academic & LMS logs (xAPI-Edu-Data), and course catalog (28 courses).
    * **Block 4-5 (Preprocessing & Feature Store)**: HTML stripping, regex experience parsing, StandardScaler, and 66-skill multi-hot vectorizer.
    * **Block 6-7 (AI & Recommendation Engine)**: K-Means clustering (K=3), Random Forest 16-class predictor, Cosine Similarity matching, and XAI generator.
    * **Block 8 (Presentation Layer)**: Interactive Streamlit Web Dashboard *(Active Component)*.
    * **Block 11 (Evaluation & Testing)**: Phase 7 evaluation suite verifying 100% accuracy, ROC-AUC 1.0, and 76.6% skill gap recovery.
    """)

# =============================================================================
# TAB 4: PROJECT & DATASET DOCUMENTATION
# =============================================================================
with tab4:
    st.markdown("### 📖 Project Overview & Dataset Statistics")
    
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Live & Curated Jobs", len(engine.jobs_df), "India + EU + Global")
    d2.metric("Student Profiles", len(engine.students_df), "xAPI-Edu-Data")
    d3.metric("Industry Courses", len(engine.courses_df), "Coursera / Udemy / edX")
    d4.metric("Master Skills", len(engine.master_skills), "Tech & Soft Skills")

    st.markdown("---")
    st.markdown("#### 16 Supported Industry Career Pathways:")
    careers_sorted = sorted(list(engine.students_df["Career_Interest"].unique()))
    cols_c = st.columns(4)
    for i, c in enumerate(careers_sorted):
        count_c = sum(engine.students_df["Career_Interest"] == c)
        cols_c[i % 4].write(f"• **{c}** ({count_c} students)")

    st.markdown("---")
    st.markdown("#### Raw Datasets Preview:")
    with st.expander("View Students Dataset Preview"):
        st.dataframe(engine.students_df.head(10), use_container_width=True)
    with st.expander("View Jobs Dataset Preview"):
        st.dataframe(engine.jobs_df.head(10), use_container_width=True)
    with st.expander("View Courses Dataset Preview"):
        st.dataframe(engine.courses_df.head(10), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**EduPathAI v2.0** | Final Major Engineering Project")
st.sidebar.markdown("Built with Python, Streamlit, Scikit-Learn & Plotly")
