import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
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
experiment_name = "EduPathAI_PS2_Clustering_Benchmark"
mlflow.set_experiment(experiment_name)

print("=" * 80)
print(" PS2_DATASET (6,901 RECORDS): K-MEANS vs ISOLATION FOREST vs HYBRID PIPELINE")
print("=" * 80)

# 2. Ingest PS2 Dataset (6,901 Records)
ps2_path = os.path.join(data_dir, "processed_ps2_dataset.csv")
df = pd.read_csv(ps2_path)
n_total = len(df)
print(f"Successfully loaded PS2_Dataset: {n_total} records.")

# Clustering Feature Set: Cognitive Aptitude, Technical Skill, and Behavioral Pacing
feature_cols = [
    "logical_quotient_rating",
    "coding_skills_rating",
    "hackathons",
    "public_speaking_points",
    "self_learning_capability",
    "extra_courses_completed",
    "reading_writing_skills",
    "memory_capability_score",
    "senior_advice_taken",
    "career_track_orientation",
    "work_ethic_style",
    "worked_in_teams",
    "introvert_tendency"
]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[feature_cols])

# Compute 2D PCA projection for consistent visualization
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

results = []

# ==============================================================================
# RUN 1: STANDARD K-MEANS (6,901 RECORDS)
# ==============================================================================
print("\n[1/3] Running Run 1: Standard K-Means on PS2 (6,901 records)...")
kmeans_params = {
    "n_clusters": 3,
    "init": "k-means++",
    "n_init": 10,
    "random_state": 42
}

with mlflow.start_run(run_name="1_PS2_Standard_KMeans_6901"):
    mlflow.log_params(kmeans_params)
    mlflow.log_param("dataset_name", "PS2_Dataset")
    mlflow.log_param("total_records", n_total)
    mlflow.log_param("features_count", len(feature_cols))
    mlflow.log_param("architecture", "Single-Stage K-Means")

    km = KMeans(**kmeans_params)
    km_labels = km.fit_predict(X_scaled)

    # Compute clustering evaluation metrics
    sil = float(silhouette_score(X_scaled, km_labels, sample_size=3000, random_state=42))
    db = float(davies_bouldin_score(X_scaled, km_labels))
    ch = float(calinski_harabasz_score(X_scaled, km_labels))

    metrics_km = {
        "silhouette_score": round(sil, 4),
        "davies_bouldin_index": round(db, 4),
        "calinski_harabasz_score": round(ch, 2),
        "records_clustered": n_total,
        "clusters_count": 3
    }
    mlflow.log_metrics(metrics_km)

    # Plot PCA Clusters
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=km_labels, cmap="viridis", alpha=0.6, edgecolors="none", s=18)
    plt.title(f"PS2_Dataset: Standard K-Means (N={n_total}, Silhouette: {sil:.4f})", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Candidate Aptitude Cluster")
    plt.tight_layout()
    km_plot_path = os.path.join(plots_dir, "ps2_cluster_standard_kmeans.png")
    plt.savefig(km_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(km_plot_path, artifact_path="plots")

    mlflow.sklearn.log_model(km, name="model", serialization_format="pickle")
    results.append({"Pipeline": "Standard K-Means (6,901 rows)", **metrics_km})
    print(f" -> Logged! PS2 Baseline Silhouette: {sil:.4f}, Davies-Bouldin: {db:.4f}")

# ==============================================================================
# RUN 2: ISOLATION FOREST ANOMALY DETECTION (6,901 RECORDS)
# ==============================================================================
print("\n[2/3] Running Run 2: Isolation Forest Anomaly Detection on PS2 (6,901 records)...")
iso_params = {
    "n_estimators": 100,
    "contamination": 0.05,  # 5% expected anomaly rate in 6,901 records (~345 anomalies)
    "random_state": 42
}

with mlflow.start_run(run_name="2_PS2_IsolationForest_Only_6901"):
    mlflow.log_params(iso_params)
    mlflow.log_param("dataset_name", "PS2_Dataset")
    mlflow.log_param("total_records", n_total)
    mlflow.log_param("architecture", "Pure Isolation Forest Anomaly Detection")

    iso = IsolationForest(**iso_params)
    iso_preds = iso.fit_predict(X_scaled)  # 1: Inlier, -1: Outlier
    anomaly_scores = iso.decision_function(X_scaled)

    is_outlier = (iso_preds == -1)
    outlier_count = int(np.sum(is_outlier))
    outlier_pct = float(outlier_count / n_total * 100)

    metrics_iso = {
        "outlier_count": outlier_count,
        "inlier_count": n_total - outlier_count,
        "outlier_percentage": round(outlier_pct, 2),
        "mean_anomaly_score": round(float(np.mean(anomaly_scores)), 4)
    }
    mlflow.log_metrics(metrics_iso)

    # Plot Outlier Distribution
    plt.figure(figsize=(8, 6))
    colors = ["#E53935" if p == -1 else "#1E88E5" for p in iso_preds]
    alphas = [0.9 if p == -1 else 0.4 for p in iso_preds]
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=colors, alpha=0.5, edgecolors="none", s=18)
    plt.title(f"PS2_Dataset: Isolation Forest (Identified {outlier_count} Anomalies / {outlier_pct:.1f}%)", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.tight_layout()
    iso_plot_path = os.path.join(plots_dir, "ps2_cluster_isolation_forest.png")
    plt.savefig(iso_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(iso_plot_path, artifact_path="plots")

    mlflow.sklearn.log_model(iso, name="model", serialization_format="pickle")
    results.append({"Pipeline": "Isolation Forest Only (6,901 rows)", "silhouette_score": np.nan, "davies_bouldin_index": np.nan, "calinski_harabasz_score": np.nan, "records_clustered": n_total, "clusters_count": 2})
    print(f" -> Logged! PS2 Outliers Detected: {outlier_count} ({outlier_pct:.1f}%), Inliers: {n_total - outlier_count}")

# ==============================================================================
# RUN 3: HYBRID ISOLATION FOREST + K-MEANS (6,901 RECORDS)
# ==============================================================================
print("\n[3/3] Running Run 3: Hybrid Isolation + K-Means on PS2 (6,901 records)...")
hybrid_params = {
    "iso_n_estimators": 100,
    "iso_contamination": 0.05,
    "kmeans_clusters": 3,
    "random_state": 42
}

with mlflow.start_run(run_name="3_PS2_Hybrid_Isolation_KMeans_6901"):
    mlflow.log_params(hybrid_params)
    mlflow.log_param("dataset_name", "PS2_Dataset")
    mlflow.log_param("total_records", n_total)
    mlflow.log_param("architecture", "Two-Stage Anomaly Filtering + Persona Clustering")

    # Stage 1: Purge anomalies
    iso_hyb = IsolationForest(
        n_estimators=hybrid_params["iso_n_estimators"],
        contamination=hybrid_params["iso_contamination"],
        random_state=hybrid_params["random_state"]
    )
    inlier_mask = (iso_hyb.fit_predict(X_scaled) == 1)
    X_inliers = X_scaled[inlier_mask]
    n_inliers = len(X_inliers)
    n_outliers = n_total - n_inliers

    # Stage 2: Fit K-Means on clean inliers
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
        "inliers_clustered": n_inliers,
        "outliers_isolated": n_outliers,
        "silhouette_gain_vs_baseline": round(sil_hyb - sil, 4)
    }
    mlflow.log_metrics(metrics_hybrid)

    # Plot Clean Inliers + Marked Red Cross Anomalies
    plt.figure(figsize=(9, 6.5))
    X_inliers_pca = X_pca[inlier_mask]
    X_outliers_pca = X_pca[~inlier_mask]

    scatter = plt.scatter(X_inliers_pca[:, 0], X_inliers_pca[:, 1], c=inlier_labels, cmap="viridis", alpha=0.6, edgecolors="none", s=18, label=f"Clean Persona Cohorts (N={n_inliers})")
    plt.scatter(X_outliers_pca[:, 0], X_outliers_pca[:, 1], color="#E53935", marker="x", s=40, linewidths=1.5, label=f"Isolated Anomalies (N={n_outliers})")
    plt.title(f"PS2_Dataset: Hybrid Isolation + K-Means (Silhouette: {sil:.4f} -> {sil_hyb:.4f})", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Clean Aptitude Persona")
    plt.legend(loc="upper right")
    plt.tight_layout()
    hybrid_plot_path = os.path.join(plots_dir, "ps2_cluster_hybrid_isolation_kmeans.png")
    plt.savefig(hybrid_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(hybrid_plot_path, artifact_path="plots")

    # Comparative Silhouette Chart
    plt.figure(figsize=(7, 4.5))
    models = ["Standard K-Means\n(All 6,901 Rows)", "Hybrid Isolation + K-Means\n(Clean 6,556 Inliers)"]
    scores = [sil, sil_hyb]
    bars = plt.bar(models, scores, color=["#90CAF9", "#1E88E5"], width=0.45)
    plt.ylabel("Silhouette Score")
    plt.title("PS2_Dataset: Silhouette Comparison (6,901 Records)", fontsize=11, fontweight="bold")
    plt.ylim(0, max(scores) * 1.35)
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2., h + 0.002, f"{h:.4f}", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    comp_plot_path = os.path.join(plots_dir, "ps2_cluster_silhouette_comparison.png")
    plt.savefig(comp_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(comp_plot_path, artifact_path="plots")

    mlflow.sklearn.log_model(km_hyb, name="kmeans_model", serialization_format="pickle")
    mlflow.sklearn.log_model(iso_hyb, name="isolation_forest_model", serialization_format="pickle")
    results.append({"Pipeline": "Hybrid: Isolation + K-Means (6,901 rows)", **metrics_hybrid})
    print(f" -> Logged! PS2 Hybrid Silhouette: {sil_hyb:.4f} (Inliers={n_inliers}, Outliers={n_outliers})")

# Summary Table
print("\n" + "=" * 80)
print(" PS2 DATASET (6,901 RECORDS) BENCHMARK SUMMARY")
print("=" * 80)
summary_df = pd.DataFrame(results)
print(summary_df[["Pipeline", "silhouette_score", "davies_bouldin_index", "records_clustered"]].to_string(index=False))
summary_path = os.path.join(data_dir, "ps2_clustering_benchmark_results.csv")
summary_df.to_csv(summary_path, index=False)
print(f"\nSaved metrics to: {summary_path}")
print("ALL RUNS ON 6,901 RECORDS LOGGED TO MLFLOW (Experiment: EduPathAI_PS2_Clustering_Benchmark)!")
