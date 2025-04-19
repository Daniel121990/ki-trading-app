# 📈 KI-Trading App – Binance Live Charts & Indikatoren

import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
import pandas_ta as ta

st.set_page_config(layout="wide", page_title="KI-Trading App")
st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .st-bb, .st-at, .st-emotion-cache-1avcm0n {background-color: #0e1117;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 KI-Trading App – Binance Live Analyse")

# ⏳ Parameter
symbol = st.selectbox("📊 Asset wählen", ["XRPUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT"])
interval = st.selectbox("⏱ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])
limit = 200

url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

try:
    response = requests.get(url)
    response.raise_for_status()
    raw_data = response.json()

    # 📦 In DataFrame umwandeln
    df = pd.DataFrame(raw_data, columns=[
        "Time", "Open", "High", "Low", "Close", "Volume",
        "Close time", "Quote asset volume", "Trades",
        "Taker buy base", "Taker buy quote", "Ignore"
    ])

    df["Time"] = pd.to_datetime(df["Time"], unit="ms")
    df.set_index("Time", inplace=True)
    df = df.astype(float)

    df["EMA20"] = ta.ema(df["Close"], length=20)
    df["RSI"] = ta.rsi(df["Close"], length=14)
    macd = ta.macd(df["Close"])
    if macd is not None and "MACD_12_26_9" in macd.columns:
        df["MACD"] = macd["MACD_12_26_9"]
    else:
        df["MACD"] = None

    # 📈 Candlestick Chart
    st.subheader("🕯️ Live Kerzenchart")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 🔎 Indikatoren als Werte
    def colored(val, low, high):
        if pd.isna(val): return "white"
        return "red" if val < low else "green" if val > high else "white"

    latest = df.iloc[-1]
    st.subheader("📊 Indikator-Werte")
    st.markdown(f"- **RSI:** <span style='color:{colored(latest['RSI'],30,70)}'>{round(latest['RSI'],2)}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20:** <span style='color:{colored(latest['EMA20'],latest['Close']*0.97, latest['Close']*1.03)}'>{round(latest['EMA20'],2)}</span>", unsafe_allow_html=True)
    macd_val = round(latest["MACD"], 4) if not pd.isna(latest["MACD"]) else "n/a"
    st.markdown(f"- **MACD:** <span style='color:{colored(macd_val, 0, 9999)}'>{macd_val}</span>", unsafe_allow_html=True)

    st.success("✅ Daten geladen – Echtzeit Binance")

except Exception as e:
    st.error(f"❌ Daten konnten nicht geladen werden. Fehler: {e}")
