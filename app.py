# 📊 KI-Trading App – Live Analyse (über Twelve Data – ohne Registrierung)

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# 🌙 Dunkles Layout
st.set_page_config(layout="wide", page_title="KI-Trading App")
st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .st-bb {background-color: #0e1117;}
        .st-at {background-color: #0e1117;}
        .st-emotion-cache-1avcm0n {background-color: #0e1117;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 KI-Trading App – Live Analyse & Prognose")

# ✅ Kategorien und Top-Auswahl
categories = {
    "Krypto": ["BTC/USD", "ETH/USD", "XRP/USD", "SOL/USD", "ADA/USD", "AVAX/USD", "DOGE/USD", "BNB/USD"],
    "Aktien": [
        "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "BABA", "NFLX", "INTC",
        "JPM", "V", "UNH", "DIS", "PFE", "KO", "MRK", "XOM", "WMT", "NKE"
    ],
    "Rohstoffe": ["XAU/USD", "XAG/USD", "WTI/USD", "NG/USD", "COPPER/USD"]
}

category = st.selectbox("🧭 Kategorie wählen", list(categories.keys()))
search = st.text_input("🔍 Suche (z. B. TSLA)", "")
filtered_assets = [a for a in categories[category] if search.upper() in a.upper()] or categories[category]
symbol = st.selectbox("📊 Asset wählen", filtered_assets)

interval = st.selectbox("⏱ Zeitintervall", ["1min", "5min", "15min", "1h", "4h", "1day"])

st.markdown(f"### 📍 Asset: `{symbol}` – Intervall: `{interval}`")

# 📡 API von Twelve Data (keine Registrierung nötig)
url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=100&format=JSON"

try:
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        st.error(f"❌ Daten konnten nicht geladen werden. Fehler: {data.get('message', 'Unbekannt')}")
        st.stop()

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.astype(float, errors='ignore')
    df.set_index("datetime", inplace=True)
    df = df.sort_index()

    # 🕯️ Kerzenchart
    st.subheader("📉 Kursverlauf")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Kerzen"
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 📊 Technische Indikatoren (vereinfachte Berechnung)
    df["EMA20"] = df["close"].rolling(window=20).mean()
    df["RSI"] = 100 - (100 / (1 + df["close"].pct_change().add(1).rolling(14).apply(lambda x: (x[x > 1].mean() / x[x <= 1].mean()) if x[x <= 1].mean() else 1)))
    df["MACD"] = df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean()

    # 🎯 Letzte Werte extrahieren
    rsi_val = round(df["RSI"].iloc[-1], 2)
    ema_val = round(df["EMA20"].iloc[-1], 2)
    macd_val = round(df["MACD"].iloc[-1], 4)

    def get_color(value, low, high):
        if pd.isna(value): return "white"
        if value < low: return "red"
        if value > high: return "green"
        return "white"

    st.subheader("📌 Indikatoren")
    st.markdown(f"- **RSI**: <span style='color:{get_color(rsi_val, 30, 70)}'>{rsi_val}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20**: <span style='color:{get_color(ema_val, 0, float('inf'))}'>{ema_val}</span>", unsafe_allow_html=True)
    st.markdown(f"- **MACD**: <span style='color:{get_color(macd_val, 0, float('inf'))}'>{macd_val}</span>", unsafe_allow_html=True)

    st.success("✅ Live-Daten erfolgreich geladen.")

except Exception as e:
    st.error(f"❌ Fehler beim Laden der Daten: {e}")
