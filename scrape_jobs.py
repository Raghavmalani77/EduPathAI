import os
import csv
import json
import re
import urllib.request
from bs4 import BeautifulSoup

def clean_html(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Get plain text and clean up whitespace
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_experience(description_text):
    # Regex to find patterns like "3+ years", "5 years", "2-4 years"
    match = re.search(r'(\d+)(?:\s*-\s*\d+)?\s*\+?\s*years?', description_text, re.IGNORECASE)
    if match:
        return f"{match.group(1)}+ years"
    # Fallback options
    if "senior" in description_text.lower():
        return "5+ years"
    if "junior" in description_text.lower() or "intern" in description_text.lower():
        return "0-1 years"
    return "2+ years"  # Sensible default

def extract_education(description_text):
    text_lower = description_text.lower()
    if "phd" in text_lower or "ph.d" in text_lower:
        return "PhD"
    if "master" in text_lower or "m.s." in text_lower or "m.tech" in text_lower:
        return "Master's Degree"
    if "bachelor" in text_lower or "b.s." in text_lower or "b.tech" in text_lower or "degree" in text_lower:
        return "Bachelor's Degree"
    return "Bachelor's Degree"  # Sensible default

def extract_skills(tags, description_text):
    # Core skills from project description and standard tech/soft skills
    known_skills = [
        "Python", "SQL", "Java", "AI/ML", "Machine Learning", "Deep Learning", 
        "Power BI", "Excel", "Statistics", "Data Visualisation", "Data Analytics",
        "Communication", "Teamwork", "Collaboration", "Professionalism", "Ethical Conduct",
        "HTML", "Javascript", "CSS", "Finance", "Marketing", "Healthcare", "Cloud"
    ]
    
    found_skills = set()
    
    # 1. Check existing tags (convert to title case if matching known skills)
    for tag in tags:
        for skill in known_skills:
            if tag.lower() == skill.lower():
                found_skills.add(skill)
            elif tag.lower() in skill.lower() and len(tag) > 3:
                found_skills.add(skill)

    # 2. Check description text for known skills
    desc_lower = description_text.lower()
    for skill in known_skills:
        # Match word boundaries to prevent substring collisions (e.g. "Java" in "Javascript")
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, desc_lower):
            found_skills.add(skill)
            
    # Substring adjustments/normalizations
    if "Machine Learning" in found_skills or "Deep Learning" in found_skills:
        found_skills.add("AI/ML")
    if "Collaboration" in found_skills:
        found_skills.add("Teamwork")

    # If no skills found, assign a couple based on title keywords
    if not found_skills:
        if "data" in desc_lower:
            found_skills.update(["SQL", "Excel", "Data Analytics"])
        elif "developer" in desc_lower or "engineer" in desc_lower:
            found_skills.update(["Python", "Java"])
        else:
            found_skills.update(["Communication", "Teamwork"])

    return ", ".join(sorted(list(found_skills)))

def main():
    # 1. Create target data directory
    output_dir = r"C:\Users\admin\.gemini\antigravity\scratch\major-project\data"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created data directory at: {output_dir}")

    # 2. Call Arbeitnow API
    api_url = "https://www.arbeitnow.com/api/job-board-api"
    print(f"Fetching job listings from: {api_url}")
    
    try:
        req = urllib.request.Request(
            api_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching API data: {e}")
        return

    jobs_list = res_data.get("data", [])
    print(f"Successfully retrieved {len(jobs_list)} jobs from Arbeitnow.")

    # 3. Process jobs and write to jobs.csv
    csv_file_path = os.path.join(output_dir, "jobs.csv")
    headers = [
        "Job_ID", "Job_Title", "Industry", "Location", 
        "Experience_Required", "Education_Required", "Skills_Required", 
        "Job_Description", "Posting_Date"
    ]

    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for idx, job in enumerate(jobs_list, start=1):
            job_id = f"JOB_{idx:03d}"
            title = job.get("title", "")
            location = job.get("location", "")
            posting_date = job.get("created_at", "")
            raw_desc = job.get("description", "")
            tags = job.get("tags", [])

            # Clean and parse text
            cleaned_desc = clean_html(raw_desc)
            experience = extract_experience(cleaned_desc)
            education = extract_education(cleaned_desc)
            skills = extract_skills(tags, cleaned_desc)

            # Determine industry based on tags or default to Technology
            industry = "Technology"
            tech_tags = [t.lower() for t in tags]
            if any(term in tech_tags for term in ["finance", "fintech", "banking"]):
                industry = "Finance"
            elif any(term in tech_tags for term in ["marketing", "sales", "seo"]):
                industry = "Marketing"
            elif any(term in tech_tags for term in ["health", "healthcare", "medical"]):
                industry = "Healthcare"

            writer.writerow([
                job_id, title, industry, location, 
                experience, education, skills, 
                cleaned_desc, posting_date
            ])

    print(f"Successfully wrote job listings to {csv_file_path}")

if __name__ == "__main__":
    main()
