import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

def detect_anomalies(df):
    print("\n[ANOMALY DETECTION] Starting...")
    os.makedirs("outputs/anomalies", exist_ok=True)

    anomalies = df[df["is_anomaly"] == 1].copy()
    anomalies["anomaly_type"] = np.where(
        anomalies["temp_zscore"] > 0, "Extreme Heat", "Extreme Cold"
    )

    Q1  = df["temperature_c"].quantile(0.25)
    Q3  = df["temperature_c"].quantile(0.75)
    IQR = Q3 - Q1
    iqr_anomalies = df[
        (df["temperature_c"] < Q1 - 2.5 * IQR) |
        (df["temperature_c"] > Q3 + 2.5 * IQR)
    ]

    n_heat = (anomalies["anomaly_type"] == "Extreme Heat").sum()
    n_cold = (anomalies["anomaly_type"] == "Extreme Cold").sum()

    print(f"\n  --- Z-Score Method (threshold |z| >= 2.5) ---")
    print(f"  Total anomalies     : {len(anomalies)}")
    print(f"  Extreme heat events : {n_heat}")
    print(f"  Extreme cold events : {n_cold}")
    print(f"\n  --- IQR Method (2.5 x IQR) ---")
    print(f"  IQR anomalies found : {len(iqr_anomalies)}")
    print(f"  Q1={Q1:.2f}C  Q3={Q3:.2f}C  IQR={IQR:.2f}C")

    top_heat = anomalies.nlargest(5, "temperature_c")[
        ["date","year","month","temperature_c","temp_zscore","anomaly_type"]
    ]
    top_cold = anomalies.nsmallest(5, "temperature_c")[
        ["date","year","month","temperature_c","temp_zscore","anomaly_type"]
    ]
    top10 = pd.concat([top_heat, top_cold]).reset_index(drop=True)
    print("\n  Top anomaly events:")
    print(top10.to_string(index=False))

    report_cols = ["date","year","month","temperature_c","temp_zscore",
                   "rainfall_mm","humidity_pct","anomaly_type"]
    anomalies[report_cols].sort_values("temp_zscore", ascending=False)\
        .to_csv("outputs/anomalies/anomaly_report.csv", index=False)
    print(f"\n  Saved: outputs/anomalies/anomaly_report.csv")

    # Timeline plot
    fig, axes = plt.subplots(2, 1, figsize=(15, 9))
    fig.suptitle("Climate Anomaly Detection — 50-Year Timeline (1975-2024)",
                 fontsize=14, fontweight="bold")

    ax = axes[0]
    ax.plot(df["date"], df["temp_30day"],
            color="#378ADD", linewidth=0.7, alpha=0.8, label="30-day rolling mean")
    heat = anomalies[anomalies["anomaly_type"] == "Extreme Heat"]
    cold = anomalies[anomalies["anomaly_type"] == "Extreme Cold"]
    ax.scatter(heat["date"], heat["temperature_c"],
               color="#D85A30", s=60, zorder=5, label=f"Extreme Heat ({len(heat)})")
    ax.scatter(cold["date"], cold["temperature_c"],
               color="#534AB7", s=60, zorder=5, label=f"Extreme Cold ({len(cold)})")
    ax.set_ylabel("Temperature (C)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    ax.set_title("Temperature Timeline with Anomaly Events", fontweight="bold")

    ax = axes[1]
    colors_z = np.where(df["temp_zscore"] > 0, "#D85A30", "#534AB7")
    ax.bar(df["date"], df["temp_zscore"], color=colors_z, alpha=0.3, linewidth=0, width=1)
    ax.axhline(y=2.5,  color="#D85A30", linestyle="--", linewidth=1.5, label="+2.5 sigma threshold")
    ax.axhline(y=-2.5, color="#534AB7", linestyle="--", linewidth=1.5, label="-2.5 sigma threshold")
    ax.axhline(y=0,    color="black",   linestyle="-",  linewidth=0.5)
    ax.set_ylabel("Z-Score"); ax.set_xlabel("Date")
    ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
    ax.set_title("Temperature Z-Score — Anomaly Zones", fontweight="bold")

    plt.tight_layout()
    plt.savefig("outputs/anomalies/anomaly_detection_timeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: outputs/anomalies/anomaly_detection_timeline.png")

    # Monthly frequency
    fig, ax = plt.subplots(figsize=(10, 4))
    month_counts = anomalies["month"].value_counts().sort_index()
    month_names  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    labels = [month_names[m-1] for m in month_counts.index]
    ax.bar(labels, month_counts.values, color="#7F77DD", alpha=0.85, edgecolor="white")
    ax.set_title("Anomaly Frequency by Month", fontsize=12, fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Anomaly Count")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/anomalies/anomaly_frequency_month.png", dpi=150)
    plt.close()
    print("  Saved: outputs/anomalies/anomaly_frequency_month.png")
    print("[ANOMALY DETECTION] Done.\n")
    return anomalies

if __name__ == "__main__":
    df = pd.read_csv("data/processed/climate_featured.csv", parse_dates=["date"])
    detect_anomalies(df)
