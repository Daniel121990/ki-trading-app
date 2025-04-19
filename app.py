import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

# Asset-Auswahl
asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
data = yf.download(asset, period="1d", interval="1m")

# Struktur prüfen und anpassen
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(1)

if data.empty or "Close" not in data.columns:
    st.error("❌ Keine gültigen Daten für das gewählte Asset.")
    st.stop()

# Technische Indikatoren berechnen
data["EMA20"] = ta.ema(data["Close"], length=20)
data["RSI"] = ta.rsi(data["Close"], length=14)

macd = ta.macd(data["Close"])
if macd is not None and "MACD_12_26_9" in macd.columns and "MACDs_12_26_9" in macd.columns:
    data["MACD"] = macd["MACD_12_26_9"]
    data["MACDs"] = macd["MACDs_12_26_9"]
else:
    data["MACD"] = None
    data["MACDs"] = None
    st.warning("⚠️ MACD konnte nicht berechnet werden – Daten unvollständig.")

# Charts anzeigen
st.subheader(f"📊 Preis & EMA für: {asset}")
try:
    st.line_chart(data[["Close", "EMA20"]].dropna())
except:
    st.line_chart(data[["Close"]].dropna())

st.subheader("📉 RSI – Relative Strength Index")
try:
    st.line_chart(data[["RSI"]].dropna())
except:
    st.info("RSI nicht verfügbar.")

st.subheader("📈 MACD & Signal")
try:
    st.line_chart(data[["MACD", "MACDs"]].dropna())
except:
    st.info("MACD-Daten nicht vollständig.")

st.success("✅ Analyse stabil geladen. Erweiterungen folgen...")
