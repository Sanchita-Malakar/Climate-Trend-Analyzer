"""
tests/test_pipeline.py
-----------------------
Basic sanity tests for Climate Trend Analyzer.
Run: python -m pytest tests/ -v
"""

import pytest
import pandas as pd
import numpy as np
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# ── Dataset Tests ────────────────────────────────────────────────────────────

def test_raw_dataset_exists():
    assert os.path.exists("data/raw/climate_data.csv"), "Raw dataset missing"

def test_raw_dataset_shape():
    df = pd.read_csv("data/raw/climate_data.csv")
    assert df.shape[0] > 18000, f"Expected > 18000 rows, got {df.shape[0]}"
    assert df.shape[1] >= 7, f"Expected >= 7 columns, got {df.shape[1]}"

def test_raw_dataset_no_nulls():
    df = pd.read_csv("data/raw/climate_data.csv")
    assert df.isnull().sum().sum() == 0, "Raw dataset has null values"

def test_raw_dataset_columns():
    df = pd.read_csv("data/raw/climate_data.csv")
    required = ["date","temperature_c","rainfall_mm","humidity_pct","year","month"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"

# ── Cleaned Data Tests ───────────────────────────────────────────────────────

def test_cleaned_dataset_exists():
    assert os.path.exists("data/processed/climate_clean.csv")

def test_cleaned_no_impossible_temps():
    df = pd.read_csv("data/processed/climate_clean.csv")
    assert df["temperature_c"].max() <= 60,  "Temperature exceeds 60°C"
    assert df["temperature_c"].min() >= -50, "Temperature below -50°C"

def test_cleaned_no_negative_rain():
    df = pd.read_csv("data/processed/climate_clean.csv")
    assert (df["rainfall_mm"] >= 0).all(), "Negative rainfall found"

# ── Feature Engineering Tests ────────────────────────────────────────────────

def test_featured_dataset_exists():
    assert os.path.exists("data/processed/climate_featured.csv")

def test_season_column():
    df = pd.read_csv("data/processed/climate_featured.csv")
    assert "season" in df.columns
    valid_seasons = {"Winter","Spring","Summer","Autumn"}
    assert set(df["season"].unique()).issubset(valid_seasons)

def test_anomaly_flag_binary():
    df = pd.read_csv("data/processed/climate_featured.csv")
    assert set(df["is_anomaly"].unique()).issubset({0, 1}), "is_anomaly not binary"

def test_anomaly_count_positive():
    df = pd.read_csv("data/processed/climate_featured.csv")
    assert df["is_anomaly"].sum() > 0, "No anomalies detected"

def test_rolling_columns_exist():
    df = pd.read_csv("data/processed/climate_featured.csv")
    for col in ["temp_7day","temp_30day","rain_30day","temp_zscore"]:
        assert col in df.columns, f"Missing feature column: {col}"

# ── Output Files Tests ───────────────────────────────────────────────────────

def test_eda_plots_generated():
    for i in range(1, 7):
        fname = f"outputs/eda/0{i}_" if i < 7 else f"outputs/eda/{i}_"
        files = [f for f in os.listdir("outputs/eda") if f.endswith(".png")]
        assert len(files) >= 6, f"Expected 6 EDA plots, found {len(files)}"
        break

def test_trend_results_csv():
    assert os.path.exists("outputs/trends/trend_results.csv")
    tr = pd.read_csv("outputs/trends/trend_results.csv")
    assert "warming_rate_per_decade" in tr.columns
    assert "r2_score" in tr.columns
    assert tr["r2_score"].iloc[0] > 0.5, "R2 score suspiciously low"

def test_anomaly_report_csv():
    assert os.path.exists("outputs/anomalies/anomaly_report.csv")
    ar = pd.read_csv("outputs/anomalies/anomaly_report.csv")
    assert len(ar) > 0, "Anomaly report is empty"
    assert "anomaly_type" in ar.columns

def test_forecast_csv():
    assert os.path.exists("outputs/forecasts/temperature_forecast.csv")
    fc = pd.read_csv("outputs/forecasts/temperature_forecast.csv")
    assert len(fc) == 120, f"Expected 120 forecast months, got {len(fc)}"
    assert "forecast_c" in fc.columns

def test_forecast_reasonable_range():
    fc = pd.read_csv("outputs/forecasts/temperature_forecast.csv")
    assert fc["forecast_c"].between(10, 50).all(), "Forecast temperatures out of range"

def test_report_generated():
    assert os.path.exists("reports/climate_insights.md")
    with open("reports/climate_insights.md") as f:
        content = f.read()
    assert "Warming rate" in content
    assert len(content) > 500, "Report too short"

# ── Trend Analysis Sanity ────────────────────────────────────────────────────

def test_warming_trend_positive():
    tr = pd.read_csv("outputs/trends/trend_results.csv").iloc[0]
    assert tr["warming_rate_per_decade"] > 0, "Trend should be warming"
    assert tr["trend_direction"] == "WARMING"

def test_pvalue_significant():
    tr = pd.read_csv("outputs/trends/trend_results.csv").iloc[0]
    assert tr["p_value"] < 0.05, "Trend not statistically significant"
