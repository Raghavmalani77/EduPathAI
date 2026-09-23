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
experiment_name = "EduPathAI_Clustering_Anomaly_Benchmark"
mlflow.set_experiment(experiment_name)

print("=" * 80)
print(" BENCHMARK: K-MEANS vs ISOLATION FOREST vs HYBRID (ISOLATION + K-MEANS)")
print("=" * 80)

# 2. Ingest and Engineer Student Behavioral Features
students_df = pd.read_csv(os.path.join(data_dir, "students_employability.csv"))
engagement_df = pd.read_csv(os.path.join(data_dir, "learning_engagement.csv"))

engagement_agg = engagement_df.groupby("Student_ID").agg(
    Avg_Logins=("Login_Count", "mean"),
    Avg_Completion=("Content_Completion_Percentage", "mean"),
    Avg_Assessment_Score=("Assessment_Score", "mean"),
    Avg_Submissions=("Assignment_Submission", "mean"),
    Courses_Enrolled=("Course_ID", "count")
).reset_index()

completion_rates = []
for sid in engagement_agg["Student_ID"]:
    sub = engagement_df[engagement_df["Student_ID"] == sid]
    comp_count = sum(sub["Course_Completed"] == "Yes")
    total = len(sub)
    completion_rates.append(comp_count / total if total > 0 else 0)
engagement_agg["Completion_Rate"] = completion_rates

cluster_df = pd.merge(students_df[["Student_ID", "Assessment_Score"]], engagement_agg, on="Student_ID")
cluster_df.rename(columns={"Assessment_Score": "GPA"}, inplace=True)
features = ["GPA", "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", "Avg_Submissions", "Completion_Rate"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(cluster_df[features])
n_samples = len(cluster_df)
print(f"Loaded {n_samples} student profiles with {len(features)} scaled features.")

results = []

# ==============================================================================
# RUN 1: BASELINE K-MEANS (K=3 on Raw Data with Outliers Included)
# ==============================================================================
print("\n[1/3] Running Run 1: Standard K-Means (Baseline)...")
kmeans_params = {
    "n_clusters": 3,
    "init": "k-means++",
    "n_init": 10,
    "random_state": 42
}

with mlflow.start_run(run_name="1_Standard_KMeans_Baseline"):
    mlflow.log_params(kmeans_params)
    mlflow.log_param("architecture", "Single-Stage Clustering")
    mlflow.log_param("outlier_filtering", "None")
    mlflow.log_param("dataset_samples", n_samples)

    km = KMeans(**kmeans_params)
    km_labels = km.fit_predict(X_scaled)

    km_sil = float(silhouette_score(X_scaled, km_labels))
    km_db = float(davies_bouldin_score(X_scaled, km_labels))
    km_ch = float(calinski_harabasz_score(X_scaled, km_labels))

    metrics_km = {
        "silhouette_score": round(km_sil, 4),
        "davies_bouldin_index": round(km_db, 4),
        "calinski_harabasz_score": round(km_ch, 2),
        "active_clusters": 3
    }
    mlflow.log_metrics(metrics_km)

    # 2D PCA Visualization
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    plt.figure(figsize=(7, 5))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=km_labels, cmap="viridis", alpha=0.8, edgecolors="k", s=40)
    plt.title(f"Standard K-Means (Silhouette: {km_sil:.4f})", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Cluster Persona")
    plt.tight_layout()
    km_plot_path = os.path.join(plots_dir, "cluster_standard_kmeans.png")
    plt.savefig(km_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(km_plot_path, artifact_path="plots")

    mlflow.sklearn.log_model(km, name="model", serialization_format="pickle")
    results.append({"Pipeline": "Standard K-Means", **metrics_km})
    print(f" -> Logged! Silhouette Score: {km_sil:.4f}, Davies-Bouldin: {km_db:.4f}")

# ==============================================================================
# RUN 2: ISOLATION FOREST ONLY (Unsupervised Anomaly Detection)
# ==============================================================================
print("\n[2/3] Running Run 2: Isolation Forest Only (Anomaly Detection)...")
iso_params = {
    "n_estimators": 100,
    "contamination": 0.06,  # ~6% anomaly expectation
    "random_state": 42
}

with mlflow.start_run(run_name="2_Isolation_Forest_Only"):
    mlflow.log_params(iso_params)
    mlflow.log_param("architecture", "Pure Anomaly Detection")
    mlflow.log_param("dataset_samples", n_samples)

    iso = IsolationForest(**iso_params)
    iso_preds = iso.fit_predict(X_scaled)  # 1 for inliers, -1 for outliers
    anomaly_scores = iso.decision_function(X_scaled)

    is_outlier = (iso_preds == -1)
    outlier_count = int(np.sum(is_outlier))
    outlier_pct = float(outlier_count / n_samples * 100)

    iso_sil = float(silhouette_score(X_scaled, iso_preds))
    iso_db = float(davies_bouldin_score(X_scaled, iso_preds))

    metrics_iso = {
        "silhouette_score": round(iso_sil, 4),
        "davies_bouldin_index": round(iso_db, 4),
        "outlier_count": outlier_count,
        "outlier_percentage": round(outlier_pct, 2),
        "mean_anomaly_score": round(float(np.mean(anomaly_scores)), 4)
    }
    mlflow.log_metrics(metrics_iso)

    # Visualization
    plt.figure(figsize=(7, 5))
    colors = ["#E53935" if p == -1 else "#1E88E5" for p in iso_preds]
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=colors, alpha=0.8, edgecolors="k", s=40)
    plt.title(f"Isolation Forest (Detected {outlier_count} Anomalies / {outlier_pct:.1f}%)", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.tight_layout()
    iso_plot_path = os.path.join(plots_dir, "cluster_isolation_forest.png")
    plt.savefig(iso_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(iso_plot_path, artifact_path="plots")

    mlflow.sklearn.log_model(iso, name="model", serialization_format="pickle")
    results.append({"Pipeline": "Isolation Forest Only", **metrics_iso})
    print(f" -> Logged! Outliers Detected: {outlier_count} ({outlier_pct:.1f}%), Inlier/Outlier Silhouette: {iso_sil:.4f}")

# ==============================================================================
# RUN 3: HYBRID ISOLATION FOREST + K-MEANS (Two-Stage Robust Pipeline)
# ==============================================================================
print("\n[3/3] Running Run 3: Hybrid (Isolation Forest -> K-Means)...")
hybrid_params = {
    "iso_n_estimators": 100,
    "iso_contamination": 0.06,
    "kmeans_clusters": 3,
    "random_state": 42
}

with mlflow.start_run(run_name="3_Hybrid_IsolationForest_KMeans"):
    mlflow.log_params(hybrid_params)
    mlflow.log_param("architecture", "Two-Stage Filter & Cluster")
    mlflow.log_param("stage_1", "Isolation Forest Outlier Purge")
    mlflow.log_param("stage_2", "K-Means on Filtered Inliers")

    # Stage 1: Detect and isolate anomalies
    iso_hybrid = IsolationForest(
        n_estimators=hybrid_params["iso_n_estimators"],
        contamination=hybrid_params["iso_contamination"],
        random_state=hybrid_params["random_state"]
    )
    inlier_mask = (iso_hybrid.fit_predict(X_scaled) == 1)
    X_inliers = X_scaled[inlier_mask]
    n_inliers = len(X_inliers)
    n_outliers = n_samples - n_inliers

    # Stage 2: Fit K-Means strictly on inliers (unpolluted centroids)
    km_hybrid = KMeans(
        n_clusters=hybrid_params["kmeans_clusters"],
        init="k-means++",
        n_init=10,
        random_state=hybrid_params["random_state"]
    )
    inlier_labels = km_hybrid.fit_predict(X_inliers)

    # Evaluate on the clean cohort
    hybrid_sil = float(silhouette_score(X_inliers, inlier_labels))
    hybrid_db = float(davies_bouldin_score(X_inliers, inlier_labels))
    hybrid_ch = float(calinski_harabasz_score(X_inliers, inlier_labels))

    metrics_hybrid = {
        "silhouette_score": round(hybrid_sil, 4),
        "davies_bouldin_index": round(hybrid_db, 4),
        "calinski_harabasz_score": round(hybrid_ch, 2),
        "inliers_clustered": n_inliers,
        "outliers_isolated": n_outliers,
        "silhouette_gain_vs_baseline": round(hybrid_sil - km_sil, 4)
    }
    mlflow.log_metrics(metrics_hybrid)

    # Visualization: Plot clean clusters + mark isolated anomalies in red
    plt.figure(figsize=(8, 5.5))
    X_inliers_pca = X_pca[inlier_mask]
    X_outliers_pca = X_pca[~inlier_mask]

    scatter = plt.scatter(X_inliers_pca[:, 0], X_inliers_pca[:, 1], c=inlier_labels, cmap="viridis", alpha=0.85, edgecolors="k", s=45, label="Clean Clusters")
    plt.scatter(X_outliers_pca[:, 0], X_outliers_pca[:, 1], color="#E53935", marker="x", s=80, linewidths=2, label="Isolated Anomalies (Stage 1)")
    plt.title(f"Hybrid Isolation + K-Means (Silhouette Boost: {km_sil:.4f} -> {hybrid_sil:.4f})", fontsize=11, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Clean Persona Cluster")
    plt.legend(loc="upper right")
    plt.tight_layout()
    hybrid_plot_path = os.path.join(plots_dir, "cluster_hybrid_isolation_kmeans.png")
    plt.savefig(hybrid_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(hybrid_plot_path, artifact_path="plots")

    # Comparative Silhouette Bar Chart
    plt.figure(figsize=(7, 4))
    comparison_models = ["Standard K-Means\n(With Outliers)", "Hybrid: Isolation + K-Means\n(Clean Inliers)"]
    comparison_scores = [km_sil, hybrid_sil]
    bars = plt.bar(comparison_models, comparison_scores, color=["#90CAF9", "#1E88E5"], width=0.45)
    plt.ylabel("Silhouette Score (Higher = More Distinct Clusters)")
    plt.title("Silhouette Score Impact: Standard vs Hybrid Isolation + K-Means", fontsize=11, fontweight="bold")
    plt.ylim(0, max(comparison_scores) * 1.25)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 0.015, f"{h:.4f}", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    comp_plot_path = os.path.join(plots_dir, "cluster_silhouette_comparison.png")
    plt.savefig(comp_plot_path, dpi=200)
    plt.close()
    mlflow.log_artifact(comp_plot_path, artifact_path="plots")

    mlflow.sklearn.log_model(km_hybrid, name="kmeans_model", serialization_format="pickle")
    mlflow.sklearn.log_model(iso_hybrid, name="isolation_forest_model", serialization_format="pickle")
    results.append({"Pipeline": "Hybrid: Isolation + K-Means", **metrics_hybrid})
    print(f" -> Logged! Clean Silhouette Score: {hybrid_sil:.4f} (+{hybrid_sil - km_sil:.4f} gain!)")

# 4. Summary Table
print("\n" + "=" * 80)
print("FINAL BENCHMARK COMPARISON TABLE")
print("=" * 80)
summary_df = pd.DataFrame(results)
print(summary_df[["Pipeline", "silhouette_score", "davies_bouldin_index"]].to_string(index=False))
summary_path = os.path.join(data_dir, "clustering_anomaly_benchmark_results.csv")
summary_df.to_csv(summary_path, index=False)
print(f"\nSaved benchmark metrics to: {summary_path}")
print("ALL RUNS SUCCESSFULLY LOGGED TO MLFLOW (Experiment: EduPathAI_Clustering_Anomaly_Benchmark)!")
