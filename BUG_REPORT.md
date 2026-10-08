# EduPathAI — Formal Software Defect & Bug Report

**Audit Target**: EduPathAI (`https://github.com/Raghavmalani77/EduPathAI.git`)  
**Commit Tested**: `42e006a840de1eda7df1cb42520455ad9c02945f` (`origin/main`)  
**Audit Date**: 2026-10-08  
**Defect Classification Standard**: IEEE 829 / ISO/IEC/IEEE 29119-3  

---

## Defect Summary Dashboard

| Bug ID | Title | Severity | Priority | Affected Component | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **BUG-API-01** | Unhandled NaN Float Value Serialization Causes HTTP 500 Crash on FastAPI Endpoints | **Critical** | **P0** | `api.py` (`/api/students`, `/api/jobs`, `/api/match`) | Open |
| **BUG-STATE-01** | Shared Singleton State Mutation in Custom Profile Onboarding Overwrites Concurrent Users | **High** | **P1** | `api.py` (`POST /api/custom-profile`, `GET /api/student/{id}`) | Open |
| **BUG-VALIDATION-01** | Missing Upper and Lower Bound Validation on Student GPA in Custom Profile API | **Medium** | **P2** | `api.py` (`CustomProfileRequest`) | Open |
| **BUG-DATA-01** | Cumulative Benchmark Dataset (7,381 Records) Uncoupled from Real-Time API Engine | **Low** | **P3** | `recommendation_engine.py` / `api.py` | Open |

---

## Detailed Bug Reports

### BUG-API-01: Unhandled `NaN` Float Serialization Causes HTTP 500 Crash on FastAPI Endpoints

- **Defect Severity**: **Critical**
- **Defect Priority**: **P0** (Blocks student roster picker & job search)
- **Defect Category**: Backend API / JSON Serialization
- **Affected Endpoints**:
  - `GET /api/students` (after any custom profile submission)
  - `GET /api/jobs?search=Machine Learning` (when matched vacancies have missing locations)
  - `GET /api/match/STU_005` (when recommended jobs include postings with null locations)

#### Steps to Reproduce (Scenario A — Post-Custom-Profile Crash)
1. Start the FastAPI backend server: `python -m uvicorn api:app --port 8000`.
2. Issue a GET request to `/api/students`. Notice it returns HTTP 200 with 480 students.
3. Issue a POST request to `/api/custom-profile` with any valid payload (e.g. `{"name": "Alice", "gpa": 8.0, ...}`).
4. Re-issue a GET request to `/api/students`.

#### Expected Behavior
The endpoint returns HTTP 200 OK with the updated list of students (481 records) serialized into valid JSON.

#### Actual Observed Behavior
The endpoint returns **HTTP 500 Internal Server Error**. The endpoint remains completely crashed for all users until the Uvicorn process is manually restarted.

```
Traceback (most recent call last):
  File "starlette/responses.py", line 195, in render
    return json.dumps(content, ensure_ascii=False, allow_nan=False, ...).encode("utf-8")
ValueError: Out of range float values are not JSON compliant
```

#### Steps to Reproduce (Scenario B — Job Search / Match Crash)
1. Query `GET /api/jobs?search=Machine Learning`.
2. In `data/jobs.csv`, 9 records have missing `Location` values (`NaN`).
3. Whenever one of these 9 records is matched and included in the output dictionary, `r.get("Location", "Remote")` returns `float('nan')` instead of `"Remote"`.
4. FastAPI crashes with HTTP 500 (`ValueError: Out of range float values are not JSON compliant`).

#### Root Cause Analysis
1. In `api.py` lines 237–239, `POST /api/custom-profile` appends a dictionary with the key `'Name'` to `engine.students_df`. Because the original 480 rows in `students_employability.csv` do not possess a `'Name'` column, pandas fills `'Name'` with `np.nan` (floating-point NaN) for all 480 rows.
2. In `get_students()`, the code accesses `row.get("Name", row["Student_ID"])`. Because the key `"Name"` now exists in every row, `.get()` returns `float('nan')`. Standard Python `json.dumps()` in Starlette strictly forbids non-finite floats (`NaN`, `Infinity`).
3. Similarly, in `jobs.csv`, missing values in `Location` are parsed as `np.nan`, returning `float('nan')` instead of falling back to default strings.

#### Recommended Code Fix
In `api.py`, sanitize the DataFrames by replacing all NaN values with safe string defaults before serialization, or initialize missing columns upon loading:

```python
# In api.py - get_students()
@app.get("/api/students")
def get_students(career_interest: Optional[str] = None):
    df = engine.students_df.fillna({"Name": "", "Degree": "N/A", "Specialisation": "N/A"})
    if career_interest and career_interest != "All":
        df = df[df["Career_Interest"].str.lower() == career_interest.lower()]
    
    records = []
    for _, r in df.iterrows():
        name_val = r.get("Name", "")
        if pd.isna(name_val) or not str(name_val).strip():
            name_val = r["Student_ID"]
        records.append({
            "student_id": r["Student_ID"],
            "name": str(name_val),
            "degree": str(r.get("Degree", "N/A")),
            "specialisation": str(r.get("Specialisation", "N/A")),
            "career_interest": str(r.get("Career_Interest", "N/A")),
            "gpa": float(r.get("Assessment_Score", 0.0))
        })
    return records

# In api.py - get_jobs()
@app.get("/api/jobs")
def get_jobs(search: Optional[str] = None, country: Optional[str] = None, industry: Optional[str] = None):
    df = engine.jobs_df.fillna({"Location": "Remote", "Company_Name": "Global Tech", "Industry": "Tech"})
    # ... rest of filter logic ...
```

---

### BUG-STATE-01: Shared Singleton State Mutation Overwrites Concurrent Users

- **Defect Severity**: **High**
- **Defect Priority**: **P1**
- **Defect Category**: Concurrency / State Isolation
- **Affected Endpoints**: `POST /api/custom-profile`, `GET /api/student/CUSTOM_USER`

#### Steps to Reproduce
1. User A (Alice, B.Tech CS, GPA 8.0) submits a profile via `POST /api/custom-profile`.
2. Concurrently or shortly after, User B (Bob, B.Des UI, GPA 7.5) submits a profile via `POST /api/custom-profile`.
3. Query `GET /api/student/CUSTOM_USER`.

#### Expected Behavior
Each user's custom profile exists in an isolated session scope, or receives a unique session identifier (e.g. `CUSTOM_USER_a1b2c3d4`), preventing cross-tenant data collisions.

#### Actual Observed Behavior
The single global in-memory DataFrame `engine.students_df` is mutated directly. User A's profile is completely erased and replaced by User B's profile under the shared ID `CUSTOM_USER`.

#### Root Cause Analysis
In `api.py` lines 197 and 238–239:
```python
custom_id = "CUSTOM_USER"
engine.students_df = engine.students_df[engine.students_df['Student_ID'] != custom_id]
engine.students_df = pd.concat([engine.students_df, custom_row], ignore_index=True)
```
The application maintains a single in-process singleton instance of `RecommendationEngine`. Writing directly to `engine.students_df` introduces race conditions and cross-user data loss in multi-user environments.

#### Recommended Code Fix
Generate a session UUID for each custom onboarding request, or compute recommendations dynamically on the transient profile without mutating the global roster:

```python
import uuid

@app.post("/api/custom-profile")
def create_custom_profile(req: CustomProfileRequest):
    custom_id = f"CUSTOM_{uuid.uuid4().hex[:8]}"
    # Build vector transiently
    # ...
    # Return recommendations for custom_id directly without mutating global engine.students_df
```

---

### BUG-VALIDATION-01: Missing GPA Numeric Boundary Enforcement

- **Defect Severity**: **Medium**
- **Defect Priority**: **P2**
- **Defect Category**: Input Validation & Integrity
- **Affected Endpoints**: `POST /api/custom-profile`

#### Steps to Reproduce
1. Send a POST request to `/api/custom-profile` with `"gpa": 999.0`.
2. Send another POST request with `"gpa": -4.5`.

#### Expected Behavior
The FastAPI Pydantic validator should reject the payload with **HTTP 422 Unprocessable Entity**, specifying that GPA must fall within a valid academic range `[0.0, 10.0]`.

#### Actual Observed Behavior
The backend returns **HTTP 200 OK**, accepting impossible academic GPAs (`999.0` and `-4.5`) without validation.

#### Root Cause Analysis
In `api.py` lines 42–50:
```python
class CustomProfileRequest(BaseModel):
    name: str = "Custom Student"
    degree: str = "B.Tech"
    specialisation: str = "Computer Science"
    gpa: float = 7.5  # <-- Missing Field(ge=0.0, le=10.0) constraint
```

#### Recommended Code Fix
Import `Field` from `pydantic` and enforce boundary constraints:
```python
from pydantic import BaseModel, Field

class CustomProfileRequest(BaseModel):
    name: str = "Custom Student"
    degree: str = "B.Tech"
    specialisation: str = "Computer Science"
    gpa: float = Field(default=7.5, ge=0.0, le=10.0, description="Academic GPA on a 10-point scale")
    # ...
```

---

### BUG-DATA-01: Cumulative Benchmark Dataset (7,381 Records) Uncoupled from Live API

- **Defect Severity**: **Low / Architectural Finding**
- **Defect Priority**: **P3**
- **Defect Category**: Data Pipeline & Documentation
- **Affected Components**: `recommendation_engine.py`, `api.py`

#### Steps to Reproduce
1. Inspect `data/unified_cumulative_dataset.csv` (contains 7,381 records).
2. Inspect `recommendation_engine.py` and `api.py`.
3. Query `GET /api/stats`.

#### Expected Behavior
The real-time recommendation engine dynamically queries all 7,381 unified student records, OR documentation clearly specifies that the 6,901 PS2 records are designated strictly for offline benchmark training.

#### Actual Observed Behavior
The real-time application (`RecommendationEngine`) only indexes `students_employability.csv` (480 records). The 6,901 PS2 records in `unified_cumulative_dataset.csv` are used solely in offline MLflow benchmarking scripts (`benchmark_ps2.py`).

#### Recommended Fix
Add a configuration flag in `recommendation_engine.py`:
```python
def __init__(self, data_dir="data", use_cumulative=False):
    self.data_dir = data_dir
    self.use_cumulative = use_cumulative
    self.students_file = "unified_cumulative_dataset.csv" if use_cumulative else "students_employability.csv"
```
And document the dual-mode architecture in `README.md`.
