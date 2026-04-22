"""
app/dashboard.py  v3.0 — India Live Weather Map Added
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# india_weather_map imports — handles both app/ and project-root placement
try:
    from india_weather_map import (
        fetch_weather_batch, INDIA_CITIES,
        build_premium_india_map, get_premium_stats,
    )
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from india_weather_map import (
        fetch_weather_batch, INDIA_CITIES,
        build_premium_india_map, get_premium_stats,
    )

st.set_page_config(page_title="Climate Trend Analyzer — Kolkata",
    page_icon="🌍", layout="wide")

# ── OLS helper — no statsmodels dependency, uses numpy only ──────────────────
def _ols_trace(x_vals, y_vals, color="#D85A30", name="OLS Trend", width=2.5):
    """Compute a least-squares regression line and return it as a go.Scatter."""
    x = np.array(x_vals, dtype=float)
    y = np.array(y_vals, dtype=float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[mask], y[mask]
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.array([x.min(), x.max()])
    y_line = slope * x_line + intercept
    return go.Scatter(
        x=x_line, y=y_line, mode="lines",
        name=f"{name} ({slope:+.4f}/yr)",
        line=dict(color=color, width=width),
        showlegend=True,
    )

@st.cache_data
def load_all():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df        = pd.read_csv(f"{base}/data/processed/climate_featured.csv", parse_dates=["date"])
    anomalies = pd.read_csv(f"{base}/outputs/anomalies/anomaly_report.csv", parse_dates=["date"])
    forecast  = pd.read_csv(f"{base}/outputs/forecasts/temperature_forecast.csv", parse_dates=["date"])
    trend_res = pd.read_csv(f"{base}/outputs/trends/trend_results.csv").iloc[0].to_dict()
    return df, anomalies, forecast, trend_res

@st.cache_data
def load_ml():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        cmp = pd.read_csv(f"{base}/outputs/models/model_comparison.csv")
        imp = pd.read_csv(f"{base}/outputs/models/feature_importance.csv")
        iso = pd.read_csv(f"{base}/outputs/models/isolation_forest_anomalies.csv", parse_dates=["date"])
        return cmp, imp, iso
    except:
        return None, None, None

@st.cache_data(ttl=600)   # refresh every 10 minutes
def load_live_weather():
    """Fetch live weather for all Indian cities. Cached for 10 minutes."""
    weather_df, fetched_at = fetch_weather_batch(INDIA_CITIES)
    return weather_df, fetched_at

df, anomalies, forecast, trend = load_all()
ml_cmp, ml_imp, iso_an = load_ml()

def risk_score(wr, ac, yrs=50):
    ts = min((wr/0.5)*100, 100)
    as_ = min((ac/yrs/4)*100, 100)
    s = round(ts*0.6 + as_*0.4, 1)
    lbl = "Low" if s<30 else ("Moderate" if s<60 else "High")
    col = "#1D9E75" if s<30 else ("#BA7517" if s<60 else "#A32D2D")
    return s, lbl, col

def make_pdf(trend, anomalies, forecast, rs, rl):
    try:
        from fpdf import FPDF
        pdf = FPDF(); pdf.add_page(); pdf.set_margins(20,20,20)
        pdf.set_fill_color(29,158,117); pdf.rect(0,0,210,32,"F")
        pdf.set_font("Helvetica","B",17); pdf.set_text_color(255,255,255)
        pdf.set_y(8); pdf.cell(0,9,"Climate Trend Analyzer — Kolkata",ln=True,align="C")
        pdf.set_font("Helvetica",size=10)
        pdf.cell(0,7,"IMD Alipore Station | 1975-2024 | 50-Year Analysis",ln=True,align="C")
        pdf.set_text_color(0,0,0); pdf.ln(12)
        pdf.set_font("Helvetica","B",13); pdf.cell(0,8,"Key Results",ln=True)
        pdf.set_font("Helvetica",size=10)
        rows = [
            ("Warming rate", f"{trend['warming_rate_per_decade']:+.3f} degC/decade"),
            ("Total rise",   f"{trend['total_rise_50yr']:+.2f} degC over 50 years"),
            ("R2 score",     f"{trend['r2_score']:.4f}"),
            ("P-value",      f"{trend['p_value']:.2e}"),
            ("Anomalies",    f"{len(anomalies)} events detected"),
            ("Forecast avg", f"{forecast['forecast_c'].mean():.2f} degC (2025-2034)"),
            ("Risk score",   f"{rs}/100 ({rl} Risk)"),
        ]
        for k,v in rows:
            pdf.set_font("Helvetica","B",10); pdf.cell(70,7,k+":",border=0)
            pdf.set_font("Helvetica",size=10); pdf.cell(0,7,v,ln=True)
        pdf.ln(6)
        pdf.set_font("Helvetica","B",13); pdf.cell(0,8,"Top Anomaly Events",ln=True)
        pdf.set_font("Helvetica",size=9)
        for _,r in anomalies.nlargest(8,"temperature_c").iterrows():
            pdf.cell(0,6,f"  {str(r['date'])[:10]} | {r['temperature_c']:.1f}degC | z={r['temp_zscore']:.2f} | {r['anomaly_type']}",ln=True)
        pdf.ln(6)
        pdf.set_font("Helvetica","I",8); pdf.set_text_color(130,130,130)
        pdf.cell(0,5,"Generated by Climate Trend Analyzer | Python, Pandas, Scikit-learn, Statsmodels, Streamlit",ln=True,align="C")
        return bytes(pdf.output())
    except:
        return None

rs, rl, rc = risk_score(trend["warming_rate_per_decade"], len(anomalies))

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🌍 Climate Trend Analyzer")
st.sidebar.caption("Kolkata (Alipore) | 22.57°N 88.36°E")
st.sidebar.caption("IMD Station | 1975–2024")
st.sidebar.markdown("---")
yr = st.sidebar.slider("Year Range", 1975, 2024, (1975, 2024))
ssn = st.sidebar.multiselect("Season", ["Winter","Spring","Summer","Autumn"],
    default=["Winter","Spring","Summer","Autumn"])
st.sidebar.markdown("---")

# Live map controls in sidebar
st.sidebar.markdown("### 🗺 India Weather Map")
if st.sidebar.button("🔄 Refresh Live Weather"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Export")
if st.sidebar.button("Generate PDF Report"):
    b = make_pdf(trend, anomalies, forecast, rs, rl)
    if b:
        st.sidebar.download_button("Download PDF", b,
            "kolkata_climate_report.pdf","application/pdf")
    else:
        st.sidebar.warning("pip install fpdf2")
st.sidebar.markdown("---")
st.sidebar.markdown("**Stack:** Python · Pandas · Scikit-learn · Statsmodels · Plotly · Streamlit")

df_f = df[(df["year"]>=yr[0])&(df["year"]<=yr[1])&(df["season"].isin(ssn))].copy()

st.title("🌍 Climate Trend Analyzer — Kolkata")
st.caption(f"**{len(df_f):,}** records | {yr[0]}–{yr[1]}")
st.divider()

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Years", f"{yr[1]-yr[0]+1} yrs")
k2.metric("Avg Temp", f"{df_f['temperature_c'].mean():.1f}°C",
    delta=f"{trend['warming_rate_per_decade']:+.3f}°C/dec")
k3.metric("Avg Rain", f"{df_f['rainfall_mm'].mean():.1f} mm")
k4.metric("Avg Humidity", f"{df_f['humidity_pct'].mean():.0f}%")
k5.metric("Anomalies", f"{len(anomalies)}")
k6.metric("Risk Score", f"{rs}/100", delta=rl, delta_color="inverse")
st.divider()

t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs([
    "📈 Trend","🔍 Anomalies","🤖 ML Models",
    "🔮 Forecast","🌦 Seasonal Shift","📊 EDA",
    "🗺️ India Live Map","📋 Report"])

# ── TAB 1 — TREND ─────────────────────────────────────────────────────────────
with t1:
    st.subheader("Long-Term Temperature Trend — Kolkata 1975–2024")
    c1,c2 = st.columns([2,1])
    with c1:
        ann = df_f.groupby("year")["temperature_c"].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ann["year"], y=ann["temperature_c"], mode="markers",
            name="Annual mean", marker=dict(color="#1D9E75", size=7, opacity=0.85)))
        fig.add_trace(_ols_trace(ann["year"], ann["temperature_c"],
            color="#D85A30", name="OLS Trend"))
        fig.update_layout(
            title="Annual Mean Temperature + OLS Trend",
            xaxis_title="Year", yaxis_title="Mean Temp (°C)",
            template="plotly_white", height=360,
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("#### Statistics")
        st.markdown(f"""
| Metric | Value |
|--------|-------|
| Warming | **{trend['warming_rate_per_decade']:+.3f} °C/decade** |
| R² | **{trend['r2_score']:.4f}** |
| P-value | **{trend['p_value']:.2e}** |
| 50-yr rise | **{trend['total_rise_50yr']:+.2f} °C** |
| 1975 temp | **{trend['start_year_temp']:.2f} °C** |
| 2024 temp | **{trend['end_year_temp']:.2f} °C** |
""")
        st.success("✅ Significant warming confirmed (p<0.001)")
        st.markdown(f"<div style='background:{rc}22;border-left:4px solid {rc};padding:10px 14px;border-radius:0 8px 8px 0;margin-top:8px'><span style='font-size:22px;font-weight:600;color:{rc}'>{rs}/100</span><br><span style='color:{rc};font-size:13px'>{rl} Climate Risk</span></div>",unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        da = df_f.groupby("decade")["temperature_c"].mean().reset_index()
        da["lbl"] = da["decade"].astype(str)+"s"
        fig2 = px.bar(da,x="lbl",y="temperature_c",title="Avg Temp by Decade",
            color="temperature_c",color_continuous_scale="YlOrRd",
            template="plotly_white",text_auto=".2f")
        fig2.update_layout(height=300,coloraxis_showscale=False)
        st.plotly_chart(fig2,use_container_width=True)
    with c4:
        ar = df_f.groupby("year")["rainfall_mm"].sum().reset_index()
        ar["cat"] = ar["rainfall_mm"].apply(lambda v:"Above avg" if v>=ar["rainfall_mm"].mean() else "Below avg")
        fig3 = px.bar(ar,x="year",y="rainfall_mm",color="cat",
            color_discrete_map={"Above avg":"#1D9E75","Below avg":"#E87040"},
            title="Annual Total Rainfall",template="plotly_white")
        fig3.update_layout(height=300)
        st.plotly_chart(fig3,use_container_width=True)

# ── TAB 2 — ANOMALIES ─────────────────────────────────────────────────────────
with t2:
    st.subheader("Climate Anomaly Detection — Z-Score + Isolation Forest")
    a1,a2,a3,a4 = st.columns(4)
    nh = (anomalies["anomaly_type"]=="Extreme Heat").sum()
    nc = (anomalies["anomaly_type"]=="Extreme Cold").sum()
    a1.metric("Total",len(anomalies)); a2.metric("Extreme Heat",nh)
    a3.metric("Extreme Cold",nc); a4.metric("Threshold","|z|≥2.5σ")
    ft = go.Figure()
    ft.add_trace(go.Scatter(x=df_f["date"],y=df_f["temp_30day"],mode="lines",
        name="30-day rolling mean",line=dict(color="#378ADD",width=1),opacity=0.8))
    ht=anomalies[anomalies["anomaly_type"]=="Extreme Heat"]
    cd=anomalies[anomalies["anomaly_type"]=="Extreme Cold"]
    ft.add_trace(go.Scatter(x=ht["date"],y=ht["temperature_c"],mode="markers",
        name=f"Heat ({len(ht)})",marker=dict(color="#D85A30",size=8,symbol="triangle-up")))
    ft.add_trace(go.Scatter(x=cd["date"],y=cd["temperature_c"],mode="markers",
        name=f"Cold ({len(cd)})",marker=dict(color="#534AB7",size=8,symbol="triangle-down")))
    ft.update_layout(title="Temperature Timeline — Anomaly Events",
        xaxis_title="Date",yaxis_title="Temp (°C)",template="plotly_white",height=360)
    st.plotly_chart(ft,use_container_width=True)
    ca,cb = st.columns(2)
    with ca:
        mc=anomalies["month"].value_counts().sort_index()
        mn=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fmx=px.bar(x=[mn[m-1] for m in mc.index],y=mc.values,
            title="Anomaly Count by Month",labels={"x":"Month","y":"Count"},
            color=mc.values,color_continuous_scale="OrRd",template="plotly_white")
        fmx.update_layout(height=300,coloraxis_showscale=False)
        st.plotly_chart(fmx,use_container_width=True)
    with cb:
        yc=anomalies["year"].value_counts().sort_index()
        fyx=px.bar(x=yc.index,y=yc.values,title="Anomaly Count by Year",
            labels={"x":"Year","y":"Count"},color=yc.values,
            color_continuous_scale="Reds",template="plotly_white")
        fyx.update_layout(height=300,coloraxis_showscale=False)
        st.plotly_chart(fyx,use_container_width=True)
    sc=["date","year","month","temperature_c","temp_zscore","rainfall_mm","anomaly_type"]
    st.markdown("#### All Anomaly Events")
    st.dataframe(anomalies[sc].sort_values("temp_zscore",key=abs,ascending=False).reset_index(drop=True),use_container_width=True)

# ── TAB 3 — ML MODELS ─────────────────────────────────────────────────────────
with t3:
    st.subheader("Machine Learning Models — Random Forest & Isolation Forest")
    if ml_cmp is not None:
        m1,m2,m3 = st.columns(3)
        m1.metric("Best R²",ml_cmp["R2"].max())
        m2.metric("Best MAE",f"{ml_cmp['MAE'].min():.3f}°C")
        m3.metric("Best Model",ml_cmp.loc[ml_cmp["R2"].idxmax(),"Model"].split("(")[0].strip())
        st.markdown("---")
        fcmp=go.Figure()
        cols_bar=["#1D9E75","#378ADD","#7F77DD"]
        mods=[m.split("(")[0].strip() for m in ml_cmp["Model"].tolist()]
        for i,met in enumerate(["MAE","RMSE","R2"]):
            fcmp.add_trace(go.Bar(name=met,x=mods,y=ml_cmp[met].values,
                marker_color=cols_bar[i],
                text=[f"{v:.3f}" for v in ml_cmp[met].values],textposition="auto"))
        fcmp.update_layout(barmode="group",
            title="Model Comparison — MAE / RMSE / R² (Test: 2015–2024)",
            template="plotly_white",height=370,
            legend=dict(orientation="h",yanchor="bottom",y=1.02))
        st.plotly_chart(fcmp,use_container_width=True)
        if ml_imp is not None:
            st.markdown("#### Random Forest — Feature Importance")
            imp=ml_imp.rename(columns={"Unnamed: 0":"feature"}).sort_values("importance",ascending=True)
            fimp=px.bar(imp,x="importance",y="feature",orientation="h",
                title="Which variables drive temperature prediction?",
                color="importance",color_continuous_scale="Teal",template="plotly_white")
            fimp.update_layout(height=350,coloraxis_showscale=False)
            st.plotly_chart(fimp,use_container_width=True)
        if iso_an is not None:
            st.markdown("#### Isolation Forest — Multivariate Anomaly Detection")
            ic1,ic2,ic3 = st.columns(3)
            ic1.metric("Z-Score anomalies",len(anomalies))
            ic2.metric("Isolation Forest anomalies",len(iso_an))
            ov=len(set(anomalies["date"].astype(str))&set(iso_an["date"].astype(str)))
            ic3.metric("Both methods agree",ov)
            st.info("⭐ Events flagged by BOTH = highest confidence anomalies")
            st.dataframe(iso_an.head(15),use_container_width=True)
        st.markdown("#### Full Comparison Table")
        st.dataframe(ml_cmp,use_container_width=True)
    else:
        st.warning("Run `python src/ml_models.py` first to generate ML outputs.")

# ── TAB 4 — FORECAST ──────────────────────────────────────────────────────────
with t4:
    st.subheader("10-Year Forecast — 2025 to 2034")
    st.caption("SARIMA(1,1,1)(1,1,0,12) | 600 months training data")
    f1,f2,f3,f4=st.columns(4)
    f1.metric("Avg Forecast",f"{forecast['forecast_c'].mean():.2f}°C")
    f2.metric("Peak",f"{forecast['forecast_c'].max():.2f}°C")
    f3.metric("Low",f"{forecast['forecast_c'].min():.2f}°C")
    f4.metric("Months ahead","120")
    mh=df.groupby(df["date"].dt.to_period("M"))["temperature_c"].mean()
    mh.index=mh.index.to_timestamp()
    ffc=go.Figure()
    ffc.add_trace(go.Scatter(x=mh.index,y=mh.values,mode="lines",
        name="Historical",line=dict(color="#1D9E75",width=1.2),opacity=0.85))
    ffc.add_trace(go.Scatter(x=forecast["date"],y=forecast["forecast_c"],
        mode="lines",name="Forecast",line=dict(color="#D85A30",width=2.5)))
    ffc.add_trace(go.Scatter(
        x=pd.concat([forecast["date"],forecast["date"].iloc[::-1]]),
        y=pd.concat([forecast["upper_95"],forecast["lower_95"].iloc[::-1]]),
        fill="toself",fillcolor="rgba(216,90,48,0.12)",
        line=dict(color="rgba(255,255,255,0)"),name="95% CI"))
    ffc.add_shape(type="line",x0="2025-01-01",x1="2025-01-01",y0=0,y1=1,yref="paper",
        line=dict(color="gray",dash="dash",width=1.5))
    ffc.add_annotation(x="2025-01-01",y=0.97,yref="paper",text="Forecast start",
        showarrow=False,xanchor="left",font=dict(size=11,color="gray"),
        bgcolor="rgba(255,255,255,0.8)",borderpad=3)
    ffc.update_layout(title="Historical (1975-2024) + 10-Year Forecast (2025-2034)",
        xaxis_title="Date",yaxis_title="Temp (°C)",
        template="plotly_white",height=430,hovermode="x unified")
    st.plotly_chart(ffc,use_container_width=True)
    fc2=forecast.copy(); fc2["year"]=pd.to_datetime(fc2["date"]).dt.year
    afc=fc2.groupby("year").agg(avg=("forecast_c","mean"),lo=("lower_95","min"),hi=("upper_95","max")).round(2).reset_index()
    afc.columns=["Year","Avg Forecast °C","Lower 95%","Upper 95%"]
    st.markdown("#### Annual Summary"); st.dataframe(afc,use_container_width=True)

# ── TAB 5 — SEASONAL SHIFT ────────────────────────────────────────────────────
with t5:
    st.subheader("Seasonal Shift Analysis — Are seasons changing?")
    def season_onset(yr_df, thr, win=7):
        roll=yr_df["temperature_c"].rolling(win).mean()
        ab=roll[roll>=thr]
        return int(ab.index.min()) if len(ab)>0 else np.nan
    sm_s,mn_s=[],[]
    yrs_lst=sorted(df["year"].unique())
    for yr2 in yrs_lst:
        yd=df[df["year"]==yr2].set_index("day_of_year")
        sm_s.append(season_onset(yd,30))
        md=df[(df["year"]==yr2)&(df["month"].isin([5,6,7,8]))]
        hv=md[md["rainfall_mm"]>=5]
        mn_s.append(int(hv["day_of_year"].min()) if len(hv)>0 else np.nan)
    sdf=pd.DataFrame({"year":yrs_lst,"summer_start":sm_s,"monsoon_start":mn_s}).dropna()
    ss1,ss2=st.columns(2)
    with ss1:
        fss = go.Figure()
        fss.add_trace(go.Scatter(
            x=sdf["year"], y=sdf["summer_start"], mode="markers",
            name="Summer onset", marker=dict(color="#D85A30", size=7, opacity=0.8)))
        fss.add_trace(_ols_trace(sdf["year"], sdf["summer_start"],
            color="#7F1D1D", name="Trend"))
        fss.update_layout(
            title="Summer Onset — Day when temp crosses 30°C",
            xaxis_title="Year", yaxis_title="Day of Year",
            template="plotly_white", height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fss,use_container_width=True)
        e1=sdf[sdf["year"]<=1994]["summer_start"].mean()
        l1=sdf[sdf["year"]>=2005]["summer_start"].mean()
        st.info(f"Summer **{abs(e1-l1):.0f} days {'earlier' if e1>l1 else 'later'}** in 2005-2024 vs 1975-1994")
    with ss2:
        fms = go.Figure()
        fms.add_trace(go.Scatter(
            x=sdf["year"], y=sdf["monsoon_start"], mode="markers",
            name="Monsoon onset", marker=dict(color="#378ADD", size=7, opacity=0.8)))
        fms.add_trace(_ols_trace(sdf["year"], sdf["monsoon_start"],
            color="#1E3A5F", name="Trend"))
        fms.update_layout(
            title="Monsoon Onset — First day with rainfall ≥5mm",
            xaxis_title="Year", yaxis_title="Day of Year",
            template="plotly_white", height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fms,use_container_width=True)
        e2=sdf[sdf["year"]<=1994]["monsoon_start"].mean()
        l2=sdf[sdf["year"]>=2005]["monsoon_start"].mean()
        st.info(f"Monsoon **{abs(e2-l2):.0f} days {'earlier' if e2>l2 else 'later'}** in 2005-2024 vs 1975-1994")
    piv=df_f.groupby(["decade","season"])["temperature_c"].mean().unstack()
    if set(["Winter","Spring","Summer","Autumn"]).issubset(piv.columns):
        piv=piv[["Winter","Spring","Summer","Autumn"]]
    fhm=px.imshow(piv,text_auto=".1f",
        title="Mean Temp (°C) — Decade × Season",
        color_continuous_scale="RdYlGn_r",template="plotly_white")
    fhm.update_layout(height=300)
    st.plotly_chart(fhm,use_container_width=True)

# ── TAB 6 — EDA ───────────────────────────────────────────────────────────────
with t6:
    st.subheader("Interactive EDA Explorer")
    cx=st.selectbox("X",["temperature_c","rainfall_mm","humidity_pct","wind_speed_kmh"],0)
    cy=st.selectbox("Y",["rainfall_mm","temperature_c","humidity_pct","wind_speed_kmh"],0)
    cb2=st.selectbox("Color by",["season","decade","year"],0)
    smp=df_f.sample(min(3000,len(df_f)),random_state=42)
    fsc=px.scatter(smp,x=cx,y=cy,color=cb2,opacity=0.45,template="plotly_white",height=350)
    st.plotly_chart(fsc,use_container_width=True)
    e1,e2=st.columns(2)
    with e1:
        fbx=px.box(df_f,x="season",y="temperature_c",color="season",
            category_orders={"season":["Winter","Spring","Summer","Autumn"]},
            title="Temperature by Season",template="plotly_white",height=300)
        st.plotly_chart(fbx,use_container_width=True)
    with e2:
        mpp=df_f.groupby(["year","month"])["temperature_c"].mean().reset_index()
        fhm2=px.density_heatmap(mpp,x="month",y="year",z="temperature_c",
            histfunc="avg",title="Year × Month Heatmap",
            color_continuous_scale="RdYlGn_r",template="plotly_white",height=300)
        st.plotly_chart(fhm2,use_container_width=True)

# ── TAB 7 — INDIA LIVE WEATHER MAP ───────────────────────────────────────────
with t7:
    st.subheader("🗺️ Premium India Live Weather Map")
    st.caption("**90+ micro-locations** | Dark Mode | Density Heatmap | Real-time Open-Meteo data")

    # In-tab controls
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
    with ctrl1:
        map_color_by = st.selectbox(
            "🌡️ Color cities by",
            ["temperature_c", "feels_like_c", "rain_probability", "humidity_pct", "wind_kmh"],
            format_func=lambda x: {
                "temperature_c":    "🌡️ Temperature (°C)",
                "feels_like_c":     "💨 Feels Like (°C)",
                "rain_probability": "🌧️ Rain Probability (%)",
                "humidity_pct":     "💧 Humidity (%)",
                "wind_kmh":         "🌬️ Wind Speed (km/h)",
            }[x],
        )
    with ctrl2:
        show_density_tab = st.checkbox("Show density heatmap", value=True)
    with ctrl3:
        show_alerts_tab  = st.checkbox("Show rain rings", value=True)

    # Fetch live data
    with st.spinner("🔄 Fetching live weather for 90+ micro-locations..."):
        try:
            weather_df, fetched_at = load_live_weather()
            is_live = weather_df["data_source"].eq("live").any()
        except Exception as ex:
            st.error(f"❌ Weather API unavailable: {ex}")
            st.stop()

    if not is_live:
        st.warning(
            "⚠️ Could not reach Open-Meteo API — showing estimated data. "
            "Check your connection and click **🔄 Refresh Live Weather** in the sidebar."
        )
    else:
        st.success(
            f"✅ Live data fetched at **{fetched_at.strftime('%I:%M %p IST, %d %b %Y')}** "
            f"for **{len(weather_df)}** cities across India"
        )

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    stats = get_premium_stats(weather_df)
    kc1, kc2, kc3, kc4, kc5, kc6 = st.columns(6)
    kc1.metric("🌡️ Avg Temp",   f"{stats['avg_temp']}°C",
               delta=f"Feels {stats['avg_feels']}°C")
    kc2.metric("🔥 Hottest",    stats['hottest_city'],
               delta=f"{stats['hottest_temp']}°C", delta_color="inverse")
    kc3.metric("❄️ Coolest",    stats['coolest_city'],
               delta=f"{stats['coolest_temp']}°C")
    kc4.metric("🌧 Rain Risk",  f"{stats['cities_high_rain']}/{stats['total_cities']} cities",
               delta=f"Max {stats['max_rain_prob']}% @ {stats['rainiest_city']}")
    kc5.metric("💨 Windiest",   stats['windiest_city'],
               delta=f"{stats['max_wind']} km/h")
    kc6.metric("💧 Avg Humidity", f"{stats['avg_humidity']:.0f}%")

    st.divider()

    # ── Premium Map ────────────────────────────────────────────────────────────
    fig_map = build_premium_india_map(
        weather_df       = weather_df,
        fetched_at       = fetched_at,
        color_by         = map_color_by,
        show_heatmap     = show_density_tab,
        show_rain_alerts = show_alerts_tab,
    )
    st.plotly_chart(
        fig_map,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo":    False,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
            "scrollZoom": True,
        },
    )
    st.caption(
        "💡 **Tip:** Scroll/pinch to zoom · "
        "Hover over a dot for full weather details · "
        "Rings = cities with ≥40% rain probability"
    )

    # ── Data Table ────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 📊 Live Weather Data — All Locations")

    tf1, tf2, tf3 = st.columns(3)
    with tf1:
        state_filter = st.multiselect(
            "Filter by State",
            sorted(weather_df["state"].unique()),
            default=[], placeholder="All states shown",
        )
    with tf2:
        temp_range = st.slider("Temperature range (°C)", 0, 55, (5, 50))
    with tf3:
        rain_filter = st.selectbox("Rain probability", ["All", "≥50%", "≥70%", "No rain (<20%)"])

    tbl = weather_df.copy()
    if state_filter:
        tbl = tbl[tbl["state"].isin(state_filter)]
    tbl = tbl[
        (tbl["temperature_c"] >= temp_range[0]) &
        (tbl["temperature_c"] <= temp_range[1])
    ]
    if rain_filter == "≥50%":             tbl = tbl[tbl["rain_probability"] >= 50]
    elif rain_filter == "≥70%":           tbl = tbl[tbl["rain_probability"] >= 70]
    elif rain_filter == "No rain (<20%)": tbl = tbl[tbl["rain_probability"] < 20]
    tbl = tbl.sort_values("temperature_c", ascending=False)

    display_cols  = ["city", "state", "temperature_c", "feels_like_c",
                     "humidity_pct", "rain_probability", "wind_kmh",
                     "weather_desc", "precipitation_mm"]
    display_names = {
        "city":             "🏙️ City",
        "state":            "🌍 State",
        "temperature_c":    "🌡️ Temp (°C)",
        "feels_like_c":     "💨 Feels (°C)",
        "humidity_pct":     "💧 Humidity (%)",
        "rain_probability": "🌧 Rain Prob (%)",
        "wind_kmh":         "🌬 Wind (km/h)",
        "weather_desc":     "☁️ Conditions",
        "precipitation_mm": "Precip (mm)",
    }
    safe_cols = [c for c in display_cols if c in tbl.columns]
    st.dataframe(
        tbl[safe_cols].rename(columns=display_names).round(1).reset_index(drop=True),
        use_container_width=True,
        height=420,
        column_config={
            "🌧 Rain Prob (%)": st.column_config.ProgressColumn(
                "Rain Prob", format="%d%%", min_value=0, max_value=100, width="small"
            ),
        },
    )
    csv_live = tbl[safe_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Live Weather CSV", csv_live,
        f"india_weather_{fetched_at.strftime('%Y%m%d_%H%M')}.csv", "text/csv",
    )

    with st.expander("ℹ️ About the data source"):
        st.markdown("""
**Data source:** [Open-Meteo](https://open-meteo.com) — Free, open-source weather API  
**No API key required** · Updated hourly from NWP models (ICON, GFS, ERA5)

**Variables fetched:**
- `temperature_2m` — Air temperature at 2 m height (°C)
- `apparent_temperature` — Feels-like temperature (°C)
- `relative_humidity_2m` — Relative humidity at 2 m (%)
- `precipitation` — Current precipitation (mm/h)
- `precipitation_probability` — Max hourly rain probability for today (%)
- `wind_speed_10m` — Wind speed at 10 m height (km/h)
- `weather_code` — WMO weather interpretation code

**Refresh:** Cached for **10 minutes**. Use **🔄 Refresh Live Weather** in the sidebar to force update.  
**Coverage:** 90+ cities/towns across all Indian states and union territories.
        """)

    with st.expander("🎨 Map Legend & Features", expanded=False):
        st.markdown("""
**🌡️ Color Coding (default — Temperature):**
- **Deep blue → Blue**: Cold regions
- **Yellow → Orange**: Warm
- **Red → Dark Red**: Hot / Extreme heat

**🔥 Features:**
- **Density Heatmap**: Regional weather gradient overlay
- **Rain Alert Rings**: Cities with ≥40% rain probability
- **Scroll/Pinch Zoom**: Zoom into any state or district
- **Hover Details**: Full weather card per city

**📡 Data:** Open-Meteo (GFS + ICON) · Refreshes every 10 min via cache
        """)

# ── TAB 8 — REPORT ────────────────────────────────────────────────────────────
with t8:
    st.subheader("Data & Report")
    avail_cols = [c for c in ["temperature_c","temp_max_c","temp_min_c",
        "rainfall_mm","humidity_pct","wind_speed_kmh"] if c in df_f.columns]
    st.dataframe(df_f.head(50),use_container_width=True)
    st.dataframe(df_f[avail_cols].describe().round(2),use_container_width=True)
    rp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"reports","climate_insights.md")
    if os.path.exists(rp):
        with open(rp) as f: st.markdown(f.read())
    csv=df_f.to_csv(index=False).encode("utf-8")
    st.download_button("Download Filtered CSV",csv,"kolkata_climate.csv","text/csv")