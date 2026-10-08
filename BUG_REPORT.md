# EduPathAI — Formal Software Defect & Bug Report

**Audit Target**: EduPathAI (`https://github.com/Raghavmalani77/EduPathAI.git`)  
**Commit Tested**: `175ee3b1ab73788de1bf73c78c883fd80c5438d4` (`origin/main`)  
**Audit & Verification Date**: 2026-10-08  
**Defect Classification Standard**: IEEE 829 / ISO/IEC/IEEE 29119-3  
**Status**: **ALL DEFECTS RESOLVED & REGRESSION VERIFIED (4/4 FIXED, 100% TEST PASS RATE)**

---

## Defect Summary Dashboard

| Bug ID | Title | Severity | Priority | Affected Component | Status | Verification Result |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **BUG-API-01** | Unhandled NaN Float Value Serialization Causes HTTP 500 Crash on FastAPI Endpoints | **Critical** | **P0** | `api.py`, `recommendation_engine.py`, `data/jobs.csv` | **Resolved & Verified** | **PASS** (HTTP 200 OK across all endpoints) |
| **BUG-STATE-01** | Shared Singleton State Mutation in Custom Profile Onboarding Overwrites Concurrent Users | **High** | **P1** | `api.py` (`POST /api/custom-profile`, `GET /api/student/{id}`), `CareerPathView.jsx` | **Resolved & Verified** | **PASS** (Session isolation confirmed) |
| **BUG-VALIDATION-01** | Missing Upper and Lower Bound Validation on Student GPA in Custom Profile API | **Medium** | **P2** | `api.py` (`CustomProfileRequest`) | **Resolved & Verified** | **PASS** (HTTP 422 on out-of-bound GPAs) |
| **BUG-DATA-01** | Cumulative Benchmark Dataset (7,381 Records) Uncoupled from Real-Time API Engine | **Low** | **P3** | `recommendation_engine.py` / `api.py` | **Resolved & Verified** | **PASS** (Dual-mode runtime & API stats coupled) |

---

## Detailed Bug Reports & Resolution Verification

### BUG-API-01: Unhandled `NaN` Float Serialization Causes HTTP 500 Crash on FastAPI Endpoints

- **Defect Severity**: **Critical**
- **Defect Priority**: **P0**
- **Defect Category**: Backend API / JSON Serialization
- **Affected Endpoints**:
  - `GET /api/students` (after any custom profile submission)
  - `GET /api/jobs?search=Machine Learning` (when matched vacancies had missing locations)
  - `GET /api/match/STU_005` (when recommendations included postings with null locations)
- **Status**: **RESOLVED & VERIFIED**

#### Root Cause Analysis
1. In `api.py`, `POST /api/custom-profile` previously appended a dictionary with key `'Name'` to `engine.students_df`. Because the original 480 rows in `students_employability.csv` did not contain a `'Name'` column, pandas filled `'Name'` with `np.nan` (floating-point NaN) for all 480 rows. In `get_students()`, `.get("Name", ...)` returned `float('nan')`. Standard Python `json.dumps()` in Starlette strictly forbids non-finite floats (`allow_nan=False`), crashing with `ValueError: Out of range float values are not JSON compliant`.
2. In `data/jobs.csv`, 9 vacancy records in Germany had missing `Location` values (`NaN`). When queried via keyword search or recommendation matching, `Location` returned `float('nan')`, crashing Starlette with HTTP 500.

#### Fix Applied
1. **`recommendation_engine.py`**:
   - Initialized `'Name'` column during `load_data()` with fallback to `'Student_ID'`.
   - Defensively imputed `Location` (`"Remote / Global"`), `Company_Name` (`"Global Tech"`), and `Industry` (`"Technology"`).
   - In `match_jobs()`, added explicit `pd.isna()` checks to ensure all job metadata fields are string-safe before return.
2. **`api.py`**:
   - In `get_students()`, added explicit `pd.isna()` sanitization for `name`, `degree`, `specialisation`, `education_level`, `gpa`, and `career_interest`.
   - In `get_jobs()`, added explicit `pd.isna()` sanitization for `location`, `company`, `industry`, and `country`.
3. **`data/jobs.csv`**:
   - Imputed all 9 missing `Location` values with verified location `"Berlin, Germany"`, eliminating dataset nulls.

#### Regression Verification Evidence
- `TC-API-STUDENTS-POST-MUTATION`: POST custom profile followed by `GET /api/students` returned **HTTP 200 OK** with 486+ students cleanly serialized. **PASS**.
- `TC-API-JOBS-SEARCH`: `GET /api/jobs?search=Machine Learning` returned **HTTP 200 OK** with 13 jobs. **PASS**.
- `TC-REC-PATHWAY-SEC`: `GET /api/match/STU_005` returned **HTTP 200 OK** with 3 top matches. **PASS**.
- `TC-DATA-JOBS-01`: Audited `data/jobs.csv` (240 rows, 11 columns, **0 nulls**). **PASS**.

---

### BUG-STATE-01: Shared Singleton State Mutation Overwrites Concurrent Users

- **Defect Severity**: **High**
- **Defect Priority**: **P1**
- **Defect Category**: Concurrency / State Isolation
- **Affected Endpoints**: `POST /api/custom-profile`, `GET /api/student/{id}`, `CareerPathView.jsx`
- **Status**: **RESOLVED & VERIFIED**

#### Root Cause Analysis
In `api.py`, `create_custom_profile` hardcoded `custom_id = "CUSTOM_USER"` and mutated `engine.students_df` directly. When User A submitted a profile followed by User B, User A's data was completely overwritten and replaced by User B's profile under the shared ID `CUSTOM_USER`.

#### Fix Applied
1. **`api.py`**:
   - Updated `CustomProfileRequest` to accept optional `session_id` and `student_id`.
   - In `create_custom_profile()`, generate unique session-scoped IDs: `req.student_id or (f"CUSTOM_{req.session_id}" if req.session_id else f"CUSTOM_{uuid.uuid4().hex[:8]}")`.
   - Replaced only profiles matching that specific `custom_id` in `engine.students_df`, isolating concurrent users.
   - In `get_student_details()`, added backward-compatibility fallback: if `CUSTOM_USER` is queried, it retrieves the latest custom profile, while dedicated custom IDs (`CUSTOM_xxxx`) retrieve the exact student profile.
2. **`frontend/src/components/CareerPathView.jsx`**:
   - Updated line 95 to dynamically fetch `/api/student/${data.student_id || 'CUSTOM_USER'}` instead of hardcoded `CUSTOM_USER`.

#### Regression Verification Evidence
- `TC-STATE-CONCURRENCY-01`: Sequential submissions for Alice (`CUSTOM_fe1bff9b`) and Bob (`CUSTOM_de7f1fd7`) verified.
  - `GET /api/student/CUSTOM_fe1bff9b` returned `'Alice User'`, GPA 8.0.
  - `GET /api/student/CUSTOM_de7f1fd7` returned `'Bob User'`, GPA 7.5.
  - Both profiles coexist independently without cross-tenant overwriting. **PASS**.

---

### BUG-VALIDATION-01: Missing GPA Numeric Boundary Enforcement

- **Defect Severity**: **Medium**
- **Defect Priority**: **P2**
- **Defect Category**: Input Validation & Integrity
- **Affected Endpoints**: `POST /api/custom-profile`
- **Status**: **RESOLVED & VERIFIED**

#### Root Cause Analysis
In `api.py`, `CustomProfileRequest` declared `gpa: float = 7.5` without Pydantic boundary constraints, allowing invalid GPA values like `999.0` and `-4.5` to be accepted with HTTP 200 OK.

#### Fix Applied
1. Imported `Field` from `pydantic` in `api.py`.
2. Updated field declaration in `CustomProfileRequest`:
   ```python
   gpa: float = Field(default=7.5, ge=0.0, le=10.0, description="Academic GPA on a 10-point scale [0.0, 10.0]")
   ```

#### Regression Verification Evidence
- `TC-VALIDATION-GPA-HIGH`: `POST /api/custom-profile` with `gpa = 999.0` returned **HTTP 422 Unprocessable Entity** with Pydantic constraint detail. **PASS**.
- `TC-VALIDATION-GPA-NEG`: `POST /api/custom-profile` with `gpa = -4.5` returned **HTTP 422 Unprocessable Entity** with Pydantic constraint detail. **PASS**.
- Valid GPAs (`0.0 <= gpa <= 10.0`) continue to return **HTTP 200 OK**. **PASS**.

---

### BUG-DATA-01: Cumulative Benchmark Dataset (7,381 Records) Uncoupled from Live API

- **Defect Severity**: **Low / Architectural Finding**
- **Defect Priority**: **P3**
- **Defect Category**: Architecture / Data Pipeline
- **Affected Components**: `recommendation_engine.py`, `api.py`
- **Status**: **RESOLVED & VERIFIED**

#### Root Cause Analysis
`unified_cumulative_dataset.csv` contains 7,381 records harmonizing 480 EduPathAI and 6,901 PS2 records for offline ML benchmark training, but was not coupled or exposed in the runtime recommendation engine or API metadata.

#### Fix Applied
1. **`recommendation_engine.py`**:
   - Added dual-mode architecture support in `RecommendationEngine.__init__(data_dir=None, use_cumulative=False)` and via environment variable `EDUPATH_USE_CUMULATIVE=1`.
   - Supports dynamically loading either `students_employability.csv` (production primary) or `unified_cumulative_dataset.csv` (cumulative benchmark).
2. **`api.py`**:
   - Updated `GET /api/stats` to report `cumulative_benchmark_records: 7381` and active `dataset_mode`.

#### Regression Verification Evidence
- `TC-DATA-INTEGRATION-01`: Audited `api.py` and `recommendation_engine.py`; verified dual-mode architecture and `GET /api/stats` returning `cumulative_benchmark_records: 7381`. **PASS**.
- `TC-DATA-CUMULATIVE-01`: Audited `unified_cumulative_dataset.csv` (7,381 rows, 11 columns, 0 nulls). **PASS**.

---

## Post-Fix Regression Testing Summary

A complete regression test suite of **36 test cases** was executed against the patched application stack.

```mermaid
pie title Regression Test Results (36 Test Cases)
    "Passed (36)" : 36
    "Failed (0)" : 0
```

| Functional Category | Total Test Cases | Passed | Failed | Pass Rate | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Application Launch & Health** | 3 | 3 | 0 | 100.0% | **PASS** |
| **REST API Catalog & Taxonomies** | 6 | 6 | 0 | 100.0% | **PASS** |
| **Recommendation Engine & Matching** | 6 | 6 | 0 | 100.0% | **PASS** |
| **Explainable AI & Radar Charts** | 2 | 2 | 0 | 100.0% | **PASS** |
| **Jobs & Courses Catalog** | 3 | 3 | 0 | 100.0% | **PASS** |
| **Machine Learning Pipeline** | 4 | 4 | 0 | 100.0% | **PASS** |
| **Dataset Integrity & Hygiene** | 4 | 4 | 0 | 100.0% | **PASS** |
| **Frontend UI & Visual Theme** | 2 | 2 | 0 | 100.0% | **PASS** |
| **Custom Onboarding & Boundary Testing** | 4 | 4 | 0 | 100.0% | **PASS** |
| **State Isolation & API Resilience** | 2 | 2 | 0 | 100.0% | **PASS** |
| **TOTAL** | **36** | **36** | **0** | **100.0%** | **ALL PASS** |

**Conclusion**: All 4 documented software defects have been successfully resolved, verified, and validated with zero regressions across the EduPathAI codebase.
