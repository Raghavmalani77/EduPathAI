import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import mlflow
import mlflow.sklearn
import mlflow.xgboost

os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"

proj_dir = r"C:\Users\admin\.gemini\antigravity\scratch\major-project"
data_dir = os.path.join(proj_dir, "data")
plots_dir = os.path.join(proj_dir, "plots")
os.makedirs(plots_dir, exist_ok=True)

# Set MLflow tracking
experiment_name = "EduPathAI_PS2_Benchmark"
mlflow.set_experiment(experiment_name)

# Load processed data
data_path = os.path.join(data_dir, "processed_ps2_dataset.csv")
meta_path = os.path.join(data_dir, "ps2_metadata.json")

df = pd.read_csv(data_path)
with open(meta_path, "r", encoding="utf-8") as f:
    meta = json.load(f)

target_col = "target_role_encoded"
drop_cols = ["target_role_encoded", "suggested_job_role"]
feature_cols = [c for c in df.columns if c not in drop_cols]

X = df[feature_cols]
y = df[target_col]
classes = meta["target_classes"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

results_summary = []

# RUN 1: Random Forest
rf_params = {
    "n_estimators": 100,
    "max_depth": 12,
    "random_state": 42
}

with mlflow.start_run(run_name="RandomForest_PS2_12Classes") as run:
    mlflow.log_params(rf_params)
    mlflow.log_param("dataset", "PS2_Dataset")
    mlflow.log_param("train_samples", len(X_train))
    mlflow.log_param("test_samples", len(X_test))

    rf = RandomForestClassifier(**rf_params)
    rf.fit(X_train, y_train)

    y_pred_rf = rf.predict(X_test)
    metrics_rf = {
        "test_accuracy": round(float(accuracy_score(y_test, y_pred_rf)), 4),
        "precision_weighted": round(float(precision_score(y_test, y_pred_rf, average="weighted", zero_division=0)), 4),
        "recall_weighted": round(float(recall_score(y_test, y_pred_rf, average="weighted", zero_division=0)), 4),
        "f1_score_weighted": round(float(f1_score(y_test, y_pred_rf, average="weighted", zero_division=0)), 4)
    }
    mlflow.log_metrics(metrics_rf)

    # Plot Confusion Matrix
    cm_rf = confusion_matrix(y_test, y_pred_rf)
    plt.figure(figsize=(9, 7))
    sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Blues",
                xticklabels=[c[:14] for c in classes],
                yticklabels=[c[:14] for c in classes])
    plt.title(f"Random Forest - PS2 Benchmark (Test Acc: {metrics_rf['test_accuracy']*100:.2f}%)")
    plt.xlabel("Predicted Role")
    plt.ylabel("Actual Role")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    cm_rf_path = os.path.join(plots_dir, "ps2_rf_confusion_matrix.png")
    plt.savefig(cm_rf_path, dpi=200)
    plt.close()
    mlflow.log_artifact(cm_rf_path, artifact_path="plots")

    # Plot Feature Importances
    feat_imp = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)[:15]
    plt.figure(figsize=(10, 5))
    feat_imp.plot(kind="barh", color="#1E88E5").invert_yaxis()
    plt.title("Top 15 Feature Importances (Random Forest on PS2)")
    plt.xlabel("Gini Feature Importance")
    plt.tight_layout()
    imp_path = os.path.join(plots_dir, "ps2_feature_importance.png")
    plt.savefig(imp_path, dpi=200)
    plt.close()
    mlflow.log_artifact(imp_path, artifact_path="plots")

    # Log model with pickle format
    mlflow.sklearn.log_model(rf, name="model", serialization_format="pickle")
    results_summary.append({"Model": "Random Forest", **metrics_rf})
    print("[MLflow] Run 1 (Random Forest) logged successfully!")

# RUN 2: XGBoost
xgb_params = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "random_state": 42,
    "eval_metric": "mlogloss"
}

with mlflow.start_run(run_name="XGBoost_PS2_12Classes") as run:
    mlflow.log_params(xgb_params)
    mlflow.log_param("dataset", "PS2_Dataset")

    xgb = XGBClassifier(**xgb_params)
    xgb.fit(X_train, y_train)

    y_pred_xgb = xgb.predict(X_test)
    metrics_xgb = {
        "test_accuracy": round(float(accuracy_score(y_test, y_pred_xgb)), 4),
        "precision_weighted": round(float(precision_score(y_test, y_pred_xgb, average="weighted", zero_division=0)), 4),
        "recall_weighted": round(float(recall_score(y_test, y_pred_xgb, average="weighted", zero_division=0)), 4),
        "f1_score_weighted": round(float(f1_score(y_test, y_pred_xgb, average="weighted", zero_division=0)), 4)
    }
    mlflow.log_metrics(metrics_xgb)
    mlflow.xgboost.log_model(xgb, name="model")
    results_summary.append({"Model": "XGBoost", **metrics_xgb})
    print("[MLflow] Run 2 (XGBoost) logged successfully!")

# Save results
res_df = pd.DataFrame(results_summary)
res_path = os.path.join(data_dir, "ps2_model_benchmark_results.csv")
res_df.to_csv(res_path, index=False)
print("\n[BENCHMARK RESULTS]")
print(res_df.to_string(index=False))
print(f"Results saved to: {res_path}")
