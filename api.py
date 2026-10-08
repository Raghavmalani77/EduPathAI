import os
import time
import uuid
from typing import List, Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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
    gpa: float = Field(default=7.5, ge=0.0, le=10.0, description="Academic GPA on a 10-point scale [0.0, 10.0]")
    career_interest: str = "Data Scientist"
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    market: str = "All"
    session_id: Optional[str] = None
    student_id: Optional[str] = None

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/api/stats")
def get_stats():
    # Coupled check for unified_cumulative_dataset (BUG-DATA-01)
    cumulative_path = os.path.join(DATA_DIR, "unified_cumulative_dataset.csv")
    cumulative_records = 0
    if os.path.exists(cumulative_path):
        try:
            cumulative_records = len(pd.read_csv(cumulative_path))
        except Exception:
            cumulative_records = 7381

    return {
        "students_count": len(engine.students_df),
        "jobs_count": len(engine.jobs_df),
        "courses_count": len(engine.courses_df),
        "skills_count": len(engine.master_skills),
        "dataset_mode": "Cumulative Benchmark (7,381 records)" if getattr(engine, "use_cumulative", False) else "Production Primary (480 records)",
        "cumulative_benchmark_records": cumulative_records,
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
        name_val = row.get("Name", "")
        if pd.isna(name_val) or not str(name_val).strip():
            name_val = row["Student_ID"]
        results.append({
            "student_id": str(row["Student_ID"]),
            "name": str(name_val),
            "degree": str(row.get("Degree", "N/A")) if pd.notna(row.get("Degree")) else "N/A",
            "specialisation": str(row.get("Specialisation", "N/A")) if pd.notna(row.get("Specialisation")) else "N/A",
            "education_level": str(row.get("Education_Level", "Undergraduate")) if pd.notna(row.get("Education_Level")) else "Undergraduate",
            "gpa": float(row.get("Assessment_Score", 0.0)) if pd.notna(row.get("Assessment_Score")) else 0.0,
            "career_interest": str(row.get("Career_Interest", "N/A")) if pd.notna(row.get("Career_Interest")) else "N/A"
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
        if student_id == 'CUSTOM_USER':
            # Graceful backward compatibility fallback to latest custom profile (BUG-STATE-01)
            custom_rows = engine.students_df[engine.students_df['Student_ID'].astype(str).str.startswith('CUSTOM_')]
            if not custom_rows.empty:
                row = custom_rows.iloc[-1]
            else:
                raise HTTPException(status_code=404, detail="Student profile not found")
        else:
            raise HTTPException(status_code=404, detail="Student profile not found")
    else:
        row = student_rows.iloc[0]
        
    actual_id = str(row['Student_ID'])
    
    # Calculate learning persona & willingness
    if actual_id.startswith('CUSTOM_') or student_id == 'CUSTOM_USER':
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
            
    name_val = row.get("Name", row["Student_ID"])
    if pd.isna(name_val) or not str(name_val).strip():
        name_val = row["Student_ID"]
        
    return {
        "student_id": actual_id,
        "name": str(name_val),
        "degree": str(row.get("Degree", "N/A")) if pd.notna(row.get("Degree")) else "N/A",
        "specialisation": str(row.get("Specialisation", "N/A")) if pd.notna(row.get("Specialisation")) else "N/A",
        "education_level": str(row.get("Education_Level", "Undergraduate")) if pd.notna(row.get("Education_Level")) else "Undergraduate",
        "gpa": float(row.get("Assessment_Score", 0.0)) if pd.notna(row.get("Assessment_Score")) else 0.0,
        "career_interest": str(row.get("Career_Interest", "N/A")) if pd.notna(row.get("Career_Interest")) else "N/A",
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
    # Support session-scoped or unique ID generation to prevent concurrent overwrites (BUG-STATE-01)
    if req.student_id:
        custom_id = req.student_id
    elif req.session_id:
        custom_id = f"CUSTOM_{req.session_id}"
    else:
        custom_id = f"CUSTOM_{uuid.uuid4().hex[:8]}"
    
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
    # Replace only if same custom_id was already present, preserving all other users (BUG-STATE-01)
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
        loc_val = r.get("Location", "Remote")
        if pd.isna(loc_val) or not str(loc_val).strip():
            loc_val = "Remote"
        comp_val = r.get("Company_Name", "Global Company")
        if pd.isna(comp_val) or not str(comp_val).strip():
            comp_val = "Global Company"
        ind_val = r.get("Industry", "Tech")
        if pd.isna(ind_val) or not str(ind_val).strip():
            ind_val = "Tech"
        cntry_val = r.get("Country", "Global")
        if pd.isna(cntry_val) or not str(cntry_val).strip():
            cntry_val = "Global"
        records.append({
            "job_id": str(r["Job_ID"]),
            "title": str(r["Job_Title"]),
            "company": str(comp_val),
            "industry": str(ind_val),
            "location": str(loc_val),
            "country": str(cntry_val),
            "experience": str(r.get("Experience_Required", "N/A")),
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
