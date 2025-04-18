import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
data = yf.download(asset, period="1d", interval="1m")

# Sicherheitsprüfung
if data.empty or "Close" not in data.columns:
    st.error("❌ Keine Daten geladen. Bitte versuche ein anderes Asset.")
    st.stop()

# Indikatoren berechnen
data["EMA20"] = ta.ema(data["Close"], length=20)
data["RSI"] = ta.rsi(data["Close"], length=14)
macd = ta.macd(data["Close"])

# MACD prüfen
if macd is not None and "MACD_12_26_9" in macd.columns and "MACDs_12_26_9" in macd.columns:
    data["MACD"] = macd["MACD_12_26_9"]
    data["MACDs"] = macd["MACDs_12_26_9"]
else:
    st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")
    data["MACD"] = None
    data["MACDs"] = None

# Charts anzeigen
st.subheader(f"📊 Chart für: {asset}")
if "EMA20" in data.columns and data["EMA20"].isnull().all() == False:
    st.line_chart(data[["Close", "EMA20"]].dropna())
else:
    st.line_chart(data[["Close"]].dropna())

st.subheader("📉 RSI – Relative Strength Index")
if "RSI" in data.columns and data["RSI"].isnull().all() == False:
    st.line_chart(data[["RSI"]].dropna())
else:
    st.info("RSI konnte nicht berechnet werden.")

st.subheader("📈 MACD & Signal")
if "MACD" in data.columns and data["MACD"].isnull().all() == False:
    st.line_chart(data[["MACD", "MACDs"]].dropna())
else:
    st.info("MACD nicht verfügbar.")

st.success("✅ Grundfunktionen stabil. Prognose folgt.")
