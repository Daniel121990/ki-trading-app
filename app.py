# 📊 KI-Trading App – Live Analyse & Prognose (über Yahoo Finance)

import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# 🌙 Dunkles Layout
st.set_page_config(layout="wide", page_title="KI-Trading App")
st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .st-bb, .st-at, .st-emotion-cache-1avcm0n {background-color: #0e1117;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 KI-Trading App – Live Analyse & Prognose")

# ✅ Kategorien & Assets
categories = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD", "ADA-USD", "AVAX-USD", "DOGE-USD", "BNB-USD"],
    "Aktien": [
        "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "BABA", "NFLX", "INTC",
        "JPM", "V", "UNH", "DIS", "PFE", "KO", "MRK", "XOM", "WMT", "NKE"
    ],
    "Rohstoffe": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "ZC=F", "ZS=F", "KC=F", "SB=F", "LE=F"]
}

# Auswahl
category = st.selectbox("📂 Wähle eine Kategorie", list(categories.keys()))
asset_list = categories[category]
search = st.text_input("🔍 Suche nach Asset (z.B. TSLA)", "")
filtered_assets = [a for a in asset_list if search.upper() in a.upper()] or asset_list
symbol = st.selectbox("📈 Wähle ein Asset", filtered_assets)
timeframe = st.selectbox("⏳ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])

st.markdown(f"### 📍 Gewähltes Asset: `{symbol}`")

try:
    # 📦 Daten abrufen
    data = yf.download(tickers=symbol, interval=timeframe, period="7d")
    if data.empty:
        st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
        st.stop()

    # Technische Indikatoren
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])
    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
    else:
        data["MACD"] = None

    # 📉 Kerzenchart
    st.subheader("📉 Kursverlauf (1-Minuten-Kerzen)")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Kerzen"
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 🔎 Indikatoren farblich
    st.subheader("🔍 Indikatoren")
    def get_color(val, low, high):
        if pd.isna(val): return "white"
        if val < low: return "red"
        if val > high: return "green"
        return "white"

    rsi = round(data["RSI"].dropna().iloc[-1], 2)
    ema = round(data["EMA20"].dropna().iloc[-1], 2)
    macd_val = round(data["MACD"].dropna().iloc[-1], 4) if not pd.isna(data["MACD"].dropna().iloc[-1]) else "n/a"

    st.markdown(f"- **RSI:** <span style='color:{get_color(rsi, 30, 70)}'>{rsi}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20:** <span style='color:{get_color(ema, 0, float('inf'))}'>{ema}</span>", unsafe_allow_html=True)
    st.markdown(f"- **MACD:** <span style='color:{get_color(macd_val, 0, float('inf'))}'>{macd_val}</span>", unsafe_allow_html=True)

    # 📈 Prozentuale Veränderung
    st.subheader("📊 Veränderung in Prozent")
    def calc_change(past_days):
        try:
            past_price = yf.download(symbol, period=f"{past_days}d")["Close"].iloc[0]
            current_price = data["Close"].iloc[-1]
            return round((current_price - past_price) / past_price * 100, 2)
        except:
            return None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("24h", f"{calc_change(1)} %")
    col2.metric("1 Woche", f"{calc_change(7)} %")
    col3.metric("1 Monat", f"{calc_change(30)} %")
    col4.metric("1 Jahr", f"{calc_change(365)} %")

    st.success("✅ Live-Daten, Indikatoren und Chart erfolgreich geladen.")

except Exception as e:
    st.error(f"❌ Fehler beim Laden oder Berechnen: {e}")
