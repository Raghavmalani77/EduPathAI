# Agent Notes for EduPathAI Project

## ⚠️ IMPORTANT: How to Run This Project

**Always start the React frontend, NOT Streamlit.**

### Start order (run all three):
```powershell
# 1. Backend API (FastAPI on port 8000)
cd c:\Users\rudra\Desktop\raghavproject
venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000

# 2. React Frontend (Vite on port 5173)
cd c:\Users\rudra\Desktop\raghavproject\frontend
node node_modules\vite\bin\vite.js

# 3. (Optional) Streamlit legacy UI - only if explicitly asked
cd c:\Users\rudra\Desktop\raghavproject
venv\Scripts\python.exe -m streamlit run app.py
```

### URLs
| Service | URL | Notes |
|---|---|---|
| ⚛️ React Frontend | http://localhost:5173 | **Primary UI** |
| 🔌 Python API | http://127.0.0.1:8000 | FastAPI backend |
| 🐍 Streamlit | http://localhost:8501 | Legacy, don't start unless asked |

### Notes on npx / .bin scripts
- `npx` is blocked by Windows execution policy
- Use `node node_modules\vite\bin\vite.js` to start Vite
- Use `venv\Scripts\python.exe -m <module>` for all Python tools

---

## Recommendation Engine — Key Fixes Applied

### Fix 1: Figma/UI course buried for Frontend Engineer gaps (Nov 2026)
**File:** `recommendation_engine.py` → `get_skill_gap_and_courses()`
**Problem:** Old scoring `exact_score = count * 2.0` meant broad multi-skill courses (React covering 3/5 gaps) always outranked specialized single-skill courses (Figma for UI Design).
**Fix:** Per-gap champion election (Steps A→D) + F1 normalized scoring + champion guarantee ordering so each gap's best course is always visible in top results.

### Fix 2: AI Engineer matched to .NET Web Developer (Nov 2026)
**File:** `recommendation_engine.py` → `match_jobs()`
**Problem:** Cosine similarity on raw skill vectors ignores the student's `Target_Role`. A student with Python/SQL skills matches .NET Web Developer (also uses Python/SQL) higher than AI Engineer jobs (which need ML/AI/Deep Learning — semantically related but not exact string matches).
**Fix:** Added target-role affinity boost — jobs whose title/industry semantically aligns with the student's declared target role get a score multiplier before ranking.
