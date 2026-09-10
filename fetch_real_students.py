import os
import csv
import urllib.request
import random
import datetime

def download_dataset(url, dest_path):
    if os.path.exists(dest_path):
        print(f"Dataset already exists at: {dest_path}")
        return True
    print(f"Downloading real dataset from: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"Raw data successfully saved to: {dest_path}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

# Master list of 16 distinct career pathways
CAREER_PATHWAYS = [
    "AI Engineer",
    "Data Analyst",
    "Data Scientist",
    "Business Analyst",
    "BI Developer",
    "Frontend Developer",
    "Backend Developer",
    "Full-Stack Developer",
    "Cloud DevOps Engineer",
    "Cybersecurity Analyst",
    "Database Administrator",
    "Financial Analyst",
    "Digital Marketing Specialist",
    "Marketing Analyst",
    "Product Manager",
    "UI/UX Designer"
]

def map_raw_record_to_career(idx, topic, stage, raised_hands, visited_resources, discussion, perf_class):
    """
    Deterministically maps a student's raw xAPI-Edu-Data attributes
    into one of the 16 industry career pathways.
    """
    topic = topic.lower().strip()
    stage = stage.lower().strip()
    
    # 16-way career classification logic combining topic, behavioral logs, and index hash
    if topic in ['it']:
        if discussion > 60 and raised_hands > 60:
            career = "Full-Stack Developer"
            degree, spec = "B.Tech", "Computer Science"
        elif visited_resources > 60:
            career = "Cloud DevOps Engineer"
            degree, spec = "B.Tech", "Cloud Computing"
        elif raised_hands < 35:
            career = "Cybersecurity Analyst"
            degree, spec = "B.Tech", "Information Security"
        elif idx % 2 == 0:
            career = "Backend Developer"
            degree, spec = "B.Tech", "Software Engineering"
        else:
            career = "Frontend Developer"
            degree, spec = "B.Tech", "Computer Science"

    elif topic in ['math']:
        if perf_class == 'H':
            career = "AI Engineer"
            degree, spec = "B.Tech", "Artificial Intelligence"
        elif discussion > 50:
            career = "Data Scientist"
            degree, spec = "B.Sc", "Data Science"
        elif idx % 2 == 0:
            career = "Database Administrator"
            degree, spec = "B.Tech", "Computer Science"
        else:
            career = "Data Analyst"
            degree, spec = "B.Sc", "Statistics & Analytics"

    elif topic in ['science', 'chemistry', 'biology']:
        if perf_class == 'H' and visited_resources > 50:
            career = "Data Scientist"
            degree, spec = "B.Sc", "Data Science"
        elif discussion > 45:
            career = "BI Developer"
            degree, spec = "B.Sc", "Business Analytics"
        elif idx % 3 == 0:
            career = "AI Engineer"
            degree, spec = "B.Tech", "Computer Science"
        else:
            career = "Data Analyst"
            degree, spec = "B.Sc", "Data Analytics"

    elif topic in ['english', 'french', 'arabic', 'history']:
        if discussion > 60:
            career = "Product Manager"
            degree, spec = "BBA", "Product Management"
        elif visited_resources > 50:
            career = "UI/UX Designer"
            degree, spec = "B.Des", "User Experience Design"
        elif idx % 2 == 0:
            career = "Digital Marketing Specialist"
            degree, spec = "BBA", "Digital Marketing"
        else:
            career = "Marketing Analyst"
            degree, spec = "BBA", "Marketing Analytics"

    elif topic in ['geography', 'quran']:
        if perf_class == 'H':
            career = "Financial Analyst"
            degree, spec = "BBA", "Finance & Accounting"
        elif discussion > 40:
            career = "Business Analyst"
            degree, spec = "BBA", "Business Analytics"
        elif idx % 2 == 0:
            career = "BI Developer"
            degree, spec = "B.Sc", "Information Systems"
        else:
            career = "Financial Analyst"
            degree, spec = "BBA", "Finance"

    else:
        career = CAREER_PATHWAYS[idx % len(CAREER_PATHWAYS)]
        degree, spec = "B.Tech", "Information Technology"

    return degree, spec, career

def map_stage_to_edu_level(stage):
    stage = stage.lower().strip()
    if stage == 'lowerlevel':
        return "Undergraduate", 2028
    elif stage == 'middleschool':
        return "Undergraduate", 2027
    else:
        return "Postgraduate", 2026

def get_skills_by_career(career, perf_class):
    """
    Returns domain-specific technical skills aligned with the career pathway.
    """
    skill_definitions = {
        "AI Engineer": ["Python", "SQL", "Machine Learning"] + (["Deep Learning"] if perf_class in ['M', 'H'] else []),
        "Data Analyst": ["Excel", "SQL"] + (["Python", "Tableau"] if perf_class in ['M', 'H'] else []),
        "Data Scientist": ["Python", "Statistics", "SQL"] + (["Machine Learning"] if perf_class in ['M', 'H'] else []),
        "Business Analyst": ["Excel", "Business Analytics"] + (["SQL", "Power BI"] if perf_class in ['M', 'H'] else []),
        "BI Developer": ["SQL", "Power BI"] + (["Tableau", "Data Warehousing"] if perf_class in ['M', 'H'] else []),
        "Frontend Developer": ["HTML", "CSS", "Javascript"] + (["React"] if perf_class in ['M', 'H'] else []),
        "Backend Developer": ["Java", "SQL"] + (["Python", "REST APIs"] if perf_class in ['M', 'H'] else []),
        "Full-Stack Developer": ["HTML", "Javascript", "SQL"] + (["React", "Node.js"] if perf_class in ['M', 'H'] else []),
        "Cloud DevOps Engineer": ["Linux", "Cloud"] + (["Docker", "AWS"] if perf_class in ['M', 'H'] else []),
        "Cybersecurity Analyst": ["Linux", "Network Security"] + (["Cryptography", "Cybersecurity"] if perf_class in ['M', 'H'] else []),
        "Database Administrator": ["SQL", "Database Management"] + (["PostgreSQL", "Linux"] if perf_class in ['M', 'H'] else []),
        "Financial Analyst": ["Excel", "Finance"] + (["Financial Modeling", "Accounting"] if perf_class in ['M', 'H'] else []),
        "Digital Marketing Specialist": ["Digital Marketing", "SEO"] + (["Social Media Analytics", "Content Strategy"] if perf_class in ['M', 'H'] else []),
        "Marketing Analyst": ["Excel", "Marketing Analytics"] + (["Python", "Customer Segmentation"] if perf_class in ['M', 'H'] else []),
        "Product Manager": ["Product Strategy", "User Research"] + (["Agile/Scrum", "Roadmapping"] if perf_class in ['M', 'H'] else []),
        "UI/UX Designer": ["Figma", "UI Design"] + (["Wireframing", "Prototyping"] if perf_class in ['M', 'H'] else [])
    }
    
    return skill_definitions.get(career, ["Python", "SQL"])

def get_soft_skills(raised_hands, discussion):
    skills = []
    if discussion > 40:
        skills.append("Communication")
    if raised_hands > 45:
        skills.append("Problem Solving")
    if raised_hands > 30 and discussion > 30:
        skills.append("Teamwork")
    
    if not skills:
        skills = ["Time Management", "Adaptability"]
    return sorted(list(set(skills)))

def main():
    random.seed(42)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "data")
    os.makedirs(output_dir, exist_ok=True)
    
    raw_csv_url = "https://raw.githubusercontent.com/basilatawneh/Students-Academic-Performance-Dataset-xAPI-Edu-Data-/master/xAPI-Edu-Data.csv"
    raw_dest_path = os.path.join(output_dir, "raw_xAPI_Edu_Data.csv")
    
    if not download_dataset(raw_csv_url, raw_dest_path):
        print("Dataset download failed. Exiting.")
        return

    students_output_path = os.path.join(output_dir, "students_employability.csv")
    engagement_output_path = os.path.join(output_dir, "learning_engagement.csv")
    
    students_data = []
    engagement_data = []
    
    career_counts = {c: 0 for c in CAREER_PATHWAYS}
    start_date = datetime.date(2026, 1, 1)

    with open(raw_dest_path, 'r', encoding='utf-8') as rf:
        reader = csv.DictReader(rf)
        
        for idx, row in enumerate(reader, start=1):
            student_id = f"STU_{idx:03d}"
            gender = row.get("gender", "M")
            stage = row.get("StageID", "MiddleSchool")
            topic = row.get("Topic", "IT")
            raised_hands = int(row.get("raisedhands", 0))
            visited_resources = int(row.get("VisITedResources", 0))
            announcements_view = int(row.get("AnnouncementsView", 0))
            discussion = int(row.get("Discussion", 0))
            perf_class = row.get("Class", "M")
            
            degree, specialisation, career_interest = map_raw_record_to_career(
                idx, topic, stage, raised_hands, visited_resources, discussion, perf_class
            )
            career_counts[career_interest] += 1
            
            edu_level, grad_year = map_stage_to_edu_level(stage)
            tech_skills = get_skills_by_career(career_interest, perf_class)
            soft_skills = get_soft_skills(raised_hands, discussion)
            
            if perf_class == 'H':
                gpa = round(random.uniform(8.5, 9.8), 2)
                projects = f"{career_interest} Capstone Portfolio"
                certifications = f"Certified {career_interest} Professional"
            elif perf_class == 'M':
                gpa = round(random.uniform(6.5, 8.4), 2)
                projects = f"{career_interest} Applied Lab Project" if random.random() > 0.4 else "None"
                certifications = "Industry Foundation Certificate" if random.random() > 0.5 else "None"
            else:
                gpa = round(random.uniform(4.5, 6.4), 2)
                projects = "None"
                certifications = "None"
                
            course_id = f"COURSE_{((idx % 28) + 1):03d}"
            course_title = f"Professional Pathway Course {course_id}"
            
            completion_pct = min(100, int((visited_resources * 0.8) + (raised_hands * 0.4)))
            if perf_class == 'H':
                completion_pct = max(88, completion_pct)
            elif perf_class == 'L':
                completion_pct = min(60, completion_pct)
                
            completed = "Yes" if completion_pct >= 85 else "No"
            
            if perf_class == 'H':
                score = random.randint(82, 100)
            elif perf_class == 'M':
                score = random.randint(62, 81)
            else:
                score = random.randint(38, 61)
                
            cert_issued = "Yes" if completed == "Yes" and score >= 60 else "No"
            submissions = min(5, int((raised_hands + announcements_view) / 25))
            if perf_class == 'L':
                submissions = min(2, submissions)
            
            reg_offset = random.randint(0, 60)
            reg_date = start_date + datetime.timedelta(days=reg_offset)
            activity_offset = random.randint(10, 90)
            last_activity = reg_date + datetime.timedelta(days=activity_offset)
            
            students_data.append({
                "Student_ID": student_id,
                "Gender": "Male" if gender == 'M' else "Female",
                "Education_Level": edu_level,
                "Degree": degree,
                "Specialisation": specialisation,
                "Graduation_Year": grad_year,
                "Technical_Skills": ", ".join(tech_skills),
                "Soft_Skills": ", ".join(soft_skills),
                "Projects": projects,
                "Certifications": certifications,
                "Assessment_Score": gpa,
                "Career_Interest": career_interest
            })
            
            engagement_data.append({
                "Student_ID": student_id,
                "Course_ID": course_id,
                "Course_Title": course_title,
                "Registration_Date": reg_date.strftime("%Y-%m-%d"),
                "Content_Completion_Percentage": completion_pct,
                "Login_Count": visited_resources,
                "Assessment_Score": score,
                "Assignment_Submission": submissions,
                "Course_Completed": completed,
                "Certificate_Issued": cert_issued,
                "Last_Activity_Date": last_activity.strftime("%Y-%m-%d")
            })

    # Save students_employability.csv
    student_fieldnames = [
        "Student_ID", "Gender", "Education_Level", "Degree", "Specialisation",
        "Graduation_Year", "Technical_Skills", "Soft_Skills", "Projects",
        "Certifications", "Assessment_Score", "Career_Interest"
    ]
    with open(students_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=student_fieldnames)
        writer.writeheader()
        writer.writerows(students_data)
    print(f"Generated {len(students_data)} student records at: {students_output_path}")

    # Save learning_engagement.csv
    engagement_fieldnames = [
        "Student_ID", "Course_ID", "Course_Title", "Registration_Date",
        "Content_Completion_Percentage", "Login_Count", "Assessment_Score",
        "Assignment_Submission", "Course_Completed", "Certificate_Issued", "Last_Activity_Date"
    ]
    with open(engagement_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=engagement_fieldnames)
        writer.writeheader()
        writer.writerows(engagement_data)
    print(f"Generated {len(engagement_data)} engagement logs at: {engagement_output_path}")

    print("\nCareer Distribution across 480 Students:")
    for c, count in sorted(career_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {c}: {count} students")

if __name__ == "__main__":
    main()
