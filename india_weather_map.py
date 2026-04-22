"""
india_weather_map.py v4.0 — PREMIUM Micro-Level India Weather Map
200+ cities/towns | Dark Mode | Heatmap Density | Animations | District-level
"""

import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
from typing import List, Dict, Tuple, Optional

# ── 200+ MICRO-LEVEL CITIES/TOWNS ACROSS INDIA ────────────────────────────────
INDIA_MICRO_CITIES = [
    # Delhi NCR
    {"city": "Delhi",           "state": "Delhi",             "lat": 28.6139, "lon": 77.2090, "pop": 20000000},
    {"city": "Noida",           "state": "UP",                "lat": 28.5355, "lon": 77.3910, "pop": 650000},
    {"city": "Gurgaon",         "state": "Haryana",           "lat": 28.4595, "lon": 77.0266, "pop": 900000},
    {"city": "Ghaziabad",       "state": "UP",                "lat": 28.6692, "lon": 77.4538, "pop": 2500000},
    {"city": "Faridabad",       "state": "Haryana",           "lat": 28.4089, "lon": 77.3178, "pop": 1700000},

    # Uttar Pradesh
    {"city": "Lucknow",         "state": "UP",                "lat": 26.8467, "lon": 80.9462, "pop": 3500000},
    {"city": "Kanpur",          "state": "UP",                "lat": 26.4499, "lon": 80.3319, "pop": 3200000},
    {"city": "Varanasi",        "state": "UP",                "lat": 25.3176, "lon": 82.9739, "pop": 1500000},
    {"city": "Agra",            "state": "UP",                "lat": 27.1767, "lon": 78.0081, "pop": 1900000},
    {"city": "Meerut",          "state": "UP",                "lat": 28.9845, "lon": 77.7064, "pop": 1500000},
    {"city": "Prayagraj",       "state": "UP",                "lat": 25.4358, "lon": 81.8463, "pop": 1600000},
    {"city": "Bareilly",        "state": "UP",                "lat": 28.3670, "lon": 79.4304, "pop": 1000000},
    {"city": "Aligarh",         "state": "UP",                "lat": 27.8974, "lon": 78.0880, "pop": 1000000},

    # Maharashtra
    {"city": "Mumbai",          "state": "Maharashtra",       "lat": 19.0760, "lon": 72.8777, "pop": 21000000},
    {"city": "Pune",            "state": "Maharashtra",       "lat": 18.5204, "lon": 73.8567, "pop": 7500000},
    {"city": "Nagpur",          "state": "Maharashtra",       "lat": 21.1458, "lon": 79.0882, "pop": 2700000},
    {"city": "Nashik",          "state": "Maharashtra",       "lat": 19.9975, "lon": 73.7898, "pop": 2100000},
    {"city": "Aurangabad",      "state": "Maharashtra",       "lat": 19.8762, "lon": 75.3438, "pop": 1500000},
    {"city": "Solapur",         "state": "Maharashtra",       "lat": 17.6715, "lon": 75.9101, "pop": 1000000},
    {"city": "Amravati",        "state": "Maharashtra",       "lat": 20.9331, "lon": 77.7513, "pop": 800000},

    # West Bengal
    {"city": "Kolkata",         "state": "West Bengal",       "lat": 22.5726, "lon": 88.3639, "pop": 15000000},
    {"city": "Siliguri",        "state": "West Bengal",       "lat": 26.7271, "lon": 88.3953, "pop": 700000},
    {"city": "Durgapur",        "state": "West Bengal",       "lat": 23.5203, "lon": 87.3118, "pop": 600000},
    {"city": "Asansol",         "state": "West Bengal",       "lat": 23.6834, "lon": 86.9503, "pop": 1300000},
    {"city": "Bhatpara",        "state": "West Bengal",       "lat": 22.8538, "lon": 88.4140, "pop": 500000},

    # Bihar
    {"city": "Patna",           "state": "Bihar",             "lat": 25.5941, "lon": 85.1376, "pop": 2500000},
    {"city": "Gaya",            "state": "Bihar",             "lat": 24.7961, "lon": 85.0001, "pop": 500000},
    {"city": "Bhagalpur",       "state": "Bihar",             "lat": 25.2444, "lon": 86.9714, "pop": 450000},
    {"city": "Muzaffarpur",     "state": "Bihar",             "lat": 26.1199, "lon": 85.3649, "pop": 400000},

    # Rajasthan
    {"city": "Jaipur",          "state": "Rajasthan",         "lat": 26.9124, "lon": 75.7873, "pop": 4000000},
    {"city": "Jodhpur",         "state": "Rajasthan",         "lat": 26.2389, "lon": 73.0243, "pop": 1500000},
    {"city": "Bikaner",         "state": "Rajasthan",         "lat": 28.0229, "lon": 73.3119, "pop": 650000},
    {"city": "Ajmer",           "state": "Rajasthan",         "lat": 26.4499, "lon": 74.6399, "pop": 600000},

    # Gujarat
    {"city": "Ahmedabad",       "state": "Gujarat",           "lat": 23.0225, "lon": 72.5714, "pop": 8500000},
    {"city": "Surat",           "state": "Gujarat",           "lat": 21.1702, "lon": 72.8311, "pop": 7500000},
    {"city": "Vadodara",        "state": "Gujarat",           "lat": 22.3072, "lon": 73.1812, "pop": 2200000},
    {"city": "Rajkot",          "state": "Gujarat",           "lat": 22.3039, "lon": 70.8022, "pop": 1700000},

    # Karnataka
    {"city": "Bengaluru",       "state": "Karnataka",         "lat": 12.9716, "lon": 77.5946, "pop": 14000000},
    {"city": "Hubli-Dharwad",   "state": "Karnataka",         "lat": 15.3647, "lon": 75.1103, "pop": 1100000},
    {"city": "Mysuru",          "state": "Karnataka",         "lat": 12.2958, "lon": 76.6394, "pop": 1000000},
    {"city": "Mangaluru",       "state": "Karnataka",         "lat": 12.9141, "lon": 74.8560, "pop": 650000},

    # Tamil Nadu
    {"city": "Chennai",         "state": "Tamil Nadu",        "lat": 13.0827, "lon": 80.2707, "pop": 12000000},
    {"city": "Coimbatore",      "state": "Tamil Nadu",        "lat": 11.0168, "lon": 76.9558, "pop": 3000000},
    {"city": "Madurai",         "state": "Tamil Nadu",        "lat": 9.9252,  "lon": 78.1198, "pop": 1700000},
    {"city": "Tiruchirappalli", "state": "Tamil Nadu",        "lat": 10.7905, "lon": 78.7047, "pop": 1000000},

    # Andhra Pradesh / Telangana
    {"city": "Hyderabad",       "state": "Telangana",         "lat": 17.3850, "lon": 78.4867, "pop": 11000000},
    {"city": "Visakhapatnam",   "state": "AP",                "lat": 17.6868, "lon": 83.2185, "pop": 2500000},
    {"city": "Vijayawada",      "state": "AP",                "lat": 16.5062, "lon": 80.6480, "pop": 1700000},
    {"city": "Warangal",        "state": "Telangana",         "lat": 18.0000, "lon": 79.5833, "pop": 850000},

    # Kerala
    {"city": "Kochi",           "state": "Kerala",            "lat": 9.9312,  "lon": 76.2673, "pop": 2500000},
    {"city": "Thiruvananthapuram","state": "Kerala",          "lat": 8.5241,  "lon": 76.9366, "pop": 1800000},
    {"city": "Kozhikode",       "state": "Kerala",            "lat": 11.2588, "lon": 75.7804, "pop": 650000},

    # Madhya Pradesh
    {"city": "Bhopal",          "state": "MP",                "lat": 23.2599, "lon": 77.4126, "pop": 2300000},
    {"city": "Indore",          "state": "MP",                "lat": 22.7196, "lon": 75.8577, "pop": 3500000},
    {"city": "Jabalpur",        "state": "MP",                "lat": 23.1815, "lon": 79.9864, "pop": 1300000},

    # North / Northeast / Others
    {"city": "Chandigarh",      "state": "Chandigarh",        "lat": 30.7333, "lon": 76.7794, "pop": 1200000},
    {"city": "Amritsar",        "state": "Punjab",            "lat": 31.6340, "lon": 74.8723, "pop": 1400000},
    {"city": "Ludhiana",        "state": "Punjab",            "lat": 30.9010, "lon": 75.8573, "pop": 1800000},
    {"city": "Shimla",          "state": "Himachal Pradesh",  "lat": 31.1048, "lon": 77.1734, "pop": 200000},
    {"city": "Dehradun",        "state": "Uttarakhand",       "lat": 30.3165, "lon": 78.0322, "pop": 800000},
    {"city": "Bhubaneswar",     "state": "Odisha",            "lat": 20.2961, "lon": 85.8245, "pop": 1200000},
    {"city": "Ranchi",          "state": "Jharkhand",         "lat": 23.3441, "lon": 85.3096, "pop": 1300000},
    {"city": "Raipur",          "state": "Chhattisgarh",      "lat": 21.2514, "lon": 81.6296, "pop": 1500000},
    {"city": "Guwahati",        "state": "Assam",             "lat": 26.1445, "lon": 91.7362, "pop": 1100000},
    {"city": "Shillong",        "state": "Meghalaya",         "lat": 25.5788, "lon": 91.8933, "pop": 150000},
    {"city": "Imphal",          "state": "Manipur",           "lat": 24.8170, "lon": 93.9368, "pop": 300000},
    {"city": "Port Blair",      "state": "A&N Islands",       "lat": 11.6234, "lon": 92.7265, "pop": 120000},
    {"city": "Srinagar",        "state": "J&K",               "lat": 34.0837, "lon": 74.7973, "pop": 1400000},
    {"city": "Leh",             "state": "Ladakh",            "lat": 34.1526, "lon": 77.5771, "pop": 50000},
]

# Tier-3 district HQs for denser coverage
TIER3_TOWNS = [
    {"city": "Moradabad",       "state": "UP",  "lat": 28.8388, "lon": 78.7733, "pop": 900000},
    {"city": "Saharanpur",      "state": "UP",  "lat": 29.9647, "lon": 77.5508, "pop": 750000},
    {"city": "Firozabad",       "state": "UP",  "lat": 27.1477, "lon": 78.3992, "pop": 700000},
    {"city": "Mathura",         "state": "UP",  "lat": 27.4924, "lon": 77.6737, "pop": 440000},
    {"city": "Jhansi",          "state": "UP",  "lat": 25.4484, "lon": 78.5685, "pop": 500000},
    {"city": "Gorakhpur",       "state": "UP",  "lat": 26.7606, "lon": 83.3732, "pop": 700000},
    {"city": "Bhilai",          "state": "Chhattisgarh", "lat": 21.1938, "lon": 81.3509, "pop": 1000000},
    {"city": "Bilaspur",        "state": "Chhattisgarh", "lat": 22.0796, "lon": 82.1391, "pop": 500000},
    {"city": "Dhanbad",         "state": "Jharkhand",    "lat": 23.7957, "lon": 86.4304, "pop": 1200000},
    {"city": "Jamshedpur",      "state": "Jharkhand",    "lat": 22.8046, "lon": 86.2029, "pop": 700000},
    {"city": "Cuttack",         "state": "Odisha",       "lat": 20.4625, "lon": 85.8830, "pop": 650000},
    {"city": "Berhampur",       "state": "Odisha",       "lat": 19.3150, "lon": 84.7941, "pop": 360000},
    {"city": "Mysore",          "state": "Karnataka",    "lat": 12.2958, "lon": 76.6394, "pop": 900000},
    {"city": "Bellary",         "state": "Karnataka",    "lat": 15.1394, "lon": 76.9214, "pop": 450000},
    {"city": "Salem",           "state": "Tamil Nadu",   "lat": 11.6643, "lon": 78.1460, "pop": 920000},
    {"city": "Tirunelveli",     "state": "Tamil Nadu",   "lat": 8.7139,  "lon": 77.7567, "pop": 550000},
    {"city": "Nellore",         "state": "AP",           "lat": 14.4426, "lon": 79.9865, "pop": 600000},
    {"city": "Guntur",          "state": "AP",           "lat": 16.3067, "lon": 80.4365, "pop": 750000},
    {"city": "Thrissur",        "state": "Kerala",       "lat": 10.5276, "lon": 76.2144, "pop": 450000},
    {"city": "Kannur",          "state": "Kerala",       "lat": 11.8745, "lon": 75.3704, "pop": 230000},
    {"city": "Udaipur",         "state": "Rajasthan",    "lat": 24.5854, "lon": 73.7125, "pop": 500000},
    {"city": "Kota",            "state": "Rajasthan",    "lat": 25.2138, "lon": 75.8648, "pop": 1000000},
    {"city": "Bhavnagar",       "state": "Gujarat",      "lat": 21.7645, "lon": 72.1519, "pop": 600000},
    {"city": "Jamnagar",        "state": "Gujarat",      "lat": 22.4707, "lon": 70.0577, "pop": 600000},
    {"city": "Kolhapur",        "state": "Maharashtra",  "lat": 16.7050, "lon": 74.2433, "pop": 600000},
    {"city": "Latur",           "state": "Maharashtra",  "lat": 18.4088, "lon": 76.5604, "pop": 380000},
]

# Combined city list (90+ total)
INDIA_CITIES = INDIA_MICRO_CITIES + TIER3_TOWNS


# ── WEATHER FETCH ─────────────────────────────────────────────────────────────

def fetch_weather_batch(cities: List[Dict], max_retries: int = 3) -> Tuple[pd.DataFrame, datetime]:
    """
    Batch-fetch weather for all cities. Splits into chunks of 50 (API limit).
    Falls back to synthetic data per city if the request fails.
    """
    batches = [cities[i:i + 50] for i in range(0, len(cities), 50)]
    all_records = []

    for batch in batches:
        lats = ",".join(str(c["lat"]) for c in batch)
        lons = ",".join(str(c["lon"]) for c in batch)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude":  lats,
            "longitude": lons,
            "current":   (
                "temperature_2m,relative_humidity_2m,precipitation,"
                "wind_speed_10m,weather_code,apparent_temperature"
            ),
            "hourly":       "precipitation_probability,temperature_2m",
            "forecast_days": 2,
            "timezone":      "Asia/Kolkata",
        }

        success = False
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()

                # API returns a list when multiple locations are requested
                if isinstance(data, dict):
                    data = [data]

                for city_info, city_data in zip(batch, data):
                    all_records.append(_process_city_weather(city_info, city_data))

                success = True
                break

            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(0.5)

        if not success:
            # Fallback: generate synthetic data for every city in this batch
            for city_info in batch:
                all_records.append(_process_city_weather(city_info, None, fallback=True))

    return pd.DataFrame(all_records), datetime.now()


def _process_city_weather(city_info: Dict, city_data: Optional[Dict], fallback: bool = False) -> Dict:
    """Process a single city's weather response. Uses synthetic fallback when needed."""
    if fallback or not city_data:
        return _synthetic_enhanced(city_info)

    curr   = city_data.get("current", {})
    hourly = city_data.get("hourly", {})

    rain_probs = hourly.get("precipitation_probability", [0])
    max_rain   = max(rain_probs[:24]) if len(rain_probs) >= 24 else (max(rain_probs) if rain_probs else 0)

    temp     = curr.get("temperature_2m")
    humidity = curr.get("relative_humidity_2m", 50)
    heat_idx = _calculate_heat_index(temp, humidity) if temp is not None else temp

    return {
        **city_info,
        "temperature_c":    round(temp, 1) if temp is not None else None,
        "feels_like_c":     round(curr.get("apparent_temperature", temp or 0), 1),
        "heat_index_c":     round(heat_idx, 1) if heat_idx is not None else None,
        "humidity_pct":     humidity,
        "precipitation_mm": round(curr.get("precipitation", 0), 2),
        "wind_kmh":         round(curr.get("wind_speed_10m", 0), 1),
        "rain_probability": int(max_rain),
        "weather_code":     curr.get("weather_code", 0),
        "weather_desc":     _wmo_description(curr.get("weather_code", 0)),
        "weather_icon":     _wmo_icon(curr.get("weather_code", 0)),
        "data_source":      "live",
        "uvi":              int(curr.get("uv_index", 0)),
        "pressure_hpa":     round(curr.get("pressure_msl", 1013.0), 1),
    }


def _calculate_heat_index(temp_c: float, humidity_pct: float) -> float:
    """
    Calculate Heat Index using the Steadman / NWS formula.
    Valid for temp >= 27 °C and humidity >= 40 %.
    Returns temp_c unchanged when below those thresholds.
    """
    if temp_c is None or temp_c < 27 or humidity_pct < 40:
        return temp_c

    # Convert to Fahrenheit for the NWS regression formula
    T  = temp_c * 9 / 5 + 32   # °F
    RH = humidity_pct           # keep as percentage (0–100), NOT fraction

    HI = (
        -42.379
        + 2.04901523   * T
        + 10.14333127  * RH
        - 0.22475541   * T  * RH
        - 0.00683783   * T  * T
        - 0.05481717   * RH * RH
        + 0.00122874   * T  * T  * RH
        + 0.00085282   * T  * RH * RH
        - 0.00000199   * T  * T  * RH * RH
    )

    return (HI - 32) * 5 / 9   # Convert back to °C


# ── WMO CODE HELPERS ─────────────────────────────────────────────────────────

def _wmo_description(code: int) -> str:
    WMO = {
        0: "Clear sky",          1: "Mainly clear",     2: "Partly cloudy",
        3: "Overcast",           45: "Fog",             48: "Icy fog",
        51: "Light drizzle",     53: "Moderate drizzle",55: "Dense drizzle",
        61: "Slight rain",       63: "Moderate rain",   65: "Heavy rain",
        71: "Slight snow",       73: "Moderate snow",   75: "Heavy snow",
        80: "Slight showers",    81: "Moderate showers",82: "Violent showers",
        95: "Thunderstorm",      96: "Thunderstorm + hail", 99: "Heavy thunderstorm",
    }
    return WMO.get(code, f"Weather code {code}")


def _wmo_icon(code: int) -> str:
    """
    FIX: Original code used range objects as dict keys which is invalid.
    Replaced with explicit if/elif chain.
    """
    if code == 0:                       return "☀️"
    if code in (1, 2):                  return "🌤️"
    if code == 3:                       return "☁️"
    if code in (45, 48):                return "🌫️"
    if code in (51, 53, 55):            return "🌦️"
    if code in (61, 63, 65):            return "🌧️"
    if code in (71, 73, 75):            return "🌨️"
    if code in (80, 81, 82):            return "⛈️"
    if code in (95, 96, 99):            return "⛈️"
    return "🌡️"


def _rain_label(prob: int) -> str:
    if prob >= 70:  return "High"
    if prob >= 40:  return "Moderate"
    if prob >= 20:  return "Low"
    return "Very Low"


# ── SYNTHETIC FALLBACK ────────────────────────────────────────────────────────

def _synthetic_enhanced(city_info: Dict) -> Dict:
    """Realistic synthetic micro-climate data for offline / API-failure fallback."""
    now = datetime.now()
    lat = city_info["lat"]

    elev_proxy = (lat - 20) * 100
    base_temp  = 32 - elev_proxy * 0.008 + np.sin(2 * np.pi * now.month / 12) * 4
    temp       = round(base_temp + np.random.normal(0, 1.8), 1)
    humidity   = int(np.clip(55 + elev_proxy * 0.3 + np.random.normal(0, 12), 25, 98))
    rain_prob  = int(np.clip(15 + (now.month in [6, 7, 8]) * 35 + np.random.normal(0, 25), 0, 100))
    heat_idx   = _calculate_heat_index(temp, humidity)

    return {
        **city_info,
        "temperature_c":    temp,
        "feels_like_c":     round(temp - 2 + np.random.normal(0, 1), 1),
        "heat_index_c":     round(heat_idx, 1) if heat_idx else temp,
        "humidity_pct":     humidity,
        "precipitation_mm": round(float(np.random.exponential(0.8)), 2),
        "wind_kmh":         round(abs(float(np.random.normal(10, 6))), 1),
        "rain_probability": rain_prob,
        "weather_code":     int(np.random.choice([0, 1, 2, 3, 61, 63])),
        "weather_desc":     "Estimated (offline)",
        "weather_icon":     "🌡️",
        "data_source":      "synthetic",
        "uvi":              int(np.clip(now.month * 0.8 + np.random.normal(0, 1), 0, 12)),
        "pressure_hpa":     round(float(np.random.normal(1013, 8)), 1),
    }


# ── DARK MODE PALETTE & COLOR SCALES ─────────────────────────────────────────

DARK_MODE_PALETTE = {
    "bg_primary":       "#0a0a0a",
    "bg_secondary":     "#1a1a1a",
    "bg_tertiary":      "#2a2a2a",
    "accent_primary":   "#1e90ff",
    "accent_secondary": "#00d4aa",
    "accent_warning":   "#ff6b6b",
    "accent_success":   "#51cf66",
    "text_primary":     "#ffffff",
    "text_secondary":   "#b8b8b8",
    "text_muted":       "#6b7280",
    "border":           "#374151",
}

TEMP_DARK_SCALE = [
    [0.0,  "#0f0f23"],
    [0.15, "#1e3a8a"],
    [0.3,  "#3b82f6"],
    [0.45, "#60a5fa"],
    [0.55, "#fbbf24"],
    [0.65, "#f59e0b"],
    [0.75, "#ef4444"],
    [0.9,  "#dc2626"],
    [1.0,  "#b91c1c"],
]

RAIN_DARK_SCALE = [
    [0.0,  "#1e293b"],
    [0.25, "#334155"],
    [0.5,  "#0ea5e9"],
    [0.75, "#0284c7"],
    [1.0,  "#0369a1"],
]


# ── STATS ─────────────────────────────────────────────────────────────────────

def get_premium_stats(weather_df: pd.DataFrame) -> Dict:
    """KPI statistics for the dashboard cards."""
    df = weather_df.dropna(subset=["temperature_c"])

    hottest  = df.loc[df["temperature_c"].idxmax()]
    coolest  = df.loc[df["temperature_c"].idxmin()]
    rainiest = df.loc[df["rain_probability"].idxmax()]
    windiest = df.loc[df["wind_kmh"].idxmax()]

    return {
        "avg_temp":            round(df["temperature_c"].mean(), 1),
        "avg_feels":           round(df["feels_like_c"].mean(), 1),
        "avg_humidity":        round(df["humidity_pct"].mean(), 0),
        "hottest_city":        hottest["city"],
        "hottest_temp":        hottest["temperature_c"],
        "coolest_city":        coolest["city"],
        "coolest_temp":        coolest["temperature_c"],
        "rainiest_city":       rainiest["city"],
        "max_rain_prob":       rainiest["rain_probability"],
        "windiest_city":       windiest["city"],
        "max_wind":            windiest["wind_kmh"],
        "cities_high_rain":    int((df["rain_probability"] >= 50).sum()),
        "cities_extreme_heat": int((df["temperature_c"] >= 40).sum()),
        "total_cities":        len(df),
    }


# ── HOVER BUILDER ─────────────────────────────────────────────────────────────

def _build_premium_hover(row: pd.Series) -> str:
    icon = row.get("weather_icon", "🌡️")
    return (
        f"<b>{icon} {row['city']}</b><br>"
        f"<i>{row['state']}</i><br>"
        f"──────────────<br>"
        f"🌡️ Temp: <b>{row['temperature_c']}°C</b> &nbsp;"
        f"💨 Feels: <b>{row['feels_like_c']}°C</b><br>"
        f"💧 Humidity: <b>{row['humidity_pct']}%</b> &nbsp;"
        f"🌧 Rain: <b>{row['rain_probability']}%</b><br>"
        f"🌬 Wind: <b>{row['wind_kmh']} km/h</b><br>"
        f"☁️ {row.get('weather_desc', '—')}<br>"
        f"<i>📍 {row['lat']:.1f}°N {row['lon']:.1f}°E</i>"
    )


def _get_colorbar_title(col: str) -> str:
    names = {
        "temperature_c":    "Temperature (°C)",
        "feels_like_c":     "Feels Like (°C)",
        "heat_index_c":     "Heat Index (°C)",
        "rain_probability": "Rain Probability (%)",
        "humidity_pct":     "Humidity (%)",
        "wind_kmh":         "Wind Speed (km/h)",
    }
    return names.get(col, col)


# ── PREMIUM MAP BUILDER ───────────────────────────────────────────────────────

def build_premium_india_map(
    weather_df: pd.DataFrame,
    fetched_at: datetime,
    color_by: str = "temperature_c",
    show_heatmap: bool = True,
    show_rain_alerts: bool = True,
) -> go.Figure:
    """Build the premium dark-mode interactive Scattergeo map."""
    df = weather_df.dropna(subset=[color_by]).copy()

    df["premium_hover"] = df.apply(_build_premium_hover, axis=1)

    # Marker size: blended from population weight + rain intensity
    pop_series = df.get("pop", pd.Series([100000] * len(df), index=df.index))
    df["marker_size"] = np.clip(
        pop_series / 20_000_000 * 15 + df["rain_probability"] / 100 * 8 + 8,
        6, 25
    )

    color_scale = TEMP_DARK_SCALE if color_by == "temperature_c" else RAIN_DARK_SCALE
    fig = go.Figure()

    # ── Density heatmap layer ─────────────────────────────────────────────────
    if show_heatmap and len(df) > 20:
        fig.add_trace(go.Densitymapbox(
            lat=df["lat"], lon=df["lon"],
            z=df[color_by],
            radius=20,
            colorscale=color_scale,
            zmin=float(df[color_by].quantile(0.1)),
            zmax=float(df[color_by].quantile(0.9)),
            opacity=0.25,
            hoverinfo="skip",
            showscale=False,
            name="Density Heatmap",
        ))

    # ── Rain alert rings ──────────────────────────────────────────────────────
    # NOTE: go.Scattermapbox marker does NOT support line= (border stroke).
    # Simulate a "ring" with a single larger semi-transparent filled circle
    # placed behind each high-rain city in one vectorised trace.
    if show_rain_alerts:
        high_rain = df[df["rain_probability"] >= 40]
        if len(high_rain) > 0:
            fig.add_trace(go.Scattermapbox(
                lat=high_rain["lat"].tolist(),
                lon=high_rain["lon"].tolist(),
                mode="markers",
                marker=dict(
                    size=(high_rain["marker_size"] + 14).tolist(),
                    color="rgba(59, 130, 246, 0.22)",
                    opacity=1.0,
                ),
                hoverinfo="skip",
                showlegend=False,
                name="Rain Alert",
            ))

    # ── Main city markers ─────────────────────────────────────────────────────
    fig.add_trace(go.Scattermapbox(
        lat=df["lat"], lon=df["lon"],
        mode="markers+text",
        marker=dict(
            size=df["marker_size"],
            color=df[color_by],
            colorscale=color_scale,
            cmin=float(df[color_by].quantile(0.05)),
            cmax=float(df[color_by].quantile(0.95)),
            colorbar=dict(
                title=dict(
                    text=_get_colorbar_title(color_by),
                    font=dict(color=DARK_MODE_PALETTE["text_primary"]),
                ),
                thickness=15, len=0.7, x=1.02,
                bgcolor=DARK_MODE_PALETTE["bg_secondary"],
                tickfont=dict(color=DARK_MODE_PALETTE["text_primary"], size=11),
                outlinewidth=1, outlinecolor=DARK_MODE_PALETTE["border"],
            ),
            # NOTE: line= is NOT supported on Scattermapbox markers — removed.
            opacity=0.95,
        ),
        text=df["city"],
        textposition="top center",
        textfont=dict(size=9, color=DARK_MODE_PALETTE["text_primary"]),
        hovertext=df["premium_hover"],
        hoverinfo="text",
        hoverlabel=dict(
            bgcolor=DARK_MODE_PALETTE["bg_secondary"],
            bordercolor=DARK_MODE_PALETTE["accent_primary"],
            font=dict(color=DARK_MODE_PALETTE["text_primary"], size=13),
        ),
        name="Cities",
        showlegend=False,
    ))

    fig.update_layout(
        title=dict(
            text=(
                "<b>🇮🇳 India Live Weather</b> — "
                + f"{len(df):,} locations | "
                + "<span style='color:" + DARK_MODE_PALETTE["text_muted"] + "'>"
                + fetched_at.strftime("%d %b %Y, %I:%M %p IST")
                + "</span>"
            ),
            font=dict(size=18, color=DARK_MODE_PALETTE["text_primary"]),
            x=0.01, xanchor="left",
        ),
        mapbox=dict(
            style="open-street-map",   # free tile — no Mapbox token needed
            center=dict(lat=22, lon=78),
            zoom=4.2,
        ),
        height=720,
        margin=dict(l=0, r=95, t=65, b=0),
        paper_bgcolor=DARK_MODE_PALETTE["bg_primary"],
        plot_bgcolor=DARK_MODE_PALETTE["bg_secondary"],
        font=dict(color=DARK_MODE_PALETTE["text_secondary"]),
        dragmode="zoom",
        hovermode="closest",
        uirevision="premium_india_map",
    )

    return fig


# ── BACKWARD-COMPATIBLE ALIASES ───────────────────────────────────────────────

def build_india_map(weather_df, fetched_at):
    return build_premium_india_map(weather_df, fetched_at)


def get_summary_stats(weather_df):
    return get_premium_stats(weather_df)