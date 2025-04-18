# 📊 KI-Trading App – Live Analyse & Prognose (mit Twelve Data)

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# 📱 Layout & Titel
st.set_page_config(layout="wide", page_title="KI-Trading App")
st.title("📊 KI-Trading App – Live Analyse & Prognose")

# ✅ Kategorien und Top-Auswahl
categories = {
    "Krypto": ["BTC/USD", "ETH/USD", "XRP/USD", "SOL/USD", "ADA/USD"],
    "Aktien": ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META"],
    "Rohstoffe": ["XAU/USD", "XAG/USD", "WTI/USD", "NG/USD"]
}

# Auswahlfelder
category = st.selectbox("🧭 Kategorie wählen", list(categories.keys()))
asset_list = categories[category]
search = st.text_input("🔍 Suche Asset", "")
filtered_assets = [a for a in asset_list if search.upper() in a.upper()] or asset_list
symbol = st.selectbox("📈 Asset wählen", filtered_assets)
timeframe = st.selectbox("⏱️ Zeitintervall", ["1min", "5min", "15min", "1h", "1day"])

# 📍 Info
st.markdown(f"### 📍 Asset: {symbol} – Intervall: {timeframe}")

# 🔗 Twelve Data API (kostenfrei, keine Registrierung notwendig)
base_url = "https://api.twelvedata.com/time_series"
params = {
    "symbol": symbol.replace("/", ""),
    "interval": timeframe,
    "outputsize": 100,
    "format": "JSON"
}

# 🔄 Daten laden
try:
    response = requests.get(base_url, params=params)
    raw = response.json()

    if "values" not in raw:
        st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
        st.stop()

    data = pd.DataFrame(raw["values"])
    data["datetime"] = pd.to_datetime(data["datetime"])
    data.set_index("datetime", inplace=True)
    data = data.astype(float).sort_index()

    # 📈 Kerzenchart
    st.subheader("📉 Kursverlauf")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"],
        name="Kerzen"
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 🔎 Indikatorberechnung (vereinfacht)
    close = data["close"]
    ema = close.ewm(span=20).mean().iloc[-1]
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]

    # 🔢 Farbige Darstellung
    def farbe(val, low, high):
        if pd.isna(val): return "white"
        if val < low: return "red"
        if val > high: return "green"
        return "white"

    st.subheader("📌 Indikatoren")
    st.markdown(f"- **RSI:** <span style='color:{farbe(rsi, 30, 70)}'>{round(rsi, 2)}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20:** <span style='color:{farbe(ema, 0, float('inf'))}'>{round(ema, 2)}</span>", unsafe_allow_html=True)

    st.success("✅ Live-Daten und Indikatoren erfolgreich geladen.")

except Exception as e:
    st.error(f"❌ Fehler: {e}")
