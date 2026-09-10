import os
import csv
import random
import datetime

def generate_data():
    output_dir = r"C:\Users\admin\.gemini\antigravity\scratch\major-project\data"
    os.makedirs(output_dir, exist_ok=True)
    
    students_path = os.path.join(output_dir, "students_employability.csv")
    engagement_path = os.path.join(output_dir, "learning_engagement.csv")
    
    random.seed(42)
    
    # 1. Define lists of possible values
    degrees = ["B.Tech", "B.E.", "B.Sc", "BBA", "M.Tech", "MCA"]
    specialisations = {
        "B.Tech": ["Computer Science", "Information Technology", "Data Science", "Electronics"],
        "B.E.": ["Computer Science", "Information Technology", "Mechanical", "Electrical"],
        "B.Sc": ["Computer Science", "Mathematics", "Statistics"],
        "BBA": ["Finance", "Marketing", "Business Analytics"],
        "M.Tech": ["Computer Science", "Artificial Intelligence", "Data Science"],
        "MCA": ["Computer Application"]
    }
    
    tech_skills_pool = ["Python", "SQL", "Java", "HTML", "Javascript", "CSS", "Excel", "Power BI", "Cloud"]
    soft_skills_pool = ["Communication", "Teamwork", "Problem Solving", "Leadership", "Time Management"]
    
    certifications_pool = [
        "AWS Cloud Practitioner", "Google Data Analytics Certificate", 
        "Microsoft Certified: Azure Fundamentals", "Oracle Certified Associate Java", 
        "Power BI Data Analyst Associate", "Scrum Product Owner"
    ]
    
    projects_pool = [
        "Customer Churn Prediction Dashboard", "E-commerce Website from Scratch",
        "Employee Attendance Tracking System", "Stock Portfolio Optimization Tool",
        "Social Media Campaign Analysis", "Healthcare Database Management System"
    ]
    
    career_interests = ["AI Engineer", "Data Analyst", "Business Analyst", "Web Developer", "Cloud Engineer"]
    
    # Standard courses we defined in courses.csv
    courses = [
        ("COURSE_001", "Python Programming Masterclass", "Python, Data Analytics"),
        ("COURSE_002", "SQL for Data Analysis and Business Intelligence", "SQL, Data Analytics"),
        ("COURSE_003", "Machine Learning Specialization", "Machine Learning, AI/ML, Python, Statistics"),
        ("COURSE_004", "Deep Learning and Neural Networks", "Deep Learning, AI/ML, Python"),
        ("COURSE_005", "Power BI Desktop for Business Intelligence", "Power BI, Data Visualisation"),
        ("COURSE_006", "Statistics and Probability for Data Science", "Statistics, Excel"),
        ("COURSE_007", "Java Programming and Software Engineering", "Java"),
        ("COURSE_008", "Web Development Bootcamp", "HTML, Javascript, CSS"),
        ("COURSE_009", "Cloud Computing Essentials (AWS & Azure)", "Cloud"),
        ("COURSE_010", "Business Communication & Presentation Skills", "Communication"),
        ("COURSE_011", "Interpersonal Skills & Team Collaboration", "Teamwork, Communication"),
        ("COURSE_012", "Professionalism & Ethical Conduct in the Workplace", "Ethical Conduct, Professionalism"),
        ("COURSE_013", "Data Analytics with Excel", "Excel, Data Analytics")
    ]
    
    num_students = 150
    students_data = []
    engagement_data = []
    
    start_date = datetime.date(2026, 1, 1)
    
    # 2. Generate Students
    for idx in range(1, num_students + 1):
        student_id = f"STU_{idx:03d}"
        
        # Inferred "Willingness to Learn" profile type
        # 3 types: High Willingness (30%), Medium (50%), Low (20%)
        rand_profile = random.random()
        if rand_profile < 0.30:
            willingness_profile = "High"
        elif rand_profile < 0.80:
            willingness_profile = "Medium"
        else:
            willingness_profile = "Low"
            
        edu_level = random.choice(["Undergraduate", "Postgraduate"])
        if edu_level == "Undergraduate":
            deg = random.choice(["B.Tech", "B.E.", "B.Sc", "BBA"])
        else:
            deg = random.choice(["M.Tech", "MCA"])
            
        spec = random.choice(specialisations[deg])
        grad_year = random.choice([2026, 2027, 2028])
        
        # Careers mapping to degree/specialisation or random
        career_interest = random.choice(career_interests)
        if "Finance" in spec or "Marketing" in spec:
            career_interest = "Business Analyst"
        elif "Data Science" in spec or "Statistics" in spec:
            career_interest = random.choice(["Data Analyst", "AI Engineer"])
            
        # Tech skills based on career interest
        if career_interest == "AI Engineer":
            tech_skills = sorted(random.sample(["Python", "SQL", "Cloud"], k=random.randint(1, 3)))
        elif career_interest == "Data Analyst":
            tech_skills = sorted(random.sample(["Excel", "SQL", "Power BI"], k=random.randint(1, 3)))
        elif career_interest == "Web Developer":
            tech_skills = sorted(random.sample(["HTML", "Javascript", "CSS"], k=random.randint(2, 3)))
        elif career_interest == "Cloud Engineer":
            tech_skills = sorted(random.sample(["Cloud", "Java", "Python"], k=random.randint(1, 3)))
        else: # Business Analyst
            tech_skills = sorted(random.sample(["Excel", "Power BI", "SQL"], k=random.randint(1, 3)))
            
        # Soft skills
        soft_skills = sorted(random.sample(soft_skills_pool, k=random.randint(1, 3)))
        
        # Certifications
        num_certs = 0
        if willingness_profile == "High":
            num_certs = random.randint(1, 2)
        elif willingness_profile == "Medium":
            num_certs = random.randint(0, 1)
        certs = random.sample(certifications_pool, k=num_certs) if num_certs > 0 else ["None"]
        
        # Projects
        num_projs = 0
        if willingness_profile == "High":
            num_projs = random.randint(1, 2)
        elif willingness_profile == "Medium":
            num_projs = random.randint(0, 1)
        projs = random.sample(projects_pool, k=num_projs) if num_projs > 0 else ["None"]
        
        # Assessment score (representing general initial assessment score e.g. entrance or test score)
        if willingness_profile == "High":
            assessment_score = round(random.uniform(7.8, 9.8), 2)
        elif willingness_profile == "Medium":
            assessment_score = round(random.uniform(6.0, 8.5), 2)
        else:
            assessment_score = round(random.uniform(4.5, 6.5), 2)
            
        # Generate learning engagement (course enrollment) for this student
        # High willingness = enrolled in 4-6 courses, high completion rate, voluntary extra courses
        # Medium willingness = enrolled in 2-4 courses, moderate completion
        # Low willingness = enrolled in 1-2 courses, poor completion
        if willingness_profile == "High":
            num_courses = random.randint(4, 6)
        elif willingness_profile == "Medium":
            num_courses = random.randint(2, 4)
        else:
            num_courses = random.randint(1, 2)
            
        enrolled_courses = random.sample(courses, k=min(num_courses, len(courses)))
        completed_course_titles = []
        
        for course_idx, (course_id, course_title, course_skills) in enumerate(enrolled_courses):
            reg_offset = random.randint(0, 120)
            reg_date = start_date + datetime.timedelta(days=reg_offset)
            
            # Engagement characteristics
            if willingness_profile == "High":
                login_count = random.randint(30, 60)
                # Increasing assessment scores over time (learning improvement)
                base_score = 75 + (course_idx * 4)  # Score rises for subsequent courses
                score = min(100, int(random.normalvariate(base_score, 5)))
                completion = 100
                submission = random.randint(4, 5) # submitted all assignments
            elif willingness_profile == "Medium":
                login_count = random.randint(15, 35)
                score = int(random.normalvariate(72, 8))
                completion = random.choice([80, 90, 100])
                submission = random.randint(3, 4)
            else:
                login_count = random.randint(2, 10)
                score = int(random.normalvariate(55, 12))
                completion = random.randint(10, 60)
                submission = random.randint(0, 2)
                
            score = max(0, min(100, score))
            completed = "Yes" if completion == 100 else "No"
            cert_issued = "Yes" if completed == "Yes" and score >= 60 else "No"
            
            activity_offset = random.randint(5, 45) if completed == "No" else random.randint(20, 60)
            last_activity = reg_date + datetime.timedelta(days=activity_offset)
            
            if completed == "Yes":
                completed_course_titles.append(course_title)
                # Append skills developed to student's tech/soft skills lists
                skills_list = [s.strip() for s in course_skills.split(",")]
                for sk in skills_list:
                    if sk in tech_skills_pool and sk not in tech_skills:
                        tech_skills.append(sk)
                    elif sk in soft_skills_pool and sk not in soft_skills:
                        soft_skills.append(sk)
            
            engagement_data.append({
                "Student_ID": student_id,
                "Course_ID": course_id,
                "Registration_Date": reg_date.isoformat(),
                "Login_Count": login_count,
                "Content_Completion_Percentage": completion,
                "Assessment_Score": score,
                "Assignment_Submission": submission,
                "Last_Activity_Date": last_activity.isoformat(),
                "Course_Completed": completed,
                "Certificate_Issued": cert_issued
            })
            
        students_data.append({
            "Student_ID": student_id,
            "Education_Level": edu_level,
            "Degree": deg,
            "Specialisation": spec,
            "Graduation_Year": grad_year,
            "Technical_Skills": ", ".join(sorted(tech_skills)),
            "Soft_Skills": ", ".join(sorted(soft_skills)),
            "Certifications": ", ".join(certs),
            "Projects": ", ".join(projs),
            "Courses_Completed": ", ".join(completed_course_titles) if completed_course_titles else "None",
            "Assessment_Score": assessment_score,
            "Career_Interest": career_interest
        })
        
    # 3. Write Students CSV
    with open(students_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Student_ID", "Education_Level", "Degree", "Specialisation", "Graduation_Year",
            "Technical_Skills", "Soft_Skills", "Certifications", "Projects", 
            "Courses_Completed", "Assessment_Score", "Career_Interest"
        ])
        writer.writeheader()
        for row in students_data:
            writer.writerow(row)
            
    # 4. Write Engagement CSV
    with open(engagement_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Student_ID", "Course_ID", "Registration_Date", "Login_Count",
            "Content_Completion_Percentage", "Assessment_Score", "Assignment_Submission",
            "Last_Activity_Date", "Course_Completed", "Certificate_Issued"
        ])
        writer.writeheader()
        for row in engagement_data:
            writer.writerow(row)
            
    print(f"Successfully generated student dataset of {num_students} records.")
    print(f"Student details written to {students_path}")
    print(f"Learning engagement logs written to {engagement_path}")

if __name__ == "__main__":
    generate_data()
