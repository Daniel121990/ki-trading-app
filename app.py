import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse")

# Kategorien und Assets
categories = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD"],
    "Aktien": ["AAPL", "TSLA", "NVDA"],
    "Rohstoffe": ["XAUUSD", "CL=F"]
}

# Kategorie auswählen
category = st.selectbox("Kategorie wählen", list(categories.keys()))

# Suchfeld mit Dropdown
query = st.text_input("Suche nach Asset (z.B. TSLA)", "")
filtered_assets = [asset for asset in categories[category] if query.upper() in asset]
asset = st.selectbox("Asset auswählen", filtered_assets or categories[category])

# Intervallauswahl
interval = st.selectbox("Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

# Daten laden
try:
    data = yf.download(asset, period="1d", interval=interval)
    st.markdown(f"### 📍 Gewähltes Asset: {asset}")
    st.dataframe(data.tail(5))

    # Indikatoren berechnen
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd_df = ta.macd(data["Close"])

    if macd_df is not None and "MACD_12_26_9" in macd_df.columns:
        data["MACD"] = macd_df["MACD_12_26_9"]
        data["Signal"] = macd_df["MACDs_12_26_9"]
    else:
        st.warning("⚠️ MACD konnte nicht berechnet werden.")

    # Chart anzeigen
    st.subheader("📊 Kursverlauf (Close & EMA20)")
    st.line_chart(data[["Close", "EMA20"]].dropna())

    # RSI farblich markieren
    latest_rsi = data["RSI"].iloc[-1] if "RSI" in data else None
    rsi_color = "white"
    if latest_rsi is not None:
        if latest_rsi < 30:
            rsi_color = "red"
        elif latest_rsi > 70:
            rsi_color = "green"
    st.markdown(f"<div style='color:{rsi_color}'>RSI: {latest_rsi:.2f}</div>", unsafe_allow_html=True)

    # MACD und Signal
    if "MACD" in data and "Signal" in data:
        st.subheader("📈 MACD & Signal")
        st.line_chart(data[["MACD", "Signal"]].dropna())

    # Veränderung in %
    if len(data) > 1:
        change_1d = ((data["Close"].iloc[-1] - data["Close"].iloc[0]) / data["Close"].iloc[0]) * 100
        st.markdown(f"**Veränderung (heute):** {change_1d:.2f}%")

except Exception as e:
    st.error(f"Fehler beim Laden oder Berechnen der Daten: {e}")

st.info("✅ Grundfunktionen aktiv. KI-Analyse, BUY-/SELL und Candle-Prognose folgen.")
