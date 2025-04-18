# KI-Trading App – Live Kerzenchart & Analyse (Binance, stabil, ohne API-Key)

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 KI-Trading App – Live Kerzenchart & Analyse")

# Kategorien
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT"],
    "Aktien": ["TSLA", "AAPL", "NVDA"],
    "Rohstoffe": ["XAUUSD", "XAGUSD"]
}

# Auswahlfelder
col1, col2, col3 = st.columns(3)
with col1:
    kategorie = st.selectbox("Kategorie wählen", kategorien.keys())
with col2:
    suche = st.text_input("🔍 Suche nach Asset (z. B. TSLA, ETHUSDT)")
with col3:
    interval = st.selectbox("🕒 Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

# Asset-Auswahl
assets = kategorien[kategorie]
if suche:
    assets = [s for s in assets if suche.upper() in s.upper() or suche == ""]
asset = st.selectbox("Asset auswählen", assets)

# Binance API Endpoint
url = f"https://api.binance.com/api/v3/klines?symbol={asset}&interval={interval}&limit=200"
try:
    response = requests.get(url)
    response.raise_for_status()
    klines = response.json()

    df = pd.DataFrame(klines, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)
    df = df.astype(float)

    # Werte berechnen
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["RSI"] = 100 - (100 / (1 + df["close"].pct_change().rolling(14).apply(lambda x: (x[x>0].mean() / abs(x[x<0].mean())) if abs(x[x<0].mean()) > 0 else 0)))

    # RSI-Status
    rsi = df["RSI"].iloc[-1]
    rsi_color = "white"
    if rsi > 70:
        rsi_color = "red"
    elif rsi < 30:
        rsi_color = "green"

    # EMA-Status
    ema = df["EMA20"].iloc[-1]
    close = df["close"].iloc[-1]
    ema_color = "green" if close > ema else "red"

    # Kerzenchart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candles"
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Indikatoren anzeigen
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📈 RSI", f"{rsi:.2f}", delta_color="off")
        st.markdown(f"<span style='color:{rsi_color}'>Bewertung: {rsi_color.upper()}</span>", unsafe_allow_html=True)
    with col2:
        st.metric("📉 EMA20", f"{ema:.2f}", delta=f"{(close - ema):.2f}")
        st.markdown(f"<span style='color:{ema_color}'>Kurs {'über' if close > ema else 'unter'} EMA</span>", unsafe_allow_html=True)

    st.success("✅ Live-Daten & Kerzenchart geladen.")

except Exception as e:
    st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
    st.exception(e)
