
import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

@st.cache_data(ttl=600)
def get_hourly_temperature(lat, lon):
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "forecast_days": 2,
            "timezone": "auto",
        },
        timeout=10,
    )
    resp.raise_for_status()
    hourly = resp.json()["hourly"]
    df = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "Temperature (°C)": hourly["temperature_2m"],
    })
    return df.set_index("time")

st.set_page_config(
    page_title="Interactive Weather Dashboard",
    layout="centered"
)

st.title("🌤️ Interactive Weather Dashboard")
st.caption("Arts and Advanced Big Data | Open API")

st.subheader("1. Pick a place (click the map)")
fmap = folium.Map(
    location=[36.5, 127.5],
    zoom_start=6
)
result = st_folium(fmap, height=380, width=700)

clicked = (result or {}).get("last_clicked")

if not clicked:
    st.info("Click anywhere on the map to see the weather.")
    st.stop()

lat = round(clicked["lat"], 3)
lon = round(clicked["lng"], 3)

st.subheader(f"2. Weather at ({lat}, {lon})")

try:
    df = get_hourly_temperature(lat, lon)
except (requests.RequestException, KeyError, ValueError):
    st.error("Could not load weather data. Please try again.")
    st.stop()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Now (first hour)",
    f"{df.iloc[0, 0]:.1f} °C"
)
col2.metric(
    "Highest",
    f"{df.iloc[:, 0].max():.1f} °C"
)
col3.metric(
    "Lowest",
    f"{df.iloc[:, 0].min():.1f} °C"
)

st.line_chart(df)
st.dataframe(df)

st.caption("Data: Open-Meteo.com (free for non-commercial use).")
