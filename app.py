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
        .st-bb {background-color: #0e1117;}
        .st-at {background-color: #0e1117;}
        .st-emotion-cache-1avcm0n {background-color: #0e1117;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 KI-Trading App – Live Analyse & Prognose")

# ✅ Kategorien und Top-Auswahl
categories = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD", "ADA-USD", "AVAX-USD", "DOGE-USD", "BNB-USD"],
    "Aktien": [
        "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "BABA", "NFLX", "INTC",
        "JPM", "V", "UNH", "DIS", "PFE", "KO", "MRK", "XOM", "WMT", "NKE"
    ],
    "Rohstoffe": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "ZC=F", "ZS=F", "KC=F", "SB=F", "LE=F"]
}

# Auswahl
category = st.selectbox("📂 Kategorie wählen", list(categories.keys()))
search = st.text_input("🔍 Suche (optional)", "")
filtered_assets = [a for a in categories[category] if search.upper() in a.upper()] or categories[category]
symbol = st.selectbox("📈 Asset auswählen", filtered_assets)
timeframe = st.selectbox("⏳ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])

st.markdown(f"### 📍 Asset: <span style='color:lightgreen'>{symbol}</span> – Intervall: <span style='color:lightblue'>{timeframe}</span>", unsafe_allow_html=True)

try:
    data = yf.download(tickers=symbol, interval=timeframe, period="1d")
    if data.empty:
        st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
        st.stop()

    # Indikatoren
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])
    data["MACD"] = macd["MACD_12_26_9"] if macd is not None and "MACD_12_26_9" in macd.columns else None

    # Chart
    st.subheader("📉 Kursverlauf – Candlestick")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name="Preis"
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Indikatoren farblich anzeigen
    st.subheader("🔧 Indikatoren (aktuellste Werte)")
    def farbe(wert, low, high):
        if pd.isna(wert): return "white"
        if isinstance(wert, str): return "white"
        if wert < low: return "red"
        if wert > high: return "green"
        return "white"

    rsi = data["RSI"].dropna().iloc[-1] if not data["RSI"].dropna().empty else None
    ema = data["EMA20"].dropna().iloc[-1] if not data["EMA20"].dropna().empty else None
    macd_val = data["MACD"].dropna().iloc[-1] if not data["MACD"].dropna().empty else None

    st.markdown(f"- **RSI:** <span style='color:{farbe(rsi, 30, 70)}'>{round(rsi,2) if rsi else 'n/a'}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20:** <span style='color:{farbe(ema, 0, 9999)}'>{round(ema,2) if ema else 'n/a'}</span>", unsafe_allow_html=True)
    st.markdown(f"- **MACD:** <span style='color:{farbe(macd_val, 0, 9999)}'>{round(macd_val,4) if macd_val else 'n/a'}</span>", unsafe_allow_html=True)

    # ✅ BUY/SELL Logik
    buy = data["Close"].iloc[-1] - 2
    sell = data["Close"].iloc[-1] + 2

    st.subheader("🟩 Signalbox")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='background-color:#ff4b4b;padding:20px;border-radius:10px;text-align:center;color:white;font-size:20px;'>SELL<br><b>{round(sell,2)}</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background-color:#2ecc71;padding:20px;border-radius:10px;text-align:center;color:white;font-size:20px;'>BUY<br><b>{round(buy,2)}</b></div>", unsafe_allow_html=True)

    st.success("✅ Alle Daten & Chart erfolgreich geladen.")

except Exception as e:
    st.error(f"❌ Fehler: {e}")
