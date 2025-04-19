import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import pandas_ta as ta

st.set_page_config(layout="wide", page_title="KI-Trading App")

st.title("📈 KI-Trading App – Live Analyse")

# Kategorien
assets = {
    "Krypto": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "XRP-USD": "XRP",
    },
    "Aktien": {
        "AAPL": "Apple",
        "TSLA": "Tesla",
        "NVDA": "NVIDIA",
    },
    "Rohstoffe": {
        "GC=F": "Gold",
        "SI=F": "Silber",
        "CL=F": "Öl"
    }
}

category = st.selectbox("📂 Kategorie wählen", list(assets.keys()))
symbols = assets[category]
search = st.text_input("🔍 Suche...", "").upper()

# Filter
filtered = {k: v for k, v in symbols.items() if search in k or search in v.upper()} or symbols
symbol = st.selectbox("📊 Asset auswählen", list(filtered.keys()))
interval = st.selectbox("⏱️ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])

st.markdown(f"📍 **Asset:** {symbol} – Intervall: {interval}")

# Live Datenquelle (ohne API)
@st.cache_data(ttl=60)
def fetch_data(symbol, interval):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range=1d"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()["chart"]["result"][0]
    timestamps = pd.to_datetime(data["timestamp"], unit="s")
    ohlc = pd.DataFrame(data["indicators"]["quote"][0])
    ohlc["timestamp"] = timestamps
    ohlc.set_index("timestamp", inplace=True)
    return ohlc

data = fetch_data(symbol, interval)

if data is None or data.empty:
    st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
    st.stop()

# Technische Indikatoren
data["EMA20"] = ta.ema(data["close"], length=20)
data["RSI"] = ta.rsi(data["close"], length=14)
macd_data = ta.macd(data["close"])
if macd_data is not None and "MACD_12_26_9" in macd_data.columns:
    data["MACD"] = macd_data["MACD_12_26_9"]
else:
    data["MACD"] = np.nan

# Live Kerzendiagramm
st.subheader("🕯️ Live-Kerzenchart")
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["open"],
    high=data["high"],
    low=data["low"],
    close=data["close"],
    name="OHLC"
))
fig.update_layout(xaxis_rangeslider_visible=False, height=400)
st.plotly_chart(fig, use_container_width=True)

# Indikatoren
def color(val, low, high):
    if pd.isna(val): return "white"
    if val < low: return "red"
    if val > high: return "green"
    return "white"

rsi = round(data["RSI"].iloc[-1], 2)
ema = round(data["EMA20"].iloc[-1], 2)
macd_val = round(data["MACD"].iloc[-1], 4)

st.subheader("🧠 Indikatoren (farbcodiert)")
st.markdown(f"- **RSI:** <span style='color:{color(rsi, 30, 70)}'>{rsi}</span>", unsafe_allow_html=True)
st.markdown(f"- **EMA20:** <span style='color:{color(ema, 0, float('inf'))}'>{ema}</span>", unsafe_allow_html=True)
st.markdown(f"- **MACD:** <span style='color:{color(macd_val, 0, float('inf'))}'>{macd_val}</span>", unsafe_allow_html=True)

# Veränderung
start = data["close"].iloc[0]
end = data["close"].iloc[-1]
delta = round(((end - start) / start) * 100, 2)
color_delta = "green" if delta > 0 else "red"

st.markdown(f"📈 **Tagesveränderung:** <span style='color:{color_delta}'>{delta}%</span>", unsafe_allow_html=True)
