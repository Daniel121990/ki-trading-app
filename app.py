import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from binance.client import Client
from dotenv import load_dotenv
import os
import time

# .env laden mit API Key + Secret
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Binance-Client initialisieren mit Key + Secret
client = Client(api_key=api_key, api_secret=api_secret)

st.set_page_config(layout="wide")
st.title("📈 Live Binance Chart – mit API Key (1-Minuten-Kerzen)")

# Auswahl: Coin-Paare
symbols = ["XRPUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
symbol = st.selectbox("Asset auswählen", symbols)

# Binance OHLCV abrufen
def get_binance_ohlcv(symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

# Candlestick-Chart zeichnen
def render_chart(df, symbol):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(
        title=f"Live Chart – {symbol}",
        xaxis_title="Zeit",
        yaxis_title="Preis (USDT)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
        yaxis=dict(
            autorange=True,
            fixedrange=False,
            tickformat=".5f"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Countdown anzeigen
countdown = st.empty()

# Live-Loop
while True:
    try:
        df = get_binance_ohlcv(symbol)
        render_chart(df, symbol)
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
    for i in range(30, 0, -1):
        countdown.markdown(f"🔄 Aktualisierung in **{i}** Sekunden…")
        time.sleep(1)
