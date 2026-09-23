import os
import json
import pandas as pd
from sklearn.preprocessing import LabelEncoder

proj_dir = r"C:\Users\admin\.gemini\antigravity\scratch\major-project"
data_dir = os.path.join(proj_dir, "data")
raw_path = os.path.join(data_dir, "raw_ps2_dataset.csv")

print("[1/4] Reading raw dataset...")
df_raw = pd.read_csv(raw_path)
print(f"Loaded {len(df_raw)} records, {df_raw.shape[1]} columns.")

print("[2/4] Standardizing column names...")
col_map = {
    "Logical quotient rating": "logical_quotient_rating",
    "hackathons": "hackathons",
    "coding skills rating": "coding_skills_rating",
    "public speaking points": "public_speaking_points",
    "self-learning capability?": "self_learning_capability",
    "Extra-courses did": "extra_courses_completed",
    "certifications": "certifications",
    "workshops": "workshops",
    "reading and writing skills": "reading_writing_skills",
    "memory capability score": "memory_capability_score",
    "Interested subjects": "interested_subjects",
    "interested career area ": "interested_career_area",
    "Type of company want to settle in?": "target_company_type",
    "Taken inputs from seniors or elders": "senior_advice_taken",
    "Interested Type of Books": "interested_book_type",
    "Management or Technical": "career_track_orientation",
    "hard/smart worker": "work_ethic_style",
    "worked in teams ever?": "worked_in_teams",
    "Introvert": "introvert_tendency",
    "Suggested Job Role": "suggested_job_role"
}
df = df_raw.rename(columns=lambda c: col_map.get(c.strip(), c.strip().lower().replace(" ", "_")))

# Clean string columns
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].astype(str).str.strip()

# Save cleaned human-readable CSV
cleaned_path = os.path.join(data_dir, "cleaned_ps2_dataset.csv")
df.to_csv(cleaned_path, index=False)
print(f"Saved cleaned human-readable CSV to: {cleaned_path}")

print("[3/4] Feature engineering & encoding...")
binary_maps = {
    "self_learning_capability": {"yes": 1, "no": 0},
    "extra_courses_completed": {"yes": 1, "no": 0},
    "senior_advice_taken": {"yes": 1, "no": 0},
    "worked_in_teams": {"yes": 1, "no": 0},
    "introvert_tendency": {"yes": 1, "no": 0},
    "career_track_orientation": {"Technical": 1, "Management": 0},
    "work_ethic_style": {"smart worker": 1, "hard worker": 0}
}
ordinal_map = {"poor": 1, "medium": 2, "excellent": 3}

df_encoded = df.copy()
for col, mapping in binary_maps.items():
    if col in df_encoded.columns:
        df_encoded[col] = df_encoded[col].map(mapping).fillna(0).astype(int)

df_encoded["reading_writing_skills"] = df_encoded["reading_writing_skills"].str.lower().map(ordinal_map).fillna(2).astype(int)
df_encoded["memory_capability_score"] = df_encoded["memory_capability_score"].str.lower().map(ordinal_map).fillna(2).astype(int)

# Target encoding
le_target = LabelEncoder()
df_encoded["target_role_encoded"] = le_target.fit_transform(df_encoded["suggested_job_role"])
target_classes = list(le_target.classes_)

# One-hot encode nominal categories
cat_nominal_cols = [
    "certifications", "workshops", "interested_subjects", 
    "interested_career_area", "target_company_type", "interested_book_type"
]
df_processed = pd.get_dummies(df_encoded, columns=cat_nominal_cols, drop_first=False, dtype=int)

print("[4/4] Saving processed dataset and metadata...")
processed_path = os.path.join(data_dir, "processed_ps2_dataset.csv")
df_processed.to_csv(processed_path, index=False)

metadata = {
    "dataset_name": "PS2_Dataset (Career Role Prediction Benchmark)",
    "source_file": "data/raw_ps2_dataset.csv",
    "cleaned_file": "data/cleaned_ps2_dataset.csv",
    "processed_file": "data/processed_ps2_dataset.csv",
    "total_records": len(df),
    "raw_features_count": df_raw.shape[1],
    "processed_features_count": df_processed.shape[1] - 2,
    "target_variable": "suggested_job_role",
    "target_classes_count": len(target_classes),
    "target_classes": target_classes,
    "class_distribution": df["suggested_job_role"].value_counts().to_dict()
}
meta_path = os.path.join(data_dir, "ps2_metadata.json")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print(f"Processed feature matrix: {df_processed.shape[0]} rows x {df_processed.shape[1]} columns")
print(f"Metadata exported to: {meta_path}")
print("ETL SUCCESSFUL!")
