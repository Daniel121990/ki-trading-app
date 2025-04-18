import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Test")

asset = st.selectbox("Wähle ein Asset", ["AAPL", "TSLA", "NVDA", "XAUUSD", "XRP-USD"])
st.write(f"📍 Gewähltes Asset: `{asset}`")

try:
    data = yf.download(asset, period="1d", interval="1m")
except Exception as e:
    st.error(f"❌ Fehler beim Laden der Daten: {e}")
    st.stop()

if data is None or data.empty:
    st.error("❌ Keine Daten verfügbar.")
    st.stop()

# Vorschau-Tabelle
st.subheader("📦 Datenvorschau")
st.dataframe(data.tail(10))

# Chart nur mit Close
st.subheader("📊 Kursverlauf (Close)")
try:
    st.line_chart(data["Close"])
except:
    st.warning("⚠️ Chart konnte nicht dargestellt werden.")

st.success("✅ Alles läuft. Jetzt bereit für Indikatoren und KI-Module.")
