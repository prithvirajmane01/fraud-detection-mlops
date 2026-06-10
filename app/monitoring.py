import pandas as pd
import numpy as np
from scipy import stats
import os
import json
from datetime import datetime


def generate_baseline_data(n=1000):
    np.random.seed(42)
    return pd.DataFrame({
        "transaction_amount": np.random.exponential(scale=100, size=n),
        "transaction_hour": np.random.randint(0, 24, size=n),
        "days_since_last_transaction": np.random.randint(0, 30, size=n),
        "customer_age": np.random.randint(18, 80, size=n),
        "is_foreign_transaction": np.random.randint(0, 2, size=n),
        "num_transactions_today": np.random.randint(1, 20, size=n),
    })


def generate_current_data_normal(n=500):
    np.random.seed(99)
    return pd.DataFrame({
        "transaction_amount": np.random.exponential(scale=105, size=n),
        "transaction_hour": np.random.randint(0, 24, size=n),
        "days_since_last_transaction": np.random.randint(0, 30, size=n),
        "customer_age": np.random.randint(18, 80, size=n),
        "is_foreign_transaction": np.random.randint(0, 2, size=n),
        "num_transactions_today": np.random.randint(1, 20, size=n),
    })


def generate_current_data_drifted(n=500):
    np.random.seed(77)
    return pd.DataFrame({
        "transaction_amount": np.random.exponential(scale=400, size=n),
        "transaction_hour": np.random.randint(0, 24, size=n),
        "days_since_last_transaction": np.random.randint(0, 10, size=n),
        "customer_age": np.random.randint(18, 80, size=n),
        "is_foreign_transaction": np.random.randint(0, 2, size=n),
        "num_transactions_today": np.random.randint(10, 50, size=n),
    })


def detect_drift(baseline, current, threshold=0.05):
    print("\n" + "="*55)
    print(f"{'FEATURE':<35} {'P-VALUE':>8}  {'STATUS':>10}")
    print("="*55)

    drift_results = {}
    drifted_features = []

    for column in baseline.columns:
        ks_stat, p_value = stats.ks_2samp(
            baseline[column].values,
            current[column].values
        )
        drifted = p_value < threshold
        status = "DRIFT" if drifted else "STABLE"
        print(f"{column:<35} {p_value:>8.4f}  {status:>10}")

        drift_results[column] = {
            "ks_statistic": round(float(ks_stat), 4),
            "p_value": round(float(p_value), 4),
            "drift_detected": drifted
        }

        if drifted:
            drifted_features.append(column)

    print("="*55)
    dataset_drift = len(drifted_features) > 0

    if dataset_drift:
        print(f"\nDATA DRIFT DETECTED in: {', '.join(drifted_features)}")
        print("Model may be giving inaccurate predictions.")
        print("Recommended action: retrain the model.")
    else:
        print("\nNO DRIFT DETECTED - Data patterns are stable.")
        print("Model predictions remain reliable.")

    print()
    return drift_results, dataset_drift


def save_report(results, dataset_drift, report_name):
    os.makedirs("monitoring_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"monitoring_reports/{report_name}_{timestamp}.json"

    report = {
        "timestamp": timestamp,
        "dataset_drift_detected": dataset_drift,
        "feature_results": results
    }

    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"Report saved to: {path}")
    return path


baseline = generate_baseline_data()

print("\n" + "-"*55)
print("SCENARIO 1: Normal traffic (no drift expected)")
print("-"*55)
normal = generate_current_data_normal()
results1, drift1 = detect_drift(baseline, normal)
save_report(results1, drift1, "scenario_normal")

print("\n" + "-"*55)
print("SCENARIO 2: Holiday season shift (drift expected)")
print("-"*55)
drifted = generate_current_data_drifted()
results2, drift2 = detect_drift(baseline, drifted)
save_report(results2, drift2, "scenario_drifted")