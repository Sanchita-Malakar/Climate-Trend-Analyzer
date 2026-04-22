"""
src/data_cleaner.py
--------------------
Cleans the raw climate CSV:
  - Parses dates
  - Removes physically impossible values
  - Forward-fills remaining missing values
  - Saves cleaned data to data/processed/
"""

import pandas as pd
import numpy as np
import os

def clean_climate_data(input_path="data/raw/climate_data.csv",
                        output_path="data/processed/climate_clean.csv"):

    print("\n[DATA CLEANER] Starting...")
    df = pd.read_csv(input_path, parse_dates=["date"])
    print(f"  Loaded          : {df.shape[0]:,} rows × {df.shape[1]} columns")

    null_before = df.isnull().sum().sum()
    print(f"  Nulls before    : {null_before}")

    # Remove physically impossible values
    before = len(df)
    df = df[(df["temperature_c"] >= -50) & (df["temperature_c"] <= 60)]
    df = df[(df["rainfall_mm"]   >= 0)   & (df["rainfall_mm"]   <= 600)]
    df = df[(df["humidity_pct"]  >= 0)   & (df["humidity_pct"]  <= 100)]
    removed = before - len(df)
    print(f"  Rows removed    : {removed} (impossible values)")

    # Forward-fill any remaining gaps
    df = df.ffill()
    null_after = df.isnull().sum().sum()
    print(f"  Nulls after     : {null_after}")

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  Saved to        : {output_path}")
    print(f"  Final shape     : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print("[DATA CLEANER] Done.\n")
    return df

if __name__ == "__main__":
    clean_climate_data()
