import os
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from recommendation_engine import RecommendationEngine

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduPathAI — Career Intelligence Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

# ─────────────────────────────────────────────────────────────
# MODERN CSS — Glassmorphism, Gradient Accents, Smooth Animations
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Global Reset & Typography ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ── Hide Streamlit Defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ── Sidebar Styling ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
    }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 32px 40px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: 10%;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.82);
        margin: 0;
        font-weight: 400;
        line-height: 1.5;
    }

    /* ── Glass Cards ── */
    .glass-card {
        background: var(--secondary-background-color, rgba(255,255,255,0.8));
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(128,128,128,0.12);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    }
    
    /* ── Stat Cards ── */
    .stat-card {
        background: var(--secondary-background-color, #f8f9ff);
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        border: 1px solid rgba(102,126,234,0.12);
        box-shadow: 0 2px 12px rgba(102,126,234,0.06);
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
    }
    .stat-icon {
        font-size: 1.8rem;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-color, #1a1a2e);
        margin: 4px 0;
        letter-spacing: -0.5px;
    }
    .stat-label {
        font-size: 0.78rem;
        color: var(--text-color, #64748b);
        opacity: 0.7;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Section Headers ── */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-color, #1a1a2e);
        margin: 24px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header .accent-line {
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px;
        display: inline-block;
    }
    .section-desc {
        font-size: 0.88rem;
        color: var(--text-color, #64748b);
        opacity: 0.75;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* ── Profile Cards ── */
    .profile-card {
        background: var(--secondary-background-color, #f8f9ff);
        border-radius: 14px;
        padding: 18px 22px;
        border-left: 4px solid;
        min-height: 120px;
        transition: transform 0.2s ease;
    }
    .profile-card:hover {
        transform: translateY(-2px);
    }
    .profile-card.academic { border-left-color: #667eea; }
    .profile-card.score { border-left-color: #f59e0b; }
    .profile-card.persona { border-left-color: #10b981; }
    .profile-card.wtl { border-left-color: #8b5cf6; }
    .profile-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-color, #94a3b8);
        opacity: 0.7;
        margin-bottom: 8px;
    }
    .profile-value {
        font-size: 0.92rem;
        font-weight: 500;
        color: var(--text-color, #334155);
        line-height: 1.6;
    }
    .profile-big-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: var(--text-color, #1a1a2e);
        letter-spacing: -0.5px;
    }

    /* ── Skill Chips ── */
    .skill-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
        color: var(--text-color, #4338ca);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px;
        border: 1px solid rgba(102,126,234,0.15);
        transition: all 0.2s ease;
    }
    .skill-chip:hover {
        background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%);
        transform: translateY(-1px);
    }
    .skill-chip.advanced { border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.08); color: #059669; }
    .skill-chip.intermediate { border-color: rgba(102,126,234,0.3); background: rgba(102,126,234,0.08); color: #4338ca; }
    .skill-chip.beginner { border-color: rgba(245,158,11,0.3); background: rgba(245,158,11,0.08); color: #d97706; }
    
    /* ── Gap Chips ── */
    .gap-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(239, 68, 68, 0.08);
        color: #dc2626;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px;
        border: 1px solid rgba(239, 68, 68, 0.15);
    }

    /* ── Job Cards ── */
    .job-card {
        background: var(--secondary-background-color, #ffffff);
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 14px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.03);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .job-card:hover {
        box-shadow: 0 8px 32px rgba(102,126,234,0.12);
        transform: translateY(-2px);
    }
    .job-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px 0 0 4px;
    }
    .job-rank {
        position: absolute;
        top: 14px;
        right: 16px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.82rem;
    }
    .job-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-color, #1e293b);
        margin-bottom: 4px;
        padding-right: 40px;
    }
    .job-company {
        font-size: 0.88rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 6px;
    }
    .job-meta {
        font-size: 0.8rem;
        color: var(--text-color, #64748b);
        opacity: 0.8;
        margin-bottom: 10px;
    }
    .match-score {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.88rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 8px;
    }
    .match-high { background: rgba(16,185,129,0.12); color: #059669; }
    .match-med { background: rgba(245,158,11,0.12); color: #d97706; }
    .match-low { background: rgba(239,68,68,0.12); color: #dc2626; }

    /* ── Course Cards ── */
    .course-card-v2 {
        background: var(--secondary-background-color, #ffffff);
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 14px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.03);
        transition: all 0.25s ease;
        position: relative;
    }
    .course-card-v2:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    .course-title-v2 {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-color, #1e293b);
        margin-bottom: 6px;
    }
    .course-meta-v2 {
        font-size: 0.82rem;
        color: var(--text-color, #64748b);
        opacity: 0.8;
        margin-bottom: 8px;
    }
    .course-desc-v2 {
        font-size: 0.84rem;
        color: var(--text-color, #475569);
        line-height: 1.55;
        opacity: 0.9;
    }
    .match-type-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .pill-exact { background: rgba(16,185,129,0.12); color: #059669; }
    .pill-semantic { background: rgba(139,92,246,0.12); color: #7c3aed; }
    .pill-hybrid { background: rgba(6,182,212,0.12); color: #0891b2; }
    
    .semantic-bridge-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(139,92,246,0.08);
        color: #7c3aed;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
        border: 1px solid rgba(139,92,246,0.15);
    }

    /* ── XAI Card ── */
    .xai-card-v2 {
        background: linear-gradient(135deg, rgba(102,126,234,0.06) 0%, rgba(118,75,162,0.06) 100%);
        border: 1px solid rgba(102,126,234,0.15);
        border-radius: 14px;
        padding: 24px 28px;
        position: relative;
    }
    .xai-card-v2::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px 0 0 4px;
    }
    .xai-title-v2 {
        font-size: 0.95rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .xai-body-v2 {
        font-size: 0.88rem;
        color: var(--text-color, #334155);
        line-height: 1.7;
    }

    /* ── Persona Badges ── */
    .persona-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.82rem;
    }
    .persona-high {
        background: rgba(16,185,129,0.12);
        color: #059669;
        border: 1px solid rgba(16,185,129,0.2);
    }
    .persona-mod {
        background: rgba(245,158,11,0.12);
        color: #d97706;
        border: 1px solid rgba(245,158,11,0.2);
    }
    .persona-low {
        background: rgba(239,68,68,0.12);
        color: #dc2626;
        border: 1px solid rgba(239,68,68,0.2);
    }

    /* ── WTL Progress Bar ── */
    .wtl-bar-outer {
        width: 100%;
        height: 10px;
        background: rgba(128,128,128,0.1);
        border-radius: 6px;
        overflow: hidden;
        margin-top: 8px;
    }
    .wtl-bar-inner {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.8s ease;
    }

    /* ── Semantic Engine Pill ── */
    .engine-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(102,126,234,0.1));
        border: 1px solid rgba(139,92,246,0.2);
        padding: 8px 18px;
        border-radius: 24px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #7c3aed;
        margin-bottom: 16px;
    }
    .engine-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.3); }
    }

    /* ── Insights Box ── */
    .insights-box {
        background: linear-gradient(135deg, rgba(16,185,129,0.06), rgba(6,182,212,0.06));
        border: 1px solid rgba(16,185,129,0.15);
        border-radius: 14px;
        padding: 20px 24px;
    }
    .insights-box h4 {
        color: #059669;
        font-size: 0.92rem;
        margin-bottom: 10px;
    }
    .insights-box li {
        font-size: 0.84rem;
        color: var(--text-color, #334155);
        line-height: 1.65;
        margin-bottom: 4px;
    }

    /* ── Divider ── */
    .styled-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.2), transparent);
        border: none;
        margin: 28px 0;
    }

    /* ── Tab Styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--secondary-background-color, rgba(248,249,255,0.8));
        padding: 6px;
        border-radius: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] {
        color: white !important;
    }
    
    /* ── Metric Override ── */
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────
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
    class_df = pd.read_csv(class_metrics_path) if os.path.exists(class_metrics_path) else None
    return class_df

engine = load_engine()
class_df = load_evaluation_data()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 16px 0 8px 0;">
        <div style="font-size: 2.5rem; margin-bottom: 4px;">🎓</div>
        <div style="font-size: 1.2rem; font-weight: 800; letter-spacing: -0.5px; color: #ffffff !important;">EduPathAI</div>
        <div style="font-size: 0.72rem; font-weight: 500; opacity: 0.6; text-transform: uppercase; letter-spacing: 1.5px; color: #e0e0e0 !important;">Career Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div style="padding: 12px 0;">
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.5; margin-bottom: 12px; color: #e0e0e0 !important;">Platform Stats</div>
    </div>
    """, unsafe_allow_html=True)

    stat_cols = st.columns(2)
    stat_cols[0].metric("👥 Students", len(engine.students_df))
    stat_cols[1].metric("💼 Jobs", len(engine.jobs_df))
    stat_cols2 = st.columns(2)
    stat_cols2[0].metric("📚 Courses", len(engine.courses_df))
    stat_cols2[1].metric("🧬 Skills", len(engine.master_skills))

    st.markdown("---")
    st.markdown("""
    <div style="padding: 8px 0;">
        <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.5; margin-bottom: 8px; color: #e0e0e0 !important;">AI Engines</div>
        <div style="font-size: 0.78rem; line-height: 1.8; color: #e0e0e0 !important;">
            ✅ Random Forest (87.5% CV)<br>
            ✅ K-Means Clusterer (K=3)<br>
            ✅ Cosine Similarity Matcher<br>
            ✅ S-BERT Dense Vectors<br>
            ✅ XAI Glass-Box Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 8px 0;">
        <div style="font-size: 0.7rem; opacity: 0.4; color: #e0e0e0 !important;">EduPathAI v2.0 — Major Project</div>
        <div style="font-size: 0.7rem; opacity: 0.4; color: #e0e0e0 !important;">Python · Streamlit · Scikit-Learn · Plotly</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎓 EduPathAI</div>
    <div class="hero-subtitle">
        AI-Powered Career Pathway Prediction · LMS Behavioral Profiling · Explainable Skill-Gap Bridging via Dense Semantic Vector Search
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# NAVIGATION TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯  Career Portal",
    "📊  Model Benchmarks",
    "🏛️  Architecture",
    "📖  Documentation"
])

# =============================================================================
# TAB 1: STUDENT CAREER & LEARNING PORTAL
# =============================================================================
with tab1:
    # ── Filter Controls ──
    col_filter1, col_filter2, col_filter3 = st.columns([1, 1.5, 1.2])

    with col_filter1:
        careers_list = ["All 16 Pathways"] + sorted(list(engine.students_df["Career_Interest"].unique()))
        selected_career_filter = st.selectbox(
            "🎯 Career Pathway",
            careers_list,
            help="Filter students by their predicted career pathway"
        )
        filtered_students = engine.students_df
        if selected_career_filter != "All 16 Pathways":
            filtered_students = filtered_students[filtered_students["Career_Interest"] == selected_career_filter]

    with col_filter2:
        student_options = []
        for _, s in filtered_students.iterrows():
            student_options.append(f"{s['Student_ID']} — {s['Career_Interest']} ({s['Degree']}, {s['Specialisation']})")

        if not student_options:
            st.warning("No student profiles found for the selected filter.")
            st.stop()

        selected_student_str = st.selectbox(
            "👤 Student Profile",
            student_options,
            help="Select a student to analyze"
        )
        selected_student_id = selected_student_str.split(" — ")[0]

    with col_filter3:
        location_options = [
            "🇮🇳 India (Bengaluru, Pune, Mumbai)",
            "🌍 All Locations (Global)",
            "🇩🇪 Germany / Europe",
            "🇬🇧 United Kingdom",
            "🌐 Remote Only"
        ]
        selected_loc_choice = st.selectbox(
            "📍 Job Market",
            location_options,
            index=0,
            help="Filter jobs by geographic preference"
        )
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

    # ── Retrieve Student Profile ──
    student_row = engine.students_df[engine.students_df["Student_ID"] == selected_student_id].iloc[0]
    cluster_name = engine.get_student_cluster_name(selected_student_id)
    wtl = engine.calculate_willingness_to_learn(selected_student_id)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Profile Cards Row ──
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="profile-card academic">
            <div class="profile-label">Academic Profile</div>
            <div class="profile-value">
                🎓 <strong>{student_row['Degree']}</strong><br>
                📚 {student_row['Specialisation']}<br>
                📅 Class of {student_row['Graduation_Year']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        gpa = student_row['Assessment_Score']
        gpa_color = "#059669" if gpa >= 8 else ("#d97706" if gpa >= 6 else "#dc2626")
        st.markdown(f"""
        <div class="profile-card score">
            <div class="profile-label">Academic Score</div>
            <div class="profile-big-value" style="color: {gpa_color};">{gpa}<span style="font-size: 0.9rem; opacity: 0.5;"> / 10.0</span></div>
            <div class="profile-value" style="margin-top: 4px;">🏅 {student_row['Certifications']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        if "High" in cluster_name:
            badge_cls = "persona-high"
            badge_icon = "🟢"
            badge_text = "High Achiever"
        elif "Steady" in cluster_name or "Moderate" in cluster_name:
            badge_cls = "persona-mod"
            badge_icon = "🟡"
            badge_text = "Steady Learner"
        else:
            badge_cls = "persona-low"
            badge_icon = "🔴"
            badge_text = "Needs Support"

        st.markdown(f"""
        <div class="profile-card persona">
            <div class="profile-label">LMS Behavioral Persona</div>
            <div style="margin: 8px 0;">
                <span class="persona-badge {badge_cls}">{badge_icon} {badge_text}</span>
            </div>
            <div style="font-size: 0.78rem; color: var(--text-color, #64748b); opacity: 0.7;">{cluster_name}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        wtl_color = "#059669" if wtl >= 70 else ("#d97706" if wtl >= 40 else "#dc2626")
        st.markdown(f"""
        <div class="profile-card wtl">
            <div class="profile-label">Willingness to Learn</div>
            <div class="profile-big-value" style="color: {wtl_color};">{wtl}<span style="font-size: 0.9rem; opacity: 0.5;">%</span></div>
            <div class="wtl-bar-outer">
                <div class="wtl-bar-inner" style="width: {min(100, max(0, wtl))}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Skills Display ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Current Skill Portfolio & Competency Depth</div>
    <div class="section-desc">Continuous proficiency weights mapped via Bloom's Cognitive Taxonomy [0.0 – 1.0]</div>
    """, unsafe_allow_html=True)

    prof_dict = {}
    if "Skill_Proficiencies" in student_row and pd.notna(student_row["Skill_Proficiencies"]):
        for item in str(student_row["Skill_Proficiencies"]).split(","):
            if ":" in item:
                s_name, s_val = item.rsplit(":", 1)
                try:
                    prof_dict[s_name.strip().lower()] = float(s_val.strip())
                except ValueError:
                    pass

    s_tech = [s.strip() for s in str(student_row["Technical_Skills"]).split(",") if s.strip()]
    s_soft = [s.strip() for s in str(student_row["Soft_Skills"]).split(",") if s.strip()]

    skills_html = ""
    for s in s_tech:
        w = prof_dict.get(s.lower(), 0.70)
        pct = int(w * 100)
        tier = "advanced" if w >= 0.85 else ("intermediate" if w >= 0.60 else "beginner")
        tier_label = "Advanced" if w >= 0.85 else ("Intermediate" if w >= 0.60 else "Beginner")
        skills_html += f'<span class="skill-chip {tier}">💻 {s} <span style="opacity:0.7;">({tier_label} {pct}%)</span></span> '
    for s in s_soft:
        w = prof_dict.get(s.lower(), 0.70)
        pct = int(w * 100)
        tier = "advanced" if w >= 0.85 else ("intermediate" if w >= 0.60 else "beginner")
        tier_label = "Advanced" if w >= 0.85 else ("Intermediate" if w >= 0.60 else "Beginner")
        skills_html += f'<span class="skill-chip {tier}">🤝 {s} <span style="opacity:0.7;">({tier_label} {pct}%)</span></span> '
    st.markdown(skills_html, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Job Matching & Skill Gap Analysis ──
    target_recommendations = engine.match_jobs(selected_student_id, top_n=3, country_filter=selected_country)
    if not target_recommendations:
        target_recommendations = engine.match_jobs(selected_student_id, top_n=3, country_filter="All")

    col_jobs, col_gaps = st.columns([1.1, 1.9])

    with col_jobs:
        market_label = "India 🇮🇳" if selected_country == "India" else (selected_country if selected_country != "All" else "Global 🌍")
        st.markdown(f"""
        <div class="section-header"><span class="accent-line"></span> Top Matched Jobs</div>
        <div class="section-desc">Cosine similarity against active vacancies in {market_label}</div>
        """, unsafe_allow_html=True)

        for idx, rec in enumerate(target_recommendations, start=1):
            score = rec["Match_Score"]
            score_cls = "match-high" if score >= 70 else ("match-med" if score >= 50 else "match-low")
            st.markdown(f"""
            <div class="job-card">
                <div class="job-rank">{idx}</div>
                <div class="job-title">{rec['Job_Title']}</div>
                <div class="job-company">🏢 {rec.get('Company_Name', 'Enterprise Tech')}</div>
                <div class="job-meta">📍 {rec.get('Location', 'Remote')} · {rec.get('Country', 'Global')} &nbsp;|&nbsp; 💼 {rec.get('Industry', 'Technology')}</div>
                <span class="match-score {score_cls}">✦ {score}% Match</span>
            </div>
            """, unsafe_allow_html=True)

    with col_gaps:
        top_match = target_recommendations[0]
        st.markdown(f"""
        <div class="section-header"><span class="accent-line"></span> Skill-Gap Analysis — {top_match['Job_Title']}</div>
        """, unsafe_allow_html=True)

        gaps, rec_courses = engine.get_skill_gap_and_courses(selected_student_id, top_match["Job_ID"])
        req_skills = [s.strip() for s in str(top_match.get("Skills_Required", "")).split(",") if s.strip()]

        if not gaps:
            st.success("🎉 **No Skill Gaps Detected!** This student already possesses all required skills for this role.")
        else:
            st.markdown(f'<div class="section-desc">⚠️ <strong>{len(gaps)} skill gap(s)</strong> detected for this role:</div>', unsafe_allow_html=True)
            gaps_html = ""
            for g in gaps:
                gaps_html += f'<span class="gap-chip">✕ {g}</span> '
            st.markdown(gaps_html, unsafe_allow_html=True)

        # ── Radar Chart ──
        sample_radar_skills = sorted(list(set(req_skills + s_tech[:4])))[:8]
        if not sample_radar_skills:
            sample_radar_skills = ["Python", "Problem Solving", "Analytics", "Communication"]

        student_prof = [prof_dict.get(sk.lower(), 0.0) for sk in sample_radar_skills]
        job_needs = [0.85 if sk.lower() in [r.lower() for r in req_skills] else 0.0 for sk in sample_radar_skills]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=job_needs + [job_needs[0]],
            theta=sample_radar_skills + [sample_radar_skills[0]],
            fill='toself',
            name='Job Requirement (85%)',
            line_color='#ef4444',
            fillcolor='rgba(239,68,68,0.08)',
            line_width=2
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=student_prof + [student_prof[0]],
            theta=sample_radar_skills + [sample_radar_skills[0]],
            fill='toself',
            name='Student Mastery',
            line_color='#667eea',
            fillcolor='rgba(102,126,234,0.12)',
            line_width=2.5
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0.0, 1.0], showticklabels=True, tickfont=dict(size=10, color='#94a3b8')),
                angularaxis=dict(tickfont=dict(size=11, color='#64748b'))
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=11)
            ),
            height=340,
            margin=dict(l=60, r=60, t=30, b=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Recommended Courses ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Recommended Course Bridges</div>
    <div class="section-desc">Personalized courses to close skill gaps with minimum cognitive overload</div>
    """, unsafe_allow_html=True)

    # Semantic engine status pill
    semantic_mode = engine.semantic_matcher.get_mode_name()
    st.markdown(f"""
    <div class="engine-pill">
        <span class="engine-dot"></span>
        <span>Dense Semantic Search: <strong>{semantic_mode}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    if not rec_courses:
        st.info("✅ No courses required — student skills are already fully aligned with job demands.")
    else:
        for c in rec_courses[:4]:
            match_type = c.get("Match_Type", "Curated Bridge")
            if match_type == "Dense Semantic Bridge":
                pill_cls = "pill-semantic"
                border_color = "#8b5cf6"
            elif match_type == "Hybrid (Exact + Semantic)":
                pill_cls = "pill-hybrid"
                border_color = "#0891b2"
            else:
                pill_cls = "pill-exact"
                border_color = "#10b981"

            semantic_badges_html = ""
            if c.get("Semantic_Bridges"):
                for b in c["Semantic_Bridges"]:
                    semantic_badges_html += f'<span class="semantic-bridge-badge">✨ {b["gap"]} ↔ {b["concept"]} ({b["similarity"]}%)</span> '

            exact_html = ""
            if c.get("Skills_Covered"):
                exact_html = f'<div style="font-size: 0.82rem; margin-top: 6px;">🎯 Directly covers: <strong>{c["Skills_Covered"]}</strong></div>'

            badges_line = f'<div style="margin-top: 6px;">{semantic_badges_html}</div>' if semantic_badges_html else ''

            st.markdown(f"""
            <div class="course-card-v2" style="border-left: 4px solid {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span class="course-title-v2">📖 {c['Course_Title']}</span>
                    <span class="match-type-pill {pill_cls}">{match_type}</span>
                </div>
                <div class="course-meta-v2">🏛️ {c['Platform']} &nbsp;·&nbsp; ⏳ {c['Duration_Hours']} Hours</div>
                {exact_html}
                {badges_line}
                <div class="course-desc-v2" style="margin-top: 8px;">{c['Description']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Explainable AI ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Explainable AI (XAI) Reasoning</div>
    """, unsafe_allow_html=True)

    xai_explanation = engine.generate_explanation(selected_student_id, top_match["Job_ID"], rec_courses[:3])
    st.markdown(f"""
    <div class="xai-card-v2">
        <div class="xai-title-v2">🧠 Why was this recommendation generated?</div>
        <div class="xai-body-v2">{xai_explanation.replace(chr(10), '<br>')}</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: MODEL EVALUATION & BENCHMARKS
# =============================================================================
with tab2:
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Machine Learning Evaluation Suite</div>
    <div class="section-desc">Rigorous benchmarks across 16 career pathways — supervised classifiers, unsupervised clustering, and recommendation metrics</div>
    """, unsafe_allow_html=True)

    # ── Key Metrics Row ──
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown("""
    <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-value">87.50%</div>
        <div class="stat-label">RF 5-Fold CV Accuracy</div>
    </div>
    """, unsafe_allow_html=True)
    m2.markdown("""
    <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-value">87.67%</div>
        <div class="stat-label">XGBoost F1-Score</div>
    </div>
    """, unsafe_allow_html=True)
    m3.markdown("""
    <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-value">0.9910</div>
        <div class="stat-label">Multi-Class ROC-AUC</div>
    </div>
    """, unsafe_allow_html=True)
    m4.markdown("""
    <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-value">0.4627</div>
        <div class="stat-label">K-Means Silhouette</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Classification Benchmark Table ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Supervised Classification Benchmarks</div>
    <div class="section-desc">16 career classes · N=96 test samples · Stratified 5-Fold Cross-Validation</div>
    """, unsafe_allow_html=True)

    if class_df is not None:
        st.dataframe(class_df, use_container_width=True, hide_index=True)
    else:
        st.info("Metrics CSV not found. Run `model_comparison.py` to generate.")

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Visual Validation Gallery ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Experimental Plots & Confusion Matrices</div>
    """, unsafe_allow_html=True)

    c_img1, c_img2 = st.columns(2)
    with c_img1:
        cm_path = os.path.join(PLOTS_DIR, "phase7_confusion_and_roc.png")
        if os.path.exists(cm_path):
            st.image(cm_path, caption="16×16 Confusion Matrix & Multi-Class ROC Curves", use_container_width=True)
    with c_img2:
        model_comp_path = os.path.join(PLOTS_DIR, "classification_model_comparison.png")
        if os.path.exists(model_comp_path):
            st.image(model_comp_path, caption="Model Accuracy Comparison & RF Feature Importance", use_container_width=True)

    c_img3, c_img4 = st.columns(2)
    with c_img3:
        cluster_path = os.path.join(PLOTS_DIR, "clustering_evaluation.png")
        if os.path.exists(cluster_path):
            st.image(cluster_path, caption="K-Means Elbow & 2D PCA Cluster Map (K=3)", use_container_width=True)
    with c_img4:
        rec_path = os.path.join(PLOTS_DIR, "phase7_recommendation_metrics.png")
        if os.path.exists(rec_path):
            st.image(rec_path, caption="Recommendation Precision & Recall @ K", use_container_width=True)

    c_img5, c_img6 = st.columns([1.3, 0.7])
    with c_img5:
        acc_roc_path = os.path.join(PLOTS_DIR, "accuracy_vs_roc_auc_comparison.png")
        if os.path.exists(acc_roc_path):
            st.image(acc_roc_path, caption="Accuracy vs. ROC-AUC Across 6 Classifiers", use_container_width=True)
    with c_img6:
        st.markdown("""
        <div class="insights-box">
            <h4>🎯 Benchmark Insights (16 Pathways)</h4>
            <ul>
                <li><strong>Random Forest Champion</strong>: 87.50% 5-fold CV and 0.9910 ROC-AUC across all 16 categories</li>
                <li><strong>Continuous Proficiencies</strong>: Bloom's Taxonomy mapping (0.0→1.0) improves boundary sensitivity over binary encoding</li>
                <li><strong>XGBoost & LightGBM</strong>: Compete strongly at 86.46% and 85.42% accuracy</li>
                <li><strong>High Separability</strong>: All top ensembles exceed 0.98 ROC-AUC</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Drift Monitoring ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Production Drift Monitoring Suite</div>
    <div class="section-desc">KS-test distribution shifts, PSI stability, and accuracy decay tracking</div>
    """, unsafe_allow_html=True)

    drift_report_path = os.path.join(DATA_DIR, "drift_monitoring_report.csv")
    if os.path.exists(drift_report_path):
        try:
            with open(drift_report_path, "r", encoding="utf-8") as f:
                content = f.read()
            sections = content.split("## ")
            for sec in sections[1:]:
                lines = sec.strip().split("\n")
                sec_title = lines[0]
                csv_text = "\n".join(lines[1:]).strip()
                sec_df = pd.read_csv(io.StringIO(csv_text))
                st.markdown(f"**{sec_title}**")
                st.dataframe(sec_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Drift report format notice: {e}")

    drift_plot_path = os.path.join(PLOTS_DIR, "drift_analysis.png")
    if os.path.exists(drift_plot_path):
        st.image(drift_plot_path, caption="Statistical Feature Drift (KS-Test) & Concept Drift Trajectory", use_container_width=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Dense Semantic Search ──
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Dense Semantic Vector Search (Sentence-BERT)</div>
    <div class="section-desc">384-D dense embeddings resolving vocabulary mismatch between job skills and course curricula</div>
    """, unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.markdown("""
    <div class="stat-card">
        <div class="stat-icon">🧠</div>
        <div class="stat-value" style="font-size: 1.1rem;">all-MiniLM-L6-v2</div>
        <div class="stat-label">Embedding Model</div>
    </div>
    """, unsafe_allow_html=True)
    col_s2.markdown("""
    <div class="stat-card">
        <div class="stat-icon">📐</div>
        <div class="stat-value">384-D</div>
        <div class="stat-label">Dense Latent Space</div>
    </div>
    """, unsafe_allow_html=True)
    col_s3.markdown("""
    <div class="stat-card">
        <div class="stat-icon">🚀</div>
        <div class="stat-value">+18.4%</div>
        <div class="stat-label">Vocabulary Recall Boost</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    | Target Skill (Query) | Course Matched | Skills in Catalog | Similarity | Type |
    | :--- | :--- | :--- | :---: | :---: |
    | `PyTorch` | **Deep Learning and Neural Networks** (Coursera) | Deep Learning, AI/ML, Python | **88.0%** | ✨ Dense Semantic |
    | `PostgreSQL` | **Enterprise Database Administration** (edX) | Database Management, SQL, PostgreSQL | **100.0%** | 🎯 Exact Match |
    | `PostgreSQL` | **SQL for Data Analysis** (Udemy) | SQL, Database Management | **88.0%** | ✨ Dense Semantic |
    | `Kubernetes` | **DevOps Engineering: Docker, K8s & CI/CD** (Udemy) | Docker, Kubernetes, CI/CD, Linux | **100.0%** | 🎯 Exact Match |
    | `Kubernetes` | **Cloud Computing Essentials** (Coursera) | Cloud, AWS, Azure, Docker | **85.0%** | ✨ Dense Semantic |
    | `NLP` | **Machine Learning Specialization** (Coursera) | Machine Learning, AI/ML, Python | **86.0%** | ✨ Dense Semantic |
    | `Figma` | **UI/UX Design Masterclass** (Coursera) | Figma, UI Design, Wireframing | **100.0%** | 🎯 Exact Match |
    """)


# =============================================================================
# TAB 3: SYSTEM ARCHITECTURE BLUEPRINT
# =============================================================================
with tab3:
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> End-to-End System Architecture</div>
    <div class="section-desc">Enterprise blueprint: data ingestion → feature store → AI engine → presentation layer</div>
    """, unsafe_allow_html=True)

    blueprint_path = os.path.join(PLOTS_DIR, "architecture_blueprint.png")
    if os.path.exists(blueprint_path):
        st.image(blueprint_path, caption="EduPathAI End-to-End System Architecture Blueprint", use_container_width=True)
    else:
        st.info("System Architecture diagram available in project presentation slides.")

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Engine Breakdown & Empirical Results</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    | Engine / Component | Model / Algorithm | Role in EduPathAI | Empirical Result |
    | :--- | :--- | :--- | :--- |
    | **Career Pathway Predictor** | Random Forest Classifier | Predicts 1 of 16 career pathways from academic profiles & Bloom's skill vectors | **87.50% CV, 0.9910 ROC-AUC** |
    | **Behavioral Segmenter** | K-Means (K=3) | Groups LMS telemetry into 3 personas (High/Steady/Critical) | **Silhouette: 0.4627** |
    | **Job Matcher** | Cosine Similarity | Geometric alignment between 66-D student vectors and 240 job postings | **85–95% precision** |
    | **Course Bridge** | Sentence-BERT (all-MiniLM-L6-v2) | 384-D embeddings resolving vocabulary mismatch | **+18.4% recall, 76.8% gap recovery** |
    | **XAI Engine** | Glass-Box Gap Decomposer + NLG | Set subtraction & natural-language justification | **100% auditable** |
    | **Presentation Layer** | Streamlit + Plotly | Interactive dashboard with radar charts, filters, and benchmarks | **Sub-120ms inference** |
    """)


# =============================================================================
# TAB 4: PROJECT & DATASET DOCUMENTATION
# =============================================================================
with tab4:
    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Project Overview & Dataset Statistics</div>
    """, unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">💼</div>
        <div class="stat-value">{len(engine.jobs_df)}</div>
        <div class="stat-label">Live & Curated Jobs</div>
    </div>
    """, unsafe_allow_html=True)
    d2.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-value">{len(engine.students_df)}</div>
        <div class="stat-label">Student Profiles</div>
    </div>
    """, unsafe_allow_html=True)
    d3.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-value">{len(engine.courses_df)}</div>
        <div class="stat-label">Industry Courses</div>
    </div>
    """, unsafe_allow_html=True)
    d4.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">🧬</div>
        <div class="stat-value">{len(engine.master_skills)}</div>
        <div class="stat-label">Master Skills Inventory</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> 16 Supported Career Pathways</div>
    """, unsafe_allow_html=True)

    careers_sorted = sorted(list(engine.students_df["Career_Interest"].unique()))
    cols_c = st.columns(4)
    for i, c in enumerate(careers_sorted):
        count_c = sum(engine.students_df["Career_Interest"] == c)
        cols_c[i % 4].markdown(f"""
        <div style="background: var(--secondary-background-color, #f8f9ff); border-radius: 8px; padding: 8px 14px; margin-bottom: 6px; border-left: 3px solid #667eea;">
            <span style="font-weight: 600; font-size: 0.85rem; color: var(--text-color, #334155);">{c}</span>
            <span style="float: right; font-size: 0.78rem; opacity: 0.6; color: var(--text-color, #94a3b8);">{count_c} students</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header"><span class="accent-line"></span> Raw Dataset Previews</div>
    """, unsafe_allow_html=True)

    with st.expander("📊 Students Dataset", expanded=False):
        st.dataframe(engine.students_df.head(10), use_container_width=True, hide_index=True)
    with st.expander("💼 Jobs Dataset", expanded=False):
        st.dataframe(engine.jobs_df.head(10), use_container_width=True, hide_index=True)
    with st.expander("📚 Courses Dataset", expanded=False):
        st.dataframe(engine.courses_df.head(10), use_container_width=True, hide_index=True)
