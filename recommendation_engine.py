import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from qwen_explainer import QwenExplainer

class DenseSemanticMatcher:
    """
    Dense Semantic Embedding & Vector Search Module using Sentence-BERT (all-MiniLM-L6-v2)
    with a robust Domain Semantic Vector fallback.
    
    Transforms skill requirements and course curricula into dense vectors
    to resolve vocabulary mismatch (e.g., 'PyTorch' <-> 'Deep Learning & Neural Networks',
    'PostgreSQL' <-> 'SQL & Database Management', 'Kubernetes' <-> 'DevOps & Docker').
    """
    def __init__(self, data_dir=None):
        self.data_dir = data_dir
        self.model = None
        self.is_transformer_active = False
        self.course_embeddings = None
        self.course_docs = []
        self.course_ids = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        # Domain Tech Ontology: Maps specific technologies and terms to conceptual clusters
        self.domain_ontology = {
            "pytorch": ["deep learning", "neural networks", "machine learning", "ai/ml", "python"],
            "tensorflow": ["deep learning", "neural networks", "machine learning", "ai/ml", "python"],
            "keras": ["deep learning", "neural networks", "machine learning", "python"],
            "deep learning": ["neural networks", "pytorch", "tensorflow", "ai/ml", "machine learning"],
            "neural networks": ["deep learning", "pytorch", "tensorflow", "ai/ml", "machine learning"],
            "computer vision": ["deep learning", "neural networks", "ai/ml", "opencv", "python"],
            "nlp": ["natural language processing", "deep learning", "machine learning", "ai/ml"],
            "natural language processing": ["nlp", "deep learning", "machine learning", "text analytics"],
            "kubernetes": ["docker", "devops", "ci/cd", "cloud", "aws", "azure", "linux"],
            "k8s": ["kubernetes", "docker", "devops", "cloud"],
            "docker": ["kubernetes", "devops", "ci/cd", "cloud", "linux"],
            "ci/cd": ["devops", "docker", "kubernetes", "jenkins", "cloud"],
            "jenkins": ["devops", "ci/cd", "docker", "kubernetes"],
            "postgresql": ["sql", "database management", "rdbms", "database"],
            "postgres": ["sql", "database management", "rdbms", "database"],
            "mysql": ["sql", "database management", "rdbms", "database"],
            "mongodb": ["database management", "nosql", "database"],
            "rdbms": ["sql", "database management", "database", "relational database"],
            "database": ["database management", "sql", "postgresql"],
            "aws": ["cloud", "cloud computing", "azure", "docker"],
            "azure": ["cloud", "cloud computing", "aws", "docker"],
            "gcp": ["cloud", "cloud computing", "aws", "azure"],
            "cloud": ["aws", "azure", "docker", "kubernetes"],
            "react": ["frontend development", "web development", "javascript", "html", "css"],
            "angular": ["frontend development", "web development", "javascript"],
            "vue": ["frontend development", "web development", "javascript"],
            "node.js": ["backend development", "javascript", "rest apis", "web development"],
            "node": ["backend development", "javascript", "rest apis", "web development"],
            "express": ["backend development", "node.js", "rest apis", "javascript"],
            "django": ["backend development", "python", "web development", "rest apis"],
            "fastapi": ["backend development", "python", "rest apis"],
            "rest apis": ["backend development", "node.js", "web development"],
            "figma": ["ui design", "ux research", "wireframing", "prototyping"],
            "ui/ux": ["figma", "ui design", "ux research", "prototyping"],
            "power bi": ["business analytics", "data visualisation", "tableau", "excel", "data analytics"],
            "tableau": ["business analytics", "data visualisation", "power bi", "excel", "data analytics"],
            "scrum": ["agile/scrum", "product strategy", "product management", "roadmapping"],
            "agile": ["agile/scrum", "product strategy", "product management"],
            "penetration testing": ["cybersecurity", "network security", "linux", "cryptography"],
            "network security": ["cybersecurity", "penetration testing", "linux", "cryptography"],
            "seo": ["digital marketing", "content strategy", "social media analytics"],
            "financial modeling": ["finance", "excel", "accounting", "valuation"]
        }
        
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.is_transformer_active = True
            print("Successfully loaded Sentence-BERT model: all-MiniLM-L6-v2")
        except Exception as e:
            self.model = None
            self.is_transformer_active = False
            print(f"SentenceTransformer not initialized ({e}). Using Domain Semantic Vector fallback.")

    def fit(self, courses_df):
        self.course_ids = courses_df["Course_ID"].tolist()
        self.course_docs = []
        for _, c in courses_df.iterrows():
            skills_dev = str(c.get("Skills_Developed", ""))
            doc = f"{c['Course_Title']}. Skills: {skills_dev}. {c.get('Description', '')}"
            self.course_docs.append(doc)
            
        if self.is_transformer_active and self.model is not None:
            try:
                embs = self.model.encode(self.course_docs, normalize_embeddings=True)
                self.course_embeddings = np.array(embs, dtype=np.float32)
            except Exception as e:
                print(f"Failed to encode course embeddings with S-BERT: {e}")
                self.is_transformer_active = False

        # Build Domain Semantic TF-IDF representations as fallback & hybrid support
        self.tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        augmented_docs = []
        for doc, (_, c) in zip(self.course_docs, courses_df.iterrows()):
            skills_tokens = [s.strip().lower() for s in str(c.get("Skills_Developed", "")).split(",")]
            synonyms = []
            for sk in skills_tokens:
                if sk in self.domain_ontology:
                    synonyms.extend(self.domain_ontology[sk])
            aug = doc + " " + " ".join(synonyms)
            augmented_docs.append(aug)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(augmented_docs)

    def compute_semantic_similarity(self, gap_skill, course_idx, course_row):
        g_clean = gap_skill.strip().lower()
        course_skills = [s.strip().lower() for s in str(course_row["Skills_Developed"]).split(",") if s.strip()]
        
        # 1. Exact string match has perfect similarity 1.0
        if g_clean in course_skills:
            return 1.0, gap_skill.title()
            
        sim_scores = []
        
        # 2. Check if Sentence-BERT Transformer is active
        if self.is_transformer_active and self.model is not None and self.course_embeddings is not None:
            try:
                gap_emb = self.model.encode([g_clean], normalize_embeddings=True)[0]
                doc_sim = float(np.dot(self.course_embeddings[course_idx], gap_emb))
                
                skill_embs = self.model.encode(course_skills, normalize_embeddings=True)
                individual_sims = np.dot(skill_embs, gap_emb)
                best_skill_idx = int(np.argmax(individual_sims))
                best_skill_sim = float(individual_sims[best_skill_idx])
                
                combined_sim = max(doc_sim * 0.85 + best_skill_sim * 0.15, best_skill_sim)
                sim_scores.append((combined_sim, course_skills[best_skill_idx].title()))
            except Exception:
                pass
                
        # 3. Domain Ontology & Vector Search
        target_synonyms = self.domain_ontology.get(g_clean, [])
        for c_sk in course_skills:
            if c_sk in target_synonyms:
                sim_scores.append((0.88, c_sk.title()))
            if g_clean in self.domain_ontology.get(c_sk, []):
                sim_scores.append((0.85, c_sk.title()))
                
        # TF-IDF Cosine Similarity
        if self.tfidf_vectorizer is not None and self.tfidf_matrix is not None:
            gap_query = g_clean + " " + " ".join(target_synonyms)
            gap_vec = self.tfidf_vectorizer.transform([gap_query])
            tfidf_sim = float((gap_vec * self.tfidf_matrix[course_idx].T).toarray()[0][0])
            if tfidf_sim > 0.25:
                scaled_score = min(0.92, 0.55 + (tfidf_sim * 0.5))
                sim_scores.append((scaled_score, course_row["Course_Title"]))
                
        if sim_scores:
            sim_scores.sort(key=lambda x: x[0], reverse=True)
            return sim_scores[0][0], sim_scores[0][1]
            
        return 0.0, None

    def get_mode_name(self):
        if self.is_transformer_active:
            return "Sentence-BERT (all-MiniLM-L6-v2)"
        return "Domain Semantic Vector Search"

class RecommendationEngine:
    def __init__(self, data_dir=None, use_cumulative=True):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir
            
        # Dual-mode architecture support: defaults to full cumulative enterprise catalog (7,381 records)
        env_cumulative = os.environ.get("EDUPATH_USE_CUMULATIVE", "1").lower() in ("1", "true", "yes")
        self.use_cumulative = use_cumulative if use_cumulative is not None else env_cumulative
        self.students_filename = "unified_cumulative_dataset.csv" if self.use_cumulative else "students_employability.csv"
        
        self.jobs_df = None
        self.courses_df = None
        self.students_df = None
        self.engagement_df = None
        
        self.master_skills = []
        self.student_behavior_profiles = None
        self.scaler = StandardScaler()
        self.kmeans = None
        self.cluster_labels = {
            0: "High Engagement & Outstanding Performance",
            1: "Moderate Engagement & Steady Progress",
            2: "Low Engagement & Critical Academic Support Needed"
        }
        self.semantic_matcher = DenseSemanticMatcher(data_dir=self.data_dir)
        self.qwen_explainer = QwenExplainer()

    def set_dataset_mode(self, use_cumulative: bool):
        """Dynamic toggle between Cumulative (7,381) and Core (480) datasets"""
        self.use_cumulative = use_cumulative
        self.students_filename = "unified_cumulative_dataset.csv" if self.use_cumulative else "students_employability.csv"
        self.load_data()
        self.build_vectors()
        self.perform_clustering()

    def load_data(self):
        print(f"Loading datasets (Mode: {'Cumulative 7,381 records' if self.use_cumulative else 'Core 480 records'})...")
        self.jobs_df = pd.read_csv(os.path.join(self.data_dir, "jobs.csv"))
        # Impute missing job metadata to prevent NaN serialization errors (BUG-API-01)
        self.jobs_df["Location"] = self.jobs_df["Location"].fillna("Remote / Global")
        self.jobs_df["Company_Name"] = self.jobs_df["Company_Name"].fillna("Global Tech")
        self.jobs_df["Industry"] = self.jobs_df["Industry"].fillna("Technology")
        
        self.courses_df = pd.read_csv(os.path.join(self.data_dir, "courses.csv"))
        
        students_path = os.path.join(self.data_dir, self.students_filename)
        if not os.path.exists(students_path) and self.use_cumulative:
            print(f"Warning: {students_path} not found. Falling back to students_employability.csv")
            students_path = os.path.join(self.data_dir, "students_employability.csv")
            self.use_cumulative = False
        self.students_df = pd.read_csv(students_path)
        
        # Ensure 'Name' column is present and properly initialized to prevent NaN float serialization (BUG-API-01)
        if "Name" not in self.students_df.columns:
            self.students_df["Name"] = self.students_df["Student_ID"]
        else:
            self.students_df["Name"] = self.students_df["Name"].fillna(self.students_df["Student_ID"])
            
        self.engagement_df = pd.read_csv(os.path.join(self.data_dir, "learning_engagement.csv"))
        
        # Build master skills list
        all_skills = set()
        for df, col in [(self.jobs_df, "Skills_Required"), (self.courses_df, "Skills_Developed"), (self.students_df, "Technical_Skills"), (self.students_df, "Soft_Skills")]:
            if col in df.columns:
                for row in df[col].dropna():
                    skills = [s.strip() for s in str(row).split(",")]
                    all_skills.update(skills)
        self.master_skills = sorted(list(all_skills))
        print(f"Master skill inventory constructed with {len(self.master_skills)} unique skills across {len(self.students_df):,} students.")

        # Fit Dense Semantic Matcher with course curricula
        print("Fitting Dense Semantic Vector Search on course curricula...")
        self.semantic_matcher.fit(self.courses_df)

    def build_vectors(self):
        # 1. Student Skill Vectors (Continuous Proficiency Weights in [0.0, 1.0])
        student_vectors = []
        for _, row in self.students_df.iterrows():
            prof_dict = {}
            if "Skill_Proficiencies" in row and pd.notna(row["Skill_Proficiencies"]):
                for item in str(row["Skill_Proficiencies"]).split(","):
                    if ":" in item:
                        s_name, s_val = item.rsplit(":", 1)
                        try:
                            prof_dict[s_name.strip().lower()] = float(s_val.strip())
                        except ValueError:
                            pass
            
            combined_skills = (str(row.get("Technical_Skills", "")) + ", " + str(row.get("Soft_Skills", ""))).lower()
            vector = []
            for skill in self.master_skills:
                s_lower = skill.lower()
                if s_lower in prof_dict:
                    vector.append(prof_dict[s_lower])
                elif s_lower in combined_skills:
                    vector.append(0.70)
                else:
                    vector.append(0.0)
            student_vectors.append(vector)
        self.students_df["Skill_Vector"] = student_vectors

        # 2. Job Requirement Vectors (Weighted by Target Seniority Benchmark)
        job_vectors = []
        for _, row in self.jobs_df.iterrows():
            req_skills = str(row["Skills_Required"]).lower()
            exp_req = str(row.get("Experience_Required", "")).lower()
            if "5+" in exp_req or "senior" in str(row["Job_Title"]).lower() or "lead" in str(row["Job_Title"]).lower():
                benchmark_w = 0.95
            elif "2+" in exp_req:
                benchmark_w = 0.85
            else:
                benchmark_w = 0.75

            vector = [benchmark_w if skill.lower() in req_skills else 0.0 for skill in self.master_skills]
            job_vectors.append(vector)
        self.jobs_df["Skill_Vector"] = job_vectors

        # 3. Course Skill Vectors
        course_vectors = []
        for _, row in self.courses_df.iterrows():
            dev_skills = str(row["Skills_Developed"]).lower()
            vector = [1.0 if skill.lower() in dev_skills else 0.0 for skill in self.master_skills]
            course_vectors.append(vector)
        self.courses_df["Skill_Vector"] = course_vectors

    def perform_clustering(self):
        print("Performing student segmentation & clustering (Step 4 in Methodology)...")
        # 1. Aggregate behavioral logs from learning_engagement.csv for core students
        core_agg = self.engagement_df.groupby("Student_ID").agg(
            Avg_Logins=("Login_Count", "mean"),
            Avg_Completion=("Content_Completion_Percentage", "mean"),
            Avg_Assessment_Score=("Assessment_Score", "mean"),
            Avg_Submissions=("Assignment_Submission", "mean"),
            Courses_Enrolled=("Course_ID", "count")
        ).reset_index()

        completion_rates = []
        for student_id in core_agg["Student_ID"]:
            sub = self.engagement_df[self.engagement_df["Student_ID"] == student_id]
            comp_count = sum(sub["Course_Completed"] == "Yes")
            total = len(sub)
            completion_rates.append(comp_count / total if total > 0 else 0)
        core_agg["Completion_Rate"] = completion_rates

        if self.use_cumulative and "source_dataset" in self.students_df.columns:
            # 2. Derive calibrated engagement profiles for PS2 benchmark candidates
            ps2_students = self.students_df[self.students_df["source_dataset"] == "PS2_Benchmark"]
            ps2_agg_rows = []
            for _, r in ps2_students.iterrows():
                cog = float(r.get("cognitive_rating", 7.0))
                coding = float(r.get("coding_technical_rating", 6.0))
                exp = float(r.get("experiential_exposure", 5.0))
                self_learn = int(r.get("self_learning_capability", 0))
                
                avg_completion = float(np.clip(35.0 + self_learn * 35.0 + coding * 2.8, 10.0, 99.0))
                avg_logins = float(np.clip(25.0 + exp * 6.5 + self_learn * 15.0, 10.0, 95.0))
                avg_assess = float(np.clip(cog * 10.0, 10.0, 98.0))
                avg_subs = float(np.clip(1.5 + exp * 0.35, 1.0, 5.0))
                courses_enrolled = int(np.clip(round(2 + exp * 0.4), 1, 6))
                comp_rate = float(np.clip(avg_completion / 100.0, 0.05, 1.0))
                
                ps2_agg_rows.append({
                    "Student_ID": r["Student_ID"],
                    "Avg_Logins": avg_logins,
                    "Avg_Completion": avg_completion,
                    "Avg_Assessment_Score": avg_assess,
                    "Avg_Submissions": avg_subs,
                    "Courses_Enrolled": courses_enrolled,
                    "Completion_Rate": comp_rate
                })
            ps2_agg = pd.DataFrame(ps2_agg_rows)
            engagement_agg = pd.concat([core_agg, ps2_agg], ignore_index=True)
        else:
            engagement_agg = core_agg

        # Merge with student GPA / Assessment_Score
        features_df = pd.merge(self.students_df[["Student_ID", "Assessment_Score"]], engagement_agg, on="Student_ID", how="left")
        features_df.rename(columns={"Assessment_Score": "Initial_GPA"}, inplace=True)
        # Fill any missing metrics with median values
        for c in ["Initial_GPA", "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", "Avg_Submissions", "Completion_Rate"]:
            features_df[c] = features_df[c].fillna(features_df[c].median())

        # Scale features and fit K-Means
        feature_cols = ["Initial_GPA", "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", "Avg_Submissions", "Completion_Rate"]
        scaled_features = self.scaler.fit_transform(features_df[feature_cols])

        # We fit 3 clusters (High, Medium, Low Engagement/Performance)
        self.kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        features_df["Cluster"] = self.kmeans.fit_predict(scaled_features)
        
        # Adjust cluster numbering to ensure consistent labels:
        # Cluster with highest Avg_Completion gets label 0 (High), lowest gets label 2 (Low)
        cluster_means = features_df.groupby("Cluster")["Avg_Completion"].mean().sort_values(ascending=False)
        mapping = {old: new for new, old in enumerate(cluster_means.index)}
        features_df["Cluster"] = features_df["Cluster"].map(mapping)

        self.student_behavior_profiles = features_df
        print(f"Clustering completed across {len(features_df):,} profiles. Assigned student behavioral personas.")

    def get_student_cluster_name(self, student_id):
        cluster_id = self.student_behavior_profiles.loc[
            self.student_behavior_profiles["Student_ID"] == student_id, "Cluster"
        ].values[0]
        return self.cluster_labels.get(cluster_id, "Unknown Profile")

    def calculate_willingness_to_learn(self, student_id):
        # Infer willingness to learn (Step 5 in Methodology) using engagement indicators
        profile = self.student_behavior_profiles[self.student_behavior_profiles["Student_ID"] == student_id]
        if profile.empty:
            return 0.0

        # Formula: Weights logins (20%), completion percentage (40%), submissions (20%), and courses enrolled (20%)
        avg_completion = profile["Avg_Completion"].values[0] / 100.0
        avg_logins = min(1.0, profile["Avg_Logins"].values[0] / 100.0) # Scaled log-in count
        avg_subs = profile["Avg_Submissions"].values[0] / 5.0 # Max submissions is 5
        courses_ratio = min(1.0, profile["Courses_Enrolled"].values[0] / 6.0) # Up to 6 courses

        willingness = (avg_completion * 0.40) + (avg_logins * 0.20) + (avg_subs * 0.20) + (courses_ratio * 0.20)
        return round(willingness * 100, 1)

    def cosine_similarity(self, vec_a, vec_b):
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    # Career Interest → keywords that should appear in matching job titles
    CAREER_INTEREST_KEYWORDS = {
        "ai engineer":          ["ai", "machine learning", "ml", "data scientist", "deep learning", "nlp", "computer vision", "ai/ml"],
        "machine learning":     ["machine learning", "ml", "ai", "data scientist", "deep learning", "ai/ml"],
        "data scientist":       ["data scientist", "data science", "machine learning", "ml", "ai", "analytics"],
        "data analyst":         ["data analyst", "analytics", "business intelligence", "bi", "data"],
        "frontend developer":   ["frontend", "front-end", "front end", "ui", "react", "angular", "vue"],
        "frontend engineer":    ["frontend", "front-end", "front end", "ui", "react", "angular", "vue"],
        "frontend":             ["frontend", "front-end", "front end", "ui", "react", "angular", "vue"],
        "backend developer":    ["backend", "back-end", "server", "api", "node", "django", "spring", "java", "go"],
        "backend engineer":     ["backend", "back-end", "server", "api", "node", "django", "spring", "java", "go"],
        "full stack":           ["full stack", "fullstack", "full-stack", "web developer"],
        "devops":               ["devops", "sre", "cloud", "infrastructure", "kubernetes", "docker", "platform"],
        "cybersecurity":        ["security", "cybersecurity", "penetration", "soc", "infosec", "network security"],
        "cloud engineer":       ["cloud", "aws", "azure", "gcp", "infrastructure", "devops", "sre"],
        "product manager":      ["product manager", "product management", "pm", "product owner"],
        "ui/ux":                ["ui", "ux", "design", "figma", "product designer", "interaction"],
        "business analyst":     ["business analyst", "business intelligence", "analyst", "strategy"],
        "software engineer":    ["software engineer", "software developer", "swe", "developer"],
    }

    def _get_career_interest_boost(self, job_title: str, career_interest: str) -> float:
        """
        Returns a score boost [0.0, 0.25] when a job title aligns with the student's
        declared Career_Interest. Uses word-boundary matching to avoid false positives
        (e.g. 'ai' inside 'retail' or 'ml' inside 'html').
        """
        if not career_interest:
            return 0.0
        import re
        ci_lower = career_interest.strip().lower()
        job_lower = job_title.strip().lower()

        # Find the best matching career interest category
        best_keywords = []
        for ci_key, keywords in self.CAREER_INTEREST_KEYWORDS.items():
            if ci_key in ci_lower or ci_lower in ci_key:
                best_keywords = keywords
                break
        # Fallback: use words from the career interest string directly
        if not best_keywords:
            best_keywords = ci_lower.replace("/", " ").replace("-", " ").split()

        hits = sum(1 for kw in best_keywords if re.search(r'(?<![a-z0-9])' + re.escape(kw) + r'(?![a-z0-9])', job_lower))
        if hits == 0:
            return 0.0
        # Scale: 1 keyword hit → +0.35, 2+ hits → +0.45
        return min(0.45, 0.25 + hits * 0.10)

    def match_jobs(self, student_id, top_n=3, country_filter="All"):
        # Career pathway classification and Job-Role matching (Steps 7 & 8)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        if student_row.empty:
            return []

        student_vector = student_row["Skill_Vector"].values[0]
        student_skills = set([
            s.strip().lower()
            for s in (str(student_row["Technical_Skills"].values[0]) + ", " + str(student_row["Soft_Skills"].values[0])).split(",")
            if s.strip()
        ])

        # Read the student's declared career interest for affinity boosting
        career_interest = str(student_row["Career_Interest"].values[0]) if "Career_Interest" in student_row.columns else ""
        if career_interest.lower() in ("nan", "none", ""):
            career_interest = ""

        target_jobs = self.jobs_df
        if country_filter and country_filter != "All":
            cf = country_filter.lower()
            if "india" in cf:
                target_jobs = target_jobs[target_jobs["Country"].str.lower() == "india"]
            elif "germany" in cf:
                target_jobs = target_jobs[target_jobs["Country"].str.lower() == "germany"]
            elif "uk" in cf or "united kingdom" in cf:
                target_jobs = target_jobs[target_jobs["Country"].str.lower() == "united kingdom"]
            elif "remote" in cf:
                target_jobs = target_jobs[(target_jobs["Location"].str.lower().str.contains("remote", na=False)) | (target_jobs["Country"].str.lower() == "remote / global")]

            # Fallback if filtered subset is empty
            if target_jobs.empty:
                target_jobs = self.jobs_df

        matches = []
        for _, job in target_jobs.iterrows():
            job_vector = job["Skill_Vector"]
            skill_similarity = self.cosine_similarity(student_vector, job_vector)

            # --- Career Interest Affinity Boost + Gap-Aware Cap ---
            # Prevents skill-overlap coincidences from outranking role-relevant jobs,
            # while ensuring a job with missing skill gaps NEVER displays 100% suitability.
            job_skills = set([s.strip().lower() for s in str(job["Skills_Required"]).split(",") if s.strip()])
            missing_count = len(job_skills - student_skills)
            coverage_ratio = len(job_skills & student_skills) / max(len(job_skills), 1)
            max_cap = 1.0 if missing_count == 0 else min(0.92, 0.72 + 0.22 * coverage_ratio)

            affinity_boost = self._get_career_interest_boost(str(job["Job_Title"]), career_interest)
            final_score = min(max_cap, skill_similarity + affinity_boost)

            loc_val = job.get("Location", "Remote / Global")
            if pd.isna(loc_val) or not str(loc_val).strip():
                loc_val = "Remote / Global"
            comp_val = job.get("Company_Name", "Global Enterprise")
            if pd.isna(comp_val) or not str(comp_val).strip():
                comp_val = "Global Enterprise"
            ind_val = job.get("Industry", "Tech")
            if pd.isna(ind_val) or not str(ind_val).strip():
                ind_val = "Tech"
            cntry_val = job.get("Country", "Global")
            if pd.isna(cntry_val) or not str(cntry_val).strip():
                cntry_val = "Global"
            matches.append({
                "Job_ID": str(job["Job_ID"]),
                "Job_Title": str(job["Job_Title"]),
                "Company_Name": str(comp_val),
                "Industry": str(ind_val),
                "Location": str(loc_val),
                "Country": str(cntry_val),
                "Skills_Required": str(job["Skills_Required"]),
                "Match_Score": round(final_score * 100, 1)
            })

        # Sort jobs by final score descending (skill similarity + career interest affinity)
        matches = sorted(matches, key=lambda x: x["Match_Score"], reverse=True)
        return matches[:top_n]

    def get_skill_gap_and_courses(self, student_id, job_id, semantic_threshold=0.55):
        # Gap analysis and Course recommendations via Hybrid Vector Search (Steps 6 & 9)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        job_row = self.jobs_df[self.jobs_df["Job_ID"] == job_id]
        
        if student_row.empty or job_row.empty:
            return [], []

        student_skills = set([s.strip().lower() for s in (str(student_row["Technical_Skills"].values[0]) + ", " + str(student_row["Soft_Skills"].values[0])).split(",") if s.strip()])
        job_skills = set([s.strip().lower() for s in str(job_row["Skills_Required"].values[0]).split(",") if s.strip()])
        
        # Skill Gap (skills in job but missing from student)
        skill_gap = sorted(list(job_skills - student_skills))
        
        # -----------------------------------------------------------------------
        # PHASE 1: Build a per-gap best-course map using Hybrid Matching.
        #
        # Problem with the old count-based score:
        #   exact_score = len(exact_matches) * 2.0
        # A React course covering 3 broad gaps (score 6.0) always outranked a
        # specialised Figma/UI-Design course covering 1 targeted gap (score 2.0),
        # even though Figma is THE key tool a Frontend Engineer needs for UI Design.
        #
        # Fix: For each individual gap skill, elect the single best matching course
        # (the "gap champion").  Then collect ALL champion courses (deduped) plus any
        # multi-gap courses that cover 2+ gaps.  Finally score with a balanced
        # formula that rewards BOTH breadth (recall) AND focus (precision).
        # -----------------------------------------------------------------------

        # --- Step A: collect per-course match metadata -----------------------
        course_meta = []  # list of dicts with match info for every qualifying course
        for idx, course in self.courses_df.iterrows():
            course_skills = set([s.strip().lower() for s in str(course["Skills_Developed"]).split(",") if s.strip()])

            # 1. Exact Lexical intersection
            exact_matches = course_skills.intersection(set(skill_gap))

            # 2. Dense Semantic Vector Search for gaps not exact-matched
            semantic_bridges = []
            for gap in skill_gap:
                if gap not in exact_matches:
                    sim, concept = self.semantic_matcher.compute_semantic_similarity(gap, idx, course)
                    if sim >= semantic_threshold:
                        semantic_bridges.append({
                            "gap": gap.title(),
                            "concept": concept if concept else course["Course_Title"],
                            "similarity": round(sim * 100, 1)
                        })

            if exact_matches or semantic_bridges:
                course_meta.append({
                    "idx": idx,
                    "course": course,
                    "exact_matches": exact_matches,
                    "semantic_bridges": semantic_bridges,
                    "course_skills": course_skills,
                })

        # --- Step B: elect a "gap champion" for every individual gap skill ----
        # For each gap find the course with the best exact/semantic fit.
        champion_course_ids = set()
        num_gaps = max(len(skill_gap), 1)
        for gap in skill_gap:
            best_score = -1
            best_id = None
            for cm in course_meta:
                if gap in cm["exact_matches"]:
                    # Exact champion: prefer focused courses (high precision)
                    precision = 1.0 / max(len(cm["course_skills"]), 1)
                    score = 1.0 + precision  # exact = 1.0 base + precision bonus
                else:
                    # Semantic champion
                    score = 0.0
                    for b in cm["semantic_bridges"]:
                        if b["gap"].lower() == gap.lower():
                            score = b["similarity"] / 100.0
                            break
                if score > best_score:
                    best_score = score
                    best_id = cm["course"]["Course_ID"]
            if best_id is not None:
                champion_course_ids.add(best_id)

        # --- Step C: build final scored list ----------------------------------
        recommended_courses = []
        for cm in course_meta:
            course = cm["course"]
            exact_matches = cm["exact_matches"]
            semantic_bridges = cm["semantic_bridges"]
            course_skills = cm["course_skills"]

            # Gap coverage recall: how many gaps does this course address?
            gap_coverage_ratio = len(exact_matches) / num_gaps
            # Precision: what fraction of the course's own skills are relevant to the gap?
            precision_ratio = len(exact_matches) / max(len(course_skills), 1)

            # Harmonic mean (F1) of recall and precision so both matter equally
            if gap_coverage_ratio + precision_ratio > 0:
                f1 = 2 * gap_coverage_ratio * precision_ratio / (gap_coverage_ratio + precision_ratio)
            else:
                f1 = 0.0

            semantic_score = sum(b["similarity"] / 100.0 for b in semantic_bridges) / num_gaps * 1.2
            duration_penalty = 0.005 * float(course.get("Duration_Hours", 20))

            # Champion bonus: if this course is the elected best for any individual gap,
            # give it a guaranteed minimum visibility boost so specialised courses
            # (e.g. Figma for UI Design) are never buried by broad multi-skill courses.
            is_champion = course["Course_ID"] in champion_course_ids
            champion_bonus = 0.5 if is_champion else 0.0

            # Final composite score (0–10 scale)
            total_score = (f1 * 7.0 + semantic_score * 3.0 + champion_bonus) - duration_penalty

            # Match Type Classification
            if exact_matches and semantic_bridges:
                match_type = "Hybrid (Exact + Semantic)"
            elif exact_matches:
                match_type = "Exact Match"
            else:
                match_type = "Dense Semantic Bridge"

            covered_exact_list = sorted([s.title() for s in exact_matches])
            covered_all_list = list(covered_exact_list)
            for b in semantic_bridges:
                covered_all_list.append(f"{b['gap']} (via {b['concept']})")

            recommended_courses.append({
                "Course_ID": course["Course_ID"],
                "Course_Title": course["Course_Title"],
                "Platform": course["Platform"],
                "Skills_Developed": course["Skills_Developed"],
                "Skills_Covered": ", ".join(covered_exact_list),
                "Skills_Covered_All": ", ".join(covered_all_list),
                "Semantic_Bridges": semantic_bridges,
                "Match_Type": match_type,
                "Composite_Score": round(total_score, 3),
                "Duration_Hours": course["Duration_Hours"],
                "Description": course["Description"]
            })
                
        # Sort courses by Composite Score descending (Greedy Maximum Coverage)
        recommended_courses = sorted(recommended_courses, key=lambda x: x["Composite_Score"], reverse=True)

        # --- Step D: Champion Guarantee -------------------------------------------
        # Ensure EVERY gap has its "best course" (champion) visible in the top results.
        # Problem: when there are 5+ gaps, a broad course covering 3 of them will always
        # score higher than a specialised course covering 1 key skill (e.g. Figma for
        # UI Design), even though that specialised course is THE most targeted resource
        # for that gap. Without this step, Figma/UI-Design courses get buried.
        #
        # Solution: build an ordered list of unique gap-champion courses (one per gap),
        # then guarantee each champion appears within the first MAX_DISPLAY slots.
        # Courses that cover multiple gaps appear once only (as champion for the gap
        # they score highest on). Non-champion surplus courses fill remaining slots.
        MAX_DISPLAY = 8  # maximum courses shown in the UI

        # Map: gap -> best champion course entry (by exact match first, then semantic)
        gap_champion_entries = {}
        for gap in skill_gap:
            best_score = -1
            best_entry = None
            for entry in recommended_courses:
                # Check exact match
                exact_set = set(s.strip().lower() for s in entry["Skills_Covered"].split(",") if s.strip())
                if gap in exact_set:
                    # Prefer the entry with best composite score for this gap
                    if entry["Composite_Score"] > best_score:
                        best_score = entry["Composite_Score"]
                        best_entry = entry
            if best_entry is None:
                # Fall back to semantic bridge
                for entry in recommended_courses:
                    for bridge in entry.get("Semantic_Bridges", []):
                        if bridge["gap"].lower() == gap.lower():
                            if entry["Composite_Score"] > best_score:
                                best_score = entry["Composite_Score"]
                                best_entry = entry
            if best_entry is not None:
                gap_champion_entries[gap] = best_entry

        # Build ordered output: champions first (deduplicated), then remaining by score
        seen_ids = set()
        ordered_output = []

        # Add unique champions in gap order
        for gap in skill_gap:
            entry = gap_champion_entries.get(gap)
            if entry and entry["Course_ID"] not in seen_ids:
                ordered_output.append(entry)
                seen_ids.add(entry["Course_ID"])

        # Fill remaining slots with the best non-champion courses
        for entry in recommended_courses:
            if entry["Course_ID"] not in seen_ids:
                ordered_output.append(entry)
                seen_ids.add(entry["Course_ID"])

        recommended_courses = ordered_output[:MAX_DISPLAY]
        # --------------------------------------------------------------------------

        # Format skill gap list to title case for output
        skill_gap_title = [s.title() for s in skill_gap]

        return skill_gap_title, recommended_courses

    def generate_explanation_detail(self, student_id, job_id, recommended_courses, use_qwen=True, force_regenerate=False):
        """
        Synthesizes an explainable recommendation rationale using the Qwen 2.5 Explainability Engine,
        returning rich metadata including provider, model, generation time, and cached status.
        """
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        job_row = self.jobs_df[self.jobs_df["Job_ID"] == job_id]
        if student_row.empty or job_row.empty:
            return {
                "explanation": "Profile or job data unavailable for explainability synthesis.",
                "provider": "none",
                "is_qwen": False,
                "model": "none",
                "cached": False
            }

        s_dict = student_row.iloc[0].to_dict()
        j_dict = job_row.iloc[0].to_dict()

        student_skills = set([s.strip().lower() for s in (str(student_row["Technical_Skills"].values[0]) + ", " + str(student_row["Soft_Skills"].values[0])).split(",") if s.strip()])
        job_skills = set([s.strip().lower() for s in str(job_row["Skills_Required"].values[0]).split(",") if s.strip()])
        overlapping = sorted([s.title() for s in student_skills.intersection(job_skills)])
        gaps = sorted([s.title() for s in (job_skills - student_skills)])

        return self.qwen_explainer.generate_explanation(
            student_id=student_id,
            student_profile=s_dict,
            job_profile=j_dict,
            overlapping_skills=overlapping,
            skill_gaps=gaps,
            recommended_courses=recommended_courses,
            use_qwen=use_qwen,
            force_regenerate=force_regenerate
        )

    def generate_explanation(self, student_id, job_id, recommended_courses, use_qwen=False, force_regenerate=False):
        """
        Explainability implementation powered by Qwen 2.5 Explainability Engine.
        Defaults to use_qwen=False for instant synchronous baseline rendering,
        and use_qwen=True for deep neural rationale synthesis.
        """
        detail = self.generate_explanation_detail(
            student_id, job_id, recommended_courses, use_qwen=use_qwen, force_regenerate=force_regenerate
        )
        return detail["explanation"]
