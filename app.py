import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pandas_ta as ta
import requests

st.set_page_config(page_title="📊 KI-Trading App", layout="wide")

st.title("📊 KI-Trading App – Live Analyse & Prognose")

# --- Kategorien und Top-Assets ---
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT", "BNBUSDT", "AVAXUSDT", "DOTUSDT", "TRXUSDT"],
    "Aktien": ["AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "JPM", "V", "NFLX"],
    "Rohstoffe": ["GC=F", "SI=F", "CL=F", "BZ=F", "HG=F", "NG=F", "ZC=F", "ZS=F", "LE=F", "PL=F"]
}

# --- Auswahlfelder ---
kategorie = st.selectbox("🔍 Wähle eine Kategorie", kategorien.keys())
asset = st.selectbox("📈 Wähle dein Asset", kategorien[kategorie])
zeitintervall = st.selectbox("⏱ Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

st.markdown(f"### 📍 Gewähltes Asset: `{asset}`")

# --- Binance Klines URL für Krypto (keine API-Keys notwendig!) ---
def get_binance_ohlcv(symbol, interval="1m", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("time", inplace=True)
    df = df.astype(float)
    return df[["open", "high", "low", "close", "volume"]]

# --- Daten laden (nur Krypto via Binance für Livechart) ---
if kategorie == "Krypto":
    try:
        df = get_binance_ohlcv(asset, interval=zeitintervall)
        st.success("✅ Live-Daten geladen.")

        # --- Technische Indikatoren (RSI, EMA20, MACD) ---
        df["EMA20"] = ta.ema(df["close"], length=20)
        df["RSI"] = ta.rsi(df["close"], length=14)
        macd = ta.macd(df["close"])
        if macd is not None and "MACD_12_26_9" in macd.columns:
            df["MACD"] = macd["MACD_12_26_9"]
        else:
            df["MACD"] = np.nan

        # --- Candlestick-Chart ---
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"]
        )])
        fig.update_layout(title="📊 Kursverlauf (1-Minuten-Kerzen)", xaxis_title="Zeit", yaxis_title="Preis", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # --- Indikatorwerte anzeigen (farbcodiert) ---
        def farbe(wert, gut, neutral):
            if wert >= gut:
                return "🟢"
            elif wert <= neutral:
                return "🔴"
            else:
                return "⚪"

        st.markdown("### 🔍 Indikatoren")
        col1, col2, col3 = st.columns(3)

        rsi = round(df["RSI"].iloc[-1], 2)
        ema = round(df["EMA20"].iloc[-1], 2)
        macd = round(df["MACD"].iloc[-1], 4)

        col1.markdown(f"**RSI:** {farbe(rsi, 70, 30)} {rsi}")
        col2.markdown(f"**EMA20:** ⚪ {ema}")
        col3.markdown(f"**MACD:** ⚪ {macd}")

    except Exception as e:
        st.error(f"❌ Daten konnten nicht geladen werden. Fehler: {str(e)}")
else:
    st.warning("⚠️ Aktuell ist nur die Kategorie 'Krypto' mit Live-Kerzen aktiviert.")
