import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt

# Sklearn imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    silhouette_score, davies_bouldin_score
)
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

def print_banner(text, char="="):
    print("\n" + char * 80)
    print(f" {text}")
    print(char * 80)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    print_banner("PHASE 6: COMPREHENSIVE MODEL DEVELOPMENT & COMPARISON")

    # 1. Load data
    students_df = pd.read_csv(os.path.join(data_dir, "students_employability.csv"))
    engagement_df = pd.read_csv(os.path.join(data_dir, "learning_engagement.csv"))
    print(f"Loaded {len(students_df)} student profiles and {len(engagement_df)} engagement records.")

    # -------------------------------------------------------------------------
    # PART 1: STUDENT SEGMENTATION / CLUSTERING COMPARISON
    # -------------------------------------------------------------------------
    print_banner("PART 1: UNSUPERVISED LEARNING - CLUSTERING COMPARISON")
    
    # Feature engineering for behavioral clustering
    engagement_agg = engagement_df.groupby("Student_ID").agg(
        Avg_Logins=("Login_Count", "mean"),
        Avg_Completion=("Content_Completion_Percentage", "mean"),
        Avg_Assessment_Score=("Assessment_Score", "mean"),
        Avg_Submissions=("Assignment_Submission", "mean"),
        Courses_Enrolled=("Course_ID", "count")
    ).reset_index()

    # Calculate completed course ratio
    completion_rates = []
    for sid in engagement_agg["Student_ID"]:
        sub = engagement_df[engagement_df["Student_ID"] == sid]
        comp_count = sum(sub["Course_Completed"] == "Yes")
        total = len(sub)
        completion_rates.append(comp_count / total if total > 0 else 0)
    engagement_agg["Completion_Rate"] = completion_rates

    cluster_df = pd.merge(students_df[["Student_ID", "Assessment_Score"]], engagement_agg, on="Student_ID")
    cluster_df.rename(columns={"Assessment_Score": "GPA"}, inplace=True)
    cluster_features = ["GPA", "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", "Avg_Submissions", "Completion_Rate"]

    scaler = StandardScaler()
    X_cluster = scaler.fit_transform(cluster_df[cluster_features])

    # A. Elbow Method & Silhouette for K-Means (K=2 to 6)
    k_range = range(2, 7)
    inertias = []
    kmeans_silhouettes = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_cluster)
        inertias.append(km.inertia_)
        kmeans_silhouettes.append(silhouette_score(X_cluster, km.labels_))

    # B. Fit K-Means with K=3 (Optimal Persona Breakdown)
    kmeans_optimal = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans_labels = kmeans_optimal.fit_predict(X_cluster)
    km_sil = silhouette_score(X_cluster, kmeans_labels)
    km_db = davies_bouldin_score(X_cluster, kmeans_labels)

    # C. Fit Agglomerative Hierarchical Clustering with K=3
    agg_clustering = AgglomerativeClustering(n_clusters=3, linkage='ward')
    agg_labels = agg_clustering.fit_predict(X_cluster)
    agg_sil = silhouette_score(X_cluster, agg_labels)
    agg_db = davies_bouldin_score(X_cluster, agg_labels)

    # Clustering comparison table
    clustering_results = pd.DataFrame([
        {
            "Clustering Model": "K-Means Clustering",
            "Clusters (K)": 3,
            "Silhouette Score (Higher=Better)": round(km_sil, 4),
            "Davies-Bouldin Index (Lower=Better)": round(km_db, 4),
            "Characteristics": "Partitioning around centroids; fast, scalable, spherical clusters"
        },
        {
            "Clustering Model": "Hierarchical Clustering (Ward)",
            "Clusters (K)": 3,
            "Silhouette Score (Higher=Better)": round(agg_sil, 4),
            "Davies-Bouldin Index (Lower=Better)": round(agg_db, 4),
            "Characteristics": "Tree-based agglomerative hierarchy; minimizes variance within clusters"
        }
    ])
    print(clustering_results.to_string(index=False))

    # Plot Clustering Analysis
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    # 1. Elbow curve
    axes[0].plot(list(k_range), inertias, marker='o', color='#1976D2', linewidth=2.5)
    axes[0].set_title("Elbow Method for Optimal K", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Number of Clusters (K)", fontsize=11)
    axes[0].set_ylabel("Inertia (Within-Cluster Sum of Squares)", fontsize=11)
    axes[0].grid(True, linestyle="--", alpha=0.6)

    # 2. PCA 2D Cluster Visualization
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_cluster)
    scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=kmeans_labels, cmap='viridis', s=45, alpha=0.8, edgecolors='k', linewidth=0.5)
    axes[1].set_title("K-Means Student Personas (PCA Projection)", fontsize=13, fontweight='bold')
    axes[1].set_xlabel(f"PC1 ({round(pca.explained_variance_ratio_[0]*100, 1)}% variance)", fontsize=11)
    axes[1].set_ylabel(f"PC2 ({round(pca.explained_variance_ratio_[1]*100, 1)}% variance)", fontsize=11)
    axes[1].grid(True, linestyle="--", alpha=0.6)
    cbar = plt.colorbar(scatter, ax=axes[1])
    cbar.set_label("Cluster ID")

    plt.tight_layout()
    clustering_plot_path = os.path.join(plots_dir, "clustering_evaluation.png")
    plt.savefig(clustering_plot_path, dpi=300)
    plt.close()
    print(f"\nSaved clustering visual plot to: {clustering_plot_path}")

    # -------------------------------------------------------------------------
    # PART 2: SUPERVISED LEARNING - CAREER PATHWAY CLASSIFICATION
    # -------------------------------------------------------------------------
    print_banner("PART 2: SUPERVISED LEARNING - MULTI-MODEL CLASSIFICATION")
    print("Task: Predict student's Career Pathway from academic profile & skills.")

    # Prepare feature matrix for classification
    # Merge engagement metrics with student profile
    full_df = pd.merge(students_df, engagement_agg, on="Student_ID")

    # Skill one-hot encoding
    all_skills = set()
    for col in ["Technical_Skills", "Soft_Skills"]:
        for row in full_df[col].dropna():
            for s in row.split(","):
                if s.strip():
                    all_skills.add(s.strip())
    master_skills = sorted(list(all_skills))

    skill_matrix = []
    for _, row in full_df.iterrows():
        combined = str(row["Technical_Skills"]) + ", " + str(row["Soft_Skills"])
        skill_matrix.append([1 if sk in combined else 0 for sk in master_skills])
    skill_df = pd.DataFrame(skill_matrix, columns=[f"Skill_{s}" for s in master_skills])

    # Encode Categoricals: Degree, Specialisation, Education_Level
    cat_df = pd.get_dummies(full_df[["Degree", "Specialisation", "Education_Level"]], drop_first=True)

    # Numerical features
    num_df = full_df[["Assessment_Score", "Graduation_Year", "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", "Avg_Submissions", "Completion_Rate"]]
    
    # Target variable: Career_Interest
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(full_df["Career_Interest"])
    target_classes = target_encoder.classes_
    print(f"Target Career Classes ({len(target_classes)}): {list(target_classes)}")

    # Combine into single feature matrix X
    X = pd.concat([num_df.reset_index(drop=True), cat_df.reset_index(drop=True), skill_df.reset_index(drop=True)], axis=1)

    # Train-test split (80% train, 20% test, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Scale numerical columns for Logistic Regression
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    scaler_cls = StandardScaler()
    num_cols = num_df.columns.tolist()
    X_train_scaled[num_cols] = scaler_cls.fit_transform(X_train[num_cols])
    X_test_scaled[num_cols] = scaler_cls.transform(X_test[num_cols])

    # Define the 4 models to compare
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, eval_metric='mlogloss', random_state=42)
    }

    results = []
    print("\nTraining and evaluating models across test set (96 samples)...")

    for name, model in models.items():
        # Fit model (use scaled features for Logistic Regression, raw/tree features for tree ensembles)
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, average='weighted', zero_division=0)
        rec = recall_score(y_test, preds, average='weighted', zero_division=0)
        f1 = f1_score(y_test, preds, average='weighted', zero_division=0)

        results.append({
            "Model": name,
            "Accuracy": round(acc * 100, 2),
            "Precision": round(prec * 100, 2),
            "Recall": round(rec * 100, 2),
            "F1-Score": round(f1 * 100, 2)
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="F1-Score", ascending=False)
    print("\n" + results_df.to_string(index=False))

    # Save metrics to CSV
    metrics_csv_path = os.path.join(data_dir, "model_comparison_metrics.csv")
    results_df.to_csv(metrics_csv_path, index=False)
    print(f"\nSaved metrics table to: {metrics_csv_path}")

    # Top Feature Importances from Random Forest
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    top_indices = np.argsort(importances)[::-1][:8]
    top_features = X.columns[top_indices]
    top_scores = importances[top_indices]

    # Plot Model Performance Comparison & Feature Importance
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart of Model Accuracies and F1-Scores
    x = np.arange(len(results_df))
    width = 0.35
    axes[0].bar(x - width/2, results_df["Accuracy"], width, label='Accuracy (%)', color='#2196F3')
    axes[0].bar(x + width/2, results_df["F1-Score"], width, label='F1-Score (%)', color='#4CAF50')
    axes[0].set_ylabel('Percentage (%)', fontsize=12)
    axes[0].set_title('Supervised Model Comparison (Career Pathway Classification)', fontsize=13, fontweight='bold')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(results_df["Model"], fontsize=11)
    axes[0].set_ylim(0, 110)
    axes[0].grid(axis='y', linestyle='--', alpha=0.6)
    axes[0].legend(fontsize=11)

    # Add text labels on bars
    for i in x:
        axes[0].text(i - width/2, results_df["Accuracy"].iloc[i] + 1.5, f"{results_df['Accuracy'].iloc[i]}%", ha='center', fontsize=10, fontweight='bold')
        axes[0].text(i + width/2, results_df["F1-Score"].iloc[i] + 1.5, f"{results_df['F1-Score'].iloc[i]}%", ha='center', fontsize=10, fontweight='bold')

    # Top Feature Importance plot
    axes[1].barh(range(len(top_features)), top_scores[::-1], color='#FF9800', align='center')
    axes[1].set_yticks(range(len(top_features)))
    axes[1].set_yticklabels(top_features[::-1], fontsize=11)
    axes[1].set_xlabel('Relative Feature Importance (MDI)', fontsize=12)
    axes[1].set_title('Top 8 Predictive Features (Random Forest)', fontsize=13, fontweight='bold')
    axes[1].grid(axis='x', linestyle='--', alpha=0.6)

    plt.tight_layout()
    comparison_plot_path = os.path.join(plots_dir, "classification_model_comparison.png")
    plt.savefig(comparison_plot_path, dpi=300)
    plt.close()
    print(f"Saved classification comparison visual plot to: {comparison_plot_path}")

    print_banner("PHASE 6 EXECUTION COMPLETE: MULTIPLE APPROACHES EVALUATED")

if __name__ == "__main__":
    main()
