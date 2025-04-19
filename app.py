import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

asset = st.selectbox("Wähle ein Asset", ["XRP-USD", "XAUUSD", "TSLA", "NVDA", "AAPL"])
st.write(f"📍 Gewähltes Asset: `{asset}`")

# Versuche, Daten zu laden
data = yf.download(asset, period="1d", interval="1m")

# Fallback bei leeren Daten
if data is None or data.empty or "Close" not in data.columns:
    st.warning("⚠️ Keine oder fehlerhafte Daten – wechsle zu Test-Asset `AAPL`")
    asset = "AAPL"
    data = yf.download(asset, period="1d", interval="1m")
    st.write("📦 Fallback-Daten geladen:", data.tail())

if data is None or data.empty:
    st.error("❌ Auch Fallback-Daten sind leer – kein Chart möglich.")
    st.stop()

# Indikatoren
try:
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])

    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
        data["MACDs"] = macd["MACDs_12_26_9"]
    else:
        st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt.")
except Exception as e:
    st.error(f"❌ Fehler bei Berechnung: {e}")
    st.stop()

# Chartanzeige
st.subheader(f"📊 Chart für: {asset}")
try:
    st.line_chart(data[["Close", "EMA20"]].dropna())
except:
    st.warning("⚠️ Chart konnte nicht angezeigt werden.")

st.subheader("📉 RSI – Relative Strength Index")
try:
    st.line_chart(data[["RSI"]].dropna())
except:
    st.warning("⚠️ RSI-Anzeige fehlgeschlagen.")

st.subheader("📈 MACD & Signal")
try:
    st.line_chart(data[["MACD", "MACDs"]].dropna())
except:
    st.warning("⚠️ MACD-Anzeige fehlgeschlagen.")

st.info("✅ Grundfunktionen aktiv. KI-Prognose & Signale folgen.")
