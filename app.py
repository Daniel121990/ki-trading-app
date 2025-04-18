import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas_ta as ta

# Binance Setup
client = Client()

st.set_page_config(layout="wide")
st.title("📊 KI-Trading App – Live Analyse & Prognose")

# Kategorien
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"],
    "Aktien": ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"],
    "Rohstoffe": ["GC=F", "CL=F", "SI=F", "HG=F", "ZC=F"]
}

kategorie = st.selectbox("🔍 Wähle eine Kategorie", list(kategorien.keys()))
asset = st.selectbox("📈 Wähle ein Asset", kategorien[kategorie])
interval = st.selectbox("⏱️ Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

try:
    if kategorie == "Krypto":
        klines = client.get_klines(symbol=asset, interval=interval, limit=200)
        df = pd.DataFrame(klines, columns=[
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base", "Taker buy quote", "Ignore"
        ])

        df = df[["Open time", "Open", "High", "Low", "Close", "Volume"]].copy()
        df["Open time"] = pd.to_datetime(df["Open time"], unit='ms')
        df.set_index("Open time", inplace=True)
        df = df.astype(float)
    else:
        df = pd.DataFrame()

    st.markdown(f"### 🔹 Gewähltes Asset: `{asset}`")

    # Chart anzeigen
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=400)
    st.markdown("#### 🌉 Kursverlauf (1-Minuten-Kerzen)")
    st.plotly_chart(fig, use_container_width=True)

    # Indikatoren berechnen
    rsi = ta.rsi(df['Close'], length=14)
    ema = ta.ema(df['Close'], length=20)
    macd = ta.macd(df['Close'])

    st.markdown("#### 🔍 Indikatoren")
    def colorize(value, low, high):
        if value < low:
            return f"<span style='color:red'>{value:.2f}</span>"
        elif value > high:
            return f"<span style='color:limegreen'>{value:.2f}</span>"
        else:
            return f"<span style='color:white'>{value:.2f}</span>"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**RSI**")
        st.markdown(colorize(rsi.iloc[-1], 30, 70), unsafe_allow_html=True)
    with col2:
        st.markdown("**EMA20**")
        st.markdown(colorize(ema.iloc[-1], df['Close'].min(), df['Close'].max()), unsafe_allow_html=True)
    with col3:
        st.markdown("**MACD**")
        if macd is not None and "MACD_12_26_9" in macd.columns:
            macd_val = macd["MACD_12_26_9"].iloc[-1]
            st.markdown(colorize(macd_val, -0.5, 0.5), unsafe_allow_html=True)
        else:
            st.warning("MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

    st.success("✅ Live Daten und Indikatoren geladen.")

except BinanceAPIException as e:
    st.error(f"Binance API-Fehler: {str(e)}")
except Exception as e:
    st.error(f"❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.\n{str(e)}")
