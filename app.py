# KI-Trading App – Binance Version mit Candlechart & Live-Analyse

import streamlit as st
import pandas as pd
from binance.client import Client
import plotly.graph_objects as go

# App Layout
st.set_page_config(layout="wide")
st.title("📊 KI-Trading App – Live Kerzenchart & Analyse")

# Binance Client (öffentliche Daten)
client = Client()

# Kategorien und Auswahlfelder
st.subheader("📁 Kategorienwahl")
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT"],
    "Aktien": ["AAPL", "TSLA", "NVDA"],  # Dummy
    "Rohstoffe": ["XAUUSD", "OILUSD"]     # Dummy
}

kategorie = st.selectbox("Kategorie wählen", list(kategorien.keys()))

suchbegriff = st.text_input("🔍 Suche nach Asset (z.B. TSLA, BTCUSDT)", "")

verfuegbare_assets = kategorien[kategorie]
if suchbegriff:
    verfuegbare_assets = [a for a in verfuegbare_assets if suchbegriff.upper() in a]

asset = st.selectbox("📈 Asset auswählen", verfuegbare_assets)
intervall = st.selectbox("🕒 Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

st.markdown(f"""
### 📍 Gewähltes Asset: `{asset}`
---
""")

# Daten von Binance holen
def get_binance_data(symbol, interval, lookback='1 day'):
    try:
        klines = client.get_historical_klines(symbol, interval, lookback)
        if not klines:
            return None
        df = pd.DataFrame(klines, columns=[
            'datetime', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df
    except Exception as e:
        st.error(f"❌ Binance-Daten konnten nicht geladen werden: {e}")
        return None

# Daten laden und anzeigen
data = get_binance_data(asset, interval)

if data is None or data.empty:
    st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
    st.stop()

# Indikatoren berechnen (nur als Werte, keine Diagramme)
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_ema(series, period=20):
    return series.ewm(span=period, adjust=False).mean()

def macd_calc(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal

close = data['close']
data['RSI'] = calc_rsi(close)
data['EMA20'] = calc_ema(close)
data['MACD'], data['Signal'] = macd_calc(close)

# Live Candlechart anzeigen
st.subheader("📊 Live Kerzenchart")
fig = go.Figure(data=[
    go.Candlestick(x=data.index,
                   open=data['open'],
                   high=data['high'],
                   low=data['low'],
                   close=data['close'])
])
fig.update_layout(height=500, margin=dict(l=0, r=0, t=25, b=0))
st.plotly_chart(fig, use_container_width=True)

# Indikator Status farblich (kein Diagramm)
st.subheader("📋 Indikator-Status (nur Werte)")

rsi = round(data['RSI'].dropna().iloc[-1], 2)
ema = round(data['EMA20'].dropna().iloc[-1], 2)
macd = round(data['MACD'].dropna().iloc[-1], 4)
signal = round(data['Signal'].dropna().iloc[-1], 4)

# Bewertung nach Farben
rsi_color = "green" if rsi < 30 or rsi > 70 else "white"
macd_color = "green" if macd > signal else ("red" if macd < signal else "white")

st.markdown(f"""
- **RSI**: <span style='color:{rsi_color};font-weight:bold'>{rsi}</span>  
- **EMA20**: {ema}  
- **MACD**: <span style='color:{macd_color};font-weight:bold'>{macd}</span> (Signal: {signal})
""", unsafe_allow_html=True)

st.success("✅ Alles läuft stabil. Jetzt bereit für KI-Logik, BUY/SELL-Signale & Prognosen.")
