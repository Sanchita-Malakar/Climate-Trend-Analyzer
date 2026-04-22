# 🌍 Climate Trend Analyzer

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0-green?style=flat-square&logo=pandas)
![Statsmodels](https://img.shields.io/badge/Statsmodels-SARIMA-orange?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-purple?style=flat-square)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-20%20Passed-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)

> A complete end-to-end climate data analysis system that detects long-term warming trends, identifies climate anomalies, and forecasts future temperature patterns using 50 years of simulated climate data (1975–2024).

---

## 📌 Project Overview

The **Climate Trend Analyzer** is a data science project modeled on the real-world pipelines used by climate agencies such as NOAA, IMD, and NASA GISS. It demonstrates:

- **Statistical trend analysis** — linear regression on annual temperature, warming rate detection
- **Anomaly detection** — z-score and IQR-based identification of extreme climate events
- **Time-series forecasting** — SARIMA model projecting 10 years into the future
- **Interactive dashboard** — Streamlit app with filters, tabs, and Plotly visualizations
- **Automated reporting** — markdown insights report generated from analysis results

---

## 🔬 Key Results

| Metric | Value |
|--------|-------|
| **Warming rate** | +0.254 °C per decade |
| **Total temperature rise (50 yr)** | +1.25 °C |
| **R² score** | 0.9550 (95.5% variance explained) |
| **P-value** | < 0.001 (statistically significant) |
| **Anomalies detected** | 14 events (10 heat, 4 cold) |
| **Forecast period** | Jan 2025 – Dec 2034 |
| **Forecast avg temp** | 26.40 °C |
| **Tests passing** | 20/20 ✅ |

---

## 🏗️ Project Architecture

```
Raw CSV Data
    ↓
generate_dataset.py     → 18,263 daily records (1975–2024)
    ↓
src/data_cleaner.py     → Remove impossible values, fill gaps
    ↓
src/feature_engineering.py → Seasons, rolling averages, z-scores
    ↓
src/eda.py              → 6 exploratory analysis plots
    ↓
src/trend_analysis.py   → OLS regression, warming rate, R²
    ↓
src/anomaly_detection.py → Z-score + IQR, anomaly timeline
    ↓
src/forecasting.py      → SARIMA 10-year forecast
    ↓
src/generate_report.py  → Markdown insights report
    ↓
app/dashboard.py        → Interactive Streamlit dashboard
```

---

## 📁 Folder Structure

```
Climate-Trend-Analyzer/
│
├── data/
│   ├── raw/                    ← original generated CSV
│   └── processed/              ← cleaned + feature-engineered data
│
├── src/                        ← all Python analysis modules
│   ├── data_cleaner.py
│   ├── feature_engineering.py
│   ├── eda.py
│   ├── trend_analysis.py
│   ├── anomaly_detection.py
│   ├── forecasting.py
│   └── generate_report.py
│
├── app/
│   └── dashboard.py            ← Streamlit interactive dashboard
│
├── outputs/
│   ├── eda/                    ← 6 EDA plots
│   ├── trends/                 ← trend analysis charts + CSV
│   ├── anomalies/              ← anomaly timeline + report CSV
│   └── forecasts/              ← 10-year forecast chart + CSV
│
├── reports/
│   └── climate_insights.md     ← full automated insights report
│
├── tests/
│   └── test_pipeline.py        ← 20 automated tests (pytest)
│
├── docs/
│   └── architecture.md         ← system design documentation
│
├── generate_dataset.py         ← synthetic dataset generator
├── main.py                     ← full pipeline runner
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/Climate-Trend-Analyzer.git
cd Climate-Trend-Analyzer
```

### Step 2 — Create virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Verify installation
```bash
python -c "import pandas, numpy, sklearn, statsmodels, streamlit; print('All OK')"
```

---

## 🚀 How to Run

### Option A — Run full pipeline (recommended)
```bash
python main.py
```
This runs all 6 stages automatically and takes ~2–4 minutes.

### Option B — Run individual modules
```bash
python generate_dataset.py          # Stage 1: generate data
python src/data_cleaner.py          # Stage 2: clean data
python src/feature_engineering.py   # Stage 3: add features
python src/eda.py                   # Stage 4: EDA plots
python src/trend_analysis.py        # Stage 5: trend analysis
python src/anomaly_detection.py     # Stage 5: anomaly detection
python src/forecasting.py           # Stage 6: forecasting
python src/generate_report.py       # Stage 6: generate report
```

### Option C — Launch the interactive dashboard
```bash
streamlit run app/dashboard.py
```
Then open your browser at: **http://localhost:8501**

### Option D — Run tests
```bash
python -m pytest tests/ -v
```
Expected: **20 tests passed**

---

## 📊 Output Files Generated

| File | Description |
|------|-------------|
| `data/raw/climate_data.csv` | 18,263 daily records (1975–2024) |
| `data/processed/climate_featured.csv` | Cleaned data with 15 feature columns |
| `outputs/eda/01_monthly_temp_boxplot.png` | Monthly temperature distribution |
| `outputs/eda/02_annual_rainfall.png` | Annual rainfall bar chart |
| `outputs/eda/03_correlation_heatmap.png` | Variable correlation matrix |
| `outputs/eda/04_seasonal_distribution.png` | Seasonal violin plot |
| `outputs/eda/05_decadal_temperature.png` | Decade-wise averages |
| `outputs/eda/06_humidity_vs_temp.png` | Humidity vs temperature scatter |
| `outputs/trends/trend_analysis_4panel.png` | 4-panel trend analysis chart |
| `outputs/trends/trend_results.csv` | Regression statistics |
| `outputs/anomalies/anomaly_detection_timeline.png` | Anomaly timeline |
| `outputs/anomalies/anomaly_report.csv` | All detected anomaly events |
| `outputs/forecasts/temperature_forecast.png` | 10-year forecast chart |
| `outputs/forecasts/temperature_forecast.csv` | Forecast data table |
| `reports/climate_insights.md` | Complete insights report |

---

## 🧪 Methods Used

| Module | Method | Library |
|--------|--------|---------|
| Trend analysis | Ordinary Least Squares (OLS) regression | scikit-learn, scipy |
| Anomaly detection | Z-score (σ ≥ 2.5) + IQR method | scipy, numpy |
| Forecasting | SARIMA(1,1,1)(1,1,0,12) | statsmodels |
| Visualization | Static charts | matplotlib, seaborn |
| Dashboard | Interactive charts | plotly, streamlit |

---

## 💼 Interview Talking Points

**Q: What does this project do?**
> "It analyzes 50 years of climate data to detect long-term warming trends, identify extreme weather anomalies, and forecast future temperatures — the same type of pipeline used by NOAA and IMD."

**Q: What did you find?**
> "A statistically significant warming rate of +0.254°C per decade with R²=0.955 and p < 0.001, plus 14 climate anomaly events. The 10-year SARIMA forecast projects continued warming averaging 26.4°C through 2034."

**Q: Why SARIMA for forecasting?**
> "SARIMA captures both the trend (integrated component) and the strong 12-month seasonal cycle in monthly climate data, making it more accurate than simple ARIMA for this use case."

**Q: How did you validate the results?**
> "I wrote 20 automated pytest tests covering data integrity, feature correctness, output file validation, and statistical sanity checks — all passing."

---

## 🌐 Real-World Applications

- **Governments** — drought and flood policy planning
- **Agriculture** — crop calendar optimization based on seasonal shifts
- **Smart cities** — urban heat island monitoring and energy grid forecasting  
- **Insurance** — climate risk modeling for extreme weather events
- **Public health** — heatwave early warning system development

---

## 📚 Dataset

This project uses a **synthetic dataset** generated with statistically realistic parameters:
- Warming trend: +0.025°C/year (consistent with IPCC global average)
- Seasonal amplitude: ±8°C
- Monsoon simulation: June–September rainfall spike
- 50 injected anomaly events for testing detection accuracy

For real data, this pipeline can be directly applied to:
- [NOAA Global Surface Temperature](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)
- [NASA GISS Surface Temperature](https://data.giss.nasa.gov/gistemp/)
- [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api)

---

## 🛠️ Tech Stack

```
Python 3.10+       pandas · numpy · scipy
Machine Learning   scikit-learn (OLS regression)
Time Series        statsmodels (SARIMA)
Visualization      matplotlib · seaborn · plotly
Dashboard          streamlit
Testing            pytest
```

---

## 👤 Author

**[Your Name]**  
Data Science Portfolio Project  
📧 your.email@example.com  
🔗 [LinkedIn](https://linkedin.com) | [GitHub](https://github.com)

---

*This project demonstrates skills in: time-series analysis, statistical modeling, anomaly detection, data visualization, automated testing, and scientific reporting.*
