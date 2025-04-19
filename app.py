import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

# Auswahlfeld für das Asset
asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])

# Versuche, die Daten zu laden und auszuwerten
try:
    data = yf.download(asset, period="1d", interval="1m")

    if data is not None and not data.empty and "Close" in data.columns:
        data = data.dropna(subset=["Close"]).copy()

        if len(data) > 30:
            # Technische Indikatoren berechnen
            data["EMA20"] = ta.ema(data["Close"], length=20)
            data["RSI"] = ta.rsi(data["Close"], length=14)
            macd = ta.macd(data["Close"])

            # MACD prüfen
            if macd is not None and not macd.empty and "MACD_12_26_9" in macd.columns:
                data["MACD"] = macd["MACD_12_26_9"]
                data["MACDs"] = macd["MACDs_12_26_9"]
            else:
                st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")
                macd = None

            # Chartausgabe
            st.subheader(f"📊 Chart für: {asset}")
            st.line_chart(data[["Close", "EMA20"]].dropna())

            st.subheader("📉 RSI – Relative Strength Index")
            st.line_chart(data[["RSI"]].dropna())

            if macd is not None:
                st.subheader("📈 MACD & Signal")
                st.line_chart(data[["MACD", "MACDs"]].dropna())

            st.success("✅ Analyse abgeschlossen.")

        else:
            st.warning("⚠️ Nicht genug Daten für eine sinnvolle Analyse (mind. 30 Werte).")

    else:
        st.error("❌ Daten ungültig oder leer.")

except Exception as e:
    st.error(f"Fehler beim Laden oder Verarbeiten der Daten: {e}")
