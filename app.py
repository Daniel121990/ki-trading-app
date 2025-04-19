import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Binance Live Analyse (ohne yfinance & pandas_ta)")

# --- Kategorien & Assets
st.subheader("📂 Kategorie wählen")
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
    "Rohstoffe": ["GOLDUSDT", "SILVERUSDT"]
}

kategorie = st.selectbox("Kategorie", list(kategorien.keys()))
suchbegriff = st.text_input("🔍 Suche nach Asset (z.B. BTC)", "")
verfuegbare_assets = kategorien[kategorie]
if suchbegriff:
    verfuegbare_assets = [a for a in verfuegbare_assets if suchbegriff.upper() in a.upper()]

asset = st.selectbox("Asset auswählen", verfuegbare_assets)
interval = st.selectbox("Zeitintervall", ["1m", "5m", "15m", "1h"], index=0)
interval_binance = interval

# --- Binance API Request
limit = 200  # Kerzenanzahl
url = f"https://api.binance.com/api/v3/klines?symbol={asset}&interval={interval_binance}&limit={limit}"
response = requests.get(url)
data = response.json()

# --- Umwandlung in DataFrame
cols = ["Time", "Open", "High", "Low", "Close", "Volume", "Close_time",
         "Quote_asset_volume", "Number_of_trades", "Taker_buy_base_vol",
         "Taker_buy_quote_vol", "Ignore"]
df = pd.DataFrame(data, columns=cols)
df["Time"] = pd.to_datetime(df["Time"], unit="ms")
df.set_index("Time", inplace=True)
df = df.astype(float)

# --- Indikatoren: EMA, RSI, MACD (eigenberechnet)
df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
delta = df["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))
exp1 = df["Close"].ewm(span=12, adjust=False).mean()
exp2 = df["Close"].ewm(span=26, adjust=False).mean()
df["MACD"] = exp1 - exp2
df["MACDs"] = df["MACD"].ewm(span=9, adjust=False).mean()

# --- BUY-/SELL-Signale
df["Signal"] = 0
df.loc[(df["MACD"] > df["MACDs"]) & (df["RSI"] < 70), "Signal"] = 1  # BUY
df.loc[(df["MACD"] < df["MACDs"]) & (df["RSI"] > 30), "Signal"] = -1  # SELL

# --- Chart
st.subheader("📈 Kurs + EMA + BUY-/SELL")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode='lines', name='EMA20'))
fig.add_trace(go.Scatter(x=df[df["Signal"] == 1].index, y=df[df["Signal"] == 1]["Close"],
                         mode='markers', name='BUY', marker=dict(color='green', size=8)))
fig.add_trace(go.Scatter(x=df[df["Signal"] == -1].index, y=df[df["Signal"] == -1]["Close"],
                         mode='markers', name='SELL', marker=dict(color='red', size=8)))
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# --- RSI
st.subheader("📉 RSI")
st.line_chart(df[["RSI"]].dropna())

# --- MACD
st.subheader("📈 MACD & Signal")
st.line_chart(df[["MACD", "MACDs"]].dropna())

# --- Live-Werte
st.subheader("🧭 Letzte Werte")
st.metric("Close", f"{df['Close'].iloc[-1]:.2f}")
st.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")
st.metric("MACD", f"{df['MACD'].iloc[-1]:.4f}")
st.metric("EMA20", f"{df['EMA20'].iloc[-1]:.2f}")

st.success("✅ Binance-Version stabil. Vollständig ohne yfinance & pandas_ta.")
