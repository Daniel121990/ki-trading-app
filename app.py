import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
data = yf.download(asset, period="1d", interval="1m")

# MultiIndex-Spalten bereinigen, falls vorhanden
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(1)

# Sicherheitsprüfung
if data.empty or "Close" not in data.columns:
    st.error("❌ Daten konnten nicht geladen werden. Bitte versuche ein anderes Asset.")
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
if "EMA20" in data.columns and not data["EMA20"].isnull().all():
    st.line_chart(data[["Close", "EMA20"]].dropna())
else:
    st.line_chart(data[["Close"]].dropna())

st.subheader("📉 RSI – Relative Strength Index")
if "RSI" in data.columns and not data["RSI"].isnull().all():
    st.line_chart(data[["RSI"]].dropna())
else:
    st.info("RSI konnte nicht berechnet werden.")

st.subheader("📈 MACD & Signal")
if "MACD" in data.columns and not data["MACD"].isnull().all():
    st.line_chart(data[["MACD", "MACDs"]].dropna())
else:
    st.info("MACD nicht verfügbar.")

st.success("✅ Grundfunktionen stabil. Prognose & Buy/Sell folgen.")
