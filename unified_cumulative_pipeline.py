import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.decomposition import PCA
import mlflow
import mlflow.sklearn

os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"

proj_dir = r"C:\Users\admin\.gemini\antigravity\scratch\major-project"
data_dir = os.path.join(proj_dir, "data")
plots_dir = os.path.join(proj_dir, "plots")
os.makedirs(plots_dir, exist_ok=True)

# 1. Setup MLflow Tracking with SQLite Backend
mlflow.set_tracking_uri("sqlite:///mlflow.db")
experiment_name = "EduPathAI_Cumulative_Unified_Pipeline"
mlflow.set_experiment(experiment_name)

print("=" * 80)
print(" CUMULATIVE UNIFIED PIPELINE (7,381 RECORDS): EDUPATHAI + PS2_DATASET")
print("=" * 80)

# 2. Ingest Both Datasets
s_df = pd.read_csv(os.path.join(data_dir, "students_employability.csv"))
e_df = pd.read_csv(os.path.join(data_dir, "learning_engagement.csv"))
p_df = pd.read_csv(os.path.join(data_dir, "cleaned_ps2_dataset.csv"))

print(f"Loaded Dataset 1 (EduPathAI Core): {len(s_df)} student profiles, {len(e_df)} engagement logs.")
print(f"Loaded Dataset 2 (PS2 Benchmark): {len(p_df)} candidate records.")

# 3. Schema Harmonization Layer
# Harmonize Dataset 1 (480 records)
e_agg = e_df.groupby("Student_ID").agg({
    "Content_Completion_Percentage": "mean",
    "Assignment_Submission": "mean"
}).reset_index()
m1 = pd.merge(s_df, e_agg, on="Student_ID")

def parse_bloom_technical_proficiency(prof_str):
    if not isinstance(prof_str, str):
        return 6.0
    vals = [float(x.split(":")[1]) for x in prof_str.split(",") if ":" in x]
    return float(np.mean(vals) * 10) if vals else 6.0

d1 = pd.DataFrame({
    "student_id": m1["Student_ID"],
    "source_dataset": "EduPathAI_Core",
    "cognitive_rating": m1["Assessment_Score"].clip(1, 10),
    "coding_technical_rating": m1["Skill_Proficiencies"].apply(parse_bloom_technical_proficiency),
    "experiential_exposure": (m1["Assignment_Submission"] * 1.2 + (m1["Projects"] != "None") * 2.5 + (m1["Certifications"] != "None") * 1.5).clip(0, 10),
    "communication_soft_skills": np.where(m1["Soft_Skills"].str.contains("Communication", na=False), 7.5, 5.0),
    "self_learning_capability": (m1["Content_Completion_Percentage"] >= 75).astype(int),
    "team_collaboration": m1["Soft_Skills"].str.contains("Teamwork", na=False).astype(int),
    "track_technical": (m1["Degree"].isin(["B.Tech", "B.Sc"])).astype(int),
    "target_role": m1["Career_Interest"]
})

# Harmonize Dataset 2 (6,901 records)
d2 = pd.DataFrame({
    "student_id": [f"PS2_{i:04d}" for i in range(1, len(p_df) + 1)],
    "source_dataset": "PS2_Benchmark",
    "cognitive_rating": p_df["logical_quotient_rating"].astype(float),
    "coding_technical_rating": p_df["coding_skills_rating"].astype(float),
    "experiential_exposure": (p_df["hackathons"] * 1.2 + (p_df["extra_courses_completed"] == "yes") * 2.0).clip(0, 10),
    "communication_soft_skills": (p_df["public_speaking_points"] * 1.1).clip(1, 10),
    "self_learning_capability": (p_df["self_learning_capability"] == "yes").astype(int),
    "team_collaboration": (p_df["worked_in_teams"] == "yes").astype(int),
    "track_technical": (p_df["career_track_orientation"] == "Technical").astype(int),
    "target_role": p_df["suggested_job_role"]
})

unified = pd.concat([d1, d2], ignore_index=True)
n_total = len(unified)

# Career Domain Vertical Taxonomy Mapping
domain_map = {
    # Software & App Engineering
    "Frontend Developer": "Software & Web Development",
    "Backend Developer": "Software & Web Development",
    "Full-Stack Developer": "Software & Web Development",
    "Applications Developer": "Software & Web Development",
    "Software Developer": "Software & Web Development",
    "Software Engineer": "Software & Web Development",
    "Mobile Applications Developer": "Software & Web Development",
    "CRM Technical Developer": "Software & Web Development",
    "Web Developer": "Software & Web Development",
    # Data Science, AI & Analytics
    "AI Engineer": "Data Science & AI",
    "Data Scientist": "Data Science & AI",
    "Data Analyst": "Data Science & AI",
    "BI Developer": "Data Science & AI",
    "Business Analyst": "Business & Analytics",
    "Financial Analyst": "Business & Analytics",
    "Marketing Analyst": "Business & Analytics",
    "Digital Marketing Specialist": "Business & Analytics",
    # Cybersecurity & Infrastructure
    "Cybersecurity Analyst": "Cybersecurity & Cloud",
    "Cloud DevOps Engineer": "Cybersecurity & Cloud",
    "Database Administrator": "Cybersecurity & Cloud",
    "Network Security Engineer": "Cybersecurity & Cloud",
    "Security Administrator": "Cybersecurity & Cloud",
    "Systems Security Administrator": "Cybersecurity & Cloud",
    "Database Developer": "Cybersecurity & Cloud",
    # UI/UX & Design
    "UI/UX Designer": "UI/UX & Product Design",
    "Product Manager": "UI/UX & Product Design",
    "UX Designer": "UI/UX & Product Design",
    # QA & Technical Support
    "Software Quality Assurance (QA) / Testing": "QA & IT Support",
    "Technical Support": "QA & IT Support"
}
unified["canonical_domain"] = unified["target_role"].map(domain_map)

# Save harmonized dataset
unified_path = os.path.join(data_dir, "unified_cumulative_dataset.csv")
unified.to_csv(unified_path, index=False)
print(f"Created Unified Cumulative Dataset: {unified_path} ({n_total} records, 0 nulls).")

# Feature Scaling
feature_cols = [
    "cognitive_rating",
    "coding_technical_rating",
    "experiential_exposure",
    "communication_soft_skills",
    "self_learning_capability",
    "team_collaboration",
    "track_technical"
]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(unified[feature_cols])

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

results = []

# ==============================================================================
# RUN 1: CUMULATIVE K-MEANS CLUSTERING (ALL 7,381 RECORDS)
# ==============================================================================
print("\n[1/4] Running Run 1: Pure K-Means on ALL 7,381 Unified Records...")
kmeans_params = {
    "n_clusters": 3,
    "init": "k-means++",
    "n_init": 10,
    "random_state": 42
}

with mlflow.start_run(run_name="1_KMeans_Clustering_ALL_7381_Records"):
    mlflow.log_params(kmeans_params)
    mlflow.log_param("dataset", "Cumulative_Unified_Dataset")
    mlflow.log_param("total_records_clustered", n_total)
    mlflow.log_param("edupathai_core_records", len(d1))
    mlflow.log_param("ps2_benchmark_records", len(d2))

    km = KMeans(**kmeans_params)
    km_labels = km.fit_predict(X_scaled)

    # Compute cluster distributions across all 7,381
    cluster_counts = pd.Series(km_labels).value_counts().sort_index().to_dict()
    for c_id, count in cluster_counts.items():
        mlflow.log_metric(f"cluster_{c_id}_size", count)
        mlflow.log_metric(f"cluster_{c_id}_pct", round(float(count / n_total * 100), 2))

    sil = float(silhouette_score(X_scaled, km_labels, sample_size=3000, random_state=42))
    db = float(davies_bouldin_score(X_scaled, km_labels))
    ch = float(calinski_harabasz_score(X_scaled, km_labels))

    metrics_km = {
        "silhouette_score": round(sil, 4),
        "davies_bouldin_index": round(db, 4),
        "calinski_harabasz_score": round(ch, 2),
        "inertia": round(float(km.inertia_), 2),
        "total_records_clustered": n_total
    }
    mlflow.log_metrics(metrics_km)

    # Cluster Size Bar Chart
    plt.figure(figsize=(7, 4.5))
    bars = plt.bar([f"Persona Cluster {k}" for k in cluster_counts.keys()], list(cluster_counts.values()), color=["#1E88E5", "#43A047", "#FB8C00"], width=0.5)
    plt.ylabel("Number of Students / Candidates")
    plt.title(f"K-Means Cluster Breakdown Across ALL {n_total} Records", fontsize=11, fontweight="bold")
    plt.ylim(0, max(cluster_counts.values()) * 1.2)
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2., h + 60, f"{h:,} ({h/n_total*100:.1f}%)", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    km_bar_plot = os.path.join(plots_dir, "cumulative_kmeans_cluster_sizes.png")
    plt.savefig(km_bar_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(km_bar_plot, artifact_path="plots")

    # 2D PCA Visual
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=km_labels, cmap="viridis", alpha=0.6, edgecolors="none", s=16)
    plt.title(f"Cumulative Dataset: Standard K-Means (N={n_total}, Silhouette: {sil:.4f})", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Harmonized Persona Cluster")
    plt.tight_layout()
    km_plot = os.path.join(plots_dir, "cumulative_cluster_standard_kmeans.png")
    plt.savefig(km_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(km_plot, artifact_path="plots")

    mlflow.sklearn.log_model(km, name="model", serialization_format="pickle")
    results.append({"Pipeline": f"Cumulative K-Means Baseline ({n_total} rows)", **metrics_km})
    print(f" -> Logged! Cumulative Silhouette: {sil:.4f}, Davies-Bouldin: {db:.4f}")
    for c_id, count in cluster_counts.items():
        print(f"    - Cluster {c_id}: {count:,} students ({count/n_total*100:.1f}%)")

# ==============================================================================
# RUN 2: CUMULATIVE ISOLATION FOREST (ALL 7,381 RECORDS)
# ==============================================================================
print("\n[2/4] Running Run 2: Pure Isolation Forest on ALL 7,381 Unified Records...")
iso_params = {
    "n_estimators": 100,
    "contamination": 0.05,
    "random_state": 42
}

with mlflow.start_run(run_name="2_Isolation_Forest_Scoring_ALL_7381_Records"):
    mlflow.log_params(iso_params)
    mlflow.log_param("dataset", "Cumulative_Unified_Dataset")
    mlflow.log_param("total_records_scored", n_total)

    iso = IsolationForest(**iso_params)
    iso_preds = iso.fit_predict(X_scaled)
    anomaly_scores = iso.decision_function(X_scaled)

    is_outlier = (iso_preds == -1)
    outlier_count = int(np.sum(is_outlier))
    inlier_count = n_total - outlier_count
    outlier_pct = float(outlier_count / n_total * 100)

    # Cross-source anomaly breakdown
    edupath_outliers = int(np.sum(is_outlier[:len(d1)]))
    ps2_outliers = int(np.sum(is_outlier[len(d1):]))

    metrics_iso = {
        "total_records_scored": n_total,
        "normal_inliers_count": inlier_count,
        "anomalies_detected": outlier_count,
        "anomaly_percentage": round(outlier_pct, 2),
        "edupath_core_anomalies": edupath_outliers,
        "ps2_benchmark_anomalies": ps2_outliers,
        "mean_anomaly_score": round(float(np.mean(anomaly_scores)), 4),
        "min_anomaly_score": round(float(np.min(anomaly_scores)), 4),
        "max_anomaly_score": round(float(np.max(anomaly_scores)), 4)
    }
    mlflow.log_metrics(metrics_iso)

    # Anomaly Score Histogram across all 7,381 students
    plt.figure(figsize=(8, 4.5))
    plt.hist(anomaly_scores[~is_outlier], bins=40, color="#1E88E5", alpha=0.7, label=f"Normal Inliers ({inlier_count:,})")
    plt.hist(anomaly_scores[is_outlier], bins=20, color="#E53935", alpha=0.9, label=f"Detected Anomalies ({outlier_count:,})")
    plt.axvline(0.0, color="black", linestyle="--", linewidth=1.5, label="Decision Boundary")
    plt.xlabel("Isolation Forest Anomaly Score (Lower = More Anomalous)")
    plt.ylabel("Number of Students")
    plt.title(f"Isolation Forest Anomaly Score Distribution Across ALL {n_total} Records", fontsize=11, fontweight="bold")
    plt.legend()
    plt.tight_layout()
    iso_hist_plot = os.path.join(plots_dir, "cumulative_anomaly_score_histogram.png")
    plt.savefig(iso_hist_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(iso_hist_plot, artifact_path="plots")

    # Plot Outlier Scatter
    plt.figure(figsize=(8, 6))
    colors = ["#E53935" if p == -1 else "#1E88E5" for p in iso_preds]
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=colors, alpha=0.5, edgecolors="none", s=16)
    plt.title(f"Cumulative Isolation Forest (Found {outlier_count} Anomalies / {outlier_pct:.1f}%)", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.tight_layout()
    iso_plot = os.path.join(plots_dir, "cumulative_cluster_isolation_forest.png")
    plt.savefig(iso_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(iso_plot, artifact_path="plots")

    mlflow.sklearn.log_model(iso, name="model", serialization_format="pickle")
    results.append({"Pipeline": f"Cumulative Isolation Forest ({n_total} rows)", "silhouette_score": np.nan, "davies_bouldin_index": np.nan, "calinski_harabasz_score": np.nan, "records_clustered": n_total})
    print(f" -> Logged! Scored all {n_total:,} records: {inlier_count:,} Normal Inliers (95%), {outlier_count:,} Anomalies (5%)")

# ==============================================================================
# RUN 3: CUMULATIVE HYBRID ISOLATION + K-MEANS (7,381 RECORDS)
# ==============================================================================
print("\n[3/4] Running Run 3: Cumulative Hybrid (Isolation -> K-Means) (7,381 records)...")
hybrid_params = {
    "iso_n_estimators": 100,
    "iso_contamination": 0.05,
    "kmeans_clusters": 3,
    "random_state": 42
}

with mlflow.start_run(run_name="3_Hybrid_Isolation_KMeans_ALL_7381_Records"):
    mlflow.log_params(hybrid_params)
    mlflow.log_param("dataset", "Cumulative_Unified_Dataset")
    mlflow.log_param("total_cohort_records", n_total)
    mlflow.log_param("architecture", "Two-Stage Anomaly Filtering + Persona Clustering")

    # Stage 1: Purge anomalies across all 7,381
    iso_hyb = IsolationForest(
        n_estimators=hybrid_params["iso_n_estimators"],
        contamination=hybrid_params["iso_contamination"],
        random_state=hybrid_params["random_state"]
    )
    inlier_mask = (iso_hyb.fit_predict(X_scaled) == 1)
    X_inliers = X_scaled[inlier_mask]
    n_inliers = len(X_inliers)
    n_outliers = n_total - n_inliers

    # Stage 2: K-Means on clean inliers
    km_hyb = KMeans(
        n_clusters=hybrid_params["kmeans_clusters"],
        init="k-means++",
        n_init=10,
        random_state=hybrid_params["random_state"]
    )
    inlier_labels = km_hyb.fit_predict(X_inliers)

    sil_hyb = float(silhouette_score(X_inliers, inlier_labels, sample_size=3000, random_state=42))
    db_hyb = float(davies_bouldin_score(X_inliers, inlier_labels))
    ch_hyb = float(calinski_harabasz_score(X_inliers, inlier_labels))

    metrics_hybrid = {
        "silhouette_score": round(sil_hyb, 4),
        "davies_bouldin_index": round(db_hyb, 4),
        "calinski_harabasz_score": round(ch_hyb, 2),
        "total_records_processed": n_total,
        "inliers_clustered": n_inliers,
        "outliers_isolated": n_outliers,
        "silhouette_gain_vs_baseline": round(sil_hyb - sil, 4)
    }
    mlflow.log_metrics(metrics_hybrid)

    # Plot Clean Inliers + Marked Red Cross Anomalies
    plt.figure(figsize=(9, 6.5))
    X_inliers_pca = X_pca[inlier_mask]
    X_outliers_pca = X_pca[~inlier_mask]

    scatter = plt.scatter(X_inliers_pca[:, 0], X_inliers_pca[:, 1], c=inlier_labels, cmap="viridis", alpha=0.6, edgecolors="none", s=18, label=f"Clean Persona Cohorts (N={n_inliers:,})")
    plt.scatter(X_outliers_pca[:, 0], X_outliers_pca[:, 1], color="#E53935", marker="x", s=40, linewidths=1.5, label=f"Isolated Anomalies (N={n_outliers:,})")
    plt.title(f"Cumulative Hybrid: Isolation + K-Means (Silhouette: {sil:.4f} -> {sil_hyb:.4f})", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Clean Aptitude Persona")
    plt.legend(loc="upper right")
    plt.tight_layout()
    hyb_plot = os.path.join(plots_dir, "cumulative_cluster_hybrid_isolation_kmeans.png")
    plt.savefig(hyb_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(hyb_plot, artifact_path="plots")

    # Comparative Silhouette Chart
    plt.figure(figsize=(7, 4.5))
    models = [f"Cumulative Standard K-Means\n(ALL {n_total:,} Rows)", f"Cumulative Hybrid\n(Clean {n_inliers:,} Inliers)"]
    scores = [sil, sil_hyb]
    bars = plt.bar(models, scores, color=["#90CAF9", "#1E88E5"], width=0.45)
    plt.ylabel("Silhouette Score (Higher=Better)")
    plt.title(f"Cumulative Pipeline: Silhouette Comparison ({n_total:,} Records)", fontsize=11, fontweight="bold")
    plt.ylim(0, max(scores) * 1.35)
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2., h + 0.003, f"{h:.4f}", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    comp_plot = os.path.join(plots_dir, "cumulative_cluster_silhouette_comparison.png")
    plt.savefig(comp_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(comp_plot, artifact_path="plots")

    # Export Per-Student Predictions Table across ALL 7,381 students
    predictions_df = unified.copy()
    predictions_df["kmeans_cluster_all_7381"] = km_labels
    predictions_df["isolation_forest_label"] = np.where(iso_preds == 1, "Normal_Inlier", "Anomalous_Outlier")
    predictions_df["isolation_forest_anomaly_score"] = np.round(anomaly_scores, 4)
    hybrid_persona_labels = np.full(n_total, "Targeted_Academic_Intervention", dtype=object)
    hybrid_persona_labels[inlier_mask] = [f"Clean_Persona_{lbl}" for lbl in inlier_labels]
    predictions_df["hybrid_persona_assignment"] = hybrid_persona_labels

    pred_csv_path = os.path.join(data_dir, "unified_cumulative_student_predictions.csv")
    predictions_df.to_csv(pred_csv_path, index=False)
    mlflow.log_artifact(pred_csv_path, artifact_path="predictions")
    print(f" -> Exported individual predictions for all {n_total:,} students to: {pred_csv_path}")

    mlflow.sklearn.log_model(km_hyb, name="kmeans_model", serialization_format="pickle")
    mlflow.sklearn.log_model(iso_hyb, name="isolation_forest_model", serialization_format="pickle")
    results.append({"Pipeline": f"Cumulative Hybrid: Isolation + K-Means ({n_total} rows)", **metrics_hybrid})
    print(f" -> Logged! Cumulative Hybrid Silhouette: {sil_hyb:.4f} (Inliers={n_inliers:,}, Outliers={n_outliers:,})")

# ==============================================================================
# RUN 4: CUMULATIVE CAREER DOMAIN CLASSIFIER (7,381 RECORDS)
# ==============================================================================
print("\n[4/4] Running Run 4: Cumulative Career Domain Classifier (Random Forest, 7,381 records)...")
le_domain = LabelEncoder()
y_domain = le_domain.fit_transform(unified["canonical_domain"])
domain_classes = list(le_domain.classes_)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_domain, test_size=0.20, random_state=42, stratify=y_domain
)

rf_params = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
}

with mlflow.start_run(run_name="4_Cumulative_Career_Domain_Classifier_7381"):
    mlflow.log_params(rf_params)
    mlflow.log_param("dataset", "Cumulative_Unified_Dataset")
    mlflow.log_param("target", "canonical_career_domain (6 classes)")
    mlflow.log_param("train_samples", len(X_train))
    mlflow.log_param("test_samples", len(X_test))

    rf_cls = RandomForestClassifier(**rf_params)
    rf_cls.fit(X_train, y_train)

    y_pred = rf_cls.predict(X_test)
    acc = round(float(accuracy_score(y_test, y_pred)), 4)
    prec = round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4)
    rec = round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4)

    metrics_rf = {
        "test_accuracy": acc,
        "precision_weighted": prec,
        "recall_weighted": rec,
        "f1_score_weighted": f1
    }
    mlflow.log_metrics(metrics_rf)

    # Plot Domain Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Purples",
                xticklabels=[c[:14] for c in domain_classes],
                yticklabels=[c[:14] for c in domain_classes])
    plt.title(f"Cumulative Career Domain Classifier (Accuracy: {acc*100:.2f}%)", fontsize=11, fontweight="bold")
    plt.xlabel("Predicted Career Domain")
    plt.ylabel("Actual Career Domain")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    cm_plot = os.path.join(plots_dir, "cumulative_domain_confusion_matrix.png")
    plt.savefig(cm_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(cm_plot, artifact_path="plots")

    # Feature Importances
    feat_imp = pd.Series(rf_cls.feature_importances_, index=feature_cols).sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    feat_imp.plot(kind="barh", color="#7E57C2").invert_yaxis()
    plt.title("Cumulative Feature Importances for Career Domain Prediction", fontsize=11, fontweight="bold")
    plt.xlabel("Importance Weight")
    plt.tight_layout()
    imp_plot = os.path.join(plots_dir, "cumulative_feature_importance.png")
    plt.savefig(imp_plot, dpi=200)
    plt.close()
    mlflow.log_artifact(imp_plot, artifact_path="plots")

    mlflow.sklearn.log_model(rf_cls, name="model", serialization_format="pickle")
    results.append({"Pipeline": "Cumulative Career Domain Classifier (7,381 rows)", "silhouette_score": np.nan, "davies_bouldin_index": np.nan, "calinski_harabasz_score": np.nan, "records_clustered": n_total})
    print(f" -> Logged! Cumulative Domain Classifier Test Accuracy: {acc*100:.2f}%, F1: {f1:.4f}")

# 5. Summary Table
print("\n" + "=" * 80)
print(" CUMULATIVE PIPELINE (7,381 RECORDS) BENCHMARK SUMMARY")
print("=" * 80)
summary_df = pd.DataFrame(results)
print(summary_df[["Pipeline", "silhouette_score", "davies_bouldin_index", "records_clustered"]].to_string(index=False))
summary_path = os.path.join(data_dir, "unified_cumulative_benchmark_results.csv")
summary_df.to_csv(summary_path, index=False)
print(f"\nSaved cumulative metrics to: {summary_path}")
print("ALL RUNS ON 7,381 RECORDS LOGGED TO MLFLOW (Experiment: EduPathAI_Cumulative_Unified_Pipeline)!")
