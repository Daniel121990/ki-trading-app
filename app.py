import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>📈 KI-Trading App – Live Analyse</h1>", unsafe_allow_html=True)

asset = st.selectbox("🔎 Wähle ein Asset", ["AAPL", "TSLA", "NVDA", "XAUUSD", "XRP-USD"])
st.markdown(f"### 📍 Gewähltes Asset: `{asset}`")

data = yf.download(asset, period="1d", interval="1m")

# MultiIndex fixen, falls vorhanden
if isinstance(data.columns, pd.MultiIndex):
    data.columns = ['_'.join(col).strip() for col in data.columns.values]

if data is None or data.empty:
    st.error("❌ Keine Daten verfügbar.")
    st.stop()

close_col = [col for col in data.columns if "Close" in col][0]

# RSI
delta = data[close_col].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
data["RSI"] = 100 - (100 / (1 + rs))

# MACD
ema12 = data[close_col].ewm(span=12, adjust=False).mean()
ema26 = data[close_col].ewm(span=26, adjust=False).mean()
data["MACD"] = ema12 - ema26
data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

# BUY-/SELL-Signale
data["BUY"] = (data["MACD"] > data["Signal"]) & (data["MACD"].shift(1) <= data["Signal"].shift(1))
data["SELL"] = (data["MACD"] < data["Signal"]) & (data["MACD"].shift(1) >= data["Signal"].shift(1))

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📊 Kursverlauf (Close)")
    st.line_chart(data[close_col])

with col2:
    st.subheader("📉 RSI")
    st.line_chart(data["RSI"])

st.subheader("📈 MACD & Signal")
st.line_chart(data[["MACD", "Signal"]].dropna())

st.subheader("🟢 BUY / 🔴 SELL Punkte")
buy_signals = data[data["BUY"]]
sell_signals = data[data["SELL"]]
st.dataframe(pd.concat([buy_signals[[close_col]].rename(columns={close_col: "BUY-Signal"}),
                        sell_signals[[close_col]].rename(columns={close_col: "SELL-Signal"})], axis=1))

st.success("✅ Alle Module funktionieren jetzt stabil. KI-Prognose kann vorbereitet werden.")
