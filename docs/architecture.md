# Climate Trend Analyzer — Architecture Documentation

## System Design

### Overview
The Climate Trend Analyzer is a modular data science pipeline with 6 stages,
each implemented as an independent Python module with a clear input/output contract.

### Data Flow

```
[INPUT]
  data/raw/climate_data.csv
  (18,263 daily records | 1975-2024)
        |
        v
[STAGE 1] generate_dataset.py
  - Simulates temperature with warming trend + seasonal cycle + noise
  - Simulates rainfall with monsoon pattern
  - Injects 50 anomaly events
  OUTPUT: data/raw/climate_data.csv
        |
        v
[STAGE 2] src/data_cleaner.py
  - Removes physically impossible values (temp > 60°C, rain < 0, etc.)
  - Forward-fills any remaining gaps
  OUTPUT: data/processed/climate_clean.csv
        |
        v
[STAGE 3] src/feature_engineering.py
  - Adds: season, decade, temp_7day, temp_30day, rain_30day
  - Adds: temp_zscore, is_anomaly (z >= 2.5)
  OUTPUT: data/processed/climate_featured.csv (15 columns)
        |
        v
[STAGE 4] src/eda.py
  - 6 exploratory plots saved to outputs/eda/
  - Summary statistics CSV
  OUTPUT: outputs/eda/*.png, outputs/eda/summary_statistics.csv
        |
        v
[STAGE 5a] src/trend_analysis.py
  - OLS linear regression on annual mean temperature
  - Warming rate (°C/decade), R², p-value
  - 4-panel trend visualization
  OUTPUT: outputs/trends/trend_analysis_4panel.png
          outputs/trends/trend_results.csv

[STAGE 5b] src/anomaly_detection.py
  - Z-score thresholding (|z| >= 2.5)
  - IQR method (secondary validation)
  - Timeline + frequency plots
  OUTPUT: outputs/anomalies/anomaly_report.csv
          outputs/anomalies/anomaly_detection_timeline.png
          outputs/anomalies/anomaly_frequency_month.png
        |
        v
[STAGE 6a] src/forecasting.py
  - Monthly aggregation
  - SARIMA(1,1,1)(1,1,0,12) fitting on 600 months
  - 10-year forecast with 95% CI
  OUTPUT: outputs/forecasts/temperature_forecast.csv
          outputs/forecasts/temperature_forecast.png

[STAGE 6b] src/generate_report.py
  - Collects all results
  - Generates markdown report with tables and findings
  OUTPUT: reports/climate_insights.md

[DASHBOARD] app/dashboard.py
  - Streamlit app with 5 tabs
  - Reads all processed outputs
  - Interactive Plotly charts with sidebar filters
```

## Module Contracts

### data_cleaner.py
- **Input**: `data/raw/climate_data.csv`
- **Output**: `data/processed/climate_clean.csv`
- **Guarantees**: zero nulls, physically valid values

### feature_engineering.py
- **Input**: `data/processed/climate_clean.csv`
- **Output**: `data/processed/climate_featured.csv`
- **Adds**: season, decade, rolling averages, z-score, anomaly flag

### trend_analysis.py
- **Input**: `data/processed/climate_featured.csv`
- **Output**: `outputs/trends/*`, returns `(results_dict, annual_df)`
- **Reports**: slope (°C/yr), R², p-value, total rise

### anomaly_detection.py
- **Input**: `data/processed/climate_featured.csv`
- **Output**: `outputs/anomalies/*`, returns `anomalies_df`
- **Method**: Z-score >= 2.5 sigma + IQR cross-check

### forecasting.py
- **Input**: `data/processed/climate_featured.csv`
- **Output**: `outputs/forecasts/*`, returns `forecast_df`
- **Model**: SARIMA(1,1,1)(1,1,0,12), 120 months ahead

## Technology Choices

| Decision | Choice | Reason |
|----------|--------|--------|
| Forecasting model | SARIMA | Handles seasonality natively, no GPU needed |
| Anomaly detection | Z-score | Interpretable, fast, industry standard |
| Trend analysis | OLS regression | Simplest valid method, explainable |
| Dashboard | Streamlit | Fast to build, professional output |
| Charts | Plotly | Interactive, publication quality |
| Testing | pytest | Industry standard, easy assertions |

## Scalability Notes

This pipeline can be scaled to real climate data by:
1. Replacing `generate_dataset.py` with a NOAA/Open-Meteo API download script
2. Increasing the SARIMA order search with `auto_arima` from `pmdarima`
3. Adding Prophet as a secondary forecasting model for comparison
4. Deploying the Streamlit dashboard to Streamlit Cloud (free)
