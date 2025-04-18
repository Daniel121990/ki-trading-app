import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>📈 KI-Trading App – Live Analyse</h1>", unsafe_allow_html=True)

asset = st.selectbox("🔎 Wähle ein Asset", ["AAPL", "TSLA", "NVDA", "XAUUSD", "XRP-USD"])
st.markdown(f"### 📍 Gewähltes Asset: `{asset}`")

data = yf.download(asset, period="1d", interval="1m")

if data is None or data.empty:
    st.error("❌ Keine Daten verfügbar.")
    st.stop()

# RSI mit Pandas-Berechnung (ohne pandas_ta)
delta = data["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
data["RSI"] = 100 - (100 / (1 + rs))

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Kursverlauf (Close)")
    st.line_chart(data["Close"])

with col2:
    st.subheader("📉 RSI")
    st.line_chart(data["RSI"])

st.success("✅ Layout + RSI funktionieren. Jetzt bereit für MACD, BUY/SELL, KI-Prognose.")
