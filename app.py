import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

# Auswahlfeld mit Assets
asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])

# Daten laden
data = yf.download(asset, period="1d", interval="1m")
data.dropna(inplace=True)

# Technische Indikatoren berechnen
data["EMA20"] = ta.ema(data["Close"], length=20)
data["RSI"] = ta.rsi(data["Close"], length=14)
macd = ta.macd(data["Close"])
data["MACD"] = macd["MACD_12_26_9"]
data["MACDs"] = macd["MACDs_12_26_9"]

# BUY-/SELL-Signale setzen (einfaches Beispiel)
data["Signal"] = 0
data.loc[(data["MACD"] > data["MACDs"]) & (data["RSI"] < 70), "Signal"] = 1  # BUY
data.loc[(data["MACD"] < data["MACDs"]) & (data["RSI"] > 30), "Signal"] = -1  # SELL

# Chart erstellen
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], mode='lines', name='EMA20'))

# BUY-/SELL-Signale als Punkte einzeichnen
fig.add_trace(go.Scatter(x=data[data["Signal"] == 1].index, y=data[data["Signal"] == 1]["Close"],
                         mode='markers', name='BUY', marker=dict(color='green', size=8)))
fig.add_trace(go.Scatter(x=data[data["Signal"] == -1].index, y=data[data["Signal"] == -1]["Close"],
                         mode='markers', name='SELL', marker=dict(color='red', size=8)))

fig.update_layout(title=f"Live Chart für {asset}", height=600)
st.plotly_chart(fig, use_container_width=True)

# RSI-Anzeige
st.subheader("📉 RSI")
st.line_chart(data[["RSI"]].dropna())

# MACD-Anzeige
st.subheader("📈 MACD & Signal")
st.line_chart(data[["MACD", "MACDs"]].dropna())

# Legende der aktuellen Werte
st.subheader("🧭 Indikatorwerte")
st.metric("Letzter Schlusskurs", f"{data['Close'].iloc[-1]:.2f}")
st.metric("RSI", f"{data['RSI'].iloc[-1]:.2f}")
st.metric("MACD", f"{data['MACD'].iloc[-1]:.4f}")
st.metric("EMA20", f"{data['EMA20'].iloc[-1]:.2f}")

st.info("✅ KI-Logik aktiv. Prognosemodul in Entwicklung. Weitere Indikatoren folgen bei Bedarf.")
