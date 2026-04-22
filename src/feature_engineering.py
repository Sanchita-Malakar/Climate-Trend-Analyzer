"""
src/feature_engineering.py
---------------------------
Adds derived columns:
  - season, decade
  - 7-day and 30-day rolling temperature averages
  - 30-day rolling rainfall average
  - z-score of temperature
  - is_anomaly flag (|z| >= 2.5)
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

def add_features(df):
    print("\n[FEATURE ENGINEERING] Starting...")

    # Season
    def get_season(m):
        if m in [12, 1, 2]:  return "Winter"
        if m in [3, 4, 5]:   return "Spring"
        if m in [6, 7, 8]:   return "Summer"
        return "Autumn"

    df = df.sort_values("date").reset_index(drop=True)
    df["season"] = df["month"].apply(get_season)
    df["decade"] = (df["year"] // 10) * 10

    # Rolling averages
    df["temp_7day"]  = df["temperature_c"].rolling(7,  center=True, min_periods=1).mean().round(2)
    df["temp_30day"] = df["temperature_c"].rolling(30, center=True, min_periods=1).mean().round(2)
    df["rain_30day"] = df["rainfall_mm"].rolling(30,   center=True, min_periods=1).mean().round(2)

    # Z-score anomaly detection
    df["temp_zscore"] = np.round(stats.zscore(df["temperature_c"]), 3)
    df["is_anomaly"]  = (df["temp_zscore"].abs() >= 2.5).astype(int)

    print(f"  Seasons added   : {df['season'].value_counts().to_dict()}")
    print(f"  Anomalies found : {df['is_anomaly'].sum()}")
    print(f"  Final shape     : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print("[FEATURE ENGINEERING] Done.\n")
    return df

if __name__ == "__main__":
    df = pd.read_csv("data/processed/climate_clean.csv", parse_dates=["date"])
    df = add_features(df)
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/climate_featured.csv", index=False)
    print(f"Saved: data/processed/climate_featured.csv")
