import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
data = yf.download(asset, period="1d", interval="1m")

# Berechne technische Indikatoren
try:
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])

    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
        data["MACDs"] = macd["MACDs_12_26_9"]
    else:
        st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

    # Chartanzeige
    st.subheader(f"📊 Chart für: {asset}")
    st.line_chart(data[["Close", "EMA20"]].dropna())

    st.subheader("📉 RSI – Relative Strength Index")
    st.line_chart(data[["RSI"]].dropna())

    st.subheader("📈 MACD & Signal")
    st.line_chart(data[["MACD", "MACDs"]].dropna())

    # Prognose-Hinweis (funktionell später einbauen)
    st.info("✅ Grundfunktionen aktiv. BUY-/SELL & Candle-Prognose folgt.")

except Exception as e:
    st.error(f"Fehler beim Laden oder Berechnen der Daten: {e}")
