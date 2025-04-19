# 📈 KI-Trading App – Live mit Binance-Minutenkerzen

import streamlit as st
import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(layout="wide", page_title="KI-Trading App")

# Darkmode
st.markdown("""<style>body {background-color: #0e1117; color: white;}</style>""", unsafe_allow_html=True)
st.title("📊 KI-Trading App – Live Analyse")

# Kategorien & Assets
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "BNBUSDT"],
    "Aktien": ["TSLA", "AAPL", "MSFT", "NVDA", "AMZN"],
    "Rohstoffe": ["GC=F", "SI=F", "CL=F", "NG=F"]
}

kategorie = st.selectbox("🌍 Kategorie wählen", list(kategorien.keys()))
assets = kategorien[kategorie]
suchbegriff = st.text_input("🔍 Suche nach Symbol", "").upper()
gefilterte_assets = [a for a in assets if suchbegriff in a] or assets
symbol = st.selectbox("📈 Wähle Asset", gefilterte_assets)
interval = st.selectbox("⏱ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])

st.markdown(f"📍 Asset: `{symbol}` – Intervall: `{interval}`")

# Daten von Binance holen (nur Krypto)
def get_binance_data(symbol, interval="1m", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        raw = response.json()
        df = pd.DataFrame(raw, columns=[
            "Time", "Open", "High", "Low", "Close", "Volume", "_", "_", "_", "_", "_", "_"
        ])
        df["Time"] = pd.to_datetime(df["Time"], unit="ms")
        df.set_index("Time", inplace=True)
        df = df.astype(float)
        return df[["Open", "High", "Low", "Close"]]
    else:
        return None

data = get_binance_data(symbol, interval)

if data is None or data.empty:
    st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
    st.stop()

# Indikatoren
data["EMA20"] = ta.ema(data["Close"], length=20)
data["RSI"] = ta.rsi(data["Close"], length=14)
macd = ta.macd(data["Close"])
data["MACD"] = macd["MACD_12_26_9"] if "MACD_12_26_9" in macd else np.nan

# Chart
st.subheader("📈 Kursverlauf (Candlestick)")
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
))
fig.update_layout(xaxis_rangeslider_visible=False, height=400)
st.plotly_chart(fig, use_container_width=True)

# Farbige Indikatoren
def color(val, low, high):
    if np.isnan(val): return "white"
    if val < low: return "red"
    if val > high: return "green"
    return "white"

rsi = round(data["RSI"].iloc[-1], 2)
ema = round(data["EMA20"].iloc[-1], 2)
macd_val = round(data["MACD"].iloc[-1], 4)

st.markdown(f"- **RSI:** <span style='color:{color(rsi, 30, 70)}'>{rsi}</span>", unsafe_allow_html=True)
st.markdown(f"- **EMA20:** <span style='color:{color(ema, 0, float('inf'))}'>{ema}</span>", unsafe_allow_html=True)
st.markdown(f"- **MACD:** <span style='color:{color(macd_val, 0, float('inf'))}'>{macd_val}</span>", unsafe_allow_html=True)

st.success("✅ Live-Daten & Chart erfolgreich geladen.")
