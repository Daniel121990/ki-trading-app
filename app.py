# 📈 KI-Trading App – Live Chart + Indikatoren
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="KI-Trading App")

# 🌙 Darkmode
st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .st-bb, .st-at, .st-emotion-cache-1avcm0n {background-color: #0e1117;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 KI-Trading App – Live Analyse & Prognose")

# Kategorien definieren
categories = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD", "ADA-USD", "AVAX-USD", "DOGE-USD", "BNB-USD"],
    "Aktien": [
        "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "BABA", "NFLX", "INTC",
        "JPM", "V", "UNH", "DIS", "PFE", "KO", "MRK", "XOM", "WMT", "NKE"
    ],
    "Rohstoffe": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "ZC=F", "ZS=F", "KC=F", "SB=F", "LE=F"]
}

# UI
category = st.selectbox("📂 Kategorie wählen", list(categories.keys()))
assets = categories[category]
search = st.text_input("🔍 Suche (optional)", "")
filtered = [a for a in assets if search.upper() in a.upper()] or assets
symbol = st.selectbox("📈 Asset auswählen", filtered)
interval = st.selectbox("⏱️ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])

st.markdown(f"### 📍 Asset: `{symbol}` – Intervall: `{interval}`")

# 🔄 Daten laden
@st.cache_data
def load_data(sym, interv):
    df = yf.download(sym, interval=interv, period="1d")
    if df.empty:
        df = yf.download(sym, interval=interv, period="5d")
    return df

try:
    df = load_data(symbol, interval)
    if df.empty or "Close" not in df.columns:
        st.error("❌ Daten ungültig oder leer. Bitte Symbol & Zeitintervall prüfen.")
        st.stop()

    # 📊 Indikatoren berechnen
    df["EMA20"] = ta.ema(df["Close"], length=20)
    df["RSI"] = ta.rsi(df["Close"], length=14)
    macd = ta.macd(df["Close"])
    df["MACD"] = macd["MACD_12_26_9"] if "MACD_12_26_9" in macd else None

    # 📉 Candlestick-Chart
    st.subheader("🕯️ Kursverlauf – Candlestick")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Kerzen"
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 🔍 Indikatoren farblich
    st.subheader("🔎 Indikatoren (aktuellste Werte)")

    def color(val, low, high):
        if pd.isna(val): return "white"
        if val < low: return "red"
        if val > high: return "green"
        return "white"

    rsi = round(df["RSI"].iloc[-1], 2)
    ema = round(df["EMA20"].iloc[-1], 2)
    macd_val = round(df["MACD"].iloc[-1], 4) if not pd.isna(df["MACD"].iloc[-1]) else "n/a"

    st.markdown(f"- **RSI:** <span style='color:{color(rsi, 30, 70)}'>{rsi}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20:** <span style='color:{color(ema, 0, float('inf'))}'>{ema}</span>", unsafe_allow_html=True)
    st.markdown(f"- **MACD:** <span style='color:{color(macd_val, 0, float('inf'))}'>{macd_val}</span>", unsafe_allow_html=True)

    st.success("✅ Live-Daten & Chart erfolgreich geladen.")

except Exception as e:
    st.error(f"❌ Fehler: {e}")
