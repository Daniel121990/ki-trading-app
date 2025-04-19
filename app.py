import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

st.set_page_config(layout="wide")
st.title("📈 Live Binance Chart – 1-Minuten-Kerzen")

# Coins zur Auswahl
symbols = ["XRPUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
symbol = st.selectbox("Asset auswählen", symbols)

# Binance OHLCV-Daten holen (kein Key nötig!)
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

# Chart anzeigen
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

# Loop für Auto-Update
countdown = st.empty()

while True:
    try:
        df = get_binance_ohlcv(symbol)
        if df.empty:
            st.warning("⚠️ Keine Daten erhalten.")
        else:
            render_chart(df, symbol)
            st.dataframe(df.tail(5))  # Zeige letzte 5 Zeilen zur Kontrolle
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")

    for i in range(30, 0, -1):
        countdown.markdown(f"🔄 Aktualisierung in **{i}** Sekunden…")
        time.sleep(1)
