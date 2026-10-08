import os
import time
from typing import List, Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recommendation_engine import RecommendationEngine

app = FastAPI(title="EduPathAI API", version="2.0.0")

# Enable CORS for React frontend (Vite defaults to 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

print("Initializing EduPathAI Engine...")
engine = RecommendationEngine(data_dir=DATA_DIR)
engine.load_data()
engine.build_vectors()
engine.perform_clustering()
print("EduPathAI Engine ready!")

class CustomProfileRequest(BaseModel):
    name: str = "Jane Doe"
    degree: str = "B.Tech"
    specialisation: str = "Computer Science"
    gpa: float = 7.5
    career_interest: str = "Data Scientist"
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    market: str = "All"

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/api/stats")
def get_stats():
    return {
        "students_count": len(engine.students_df),
        "jobs_count": len(engine.jobs_df),
        "courses_count": len(engine.courses_df),
        "skills_count": len(engine.master_skills),
        "embedding_model": "Sentence-BERT (all-MiniLM-L6-v2)" if getattr(engine.semantic_matcher, "is_transformer_active", False) else "Domain Semantic Vector Fallback"
    }

@app.get("/api/filters")
def get_filters():
    interests = sorted([str(x) for x in engine.students_df['Career_Interest'].dropna().unique()])
    markets = sorted([str(x) for x in engine.jobs_df['Country'].dropna().unique()])
    degrees = sorted([str(x) for x in engine.students_df['Degree'].dropna().unique()])
    specialisations = sorted([str(x) for x in engine.students_df['Specialisation'].dropna().unique()]) if 'Specialisation' in engine.students_df.columns else []
    
    return {
        "career_interests": interests,
        "markets": markets,
        "degrees": degrees,
        "specialisations": specialisations,
        "master_skills": engine.master_skills
    }

@app.get("/api/students")
def get_students(career_interest: Optional[str] = Query(None)):
    df = engine.students_df
    if career_interest and career_interest != "All":
        df = df[df['Career_Interest'] == career_interest]
        
    results = []
    for _, row in df.iterrows():
        results.append({
            "student_id": row["Student_ID"],
            "name": row.get("Name", row["Student_ID"]),
            "degree": row.get("Degree", "N/A"),
            "specialisation": row.get("Specialisation", "N/A"),
            "education_level": row.get("Education_Level", "Undergraduate"),
            "gpa": float(row.get("Assessment_Score", 0.0)),
            "career_interest": row.get("Career_Interest", "N/A")
        })
    return results

def compute_radar_skills(student_id: str, job_id: str):
    s_rows = engine.students_df[engine.students_df['Student_ID'] == student_id]
    j_rows = engine.jobs_df[engine.jobs_df['Job_ID'] == job_id]
    if s_rows.empty or j_rows.empty:
        return []
        
    s_vec = np.array(s_rows.iloc[0]['Skill_Vector'])
    j_vec = np.array(j_rows.iloc[0]['Skill_Vector'])
    
    importance = s_vec + j_vec
    top_indices = np.argsort(importance)[::-1][:7]
    
    radar = []
    for idx in top_indices:
        skill_name = engine.master_skills[idx]
        radar.append({
            "skill": skill_name,
            "student_score": round(float(s_vec[idx] * 100), 1),
            "job_score": round(float(j_vec[idx] * 100), 1)
        })
    return radar

@app.get("/api/student/{student_id}")
def get_student_details(student_id: str):
    student_rows = engine.students_df[engine.students_df['Student_ID'] == student_id]
    if student_rows.empty:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    row = student_rows.iloc[0]
    
    # Calculate learning persona & willingness
    if student_id == 'CUSTOM_USER':
        cluster_name = "Custom Explorer"
        wtl = 85.0
    else:
        try:
            cluster_name = engine.get_student_cluster_name(student_id)
            wtl = engine.calculate_willingness_to_learn(student_id)
        except Exception:
            cluster_name = "Standard Learner"
            wtl = 50.0

    # Parse skills
    skills_list = []
    profs_str = str(row.get("Skill_Proficiencies", ""))
    if profs_str and pd.notna(profs_str):
        for s in profs_str.split(","):
            s = s.strip()
            if not s:
                continue
            if ":" in s:
                parts = s.split(":")
                name = parts[0].strip()
                try:
                    pct = float(parts[1].strip()) * 100
                except:
                    pct = 50.0
            else:
                name = s
                pct = 50.0
            skills_list.append({"name": name, "proficiency": round(pct, 1)})
            
    return {
        "student_id": row["Student_ID"],
        "name": row.get("Name", row["Student_ID"]),
        "degree": row.get("Degree", "N/A"),
        "specialisation": row.get("Specialisation", "N/A"),
        "education_level": row.get("Education_Level", "Undergraduate"),
        "gpa": float(row.get("Assessment_Score", 0.0)),
        "career_interest": row.get("Career_Interest", "N/A"),
        "cluster_name": cluster_name,
        "willingness_to_learn": wtl,
        "skills": skills_list
    }

@app.get("/api/match/{student_id}")
def match_student(student_id: str, market: str = "All", top_n: int = 3):
    student_rows = engine.students_df[engine.students_df['Student_ID'] == student_id]
    if student_rows.empty:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    matches = engine.match_jobs(student_id, top_n=top_n, country_filter=market)
    
    enriched_matches = []
    for job in matches:
        job_id = job["Job_ID"]
        gaps, courses = engine.get_skill_gap_and_courses(student_id, job_id)
        explanation = engine.generate_explanation(student_id, job_id, courses)
        radar = compute_radar_skills(student_id, job_id)
        
        enriched_matches.append({
            "job": job,
            "skill_gaps": gaps,
            "recommended_courses": courses[:3],
            "explanation": explanation,
            "radar_skills": radar
        })
        
    return {
        "student_id": student_id,
        "market": market,
        "matches": enriched_matches
    }

@app.post("/api/custom-profile")
def create_custom_profile(req: CustomProfileRequest):
    custom_id = "CUSTOM_USER"
    
    tech_skills_clean = [s.strip() for s in req.technical_skills if s.strip()]
    soft_skills_clean = [s.strip() for s in req.soft_skills if s.strip()]
    
    # 0.85 for selected technical, 0.90 for soft
    prof_dict = {s.lower(): 0.85 for s in tech_skills_clean}
    prof_dict.update({s.lower(): 0.90 for s in soft_skills_clean})
    
    skill_profs_str = ", ".join([f"{s}:0.85" for s in tech_skills_clean] + [f"{s}:0.90" for s in soft_skills_clean])
    
    # Build vector
    vector = []
    for skill in engine.master_skills:
        s_lower = skill.lower()
        if s_lower in prof_dict:
            vector.append(prof_dict[s_lower])
        elif any(s_lower in ts.lower() for ts in tech_skills_clean):
            vector.append(0.70)
        else:
            vector.append(0.0)
            
    custom_row_dict = {
        'Student_ID': custom_id,
        'Name': req.name,
        'Gender': 'Not Specified',
        'Education_Level': 'Undergraduate',
        'Degree': req.degree,
        'Specialisation': req.specialisation,
        'Graduation_Year': 2025,
        'Technical_Skills': ', '.join(tech_skills_clean),
        'Soft_Skills': ', '.join(soft_skills_clean),
        'Skill_Proficiencies': skill_profs_str,
        'Projects': '',
        'Certifications': '',
        'Assessment_Score': req.gpa,
        'Career_Interest': req.career_interest,
        'Skill_Vector': vector
    }
    
    custom_row = pd.DataFrame([custom_row_dict])
    engine.students_df = engine.students_df[engine.students_df['Student_ID'] != custom_id]
    engine.students_df = pd.concat([engine.students_df, custom_row], ignore_index=True)
    
    # Run match
    return match_student(custom_id, market=req.market, top_n=3)

@app.get("/api/jobs")
def get_jobs(search: Optional[str] = None, country: Optional[str] = None, industry: Optional[str] = None):
    df = engine.jobs_df
    if country and country != "All":
        df = df[df["Country"].str.lower() == country.lower()]
    if industry and industry != "All":
        df = df[df["Industry"].str.lower() == industry.lower()]
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]
        
    records = []
    for _, r in df.head(100).iterrows():
        records.append({
            "job_id": r["Job_ID"],
            "title": r["Job_Title"],
            "company": r.get("Company_Name", "Global Company"),
            "industry": r.get("Industry", "Tech"),
            "location": r.get("Location", "Remote"),
            "country": r.get("Country", "Global"),
            "experience": r.get("Experience_Required", "N/A"),
            "skills": [s.strip() for s in str(r.get("Skills_Required", "")).split(",") if s.strip()]
        })
    return records

@app.get("/api/courses")
def get_courses(search: Optional[str] = None, platform: Optional[str] = None):
    df = engine.courses_df
    if platform and platform != "All":
        df = df[df["Platform"].str.lower() == platform.lower()]
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]
        
    records = []
    for _, r in df.iterrows():
        records.append({
            "course_id": r["Course_ID"],
            "title": r["Course_Title"],
            "platform": r.get("Platform", "Online"),
            "duration_hours": r.get("Duration_Hours", 20),
            "description": r.get("Description", ""),
            "skills_developed": [s.strip() for s in str(r.get("Skills_Developed", "")).split(",") if s.strip()]
        })
    return records

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
