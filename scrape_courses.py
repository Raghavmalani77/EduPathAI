import os
import csv

def main():
    output_dir = r"C:\Users\admin\.gemini\antigravity\scratch\major-project\data"
    os.makedirs(output_dir, exist_ok=True)
    csv_file_path = os.path.join(output_dir, "courses.csv")

    # Comprehensive course catalog covering all 16 career pathways
    courses = [
        {
            "Course_ID": "COURSE_001",
            "Course_Title": "Python Programming Masterclass",
            "Platform": "Coursera",
            "Skills_Developed": "Python, Data Analytics",
            "Duration_Hours": 32,
            "Description": "Comprehensive introduction to Python programming including variables, loops, data structures, and standard libraries."
        },
        {
            "Course_ID": "COURSE_002",
            "Course_Title": "SQL for Data Analysis and Business Intelligence",
            "Platform": "Udemy",
            "Skills_Developed": "SQL, Data Analytics, Database Management",
            "Duration_Hours": 24,
            "Description": "Learn SQL from scratch, including database management, complex joins, subqueries, and window functions."
        },
        {
            "Course_ID": "COURSE_003",
            "Course_Title": "Machine Learning Specialization",
            "Platform": "Coursera",
            "Skills_Developed": "Machine Learning, AI/ML, Python, Statistics",
            "Duration_Hours": 40,
            "Description": "Supervised and unsupervised learning, decision trees, neural networks, and machine learning practical workflows."
        },
        {
            "Course_ID": "COURSE_004",
            "Course_Title": "Deep Learning and Neural Networks",
            "Platform": "Coursera",
            "Skills_Developed": "Deep Learning, AI/ML, Python",
            "Duration_Hours": 35,
            "Description": "Deep dive into building, training, and fine-tuning neural networks, convolutional nets, and recurrent networks."
        },
        {
            "Course_ID": "COURSE_005",
            "Course_Title": "Power BI Desktop for Business Intelligence",
            "Platform": "Udemy",
            "Skills_Developed": "Power BI, Data Visualisation, Business Analytics",
            "Duration_Hours": 18,
            "Description": "Master data modeling, DAX expressions, and building interactive, professional dashboards in Power BI."
        },
        {
            "Course_ID": "COURSE_006",
            "Course_Title": "Statistics and Probability for Data Science",
            "Platform": "edX",
            "Skills_Developed": "Statistics, Excel, Python",
            "Duration_Hours": 28,
            "Description": "Probability theory, statistical significance, regression, and data distributions using Excel and Python."
        },
        {
            "Course_ID": "COURSE_007",
            "Course_Title": "Java Programming and Software Engineering",
            "Platform": "Coursera",
            "Skills_Developed": "Java, REST APIs",
            "Duration_Hours": 45,
            "Description": "Introduction to Java and object-oriented programming concepts, algorithms, and software design principles."
        },
        {
            "Course_ID": "COURSE_008",
            "Course_Title": "Web Development Bootcamp (HTML, CSS, JS, React)",
            "Platform": "Udemy",
            "Skills_Developed": "HTML, Javascript, CSS, React, Web Development",
            "Duration_Hours": 55,
            "Description": "Modern front-end and full-stack development covering HTML5, CSS3, ES6+ Javascript, React, and responsive layouts."
        },
        {
            "Course_ID": "COURSE_009",
            "Course_Title": "Cloud Computing Essentials (AWS & Azure)",
            "Platform": "Coursera",
            "Skills_Developed": "Cloud, AWS, Azure, Docker",
            "Duration_Hours": 30,
            "Description": "Fundamental architectural principles of cloud computing, covering virtual machines, S3 storage, IAM, and serverless containers."
        },
        {
            "Course_ID": "COURSE_010",
            "Course_Title": "Business Communication & Presentation Skills",
            "Platform": "LinkedIn Learning",
            "Skills_Developed": "Communication, Presentation",
            "Duration_Hours": 12,
            "Description": "Techniques for concise written and verbal workplace communication, storytelling with data, and effective slide delivery."
        },
        {
            "Course_ID": "COURSE_011",
            "Course_Title": "Interpersonal Skills & Team Collaboration",
            "Platform": "edX",
            "Skills_Developed": "Teamwork, Collaboration, Interpersonal Skills",
            "Duration_Hours": 10,
            "Description": "Conflict resolution, active listening, cross-functional collaboration, and effective teamwork in hybrid work environments."
        },
        {
            "Course_ID": "COURSE_012",
            "Course_Title": "Professionalism & Problem Solving in Tech",
            "Platform": "Coursera",
            "Skills_Developed": "Problem Solving, Critical Thinking",
            "Duration_Hours": 15,
            "Description": "Analytical frameworks for root-cause analysis, workplace ethics, and pragmatic technical decision-making."
        },
        {
            "Course_ID": "COURSE_013",
            "Course_Title": "Advanced Excel for Financial Analysis",
            "Platform": "Udemy",
            "Skills_Developed": "Excel, Finance, Financial Modeling",
            "Duration_Hours": 20,
            "Description": "Financial functions, dynamic array formulas, Pivot Tables, lookup logic, and spreadsheet financial modeling."
        },
        {
            "Course_ID": "COURSE_014",
            "Course_Title": "Search Engine Optimization (SEO) & Content Strategy",
            "Platform": "Coursera",
            "Skills_Developed": "SEO, Digital Marketing, Content Strategy",
            "Duration_Hours": 22,
            "Description": "Keyword research, technical on-page optimization, backlink strategies, and conversion rate optimization."
        },
        {
            "Course_ID": "COURSE_015",
            "Course_Title": "Social Media Marketing & Consumer Analytics",
            "Platform": "Udemy",
            "Skills_Developed": "Social Media Analytics, Digital Marketing, Marketing Analytics",
            "Duration_Hours": 16,
            "Description": "Campaign management across social platforms, audience targeting, attribution modeling, and customer segmentation."
        },
        {
            "Course_ID": "COURSE_016",
            "Course_Title": "Introduction to Corporate Finance & Accounting",
            "Platform": "edX",
            "Skills_Developed": "Finance, Accounting",
            "Duration_Hours": 25,
            "Description": "Core financial statements, revenue recognition, budgeting, cash flow forecasting, and financial ratios."
        },
        # Expanded courses for the 16 career pathways
        {
            "Course_ID": "COURSE_017",
            "Course_Title": "Tableau for Advanced Data Visualization",
            "Platform": "Coursera",
            "Skills_Developed": "Tableau, Data Visualisation, Business Analytics",
            "Duration_Hours": 22,
            "Description": "Build executive interactive dashboards, calculate level of detail expressions, and master visual storytelling."
        },
        {
            "Course_ID": "COURSE_018",
            "Course_Title": "DevOps Engineering: Docker, Kubernetes & CI/CD",
            "Platform": "Udemy",
            "Skills_Developed": "Docker, Kubernetes, CI/CD, Linux, Cloud",
            "Duration_Hours": 38,
            "Description": "Containerization, microservices deployment, Helm charts, automated GitHub Actions pipelines, and cloud orchestration."
        },
        {
            "Course_ID": "COURSE_019",
            "Course_Title": "Cybersecurity Fundamentals & Network Defense",
            "Platform": "Coursera",
            "Skills_Developed": "Cybersecurity, Network Security, Cryptography, Linux",
            "Duration_Hours": 36,
            "Description": "Threat modeling, network architecture, penetration testing basics, firewall configuration, and vulnerability management."
        },
        {
            "Course_ID": "COURSE_020",
            "Course_Title": "Full-Stack Node.js and Express Backend Development",
            "Platform": "Udemy",
            "Skills_Developed": "Node.js, Javascript, REST APIs, SQL, Full-Stack",
            "Duration_Hours": 42,
            "Description": "Build asynchronous server-side REST APIs, integrate databases, handle user authentication, and deploy web applications."
        },
        {
            "Course_ID": "COURSE_021",
            "Course_Title": "UI/UX Design Masterclass: Figma to Prototype",
            "Platform": "Coursera",
            "Skills_Developed": "Figma, UI Design, UX Research, Wireframing, Prototyping",
            "Duration_Hours": 30,
            "Description": "User journey mapping, wireframing, component design systems in Figma, interactive micro-interactions, and usability testing."
        },
        {
            "Course_ID": "COURSE_022",
            "Course_Title": "Product Management Fundamentals: Strategy to Launch",
            "Platform": "Udemy",
            "Skills_Developed": "Product Strategy, Agile/Scrum, User Research, Roadmapping",
            "Duration_Hours": 26,
            "Description": "Define product vision, craft user stories, prioritize backlogs using RICE framework, and lead cross-functional sprints."
        },
        {
            "Course_ID": "COURSE_023",
            "Course_Title": "Enterprise Database Administration & PostgreSQL Tuning",
            "Platform": "edX",
            "Skills_Developed": "Database Management, SQL, PostgreSQL, Linux",
            "Duration_Hours": 32,
            "Description": "Index optimization, query execution plan tuning, high-availability clustering, backup strategies, and replication."
        },
        {
            "Course_ID": "COURSE_024",
            "Course_Title": "Data Warehousing and ETL Pipelines with SQL",
            "Platform": "Coursera",
            "Skills_Developed": "Data Warehousing, ETL, SQL, Business Analytics",
            "Duration_Hours": 28,
            "Description": "Star schema modeling, building automated ETL extraction pipelines, data staging, and dimensional data modeling."
        },
        {
            "Course_ID": "COURSE_025",
            "Course_Title": "Modern Frontend React and Redux Development",
            "Platform": "Udemy",
            "Skills_Developed": "React, Javascript, CSS, HTML, Frontend Development",
            "Duration_Hours": 35,
            "Description": "Hooks, component lifecycles, global state management with Redux Toolkit, and performance optimization in React."
        },
        {
            "Course_ID": "COURSE_026",
            "Course_Title": "Customer Segmentation & Marketing Analytics",
            "Platform": "Coursera",
            "Skills_Developed": "Marketing Analytics, Customer Segmentation, Python, Excel",
            "Duration_Hours": 24,
            "Description": "RFM analysis, customer lifetime value modeling, churn modeling, and A/B testing analytics for modern marketing."
        },
        {
            "Course_ID": "COURSE_027",
            "Course_Title": "Financial Modeling & Valuation Masterclass",
            "Platform": "Udemy",
            "Skills_Developed": "Financial Modeling, Finance, Excel, Accounting",
            "Duration_Hours": 30,
            "Description": "Discounted cash flow (DCF) modeling, leveraged buyout (LBO) fundamentals, and M&A valuation techniques."
        },
        {
            "Course_ID": "COURSE_028",
            "Course_Title": "Linux System Administration and Shell Scripting",
            "Platform": "edX",
            "Skills_Developed": "Linux, Cloud, Problem Solving",
            "Duration_Hours": 20,
            "Description": "Command line mastery, bash shell scripting, system permissions, cron jobs, process management, and networking diagnostics."
        }
    ]

    fieldnames = ["Course_ID", "Course_Title", "Platform", "Skills_Developed", "Duration_Hours", "Description"]

    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for course in courses:
            writer.writerow(course)

    print(f"Successfully compiled {len(courses)} courses to: {csv_file_path}")

if __name__ == "__main__":
    main()
