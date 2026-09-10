from recommendation_engine import RecommendationEngine

def print_separator(char="=", length=80):
    print(char * length)

def main():
    print_separator()
    print("AI-POWERED RECOMMENDATION ENGINE - PROTOTYPE DEMO")
    print_separator()
    
    # 1. Initialize and load datasets
    engine = RecommendationEngine()
    engine.load_data()
    engine.build_vectors()
    engine.perform_clustering()
    
    print_separator("-")
    
    # 2. Select diverse test students to inspect
    test_students = ["STU_011", "STU_029", "STU_046"]
    
    for target_student_id in test_students:
        student_row = engine.students_df[engine.students_df["Student_ID"] == target_student_id]
        if student_row.empty:
            print(f"Student {target_student_id} not found.")
            continue
            
        print_separator("-")
        print(f"TARGET STUDENT PROFILE: {target_student_id}")
        print(f"Academic Degree: {student_row['Degree'].values[0]} in {student_row['Specialisation'].values[0]}")
        print(f"Current GPA: {student_row['Assessment_Score'].values[0]} / 10.0")
        print(f"Expressed Career Interest: {student_row['Career_Interest'].values[0]}")
        print(f"Current Skills: {student_row['Technical_Skills'].values[0]} | {student_row['Soft_Skills'].values[0]}")
        
        # 3. Display Behavioral Profiling
        cluster_name = engine.get_student_cluster_name(target_student_id)
        willingness_score = engine.calculate_willingness_to_learn(target_student_id)
        print(f"Behavioral Cluster: {cluster_name}")
        print(f"Inferred 'Willingness to Learn' Score: {willingness_score}%")
        
        # 4. Display Job-Role Matching
        print("\nTOP JOB MATCHES:")
        top_matches = engine.match_jobs(target_student_id, top_n=2)
        for idx, match in enumerate(top_matches, start=1):
            print(f"  {idx}. {match['Job_Title']} (Match: {match['Match_Score']}%)")
            
        # 5. Take top matching job and find gaps/courses
        best_match = top_matches[0]
        best_job_id = best_match["Job_ID"]
        skill_gap, recommended_courses = engine.get_skill_gap_and_courses(target_student_id, best_job_id)
        
        print(f"\nANALYSIS FOR TOP ROLE: {best_match['Job_Title']}")
        print(f"  - Skills Required by Job: {best_match['Skills_Required']}")
        print(f"  - Detected Gaps in Student: {', '.join(skill_gap) if skill_gap else 'None (Skills fully aligned)'}")
        
        print("  - Recommended Pathway (Courses to Close Gaps):")
        if recommended_courses:
            for idx, course in enumerate(recommended_courses, start=1):
                print(f"     [{idx}] {course['Course_Title']} ({course['Platform']}) - Covers: {course['Skills_Covered']}")
        else:
            print("     No courses recommended (Skills already covered).")
            
        print("\nEXPLAINABLE AI (XAI) GENERATOR OUTPUT:")
        explanation = engine.generate_explanation(target_student_id, best_job_id, recommended_courses)
        print(explanation)
        print_separator("-")
    
    print_separator()

if __name__ == "__main__":
    main()
