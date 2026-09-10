import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, accuracy_score

def print_banner(text, char="="):
    print("\n" + char * 80)
    print(f" {text}")
    print(char * 80)

def calculate_psi(baseline, target, num_bins=10):
    """
    Calculates the Population Stability Index (PSI) between baseline and target distributions.
    Thresholds:
      PSI < 0.1: No significant shift (Stable)
      0.1 <= PSI < 0.2: Moderate shift (Monitor)
      PSI >= 0.2: Significant drift (Model retraining recommended)
    """
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)
    
    baseline = baseline[~np.isnan(baseline)]
    target = target[~np.isnan(target)]
    
    if len(baseline) == 0 or len(target) == 0:
        return 0.0
    
    quantiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(baseline, quantiles)
    bin_edges = np.unique(bin_edges)
    
    if len(bin_edges) < 2:
        bin_edges = np.linspace(baseline.min() - 1e-5, baseline.max() + 1e-5, num_bins + 1)
        
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf
    
    base_counts, _ = np.histogram(baseline, bins=bin_edges)
    target_counts, _ = np.histogram(target, bins=bin_edges)
    
    base_pct = (base_counts + 1e-4) / (len(baseline) + 1e-4 * len(base_counts))
    target_pct = (target_counts + 1e-4) / (len(target) + 1e-4 * len(target_counts))
    
    psi_val = np.sum((target_pct - base_pct) * np.log(target_pct / base_pct))
    return float(round(psi_val, 4))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    print_banner("DATA & CONCEPT DRIFT DETECTION MODULE")
    
    # 1. Load baseline historical data
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
    
    baseline_df = pd.merge(students_df, engagement_agg, on="Student_ID")
    print(f"Loaded baseline reference cohort: {len(baseline_df)} student profiles.")
    
    # 2. Simulate Production / Subsequent Semester Batch with Realistic Domain Shifts
    np.random.seed(101)
    target_df = baseline_df.copy()
    
    # Simulate realistic covariate drift in engagement:
    target_df["Avg_Logins"] = np.clip(target_df["Avg_Logins"] * np.random.normal(0.82, 0.12, len(target_df)), 5, 100)
    target_df["Avg_Completion"] = np.clip(target_df["Avg_Completion"] * np.random.normal(0.88, 0.10, len(target_df)), 10, 100)
    target_df["Assessment_Score"] = np.clip(target_df["Assessment_Score"] + np.random.normal(-0.4, 0.3, len(target_df)), 3.0, 10.0)
    
    # Simulate slight prior drift in career interest (surge in AI & Cloud interest)
    shift_indices = np.random.choice(target_df.index, size=int(len(target_df) * 0.15), replace=False)
    for idx in shift_indices:
        target_df.at[idx, "Career_Interest"] = np.random.choice(["AI Engineer", "Cloud DevOps Engineer", "Data Scientist"])
        
    print(f"Constructed target production batch (N={len(target_df)}) for drift monitoring.")
    
    # =========================================================================
    # PART 1: COVARIATE / FEATURE DATA DRIFT (KS-TEST & PSI)
    # =========================================================================
    print_banner("1. COVARIATE / FEATURE DATA DRIFT (KS-TEST & PSI)")
    
    features_to_monitor = [
        "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", 
        "Avg_Submissions", "Assessment_Score", "Completion_Rate"
    ]
    
    drift_results = []
    psi_dict = {}
    ks_dict = {}
    
    for feat in features_to_monitor:
        base_vals = baseline_df[feat].dropna().values
        target_vals = target_df[feat].dropna().values
        
        # Two-Sample Kolmogorov-Smirnov test
        ks_stat, p_val = stats.ks_2samp(base_vals, target_vals)
        ks_drift = p_val < 0.05
        
        # Population Stability Index
        psi = calculate_psi(base_vals, target_vals, num_bins=10)
        
        if psi < 0.1:
            psi_status = "Stable (No Drift)"
        elif psi < 0.2:
            psi_status = "Moderate Shift"
        else:
            psi_status = "Significant Drift (Alert)"
            
        ks_dict[feat] = (ks_stat, p_val)
        psi_dict[feat] = psi
        
        drift_results.append({
            "Feature": feat,
            "KS-Statistic": round(ks_stat, 4),
            "p-value": f"{p_val:.2e}" if p_val < 1e-4 else str(round(p_val, 4)),
            "KS Drift Detected (p<0.05)": "YES" if ks_drift else "No",
            "PSI Score": psi,
            "PSI Stability Status": psi_status
        })
        
    drift_df = pd.DataFrame(drift_results)
    print(drift_df.to_string(index=False))
    
    # =========================================================================
    # PART 2: TARGET / PRIOR LABEL DRIFT (CHI-SQUARE TEST)
    # =========================================================================
    print_banner("2. TARGET / LABEL DISTRIBUTION DRIFT (CHI-SQUARE TEST)")
    
    all_classes = sorted(list(set(baseline_df["Career_Interest"]).union(set(target_df["Career_Interest"]))))
    base_counts = baseline_df["Career_Interest"].value_counts().reindex(all_classes, fill_value=0).values
    target_counts = target_df["Career_Interest"].value_counts().reindex(all_classes, fill_value=0).values
    
    contingency = np.array([base_counts, target_counts])
    chi2_stat, chi2_p, dof, _ = stats.chi2_contingency(contingency)
    target_drift_detected = chi2_p < 0.05
    
    print(f"Chi-Square Statistic : {round(chi2_stat, 4)}")
    print(f"Degrees of Freedom   : {dof}")
    print(f"p-value              : {round(chi2_p, 4)}")
    print(f"Target Drift Detected: {'YES (Distribution Shift Detected)' if target_drift_detected else 'No (Stable)'}")
    
    # =========================================================================
    # PART 3: CONCEPT DRIFT MONITORING (P(Y|X) Model Performance Degradation)
    # =========================================================================
    print_banner("3. CONCEPT DRIFT MONITORING (PERFORMANCE DEGRADATION)")
    
    all_skills = set()
    for col in ["Technical_Skills", "Soft_Skills"]:
        for row in baseline_df[col].dropna():
            for s in row.split(","):
                if s.strip():
                    all_skills.add(s.strip())
    master_skills = sorted(list(all_skills))
    
    def extract_X(df):
        sm = []
        for _, row in df.iterrows():
            comb = str(row["Technical_Skills"]) + ", " + str(row["Soft_Skills"])
            sm.append([1 if sk in comb else 0 for sk in master_skills])
        s_df = pd.DataFrame(sm, columns=[f"Skill_{s}" for s in master_skills])
        c_df = pd.get_dummies(df[["Degree", "Specialisation", "Education_Level"]], drop_first=True)
        n_df = df[["Assessment_Score", "Graduation_Year", "Avg_Logins", "Avg_Completion", "Avg_Assessment_Score", "Avg_Submissions", "Completion_Rate"]]
        return pd.concat([n_df.reset_index(drop=True), c_df.reset_index(drop=True), s_df.reset_index(drop=True)], axis=1)

    X_base = extract_X(baseline_df)
    target_encoder = LabelEncoder()
    y_base = target_encoder.fit_transform(baseline_df["Career_Interest"])
    
    X_tr, X_te, y_tr, y_te = train_test_split(X_base, y_base, test_size=0.20, random_state=42, stratify=y_base)
    
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    rf.fit(X_tr, y_tr)
    
    base_preds = rf.predict(X_te)
    base_acc = accuracy_score(y_te, base_preds) * 100
    base_f1 = f1_score(y_te, base_preds, average='weighted', zero_division=0) * 100
    
    X_targ = extract_X(target_df)
    X_targ = X_targ.reindex(columns=X_base.columns, fill_value=0)
    y_targ = target_encoder.transform(target_df["Career_Interest"])
    
    target_preds = rf.predict(X_targ)
    target_acc = accuracy_score(y_targ, target_preds) * 100
    target_f1 = f1_score(y_targ, target_preds, average='weighted', zero_division=0) * 100
    
    f1_drop = base_f1 - target_f1
    concept_drift_alert = f1_drop > 10.0
    
    concept_eval = pd.DataFrame([
        {
            "Evaluation Scenario": "Baseline Holdout Test Set",
            "Accuracy (%)": round(base_acc, 2),
            "F1-Score (%)": round(base_f1, 2),
            "F1 Delta (%)": 0.0,
            "Concept Drift Alert": "Normal Baseline"
        },
        {
            "Evaluation Scenario": "New Production Batch (Shifted)",
            "Accuracy (%)": round(target_acc, 2),
            "F1-Score (%)": round(target_f1, 2),
            "F1 Delta (%)": round(-f1_drop, 2),
            "Concept Drift Alert": "ALERT: Retrain Model" if concept_drift_alert else "Acceptable Performance"
        }
    ])
    print(concept_eval.to_string(index=False))
    
    # =========================================================================
    # PART 4: VISUAL DRIFT REPORT GENERATION
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    axes[0, 0].hist(baseline_df["Avg_Logins"], bins=15, alpha=0.6, color="#2196F3", label="Baseline Historical", density=True)
    axes[0, 0].hist(target_df["Avg_Logins"], bins=15, alpha=0.6, color="#F44336", label="Target Production Batch", density=True)
    axes[0, 0].set_title(f"Feature Shift: Avg_Logins (KS p-val: {drift_df.loc[drift_df['Feature']=='Avg_Logins', 'p-value'].values[0]})", fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel("Average LMS Logins", fontsize=10)
    axes[0, 0].set_ylabel("Probability Density", fontsize=10)
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle="--", alpha=0.5)
    
    feats = list(psi_dict.keys())
    psi_scores = [psi_dict[f] for f in feats]
    colors = ['#4CAF50' if s < 0.1 else ('#FF9800' if s < 0.2 else '#F44336') for s in psi_scores]
    axes[0, 1].barh(feats, psi_scores, color=colors)
    axes[0, 1].axvline(0.1, color="#FF9800", linestyle="--", lw=1.5, label="Moderate Shift (PSI=0.1)")
    axes[0, 1].axvline(0.2, color="#F44336", linestyle="--", lw=1.5, label="Action Required (PSI=0.2)")
    axes[0, 1].set_title("Population Stability Index (PSI) by Feature", fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel("PSI Score", fontsize=10)
    axes[0, 1].legend(loc="lower right")
    axes[0, 1].grid(True, linestyle="--", alpha=0.5)
    for i, v in enumerate(psi_scores):
        axes[0, 1].text(v + 0.005, i, f"{v}", va='center', fontweight='bold', fontsize=9)
        
    x_cls = np.arange(len(all_classes))
    w = 0.4
    axes[1, 0].bar(x_cls - w/2, base_counts, w, label="Baseline", color="#3F51B5")
    axes[1, 0].bar(x_cls + w/2, target_counts, w, label="Target Production", color="#E91E63")
    axes[1, 0].set_title(f"Career Interest Target Drift (Chi-Square p={round(chi2_p, 4)})", fontsize=12, fontweight='bold')
    axes[1, 0].set_xticks(x_cls)
    axes[1, 0].set_xticklabels(all_classes, rotation=45, ha='right', fontsize=8)
    axes[1, 0].set_ylabel("Student Count", fontsize=10)
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle="--", alpha=0.5)
    
    scenarios = ["Baseline Holdout", "Production Batch"]
    accs = [base_acc, target_acc]
    f1s = [base_f1, target_f1]
    xs = np.arange(len(scenarios))
    axes[1, 1].bar(xs - 0.15, accs, 0.3, label="Accuracy (%)", color="#00BCD4")
    axes[1, 1].bar(xs + 0.15, f1s, 0.3, label="F1-Score (%)", color="#9C27B0")
    axes[1, 1].set_title("Concept Drift: Model Performance Impact", fontsize=12, fontweight='bold')
    axes[1, 1].set_xticks(xs)
    axes[1, 1].set_xticklabels(scenarios, fontsize=10)
    axes[1, 1].set_ylabel("Score (%)", fontsize=10)
    axes[1, 1].set_ylim(0, 110)
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle="--", alpha=0.5)
    for i in xs:
        axes[1, 1].text(i - 0.15, accs[i] + 2, f"{round(accs[i], 1)}%", ha='center', fontweight='bold', fontsize=9)
        axes[1, 1].text(i + 0.15, f1s[i] + 2, f"{round(f1s[i], 1)}%", ha='center', fontweight='bold', fontsize=9)
        
    plt.tight_layout()
    drift_plot_path = os.path.join(plots_dir, "drift_analysis.png")
    plt.savefig(drift_plot_path, dpi=300)
    plt.close()
    print(f"\nSaved Drift Analysis plots to: {drift_plot_path}")
    
    report_csv = os.path.join(data_dir, "drift_monitoring_report.csv")
    with open(report_csv, "w", encoding="utf-8") as f:
        f.write("# DRIFT MONITORING AND VALIDATION REPORT\n\n")
        f.write("## 1. COVARIATE FEATURE DRIFT\n")
        drift_df.to_csv(f, index=False)
        f.write("\n## 2. TARGET LABEL DRIFT\n")
        pd.DataFrame([{
            "Test": "Chi-Square Contingency Test",
            "Chi2-Statistic": round(chi2_stat, 4),
            "p-value": round(chi2_p, 4),
            "Drift Detected": "YES" if target_drift_detected else "No"
        }]).to_csv(f, index=False)
        f.write("\n## 3. CONCEPT DRIFT & PERFORMANCE DEGRADATION\n")
        concept_eval.to_csv(f, index=False)
    print(f"Saved drift monitoring metrics to: {report_csv}")
    print_banner("DRIFT MONITORING SUITE EXECUTION COMPLETED")

if __name__ == "__main__":
    main()
