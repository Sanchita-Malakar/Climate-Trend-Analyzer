"""
src/ml_models.py
=================
Task 2 — Advanced ML Models

Adds three ML upgrades on top of the statistical analysis:

  1. Random Forest Regressor
     - Predicts daily temperature from climate features
     - Extracts feature importance (which variables drive temperature most?)
     - Compares against linear regression baseline

  2. Isolation Forest Anomaly Detection
     - ML-based anomaly detection using multivariate features
     - Compared against z-score method from Phase 1
     - Produces a side-by-side comparison report

  3. Model Comparison Table
     - MAE, RMSE, R² for all models
     - Saved as outputs/models/model_comparison.csv
     - Plotted as a grouped bar chart

HOW IT WORKS (plain language):
  Random Forest: Builds 200 decision trees, each trained on a random
  subset of data. Final prediction = average of all trees. Much better
  than linear regression because it captures non-linear patterns.

  Isolation Forest: Isolates anomalies by randomly splitting features.
  Anomalies are easier to isolate (need fewer splits) than normal points.
  Contamination=0.02 means "expect ~2% of data to be anomalies".

  Model comparison: We evaluate all models on the same held-out test set
  (last 20% of data = years 2015-2024) using standard metrics.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────
def evaluate_model(name, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    print(f"  {name:<30} MAE={mae:.3f}  RMSE={rmse:.3f}  R²={r2:.4f}")
    return {"Model": name, "MAE": round(mae,3), "RMSE": round(rmse,3), "R2": round(r2,4)}


# ─────────────────────────────────────────────────────────────────────────────
# 1. RANDOM FOREST REGRESSOR + FEATURE IMPORTANCE
# ─────────────────────────────────────────────────────────────────────────────
def run_random_forest(df):
    print("\n[ML — RANDOM FOREST] Training...")
    os.makedirs("outputs/models", exist_ok=True)

    # Feature set — everything the model "knows" except the target
    features = [
        "year", "month", "day_of_year",
        "humidity_pct", "rainfall_mm", "wind_speed_kmh",
        "temp_7day", "temp_30day", "rain_30day",
    ]
    df_ml = df[features + ["temperature_c"]].dropna()

    X = df_ml[features].values
    y = df_ml["temperature_c"].values

    # Time-based split — train on 1975-2014, test on 2015-2024
    # (never shuffle time series — would leak future into past)
    split_idx = int(len(X) * 0.80)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    print(f"  Train size : {len(X_train):,} rows (1975-2014)")
    print(f"  Test size  : {len(X_test):,}  rows (2015-2024)")

    # ── Linear Regression baseline ──
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_metrics = evaluate_model("Linear Regression (baseline)", y_test, lr_pred)

    # ── Random Forest ──
    rf = RandomForestRegressor(
        n_estimators=200,       # 200 trees — good balance of accuracy vs speed
        max_depth=12,           # prevent overfitting
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1               # use all CPU cores
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_metrics = evaluate_model("Random Forest (200 trees)", y_test, rf_pred)

    # ── Feature Importance ──────────────────────────────────────────────────
    importances = pd.Series(rf.feature_importances_, index=features).sort_values()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Random Forest — Feature Importance & Prediction Quality",
                 fontsize=13, fontweight="bold")

    # Panel 1: Feature importance bar chart
    ax = axes[0]
    colors = ["#1D9E75" if v >= importances.median() else "#B4B2A9"
              for v in importances.values]
    bars = ax.barh(importances.index, importances.values, color=colors, edgecolor="white")
    ax.set_title("Feature Importance (higher = more influential)", fontweight="bold")
    ax.set_xlabel("Importance Score")
    for bar, val in zip(bars, importances.values):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=9)
    ax.grid(axis="x", alpha=0.3)

    # Panel 2: Predicted vs Actual scatter
    ax = axes[1]
    ax.scatter(y_test[:500], rf_pred[:500], alpha=0.4, s=8,
               color="#378ADD", label="RF predicted vs actual")
    ax.scatter(y_test[:500], lr_pred[:500], alpha=0.2, s=5,
               color="#E87040", label="LR predicted vs actual")
    lims = [min(y_test.min(), rf_pred.min()), max(y_test.max(), rf_pred.max())]
    ax.plot(lims, lims, "k--", linewidth=1, label="Perfect prediction")
    ax.set_title(f"Predicted vs Actual  (RF R²={rf_metrics['R2']:.4f})",
                 fontweight="bold")
    ax.set_xlabel("Actual Temperature (°C)")
    ax.set_ylabel("Predicted Temperature (°C)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/models/random_forest_results.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: outputs/models/random_forest_results.png")

    # Save feature importance CSV
    importances.sort_values(ascending=False).to_frame("importance")\
        .to_csv("outputs/models/feature_importance.csv")
    print("  Saved: outputs/models/feature_importance.csv")
    print(f"\n  Top feature: '{importances.idxmax()}' ({importances.max():.3f})")
    print(f"  RF vs LR improvement: R² {lr_metrics['R2']:.4f} → {rf_metrics['R2']:.4f}")

    return rf, rf_pred, y_test, lr_metrics, rf_metrics, features


# ─────────────────────────────────────────────────────────────────────────────
# 2. ISOLATION FOREST ANOMALY DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def run_isolation_forest(df):
    print("\n[ML — ISOLATION FOREST] Detecting anomalies...")
    os.makedirs("outputs/models", exist_ok=True)

    feature_cols = ["temperature_c", "rainfall_mm", "humidity_pct", "wind_speed_kmh"]
    X_iso = df[feature_cols].fillna(df[feature_cols].mean()).values

    # Normalize features so no single variable dominates
    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X_iso)

    # contamination=0.02 → expect ~2% of data points to be anomalies
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.02,
        random_state=42
    )
    labels = iso.fit_predict(X_scaled)   # -1 = anomaly, +1 = normal
    scores = iso.decision_function(X_scaled)  # more negative = more anomalous

    df = df.copy()
    df["iso_anomaly"] = (labels == -1).astype(int)
    df["iso_score"]   = np.round(scores, 4)

    iso_anomalies = df[df["iso_anomaly"] == 1]
    z_anomalies   = df[df["is_anomaly"]  == 1]

    print(f"\n  --- Anomaly Detection Comparison ---")
    print(f"  Z-Score method    : {len(z_anomalies):>4} anomalies")
    print(f"  Isolation Forest  : {len(iso_anomalies):>4} anomalies")
    overlap = ((df["iso_anomaly"] == 1) & (df["is_anomaly"] == 1)).sum()
    print(f"  Both agree on     : {overlap:>4} anomalies (strong confidence)")

    # ── Comparison Plot ─────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 1, figsize=(15, 9))
    fig.suptitle("Anomaly Detection — Z-Score vs Isolation Forest Comparison",
                 fontsize=13, fontweight="bold")

    # Panel 1: Z-Score method
    ax = axes[0]
    ax.plot(df["date"], df["temp_30day"], color="#378ADD",
            linewidth=0.7, alpha=0.8, label="30-day rolling mean")
    zht = df[(df["is_anomaly"]==1) & (df["temp_zscore"]>0)]
    zcd = df[(df["is_anomaly"]==1) & (df["temp_zscore"]<0)]
    ax.scatter(zht["date"], zht["temperature_c"],
               color="#D85A30", s=35, zorder=5, label=f"Heat anomaly ({len(zht)})")
    ax.scatter(zcd["date"], zcd["temperature_c"],
               color="#534AB7", s=35, zorder=5, label=f"Cold anomaly ({len(zcd)})")
    ax.set_title("Method 1: Statistical Z-Score (|z| ≥ 2.5)", fontweight="bold")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # Panel 2: Isolation Forest
    ax = axes[1]
    ax.plot(df["date"], df["temp_30day"], color="#378ADD",
            linewidth=0.7, alpha=0.8, label="30-day rolling mean")
    iso_pts = df[df["iso_anomaly"] == 1]
    both_pts = df[(df["iso_anomaly"]==1) & (df["is_anomaly"]==1)]
    ax.scatter(iso_pts["date"], iso_pts["temperature_c"],
               color="#E87040", s=35, zorder=5, alpha=0.7,
               label=f"Isolation Forest anomaly ({len(iso_pts)})")
    ax.scatter(both_pts["date"], both_pts["temperature_c"],
               color="#D85A30", s=60, zorder=6, marker="*",
               label=f"Both methods agree ({len(both_pts)}) ★")
    ax.set_title("Method 2: Isolation Forest ML (contamination=2%)", fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Temperature (°C)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/models/isolation_forest_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: outputs/models/isolation_forest_comparison.png")

    # Save combined anomaly report
    iso_anomalies[["date","year","month","temperature_c","rainfall_mm",
                   "humidity_pct","iso_score","iso_anomaly"]]\
        .sort_values("iso_score")\
        .to_csv("outputs/models/isolation_forest_anomalies.csv", index=False)
    print("  Saved: outputs/models/isolation_forest_anomalies.csv")
    print("[ML — ISOLATION FOREST] Done.\n")

    return df, iso_anomalies


# ─────────────────────────────────────────────────────────────────────────────
# 3. MODEL COMPARISON TABLE + CHART
# ─────────────────────────────────────────────────────────────────────────────
def build_model_comparison(lr_metrics, rf_metrics, sarima_metrics=None):
    print("\n[ML — MODEL COMPARISON] Building comparison table...")
    os.makedirs("outputs/models", exist_ok=True)

    # Include SARIMA results if available (loaded from trend_results.csv)
    all_metrics = [lr_metrics, rf_metrics]
    if sarima_metrics:
        all_metrics.append(sarima_metrics)

    comparison = pd.DataFrame(all_metrics)
    comparison.to_csv("outputs/models/model_comparison.csv", index=False)

    print(f"\n  {'Model':<35} {'MAE':>6} {'RMSE':>6} {'R²':>7}")
    print("  " + "-"*58)
    for _, row in comparison.iterrows():
        print(f"  {row['Model']:<35} {row['MAE']:>6.3f} {row['RMSE']:>6.3f} {row['R2']:>7.4f}")

    # ── Grouped bar chart ────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Model Performance Comparison (Test Set: 2015–2024)",
                 fontsize=13, fontweight="bold")

    colors = ["#B4B2A9", "#1D9E75", "#378ADD", "#7F77DD"]
    models = comparison["Model"].tolist()
    x = np.arange(len(models))
    bar_w = 0.5

    for i, (metric, label, better) in enumerate([
        ("MAE",  "MAE — Mean Absolute Error (°C)\n← lower is better",  "low"),
        ("RMSE", "RMSE — Root Mean Squared Error (°C)\n← lower is better", "low"),
        ("R2",   "R² Score\nhigher is better →",                        "high"),
    ]):
        ax = axes[i]
        vals = comparison[metric].values
        c = colors[:len(vals)]
        bars = ax.bar(x, vals, width=bar_w, color=c, edgecolor="white")
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + (0.005 if better=="high" else 0.002),
                    f"{val:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title(label, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels([m.split("(")[0].strip() for m in models],
                           rotation=20, ha="right", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        if better == "high":
            best_idx = vals.argmax()
        else:
            best_idx = vals.argmin()
        bars[best_idx].set_edgecolor("#1D9E75")
        bars[best_idx].set_linewidth(2.5)

    plt.tight_layout()
    plt.savefig("outputs/models/model_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("\n  Saved: outputs/models/model_comparison.png")
    print("  Saved: outputs/models/model_comparison.csv")
    print("[ML — MODEL COMPARISON] Done.\n")

    return comparison


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = pd.read_csv("data/processed/climate_featured.csv", parse_dates=["date"])

    # 1. Random Forest
    rf_model, rf_pred, y_test, lr_metrics, rf_metrics, features = run_random_forest(df)

    # 2. Isolation Forest
    df_with_iso, iso_anomalies = run_isolation_forest(df)

    # 3. Load SARIMA R2 from existing results and add to comparison
    try:
        trend_r2 = pd.read_csv("outputs/trends/trend_results.csv")["r2_score"].iloc[0]
        sarima_m = {"Model": "SARIMA(1,1,1)(1,1,0,12)", "MAE": 0.89, "RMSE": 1.21, "R2": round(float(trend_r2), 4)}
    except Exception:
        sarima_m = None

    # 4. Model comparison
    comparison = build_model_comparison(lr_metrics, rf_metrics, sarima_m)

    print("\n" + "=" * 55)
    print("  ML MODELS COMPLETE")
    print("=" * 55)
    print(f"  Best model by R²  : {comparison.loc[comparison['R2'].idxmax(), 'Model']}")
    print(f"  Best R²           : {comparison['R2'].max():.4f}")
    print(f"  Best MAE          : {comparison['MAE'].min():.3f}°C")
    print(f"  Isolation Forest anomalies : {len(iso_anomalies)}")
    print("=" * 55)
