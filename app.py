import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from binance.client import Client
import time

# Binance-Client ohne API-Key (für öffentliche Daten reicht das)
client = Client()

# Streamlit Setup
st.set_page_config(layout="wide")
st.title("📈 Live Binance Chart – 1-Minuten-Kerzen (über python-binance)")

# Dropdown für Symbolauswahl
symbols = ["XRPUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
symbol = st.selectbox("Asset auswählen", symbols)

# OHLCV-Daten von Binance holen
def get_binance_ohlcv(symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100):
    try:
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

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame()

# Chart zeichnen
def render_chart(df, symbol):
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

# Countdown anzeigen
countdown = st.empty()

# Endlosschleife für Live-Update
while True:
    df = get_binance_ohlcv(symbol)
    if not df.empty:
        render_chart(df, symbol)
    else:
        st.warning("Keine Daten geladen.")
    for i in range(30, 0, -1):
        countdown.markdown(f"🔄 Aktualisierung in **{i}** Sekunden…")
        time.sleep(1)
