import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import time

# Attempt to import RecommendationEngine
try:
    from recommendation_engine import RecommendationEngine
except ImportError:
    st.error("Could not import RecommendationEngine. Please ensure `recommendation_engine.py` exists in the same directory.")
    st.stop()

# ------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CSS
# ------------------------------------------------------------------------
st.set_page_config(
    page_title="EduPathAI - Student Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, modern CSS for student-friendly UI
CSS = """
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
    color: #0f172a;
}

/* Ensure root app container has clean light background */
.stApp {
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

/* Hide Streamlit Chrome */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] * {
    color: #1e293b;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] p {
    color: #0f172a !important;
}

/* Sidebar Radio Navigation items */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    margin-bottom: 8px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background-color: #eff6ff !important;
    border-color: #93c5fd !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span {
    color: #0f172a !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

/* Form inputs & selectbox labels readability */
.stSelectbox label, .stTextInput label, .stSlider label {
    color: #1e293b !important;
    font-weight: 600 !important;
}

.sidebar-logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2563eb;
    margin-bottom: 2rem;
    padding: 0.5rem;
}
.sidebar-tagline {
    font-size: 0.85rem;
    font-weight: 400;
    color: #64748b;
    margin-top: -5px;
    display: block;
}

/* Cards */
.custom-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.custom-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    transform: translateY(-2px);
}
.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.5rem;
}
.card-subtitle {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 1rem;
}

/* Skill Chips */
.skill-chip {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.2rem;
}
.skill-chip-strong {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
}
.skill-chip-moderate {
    background-color: #dbeafe;
    color: #1e40af;
    border: 1px solid #bfdbfe;
}
.skill-chip-basic {
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
}
.skill-chip-gap {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
}

/* Progress Bars */
.progress-bg {
    width: 100%;
    background-color: #e2e8f0;
    border-radius: 9999px;
    height: 6px;
    margin-top: 4px;
}
.progress-fill-green {
    background-color: #10b981;
    height: 100%;
    border-radius: 9999px;
}
.progress-fill-amber {
    background-color: #f59e0b;
    height: 100%;
    border-radius: 9999px;
}
.progress-fill-red {
    background-color: #ef4444;
    height: 100%;
    border-radius: 9999px;
}

/* Hero Section */
.hero-container {
    background: linear-gradient(135deg, #2563eb 0%, #0891b2 100%);
    border-radius: 16px;
    padding: 3rem 2rem;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: white;
}
.hero-subtitle {
    font-size: 1.1rem;
    font-weight: 400;
    opacity: 0.9;
    max-width: 600px;
    margin: 0 auto;
}

/* Metrics Row */
.metric-box {
    text-align: center;
    padding: 1rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2563eb;
}
.metric-label {
    font-size: 0.85rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background-color: #2563eb !important;
    color: white !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #1d4ed8 !important;
    box-shadow: 0 4px 6px -1px rgba(37,99,235,0.2) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------------
# 2. INITIALIZATION & DATA LOADING
# ------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

@st.cache_resource(show_spinner="Loading EduPathAI Engine...")
def init_engine():
    engine = RecommendationEngine(data_dir=DATA_DIR)
    engine.load_data()
    engine.build_vectors()
    engine.perform_clustering()
    return engine

engine = init_engine()

# Helper function to get clean progress bar HTML
def get_progress_bar_html(percentage, height="6px"):
    color_class = "progress-fill-green" if percentage >= 70 else "progress-fill-amber" if percentage >= 50 else "progress-fill-red"
    return f"""
    <div class="progress-bg" style="height: {height};">
        <div class="{color_class}" style="width: {percentage}%; height: 100%;"></div>
    </div>
    """

# ------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------
NAV_PAGES = ["🏠 Home", "🎯 Find My Career Path", "🔍 Explore Jobs & Courses", "ℹ️ About"]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = NAV_PAGES[0]

with st.sidebar:
    st.markdown("""
        <div class='sidebar-logo'>
            🎓 EduPathAI
            <span class='sidebar-tagline'>Your AI Career Guide</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:0.9rem; font-weight:700; color:#334155; margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.05em;'>Navigation</p>", unsafe_allow_html=True)
    
    curr_index = NAV_PAGES.index(st.session_state.nav_page) if st.session_state.nav_page in NAV_PAGES else 0
    selected_page = st.radio(
        "Navigation Menu",
        NAV_PAGES,
        index=curr_index,
        key="sidebar_radio_selection",
        label_visibility="collapsed"
    )
    if selected_page != st.session_state.nav_page:
        st.session_state.nav_page = selected_page
    
    st.markdown("<div style='margin-top: 35vh; font-size: 0.8rem; color: #64748b; font-weight: 500;'>v2.0.0 | Student Portal</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------
# 4. PAGE IMPLEMENTATIONS
# ------------------------------------------------------------------------

def render_home():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Discover Your Perfect Career Path with AI</div>
            <div class="hero-subtitle">Get personalized job matches, identify skill gaps, and find the right courses to bridge them. Start your journey today!</div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
            <div class="custom-card" style="text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:1rem;">🤖</div>
                <div class="card-title">AI Job Matching</div>
                <div class="card-subtitle" style="margin:0;">Semantic skill analysis matches you with roles that fit your unique profile.</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="custom-card" style="text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:1rem;">🎯</div>
                <div class="card-title">Skill Gap Analysis</div>
                <div class="card-subtitle" style="margin:0;">Pinpoint exactly what you need to learn to land your dream job.</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="custom-card" style="text-align:center;">
                <div style="font-size:2.5rem; margin-bottom:1rem;">📚</div>
                <div class="card-title">Smart Recommendations</div>
                <div class="card-subtitle" style="margin:0;">Curated courses designed specifically to bridge your skill gaps.</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    num_students = len(engine.students_df)
    num_jobs = len(engine.jobs_df)
    num_courses = len(engine.courses_df)
    num_skills = len(engine.master_skills)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='metric-box'><div class='metric-value'>{num_students}+</div><div class='metric-label'>Students Analyzed</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-box'><div class='metric-value'>{num_jobs}</div><div class='metric-label'>Job Opportunities</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-box'><div class='metric-value'>{num_courses}</div><div class='metric-label'>Curated Courses</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-box'><div class='metric-value'>{num_skills}</div><div class='metric-label'>Skills Tracked</div></div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Get Started → Find My Career Path", type="primary", use_container_width=True):
            st.session_state.nav_page = "🎯 Find My Career Path"
            st.rerun()

def render_radar_chart(student_id, job_id):
    student_row = engine.students_df[engine.students_df['Student_ID'] == student_id]
    job_row = engine.jobs_df[engine.jobs_df['Job_ID'] == job_id]
    
    if student_row.empty or job_row.empty:
        return None
        
    s_vec = student_row.iloc[0]['Skill_Vector']
    j_vec = job_row.iloc[0]['Skill_Vector']
    
    # To make radar chart readable, pick top N skills relevant to the job or student
    # Sort by importance in job + student
    importance = np.array(s_vec) + np.array(j_vec)
    top_indices = np.argsort(importance)[::-1][:8] # top 8 skills
    
    categories = [engine.master_skills[i] for i in top_indices]
    s_vals = [s_vec[i] * 100 for i in top_indices]
    j_vals = [j_vec[i] * 100 for i in top_indices]
    
    # Close the loop
    categories.append(categories[0])
    s_vals.append(s_vals[0])
    j_vals.append(j_vals[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=s_vals,
        theta=categories,
        fill='toself',
        name='Your Skills',
        line_color='#2563eb',
        fillcolor='rgba(37, 99, 235, 0.2)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=j_vals,
        theta=categories,
        fill='toself',
        name='Job Requirements',
        line_color='#ef4444',
        fillcolor='rgba(239, 68, 68, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=20, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_job_analysis(student_id, job_id, job_title, match_score):
    st.markdown(f"### Analysis for **{job_title}** (Match: {match_score:.1f}%)")
    
    # 1. Skill Gap Analysis
    skill_gaps, recommended_courses = engine.get_skill_gap_and_courses(student_id, job_id)
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("<div class='card-title'>Missing/Weak Skills</div>", unsafe_allow_html=True)
        if not skill_gaps:
            st.success("🎉 You have all the primary skills required for this job!")
        else:
            gap_html = ""
            for gap in skill_gaps:
                gap_html += f"<span class='skill-chip skill-chip-gap'>{gap}</span>"
            st.markdown(gap_html, unsafe_allow_html=True)
            
    with c2:
        st.markdown("<div class='card-title'>Skills Match Radar</div>", unsafe_allow_html=True)
        fig = render_radar_chart(student_id, job_id)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 2. Recommended Courses
    st.markdown("### 📚 Recommended Courses to Bridge the Gap")
    if not recommended_courses:
        st.info("No specific courses needed based on your current skill profile.")
    else:
        for course in recommended_courses:
            match_type_color = "#10b981" if "Direct" in course.get('Match_Type', '') else "#3b82f6"
            st.markdown(f"""
                <div class="custom-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-size:0.8rem; color:#64748b; font-weight:600; text-transform:uppercase;">
                                {course.get('Platform', 'Online')} • {course.get('Duration_Hours', 'N/A')} hours
                            </div>
                            <div class="card-title" style="margin-top:0.25rem;">{course.get('Course_Title', 'Course')}</div>
                        </div>
                        <div style="background-color:{match_type_color}20; color:{match_type_color}; padding:4px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">
                            {course.get('Match_Type', 'Match')}
                        </div>
                    </div>
                    <div style="font-size:0.9rem; color:#475569; margin-top:0.5rem; margin-bottom:1rem;">
                        {course.get('Description', '')}
                    </div>
                    <div>
                        <span style="font-size:0.8rem; font-weight:600; color:#64748b;">Covers Gaps:</span> 
                        {' '.join([f"<span class='skill-chip skill-chip-strong' style='font-size:0.7rem; padding:2px 6px;'>{g.strip()}</span>" for g in str(course.get('Skills_Covered_All', course.get('Skills_Covered', ''))).split(',') if g.strip()])}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    # 3. Explanation
    st.markdown("### 💡 Why this matches")
    explanation = engine.generate_explanation(student_id, job_id, recommended_courses)
    # Strip some technical jargon if possible, though mostly it's just formatting
    st.markdown(f"<div style='background-color:#f1f5f9; padding:1.5rem; border-radius:12px; font-size:0.95rem; line-height:1.6;'>{explanation}</div>", unsafe_allow_html=True)

def render_student_dashboard(student_id, job_market="All"):
    student_row = engine.students_df[engine.students_df['Student_ID'] == student_id].iloc[0]
    
    # -- Profile Summary Card --
    if student_id == 'CUSTOM_USER':
        cluster_name = "New User (Data Pending)"
        wtl = 75.0 # Default positive willingness
    else:
        try:
            cluster_name = engine.get_student_cluster_name(student_id)
            wtl = engine.calculate_willingness_to_learn(student_id)
        except:
            cluster_name = "Standard Profile"
            wtl = 50.0

    st.markdown(f"""
        <div class="custom-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h2 style="margin:0; color:#0f172a;">{student_row.get('Name', student_id)}</h2>
                    <div style="color:#64748b; font-size:1rem; margin-top:0.25rem;">
                        {student_row['Degree']} in {student_row['Specialisation']} • {student_row['Education_Level']}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.5rem; font-weight:700; color:#2563eb;">GPA: {student_row['Assessment_Score']:.1f}/10</div>
                    <div style="font-size:0.85rem; color:#64748b; margin-top:0.2rem;">Target: {student_row['Career_Interest']}</div>
                </div>
            </div>
            <hr style="border-color:#e2e8f0; margin:1rem 0;">
            <div style="display:flex; gap:2rem;">
                <div style="flex:1;">
                    <div style="font-size:0.85rem; font-weight:600; color:#64748b; margin-bottom:0.25rem;">Learning Style Profile</div>
                    <div style="font-weight:500; color:#0f172a;">{cluster_name}</div>
                </div>
                <div style="flex:1;">
                    <div style="font-size:0.85rem; font-weight:600; color:#64748b; margin-bottom:0.25rem;">Motivation Score ({wtl:.0f}%)</div>
                    {get_progress_bar_html(wtl)}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # -- Your Skills --
    st.markdown("### Your Top Skills")
    skill_profs = student_row['Skill_Proficiencies']
    if pd.isna(skill_profs) or not skill_profs:
        st.info("No skills recorded.")
    else:
        skills = [s.strip() for s in skill_profs.split(',') if s.strip()]
        skill_html = "<div style='display:flex; flex-wrap:wrap; gap:10px;'>"
        for s in skills:
            if ':' in s:
                parts = s.split(':')
                name = parts[0]
                try:
                    val = float(parts[1]) * 100
                except:
                    val = 50
            else:
                name = s
                val = 50
                
            chip_class = "skill-chip-strong" if val >= 70 else "skill-chip-moderate" if val >= 40 else "skill-chip-basic"
            skill_html += f"""
                <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:10px; width:180px;">
                    <div style="font-size:0.85rem; font-weight:600; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{name}">{name}</div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="flex:1;">{get_progress_bar_html(val, "4px")}</div>
                        <div style="font-size:0.7rem; color:#64748b;">{int(val)}%</div>
                    </div>
                </div>
            """
        skill_html += "</div>"
        st.markdown(skill_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -- Top Matched Jobs --
    st.markdown("### 🎯 Your Top Career Matches")
    country_filter = job_market if job_market != "All" else "All"
    matched_jobs = engine.match_jobs(student_id, top_n=3, country_filter=country_filter)
    
    if not matched_jobs:
        st.warning(f"No jobs found matching your profile in the '{country_filter}' market.")
        return

    # Create selectable buttons/radio for jobs
    job_options = [f"#{i+1} {job['Job_Title']} ({job['Match_Score']:.1f}%)" for i, job in enumerate(matched_jobs)]
    
    # Store selected index in session state
    if 'selected_job_idx' not in st.session_state:
        st.session_state.selected_job_idx = 0
        
    selected_job_label = st.radio("Select a role to analyze:", job_options, horizontal=True, label_visibility="collapsed")
    selected_idx = job_options.index(selected_job_label)
    st.session_state.selected_job_idx = selected_idx
    
    selected_job = matched_jobs[selected_idx]
    
    # Show detailed analysis panel for selected job
    st.markdown("---")
    render_job_analysis(student_id, selected_job['Job_ID'], selected_job['Job_Title'], selected_job['Match_Score'])


def render_existing_profile():
    st.markdown("### Select Your Profile")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        interests = ["All"] + sorted(list(engine.students_df['Career_Interest'].dropna().unique()))
        selected_interest = st.selectbox("Filter by Career Interest", interests)
        
    filtered_df = engine.students_df
    if selected_interest != "All":
        filtered_df = filtered_df[filtered_df['Career_Interest'] == selected_interest]
        
    with col2:
        # Format student dropdown
        def format_student(row):
            return f"{row['Student_ID']} — {row['Career_Interest']} ({row['Degree']}, {row['Specialisation']})"
            
        student_options = []
        student_mapping = {}
        for _, row in filtered_df.iterrows():
            if row['Student_ID'] == 'CUSTOM_USER':
                label = f"✨ Custom Profile — {row['Career_Interest']} ({row['Degree']})"
            else:
                label = format_student(row)
            student_options.append(label)
            student_mapping[label] = row['Student_ID']
            
        if not student_options:
            st.warning("No students found with this filter.")
            return
            
        selected_student_label = st.selectbox("Select Profile", student_options)
        student_id = student_mapping[selected_student_label]
        
    with col3:
        markets = ["All"] + sorted(list(engine.jobs_df['Country'].dropna().unique()))
        job_market = st.selectbox("Job Market", markets)
        
    st.markdown("<br>", unsafe_allow_html=True)
    render_student_dashboard(student_id, job_market)

def render_create_profile():
    st.markdown("### ✨ Create My Own Profile")
    st.markdown("Tell us about your background and skills to get personalized AI career recommendations.")
    
    with st.form("custom_profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", value="Jane Doe")
            degree = st.selectbox("Degree", ["B.Tech", "B.Sc", "BBA", "B.Des", "MCA", "M.Tech", "MBA"])
            gpa = st.slider("GPA / Assessment Score (Out of 10)", min_value=0.0, max_value=10.0, value=7.5, step=0.1)
        with c2:
            specs = sorted(list(engine.students_df['Specialisation'].dropna().unique())) if 'Specialisation' in engine.students_df.columns else ["Computer Science", "Data Science", "IT"]
            specialization = st.selectbox("Specialization", specs)
            interests = sorted(list(engine.students_df['Career_Interest'].dropna().unique())) if 'Career_Interest' in engine.students_df.columns else ["Software Engineering", "Data Analytics"]
            career_interest = st.selectbox("Target Career Interest", interests)
            
        markets = ["All"] + sorted(list(engine.jobs_df['Country'].dropna().unique()))
        job_market = st.selectbox("Target Job Market", markets)
            
        st.markdown("#### Your Skills")
        st.markdown("<span style='font-size:0.85rem; color:#64748b;'>Select the skills you possess and your general proficiency level.</span>", unsafe_allow_html=True)
        
        c3, c4 = st.columns([2, 1])
        with c3:
            # Title case the skills for better UI
            skill_options = [s.title() for s in engine.master_skills]
            selected_skills_title = st.multiselect("Select Skills", skill_options, default=["Python", "Communication", "Teamwork"])
            selected_skills = [s.lower() for s in selected_skills_title] # For matching
            
        with c4:
            skill_level = st.radio("General Skill Level", ["Beginner", "Intermediate", "Advanced"], index=1)
            
        submitted = st.form_submit_button("Find My Career Path 🚀", type="primary")
        
    if submitted:
        with st.spinner("Analyzing your profile..."):
            custom_id = 'CUSTOM_USER'
            level_weights = {'Beginner': 0.45, 'Intermediate': 0.70, 'Advanced': 0.90}
            weight = level_weights[skill_level]
            
            # Master skills are lowercase internally typically, or matching exact case.
            # Let's use lower for safe matching
            ms_lower = [s.lower() for s in engine.master_skills]
            vector = [weight if s.lower() in selected_skills else 0.0 for s in engine.master_skills]
            
            soft_skill_set = {'communication', 'teamwork', 'leadership', 'adaptability', 'time management', 'problem-solving', 'critical thinking', 'presentation', 'negotiation'}
            
            tech_s = [s.title() for s in selected_skills if s not in soft_skill_set]
            soft_s = [s.title() for s in selected_skills if s in soft_skill_set]
            
            skill_profs_str = ', '.join([f"{s.title()}:{weight}" for s in selected_skills])
            
            custom_row_dict = {
                'Student_ID': custom_id,
                'Name': name,
                'Gender': 'Not Specified',
                'Education_Level': 'Undergraduate',
                'Degree': degree,
                'Specialisation': specialization,
                'Graduation_Year': 2025,
                'Technical_Skills': ', '.join(tech_s),
                'Soft_Skills': ', '.join(soft_s),
                'Skill_Proficiencies': skill_profs_str,
                'Projects': '',
                'Certifications': '',
                'Assessment_Score': gpa,
                'Career_Interest': career_interest,
                'Skill_Vector': vector
            }
            
            custom_row = pd.DataFrame([custom_row_dict])
            
            # Clean up existing custom user
            engine.students_df = engine.students_df[engine.students_df['Student_ID'] != custom_id]
            
            # Concat
            engine.students_df = pd.concat([engine.students_df, custom_row], ignore_index=True)
            
            # Reset session state for job selection
            st.session_state.selected_job_idx = 0
            st.session_state.custom_profile_created = True
            st.session_state.custom_job_market = job_market
            
            st.success("Profile created successfully! Scrolling to results...")
            time.sleep(0.5)
            
    if st.session_state.get('custom_profile_created', False):
        st.markdown("---")
        render_student_dashboard('CUSTOM_USER', st.session_state.get('custom_job_market', 'All'))

def render_find_path():
    mode = st.radio("Select Mode", ["Use an existing profile", "✨ Create my own profile"], horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    if mode == "Use an existing profile":
        render_existing_profile()
    else:
        render_create_profile()

def render_explore():
    st.markdown("## 🔍 Explore Jobs & Courses")
    
    tab1, tab2, tab3 = st.tabs(["💼 Job Market", "📚 Course Catalog", "🗺️ Career Pathways"])
    
    with tab1:
        st.markdown("Browse all available job opportunities tracked by EduPathAI.")
        # Filterable dataframe
        search_job = st.text_input("Search Jobs (Title, Company, Industry)...", "")
        
        display_df = engine.jobs_df[['Job_ID', 'Job_Title', 'Company_Name', 'Industry', 'Location', 'Country', 'Experience_Required']].copy()
        if search_job:
            mask = display_df.apply(lambda row: row.astype(str).str.contains(search_job, case=False).any(), axis=1)
            display_df = display_df[mask]
            
        st.dataframe(
            display_df, 
            use_container_width=True,
            column_config={
                "Job_ID": "ID",
                "Job_Title": "Role",
                "Company_Name": "Company",
                "Experience_Required": "Exp. Level"
            },
            hide_index=True
        )
        
    with tab2:
        st.markdown("Browse recommended learning resources.")
        search_course = st.text_input("Search Courses (Title, Platform, Skills)...", "")
        
        display_courses = engine.courses_df[['Course_ID', 'Course_Title', 'Platform', 'Duration_Hours', 'Skills_Developed']].copy()
        if search_course:
            mask = display_courses.apply(lambda row: row.astype(str).str.contains(search_course, case=False).any(), axis=1)
            display_courses = display_courses[mask]
            
        st.dataframe(
            display_courses,
            use_container_width=True,
            column_config={
                "Course_ID": "ID",
                "Course_Title": "Course Name",
                "Duration_Hours": "Hours",
                "Skills_Developed": "Teaches"
            },
            hide_index=True
        )
        
    with tab3:
        st.markdown("### Career Pathways Overview")
        if 'Career_Interest' in engine.students_df.columns:
            pathways = sorted(list(engine.students_df['Career_Interest'].dropna().unique()))
            
            # Display in grid
            cols = st.columns(4)
            for i, path in enumerate(pathways):
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="custom-card" style="text-align:center; padding:1rem; min-height:100px; display:flex; align-items:center; justify-content:center;">
                            <div style="font-weight:600; color:#0f172a;">{path}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Career pathways data not available.")

def render_about():
    st.markdown("## ℹ️ About EduPathAI")
    
    st.markdown("""
    **EduPathAI** is your personal, AI-powered career guide. We analyze your academic background, 
    technical abilities, and soft skills to match you with real-world job opportunities.
    
    ### How it Works (Simply)
    1. **Tell us about yourself**: You provide your degree, interests, and current skill levels.
    2. **AI Matching**: Our system compares your profile against hundreds of jobs using semantic matching (understanding the *meaning* of skills, not just exact keywords).
    3. **Find the Gaps**: We identify exactly what skills you're missing for your dream job.
    4. **Bridge the Gap**: We recommend highly specific courses that teach exactly what you need.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("🛠️ For Researchers & Developers"):
        st.markdown(f"""
        **System Architecture & Details:**
        - **Embedding Model:** `{engine.semantic_matcher.get_mode_name() if hasattr(engine, 'semantic_matcher') else 'Sentence-BERT (all-MiniLM-L6-v2)'}`
        - **Clustering:** K-Means clustering is used on student engagement data to categorize learning behaviors.
        - **Similarity Metric:** Cosine Similarity between 384-dimensional skill vectors.
        - **Data Dimensions:**
          - `{len(engine.students_df)}` Students
          - `{len(engine.jobs_df)}` Job Postings
          - `{len(engine.courses_df)}` Courses
          - `{len(engine.master_skills)}` Unique Skills Tracked
        
        *EduPathAI leverages advanced NLP to map educational outcomes directly to labor market requirements, providing a transparent, explainable recommendation pipeline.*
        """)

# ------------------------------------------------------------------------
# 5. MAIN ROUTING
# ------------------------------------------------------------------------
current_page = st.session_state.get('nav_page', '🏠 Home')

if current_page == "🏠 Home":
    render_home()
elif current_page == "🎯 Find My Career Path":
    render_find_path()
elif current_page == "🔍 Explore Jobs & Courses":
    render_explore()
elif current_page == "ℹ️ About":
    render_about()
    
# Empty container to push footer down if content is short
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
