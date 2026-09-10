import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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

    def build_vectors(self):
        # 1. Student Skill Vectors
        student_vectors = []
        for _, row in self.students_df.iterrows():
            combined_skills = str(row["Technical_Skills"]) + ", " + str(row["Soft_Skills"])
            vector = [1 if skill in combined_skills else 0 for skill in self.master_skills]
            student_vectors.append(vector)
        self.students_df["Skill_Vector"] = student_vectors

        # 2. Job Requirement Vectors
        job_vectors = []
        for _, row in self.jobs_df.iterrows():
            req_skills = str(row["Skills_Required"])
            vector = [1 if skill in req_skills else 0 for skill in self.master_skills]
            job_vectors.append(vector)
        self.jobs_df["Skill_Vector"] = job_vectors

        # 3. Course Skill Vectors
        course_vectors = []
        for _, row in self.courses_df.iterrows():
            dev_skills = str(row["Skills_Developed"])
            vector = [1 if skill in dev_skills else 0 for skill in self.master_skills]
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

    def match_jobs(self, student_id, top_n=3):
        # Career pathway classification and Job-Role matching (Steps 7 & 8)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        if student_row.empty:
            return []

        student_vector = student_row["Skill_Vector"].values[0]
        matches = []

        for _, job in self.jobs_df.iterrows():
            job_vector = job["Skill_Vector"]
            similarity = self.cosine_similarity(student_vector, job_vector)
            matches.append({
                "Job_ID": job["Job_ID"],
                "Job_Title": job["Job_Title"],
                "Industry": job["Industry"],
                "Location": job["Location"],
                "Skills_Required": job["Skills_Required"],
                "Match_Score": round(similarity * 100, 1)
            })

        # Sort jobs by matching similarity score descending
        matches = sorted(matches, key=lambda x: x["Match_Score"], reverse=True)
        return matches[:top_n]

    def get_skill_gap_and_courses(self, student_id, job_id):
        # Gap analysis and Course recommendations (Steps 6 & 9)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        job_row = self.jobs_df[self.jobs_df["Job_ID"] == job_id]
        
        if student_row.empty or job_row.empty:
            return [], []

        student_skills = set([s.strip().lower() for s in (str(student_row["Technical_Skills"].values[0]) + ", " + str(student_row["Soft_Skills"].values[0])).split(",") if s.strip()])
        job_skills = set([s.strip().lower() for s in str(job_row["Skills_Required"].values[0]).split(",") if s.strip()])
        
        # Skill Gap (skills in job but missing from student)
        skill_gap = sorted(list(job_skills - student_skills))
        
        # Map missing skills to courses in our catalog
        recommended_courses = []
        for _, course in self.courses_df.iterrows():
            course_skills = set([s.strip().lower() for s in str(course["Skills_Developed"]).split(",") if s.strip()])
            
            # Find the intersection of skills developed and the student's gaps
            matching_skills = course_skills.intersection(set(skill_gap))
            if matching_skills:
                recommended_courses.append({
                    "Course_ID": course["Course_ID"],
                    "Course_Title": course["Course_Title"],
                    "Platform": course["Platform"],
                    "Skills_Developed": course["Skills_Developed"],
                    "Skills_Covered": ", ".join(sorted([s.title() for s in matching_skills])),
                    "Duration_Hours": course["Duration_Hours"]
                })
                
        # Sort courses by duration or coverage (let's do count of matching skills covered)
        recommended_courses = sorted(recommended_courses, key=lambda x: len(x["Skills_Covered"].split(",")), reverse=True)
        # Format skill gap list to title case for output
        skill_gap_title = [s.title() for s in skill_gap]
        
        return skill_gap_title, recommended_courses

    def generate_explanation(self, student_id, job_id, recommended_courses):
        # Explainability implementation (Step 11 in Methodology)
        student_row = self.students_df[self.students_df["Student_ID"] == student_id]
        job_row = self.jobs_df[self.jobs_df["Job_ID"] == job_id]
        
        student_name = student_id
        job_title = job_row["Job_Title"].values[0]
        
        explanations = []
        
        # 1. Explain the Job matching score
        # Find overlapping skills
        student_skills = set([s.strip().lower() for s in (str(student_row["Technical_Skills"].values[0]) + ", " + str(student_row["Soft_Skills"].values[0])).split(",") if s.strip()])
        job_skills = set([s.strip().lower() for s in str(job_row["Skills_Required"].values[0]).split(",") if s.strip()])
        overlapping = sorted([s.title() for s in student_skills.intersection(job_skills)])
        
        explanations.append(
            f"The student profile shows a strong alignment with the '{job_title}' position. "
            f"This is based on an existing skill overlap including: {', '.join(overlapping) if overlapping else 'General background qualifications'}."
        )
        
        # 2. Explain Course Recommendations based on specific gaps
        if recommended_courses:
            explanations.append("To close the detected skill gaps, the following pathways are recommended:")
            for course in recommended_courses:
                explanations.append(
                    f"- **{course['Course_Title']}** ({course['Platform']}): Recommended because it directly develops "
                    f"**{course['Skills_Covered']}**, which are currently required for the target '{job_title}' role."
                )
        else:
            explanations.append("The student already possesses the required skillset for this job role. No immediate course gaps identified.")
            
        return "\n".join(explanations)
