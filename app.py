import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")
st.title("✅ Live Binance Chart – 1-Minuten-Kerzen")

# Auswahlfeld für Symbol
symbols = ["XRPUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
symbol = st.selectbox("Asset auswählen", symbols)

# Binance API URL
def get_binance_ohlcv(symbol="XRPUSDT", interval="1m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

    return df

# Live-Daten abrufen und anzeigen
def render_chart():
    df = get_binance_ohlcv(symbol=symbol)
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name=symbol
    )])
    
    fig.update_layout(
        title=f"Live Chart – {symbol}",
        xaxis_title="Zeit",
        yaxis_title="Preis (USDT)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=600,
        yaxis=dict(
            autorange=True,
            fixedrange=False,
            tickformat=".5f"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Auto-Reload alle 30 Sekunden
countdown = st.empty()
while True:
    render_chart()
    for i in range(30, 0, -1):
        countdown.markdown(f"Aktualisierung in **{i}** Sekunden…")
        time.sleep(1)
