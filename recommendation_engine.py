import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

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
    def __init__(self, data_dir=None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir
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

    def load_data(self):
        print("Loading datasets...")
        self.jobs_df = pd.read_csv(os.path.join(self.data_dir, "jobs.csv"))
        self.courses_df = pd.read_csv(os.path.join(self.data_dir, "courses.csv"))
        self.students_df = pd.read_csv(os.path.join(self.data_dir, "students_employability.csv"))
        self.engagement_df = pd.read_csv(os.path.join(self.data_dir, "learning_engagement.csv"))
        
        # Build master skills list
        all_skills = set()
        for df, col in [(self.jobs_df, "Skills_Required"), (self.courses_df, "Skills_Developed"), (self.students_df, "Technical_Skills"), (self.students_df, "Soft_Skills")]:
            for row in df[col].dropna():
                skills = [s.strip() for s in row.split(",")]
                all_skills.update(skills)
        self.master_skills = sorted(list(all_skills))
        print(f"Master skill inventory constructed with {len(self.master_skills)} unique skills.")

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
        # Aggregate behavioral logs from learning_engagement.csv per student
        engagement_agg = self.engagement_df.groupby("Student_ID").agg(
            Avg_Logins=("Login_Count", "mean"),
            Avg_Completion=("Content_Completion_Percentage", "mean"),
            Avg_Assessment_Score=("Assessment_Score", "mean"),
            Avg_Submissions=("Assignment_Submission", "mean"),
            Courses_Enrolled=("Course_ID", "count")
        ).reset_index()

        # Calculate course completion rate (how many courses marked completed)
        completion_rates = []
        for student_id in engagement_agg["Student_ID"]:
            sub = self.engagement_df[self.engagement_df["Student_ID"] == student_id]
            comp_count = sum(sub["Course_Completed"] == "Yes")
            total = len(sub)
            completion_rates.append(comp_count / total if total > 0 else 0)
        engagement_agg["Completion_Rate"] = completion_rates

        # Merge with initial student GPA
        features_df = pd.merge(self.students_df[["Student_ID", "Assessment_Score"]], engagement_agg, on="Student_ID")
        features_df.rename(columns={"Assessment_Score": "Initial_GPA"}, inplace=True)

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
        print("Clustering completed. Assigned student behavioral personas.")

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

    def match_jobs(self, student_id, top_n=3, country_filter="All"):
        # Career pathway classification and Job-Role matching (Steps 7 & 8)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        if student_row.empty:
            return []

        student_vector = student_row["Skill_Vector"].values[0]
        
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
            similarity = self.cosine_similarity(student_vector, job_vector)
            matches.append({
                "Job_ID": job["Job_ID"],
                "Job_Title": job["Job_Title"],
                "Company_Name": job.get("Company_Name", "Global Enterprise"),
                "Industry": job["Industry"],
                "Location": job["Location"],
                "Country": job.get("Country", "Global"),
                "Skills_Required": job["Skills_Required"],
                "Match_Score": round(similarity * 100, 1)
            })

        # Sort jobs by matching similarity score descending
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
        
        # Map missing skills to courses using Hybrid (Lexical Exact + Dense Semantic) matching
        recommended_courses = []
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
            
            # If the course covers skills either lexically or semantically:
            if exact_matches or semantic_bridges:
                # Composite Score: Exact Matches weighted 2.0x, Semantic Bridges weighted 1.2x * similarity
                exact_score = len(exact_matches) * 2.0
                semantic_score = sum(b["similarity"] / 100.0 for b in semantic_bridges) * 1.2
                duration_penalty = 0.005 * float(course.get("Duration_Hours", 20))
                total_score = exact_score + semantic_score - duration_penalty
                
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
        # Format skill gap list to title case for output
        skill_gap_title = [s.title() for s in skill_gap]
        
        return skill_gap_title, recommended_courses

    def generate_explanation(self, student_id, job_id, recommended_courses):
        # Explainability implementation with Dense Semantic Search (Step 11 in Methodology)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        job_row = self.jobs_df[self.jobs_df["Job_ID"] == job_id]
        
        student_name = student_id
        job_title = job_row["Job_Title"].values[0]
        company_name = job_row["Company_Name"].values[0] if "Company_Name" in job_row else "Tech Enterprise"
        job_loc = job_row["Location"].values[0] if "Location" in job_row else "Global"
        
        explanations = []
        
        # 1. Explain the Job matching score
        student_skills = set([s.strip().lower() for s in (str(student_row["Technical_Skills"].values[0]) + ", " + str(student_row["Soft_Skills"].values[0])).split(",") if s.strip()])
        job_skills = set([s.strip().lower() for s in str(job_row["Skills_Required"].values[0]).split(",") if s.strip()])
        overlapping = sorted([s.title() for s in student_skills.intersection(job_skills)])
        
        explanations.append(
            f"The student profile shows strong alignment with the role of **'{job_title}'** at **{company_name}** ({job_loc}). "
            f"This is based on an existing skill overlap including: {', '.join(overlapping) if overlapping else 'Foundational qualifications'}."
        )
        
        # 2. Explain Course Recommendations based on specific gaps & dense semantic vector search
        if recommended_courses:
            mode_name = self.semantic_matcher.get_mode_name()
            explanations.append(f"To close the detected skill gaps, the following pathways are prescribed via **{mode_name}**:")
            for course in recommended_courses:
                parts = []
                if course.get("Skills_Covered"):
                    parts.append(f"directly develops **{course['Skills_Covered']}**")
                if course.get("Semantic_Bridges"):
                    bridge_strs = [f"**{b['gap']}** via **{b['concept']}** ({b['similarity']}% semantic match)" for b in course["Semantic_Bridges"]]
                    parts.append(f"semantically bridges {', '.join(bridge_strs)}")
                
                reason = " and ".join(parts) if parts else f"develops competencies in {course['Skills_Developed']}"
                explanations.append(
                    f"- **{course['Course_Title']}** ({course['Platform']}): Recommended because it {reason}, fulfilling prerequisites for the '{job_title}' role."
                )
        else:
            explanations.append("The student already possesses the required skillset for this job role. No immediate course gaps identified.")
            
        return "\n".join(explanations)
