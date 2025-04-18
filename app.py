import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

# 🟡 Asset-Auswahl (Dropdown)
asset = st.selectbox("Wähle ein Asset", ["XRP-USD", "XAUUSD", "TSLA", "NVDA", "AAPL"])
st.write(f"📍 Gewähltes Asset: `{asset}`")

# 🔄 Daten abrufen
data = yf.download(asset, period="1d", interval="1m")
st.write("📦 Datenvorschau:", data.tail())

if data is None or data.empty:
    st.error("❌ Daten ungültig oder leer.")
    st.stop()

# 📊 Technische Indikatoren berechnen
try:
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])

    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
        data["MACDs"] = macd["MACDs_12_26_9"]
    else:
        st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

except Exception as e:
    st.error(f"❌ Fehler beim Berechnen der Indikatoren: {e}")
    st.stop()

# 📈 Preis-Chart
st.subheader(f"📊 Chart für: {asset}")
try:
    st.line_chart(data[["Close", "EMA20"]].dropna())
except:
    st.warning("⚠️ Chart konnte nicht dargestellt werden.")

# 🔍 RSI-Anzeige
st.subheader("📉 RSI – Relative Strength Index")
try:
    st.line_chart(data[["RSI"]].dropna())
except:
    st.warning("⚠️ RSI konnte nicht dargestellt werden.")

# 📈 MACD-Anzeige
st.subheader("📈 MACD & Signal")
try:
    st.line_chart(data[["MACD", "MACDs"]].dropna())
except:
    st.warning("⚠️ MACD konnte nicht dargestellt werden.")

st.info("✅ Grundfunktionen aktiv. KI-Analyse, BUY-/SELL und Candle-Prognose folgt.")
