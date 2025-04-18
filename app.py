import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse")

# --- Kategorien & Assets ---
kategorien = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "BNB-USD"],
    "Aktien": ["AAPL", "TSLA", "NVDA", "META"],
    "Rohstoffe": ["XAUUSD", "XAGUSD", "CL=F", "BZ=F"]
}

kategorie = st.selectbox("📂 Kategorie wählen", list(kategorien.keys()))
suchtext = st.text_input("🔍 Suche nach Asset (z.B. TSLA)", "")

asset_liste = [a for a in kategorien[kategorie] if suchtext.upper() in a.upper()]
asset = st.selectbox("🎯 Asset auswählen", asset_liste)

interval = st.selectbox("⏱️ Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

# --- Daten laden ---
st.markdown(f"### 📍 Gewähltes Asset: `{asset}`")

data = yf.download(asset, period="1d", interval=interval)
if data is None or data.empty:
    st.error("❌ Keine Daten gefunden – bitte anderes Asset oder Intervall wählen.")
    st.stop()

st.subheader("📊 Datenvorschau:")
st.dataframe(data.tail(10))

# --- Technische Indikatoren ---
try:
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])
    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
        data["Signal"] = macd["MACDs_12_26_9"]
        macd_ok = True
    else:
        macd_ok = False
except Exception as e:
    st.warning("⚠️ Indikatoren konnten nicht berechnet werden.")
    macd_ok = False

# --- Charts ---
try:
    st.subheader("📈 Kursverlauf (Close & EMA20)")
    st.line_chart(data[["Close", "EMA20"]].dropna())
except:
    st.warning("⚠️ Kursverlauf konnte nicht angezeigt werden.")

try:
    st.subheader("📉 RSI")
    st.line_chart(data[["RSI"]].dropna())
except:
    st.warning("⚠️ RSI konnte nicht angezeigt werden.")

if macd_ok:
    try:
        st.subheader("📈 MACD & Signal")
        st.line_chart(data[["MACD", "Signal"]].dropna())
    except:
        st.warning("⚠️ MACD konnte nicht dargestellt werden.")
else:
    st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

# --- Abschluss
st.success("✅ Grundfunktionen aktiv. KI-Analyse, BUY-/SELL und Candle-Prognose folgen.")
