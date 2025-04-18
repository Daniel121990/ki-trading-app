import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("KI-Trading App – Live Analyse & Prognose")

asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
data = yf.download(asset, period="1d", interval="1m")

data["EMA20"] = ta.ema(data["Close"], length=20)
data["RSI"] = ta.rsi(data["Close"], length=14)
macd = ta.macd(data["Close"])
data["MACD"] = macd["MACD_12_26_9"]
data["MACDs"] = macd["MACDs_12_26_9"]

st.line_chart(data[["Close", "EMA20"]].dropna())
st.line_chart(data[["RSI"]].dropna())
st.line_chart(data[["MACD", "MACDs"]].dropna())

st.success("KI-Signale & Candle-Prognose folgen im Ausbau")
