import pandas as pd
import numpy as np
import os

np.random.seed(42)

dates = pd.date_range(start="1975-01-01", end="2024-12-31", freq="D")
n = len(dates)

years_elapsed = np.array((dates - dates[0]).days / 365.25)
day_of_year   = np.array(dates.day_of_year)
month         = np.array(dates.month)

baseline     = 25.0
warming_rate = 0.025
seasonal_amp = 8.0
noise_std    = 1.5

temperature = np.array(
    baseline
    + warming_rate * years_elapsed
    + seasonal_amp * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    + np.random.normal(0, noise_std, n),
    dtype=float
)

rain_base = np.where((month >= 6) & (month <= 9), 9.0, 1.5)
rainfall  = np.abs(np.random.exponential(rain_base))

humidity = np.clip(
    55 + 25 * np.sin(2 * np.pi * (day_of_year - 170) / 365)
    + np.random.normal(0, 5, n), 20, 100
)

wind_speed = np.clip(np.abs(np.random.normal(15, 7, n)), 0, 80)

anomaly_idx    = np.random.choice(n, 50, replace=False)
anomaly_deltas = np.random.choice([-9, -8, 9, 10, 11], 50)
temperature[anomaly_idx] += anomaly_deltas

df = pd.DataFrame({
    "date":           dates,
    "temperature_c":  np.round(temperature, 2),
    "rainfall_mm":    np.round(rainfall, 2),
    "humidity_pct":   np.round(humidity, 1),
    "wind_speed_kmh": np.round(wind_speed, 1),
    "year":           dates.year,
    "month":          dates.month,
    "day_of_year":    day_of_year,
})

os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/climate_data.csv", index=False)
print("=" * 50)
print("DATASET GENERATED")
print(f"Records   : {len(df):,}")
print(f"Date range: {df['date'].min().date()} -> {df['date'].max().date()}")
print(f"Columns   : {list(df.columns)}")
print("=" * 50)
