"""
src/eda.py
----------
Exploratory Data Analysis:
  - Summary statistics
  - Monthly temperature boxplot
  - Annual rainfall bar chart
  - Correlation heatmap
  - Seasonal distribution
  - Decade-wise temperature comparison
  - Humidity vs Temperature scatter
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

def run_eda(df):
    print("\n[EDA] Starting exploratory data analysis...")
    os.makedirs("outputs/eda", exist_ok=True)

    # --- 1. Summary Statistics ---
    print("\n  --- Summary Statistics ---")
    summary = df[["temperature_c","rainfall_mm","humidity_pct","wind_speed_kmh"]].describe().round(2)
    print(summary.to_string())
    summary.to_csv("outputs/eda/summary_statistics.csv")

    # --- 2. Monthly Temperature Boxplot ---
    fig, ax = plt.subplots(figsize=(14, 5))
    monthly = df.groupby(["year","month"])["temperature_c"].mean().reset_index()
    monthly["month_name"] = monthly["month"].apply(lambda x: MONTH_NAMES[x-1])
    sns.boxplot(data=monthly, x="month_name", y="temperature_c",
                order=MONTH_NAMES, ax=ax, palette="coolwarm")
    ax.set_title("Monthly Temperature Distribution (1975–2024)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Temperature (°C)")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/eda/01_monthly_temp_boxplot.png", dpi=150)
    plt.close()
    print("  Saved: outputs/eda/01_monthly_temp_boxplot.png")

    # --- 3. Annual Rainfall Bar Chart ---
    fig, ax = plt.subplots(figsize=(14, 5))
    annual_rain = df.groupby("year")["rainfall_mm"].sum()
    colors = ["#1D9E75" if v >= annual_rain.mean() else "#E87040" for v in annual_rain.values]
    ax.bar(annual_rain.index, annual_rain.values, color=colors, alpha=0.85)
    ax.axhline(annual_rain.mean(), color="black", linestyle="--", linewidth=1.2,
               label=f"Mean = {annual_rain.mean():.0f} mm")
    ax.set_title("Annual Total Rainfall (1975–2024)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Total Rainfall (mm)")
    ax.legend(); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/eda/02_annual_rainfall.png", dpi=150)
    plt.close()
    print("  Saved: outputs/eda/02_annual_rainfall.png")

    # --- 4. Correlation Heatmap ---
    fig, ax = plt.subplots(figsize=(7, 5))
    corr = df[["temperature_c","rainfall_mm","humidity_pct","wind_speed_kmh"]].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                ax=ax, linewidths=0.5, square=True)
    ax.set_title("Variable Correlation Heatmap", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("outputs/eda/03_correlation_heatmap.png", dpi=150)
    plt.close()
    print("  Saved: outputs/eda/03_correlation_heatmap.png")

    # --- 5. Seasonal Temperature Distribution ---
    fig, ax = plt.subplots(figsize=(10, 5))
    season_order = ["Winter","Spring","Summer","Autumn"]
    palette = {"Winter":"#5B8DB8","Spring":"#76B041","Summer":"#E87040","Autumn":"#D4A017"}
    sns.violinplot(data=df, x="season", y="temperature_c",
                   order=season_order, palette=palette, ax=ax)
    ax.set_title("Seasonal Temperature Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel("Season"); ax.set_ylabel("Temperature (°C)")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/eda/04_seasonal_distribution.png", dpi=150)
    plt.close()
    print("  Saved: outputs/eda/04_seasonal_distribution.png")

    # --- 6. Decadal Average Temperature ---
    fig, ax = plt.subplots(figsize=(10, 5))
    decade_avg = df.groupby("decade")["temperature_c"].mean()
    bars = ax.bar(decade_avg.index.astype(str) + "s", decade_avg.values,
                  color="#378ADD", alpha=0.85, edgecolor="white")
    for bar, val in zip(bars, decade_avg.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{val:.2f}°C", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Average Temperature by Decade", fontsize=13, fontweight="bold")
    ax.set_xlabel("Decade"); ax.set_ylabel("Avg Temperature (°C)")
    ax.set_ylim(decade_avg.min() - 1, decade_avg.max() + 1)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/eda/05_decadal_temperature.png", dpi=150)
    plt.close()
    print("  Saved: outputs/eda/05_decadal_temperature.png")

    # --- 7. Humidity vs Temperature Scatter ---
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = df.sample(2000, random_state=42)
    scatter = ax.scatter(sample["temperature_c"], sample["humidity_pct"],
                         c=sample["year"], cmap="RdYlGn_r", alpha=0.5, s=10)
    plt.colorbar(scatter, ax=ax, label="Year")
    ax.set_title("Humidity vs Temperature (colored by Year)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Humidity (%)")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/eda/06_humidity_vs_temp.png", dpi=150)
    plt.close()
    print("  Saved: outputs/eda/06_humidity_vs_temp.png")

    print("[EDA] All 6 plots saved to outputs/eda/\n")

if __name__ == "__main__":
    df = pd.read_csv("data/processed/climate_featured.csv", parse_dates=["date"])
    run_eda(df)
