"""
src/forecasting.py
------------------
10-year temperature forecasting using:
  - ARIMA model via statsmodels (no external API needed)
  - Monthly aggregated data
  - Confidence intervals plotted
  - Saves forecast chart + CSV
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os

warnings.filterwarnings("ignore")

def forecast_temperature(df, periods=120):
    """
    periods: number of months to forecast (default 120 = 10 years)
    """
    print("\n[FORECASTING] Starting 10-year temperature forecast...")
    os.makedirs("outputs/forecasts", exist_ok=True)

    # Aggregate to monthly mean
    df["ym"] = df["date"].dt.to_period("M")
    monthly  = df.groupby("ym")["temperature_c"].mean()
    monthly.index = monthly.index.to_timestamp()
    monthly = monthly.asfreq("MS")

    print(f"  Monthly series  : {len(monthly)} months")
    print(f"  Range           : {monthly.index[0].date()} → {monthly.index[-1].date()}")

    # SARIMA model — handles seasonality automatically
    # (1,1,1)(1,1,0,12) is a robust choice for monthly climate data
    print("  Fitting SARIMA(1,1,1)(1,1,0,12) model...")
    model  = SARIMAX(monthly,
                     order=(1, 1, 1),
                     seasonal_order=(1, 1, 0, 12),
                     enforce_stationarity=False,
                     enforce_invertibility=False)
    fitted = model.fit(disp=False)
    print(f"  AIC: {fitted.aic:.2f}  BIC: {fitted.bic:.2f}")

    # Forecast
    forecast_result = fitted.get_forecast(steps=periods)
    forecast_mean   = forecast_result.predicted_mean
    forecast_ci     = forecast_result.conf_int()

    # Build future date index
    future_dates = pd.date_range(
        start=monthly.index[-1] + pd.DateOffset(months=1),
        periods=periods, freq="MS"
    )
    forecast_mean.index = future_dates
    forecast_ci.index   = future_dates

    # Save forecast CSV
    forecast_df = pd.DataFrame({
        "date":       future_dates,
        "forecast_c": forecast_mean.round(3).values,
        "lower_95":   forecast_ci.iloc[:, 0].round(3).values,
        "upper_95":   forecast_ci.iloc[:, 1].round(3).values,
    })
    forecast_df.to_csv("outputs/forecasts/temperature_forecast.csv", index=False)
    print(f"\n  Forecast summary:")
    print(f"  Period covered  : {future_dates[0].date()} → {future_dates[-1].date()}")
    print(f"  Avg forecast    : {forecast_mean.mean():.2f}°C")
    print(f"  Max forecast    : {forecast_mean.max():.2f}°C")
    print(f"  Min forecast    : {forecast_mean.min():.2f}°C")

    # --- Main Forecast Plot ---
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    fig.suptitle("10-Year Temperature Forecast (2025–2034)\nSARIMA Model",
                 fontsize=14, fontweight="bold")

    # Panel 1: Full view
    ax = axes[0]
    ax.plot(monthly.index, monthly.values,
            color="#1D9E75", linewidth=1.0, alpha=0.9, label="Historical (monthly mean)")
    ax.plot(forecast_mean.index, forecast_mean.values,
            color="#D85A30", linewidth=2.2, label="10-Year Forecast")
    ax.fill_between(forecast_ci.index,
                    forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1],
                    color="#D85A30", alpha=0.18, label="95% Confidence Interval")
    ax.axvline(x=monthly.index[-1], color="gray", linestyle="--",
               linewidth=1.2, alpha=0.7, label="Forecast start (Jan 2025)")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    ax.set_title("Historical + 10-Year Forecast", fontweight="bold")

    # Panel 2: Forecast only (zoomed)
    ax = axes[1]
    last_3yr = monthly[monthly.index >= "2022-01-01"]
    ax.plot(last_3yr.index, last_3yr.values,
            color="#1D9E75", linewidth=1.5, label="Recent historical (2022–2024)")
    ax.plot(forecast_mean.index, forecast_mean.values,
            color="#D85A30", linewidth=2.2, label="Forecast (2025–2034)")
    ax.fill_between(forecast_ci.index,
                    forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1],
                    color="#D85A30", alpha=0.2)
    ax.axvline(x=monthly.index[-1], color="gray", linestyle="--", linewidth=1.2)
    ax.set_ylabel("Temperature (°C)"); ax.set_xlabel("Date")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    ax.set_title("Zoomed Forecast View (2022–2034)", fontweight="bold")

    plt.tight_layout()
    plt.savefig("outputs/forecasts/temperature_forecast.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: outputs/forecasts/temperature_forecast.png")
    print("[FORECASTING] Done.\n")

    return forecast_df

if __name__ == "__main__":
    df = pd.read_csv("data/processed/climate_featured.csv", parse_dates=["date"])
    forecast_temperature(df)
