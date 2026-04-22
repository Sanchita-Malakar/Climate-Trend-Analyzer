"""
main.py
-------
Master pipeline runner for Climate Trend Analyzer.
Run: python main.py

Executes all 6 stages in sequence:
  1. Generate synthetic dataset
  2. Clean data
  3. Feature engineering
  4. EDA
  5. Trend analysis + Anomaly detection
  6. Forecasting + Report generation
"""

import os
import sys
import time
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def banner(text):
    print("\n" + "═" * 55)
    print(f"  {text}")
    print("═" * 55)

def step(n, total, text):
    print(f"\n[{n}/{total}] {text}...")

start_time = time.time()

banner("CLIMATE TREND ANALYZER — FULL PIPELINE")
print("  Student Project | Data Science & Climate Analysis")
print("  50-Year Simulation | 1975–2024")

# Create all output directories
for folder in [
    "data/raw", "data/processed",
    "outputs/eda", "outputs/trends",
    "outputs/anomalies", "outputs/forecasts",
    "models", "reports", "images", "tests"
]:
    os.makedirs(folder, exist_ok=True)

# ── Stage 1: Generate Dataset ─────────────────────────────
step(1, 6, "Generating synthetic 50-year climate dataset")
import generate_dataset  # noqa: runs the script

# ── Stage 2: Data Cleaning ────────────────────────────────
step(2, 6, "Cleaning and validating data")
from data_cleaner import clean_climate_data
df = clean_climate_data(
    input_path="data/raw/climate_data.csv",
    output_path="data/processed/climate_clean.csv"
)

# ── Stage 3: Feature Engineering ─────────────────────────
step(3, 6, "Engineering climate features")
from feature_engineering import add_features
df = add_features(df)
df.to_csv("data/processed/climate_featured.csv", index=False)
print(f"  Saved: data/processed/climate_featured.csv  [{df.shape}]")

# ── Stage 4: EDA ──────────────────────────────────────────
step(4, 6, "Running exploratory data analysis")
from eda import run_eda
run_eda(df)

# ── Stage 5: Trend + Anomaly ──────────────────────────────
step(5, 6, "Trend analysis and anomaly detection")
from trend_analysis import analyze_trends
from anomaly_detection import detect_anomalies
trend_results, annual_df = analyze_trends(df)
anomaly_df = detect_anomalies(df)

# ── Stage 6: Forecasting + Report ────────────────────────
step(6, 6, "10-year forecasting and report generation")
from forecasting import forecast_temperature
forecast_df = forecast_temperature(df)

from generate_report import generate_report
generate_report(trend_results, anomaly_df, forecast_df)

# ── Final Summary ─────────────────────────────────────────
elapsed = time.time() - start_time
banner("PIPELINE COMPLETE")
print(f"  Duration           : {elapsed:.1f} seconds")
print(f"  Records processed  : {len(df):,}")
print(f"  Warming rate       : {trend_results['warming_rate_per_decade']:+.3f} °C/decade")
print(f"  R² score           :  {trend_results['r2_score']:.4f}")
print(f"  P-value            :  {trend_results['p_value']:.2e}")
print(f"  Anomalies detected :  {len(anomaly_df)}")
print(f"  Forecast period    :  Jan 2025 – Dec 2034")
print()
print("  Output files:")
print("    outputs/eda/                  — 6 EDA plots")
print("    outputs/trends/               — trend chart + CSV")
print("    outputs/anomalies/            — anomaly timeline + CSV")
print("    outputs/forecasts/            — forecast chart + CSV")
print("    reports/climate_insights.md  — full insights report")
print()
print("  Next step → Dashboard:")
print("    streamlit run app/dashboard.py")
print("═" * 55)
