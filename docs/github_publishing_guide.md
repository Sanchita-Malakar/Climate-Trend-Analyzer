# GitHub Publishing Guide — Step by Step

## Prerequisites
- GitHub account (free at github.com)
- Git installed on your computer

---

## Step 1 — Create GitHub repository

1. Go to https://github.com/new
2. Repository name: `Climate-Trend-Analyzer`
3. Description: `50-year climate trend analysis with anomaly detection and 10-year SARIMA forecasting`
4. Set to **Public**
5. Do NOT check "Add a README" (we have our own)
6. Click **Create repository**

---

## Step 2 — Initialize git in your project folder

Open terminal in your `Climate-Trend-Analyzer/` folder:

```bash
git init
git add .
git commit -m "Initial commit: Complete Climate Trend Analyzer project"
```

---

## Step 3 — Connect and push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/Climate-Trend-Analyzer.git
git branch -M main
git push -u origin main
```

---

## Step 4 — Add output images to the repo

The `.gitignore` excludes `data/raw/*.csv` (large file) but keeps all outputs.
To make sure images show in README, copy key screenshots to `images/`:

```bash
cp outputs/trends/trend_analysis_4panel.png images/
cp outputs/anomalies/anomaly_detection_timeline.png images/
cp outputs/forecasts/temperature_forecast.png images/
cp outputs/eda/01_monthly_temp_boxplot.png images/
git add images/
git commit -m "Add project output screenshots"
git push
```

---

## Step 5 — Add images to README (optional but impressive)

In `README.md`, add after the Key Results table:

```markdown
## 📸 Screenshots

### Trend Analysis
![Trend Analysis](images/trend_analysis_4panel.png)

### Anomaly Detection
![Anomaly Detection](images/anomaly_detection_timeline.png)

### 10-Year Forecast
![Forecast](images/temperature_forecast.png)
```

Then commit and push again.

---

## Step 6 — Add GitHub topics for discoverability

On your GitHub repo page:
1. Click the gear icon next to "About"
2. Add topics: `python`, `data-science`, `climate-analysis`, `time-series`, `anomaly-detection`, `streamlit`, `pandas`, `statsmodels`, `sarima`, `machine-learning`

---

## Step 7 — Pin the repo on your profile

1. Go to your GitHub profile
2. Click "Customize your pins"
3. Select `Climate-Trend-Analyzer`
4. Click Save

---

## Step 8 — Deploy dashboard to Streamlit Cloud (FREE)

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repo: `Climate-Trend-Analyzer`
5. Branch: `main`
6. Main file path: `app/dashboard.py`
7. Click **Deploy**

Your dashboard will be live at:
`https://YOUR_USERNAME-climate-trend-analyzer-appdashboard-XXXX.streamlit.app`

Add this URL to your README and LinkedIn!

---

## What your GitHub profile will show

- Professional repo with 20+ files
- Green commit history
- Badges (Python, Tests passing, Streamlit)
- 9 output charts and graphs
- Complete README with results
- Automated tests (20 passed)
- Live dashboard link

This is interview-ready proof of work.
