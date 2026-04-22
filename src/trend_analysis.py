"""
src/trend_analysis.py
----------------------
Climate trend analysis:
  - Annual mean temperature linear regression
  - Warming rate (°C/decade), R², p-value
  - Decade-wise comparison
  - 4-panel trend chart
  - Saves results to outputs/trends/
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from scipy import stats
import os

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

def analyze_trends(df):
    print("\n[TREND ANALYSIS] Starting...")
    os.makedirs("outputs/trends", exist_ok=True)

    # Annual mean temperature
    annual = df.groupby("year")["temperature_c"].mean().reset_index()
    annual.columns = ["year", "mean_temp"]

    # Linear regression
    X = annual["year"].values.reshape(-1, 1)
    y = annual["mean_temp"].values
    model = LinearRegression()
    model.fit(X, y)
    slope     = model.coef_[0]
    r2        = model.score(X, y)
    _, pvalue = stats.pearsonr(annual["year"], annual["mean_temp"])
    predicted = model.predict(X)

    results = {
        "warming_rate_per_decade": round(slope * 10, 4),
        "r2_score":                round(r2, 4),
        "p_value":                 round(pvalue, 8),
        "trend_direction":         "WARMING" if slope > 0 else "COOLING",
        "slope_per_year":          round(slope, 5),
        "start_year_temp":         round(predicted[0], 2),
        "end_year_temp":           round(predicted[-1], 2),
        "total_rise_50yr":         round(predicted[-1] - predicted[0], 2),
    }

    print("\n  ╔══════════════════════════════════════════════╗")
    print("  ║      CLIMATE TREND ANALYSIS RESULTS         ║")
    print("  ╠══════════════════════════════════════════════╣")
    print(f"  ║  Warming rate  : {results['warming_rate_per_decade']:+.3f} °C per decade      ║")
    print(f"  ║  R² score      :  {results['r2_score']:.4f}                      ║")
    print(f"  ║  P-value       :  {results['p_value']:.2e}               ║")
    print(f"  ║  Trend         :  {results['trend_direction']:<30}║")
    print(f"  ║  Total rise    : {results['total_rise_50yr']:+.2f} °C over 50 years    ║")
    print(f"  ║  Start temp    :  {results['start_year_temp']:.2f} °C (1975 baseline)    ║")
    print(f"  ║  End temp      :  {results['end_year_temp']:.2f} °C (2024 projected)    ║")
    print("  ╚══════════════════════════════════════════════╝\n")

    # Save results CSV
    pd.DataFrame([results]).to_csv("outputs/trends/trend_results.csv", index=False)

    # --- 4-panel figure ---
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("Climate Trend Analysis — 50 Year Overview (1975–2024)",
                 fontsize=15, fontweight="bold", y=1.01)

    # Panel 1: Annual trend + regression line
    ax = axes[0, 0]
    ax.scatter(annual["year"], annual["mean_temp"],
               color="#1D9E75", s=40, alpha=0.8, zorder=3, label="Annual mean")
    ax.plot(annual["year"], predicted,
            color="#D85A30", linewidth=2.5, zorder=4,
            label=f"Trend: {slope*10:+.3f}°C/decade  R²={r2:.3f}")
    ax.fill_between(annual["year"], annual["mean_temp"], predicted,
                    alpha=0.08, color="#D85A30")
    ax.set_title("Annual Mean Temperature Trend", fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Temperature (°C)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # Panel 2: Monthly boxplot
    ax = axes[0, 1]
    monthly = df.groupby(["year","month"])["temperature_c"].mean().reset_index()
    monthly["month_name"] = monthly["month"].apply(lambda x: MONTH_NAMES[x-1])
    sns.boxplot(data=monthly, x="month_name", y="temperature_c",
                order=MONTH_NAMES, ax=ax, palette="coolwarm", linewidth=0.8)
    ax.set_title("Monthly Temperature Distribution", fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Temperature (°C)")
    ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=0.3)

    # Panel 3: Decade averages
    ax = axes[1, 0]
    decade_avg = df.groupby("decade")["temperature_c"].mean()
    colors_d = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(decade_avg)))
    bars = ax.bar(decade_avg.index.astype(str) + "s", decade_avg.values,
                  color=colors_d, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, decade_avg.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                f"{val:.2f}°C", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_title("Average Temperature by Decade", fontweight="bold")
    ax.set_xlabel("Decade"); ax.set_ylabel("Avg Temperature (°C)")
    ax.set_ylim(decade_avg.min() - 0.8, decade_avg.max() + 0.8)
    ax.grid(axis="y", alpha=0.3)

    # Panel 4: Annual rainfall trend
    ax = axes[1, 1]
    annual_rain = df.groupby("year")["rainfall_mm"].sum()
    col_rain = ["#1D9E75" if v >= annual_rain.mean() else "#E87040" for v in annual_rain.values]
    ax.bar(annual_rain.index, annual_rain.values, color=col_rain, alpha=0.8, edgecolor="white")
    ax.axhline(annual_rain.mean(), color="black", linestyle="--", linewidth=1.2,
               label=f"Mean = {annual_rain.mean():.0f} mm")
    ax.set_title("Annual Total Rainfall", fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Total Rainfall (mm)")
    ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/trends/trend_analysis_4panel.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: outputs/trends/trend_analysis_4panel.png")
    print("[TREND ANALYSIS] Done.\n")
    return results, annual

if __name__ == "__main__":
    df = pd.read_csv("data/processed/climate_featured.csv", parse_dates=["date"])
    analyze_trends(df)
