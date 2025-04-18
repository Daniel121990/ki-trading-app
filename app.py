import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse")

# --- Kategorien & Auswahl ---
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

# Fix: Index zurücksetzen, damit keine Probleme entstehen
data.reset_index(inplace=True)

# --- Indikatoren berechnen ---
indikatoren_ok = False
try:
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])
    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
        data["Signal"] = macd["MACDs_12_26_9"]
        indikator_spalten = ["Close", "EMA20", "RSI", "MACD", "Signal"]
        indikator_spalten = [col for col in indikator_spalten if col in data.columns]
        indikatoren_ok = True
except:
    indikatoren_ok = False

# --- Datenvorschau
st.subheader("📊 Datenvorschau:")
st.dataframe(data.tail(10))

# --- Charts ---
if "Close" in data.columns and "EMA20" in data.columns:
    st.subheader("📈 Kursverlauf (Close & EMA20)")
    st.line_chart(data[["Close", "EMA20"]].dropna())
else:
    st.warning("⚠️ Kursverlauf konnte nicht angezeigt werden.")

if "RSI" in data.columns:
    st.subheader("📉 RSI")
    st.line_chart(data[["RSI"]].dropna())
else:
    st.warning("⚠️ RSI konnte nicht angezeigt werden.")

if "MACD" in data.columns and "Signal" in data.columns:
    st.subheader("📈 MACD & Signal")
    st.line_chart(data[["MACD", "Signal"]].dropna())
else:
    st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

# --- Abschluss
st.success("✅ Grundfunktionen aktiv. KI-Analyse, BUY-/SELL und Candle-Prognose folgen.")
