import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 BTCUSDT Demo – Historische 5-Minuten-Daten aus CSV")

# CSV laden
try:
    df = pd.read_csv("historisch_btc_5min.csv")
    df["Zeit"] = pd.to_datetime(df["Zeit"])
    df.set_index("Zeit", inplace=True)
except Exception as e:
    st.error(f"❌ Fehler beim Laden der CSV-Datei: {e}")
    st.stop()

# EMA, RSI, MACD berechnen
df["EMA20"] = df["Preis"].ewm(span=20, adjust=False).mean()
delta = df["Preis"].diff()
gain = delta.clip(lower=0).rolling(window=14).mean()
loss = -delta.clip(upper=0).rolling(window=14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))
exp1 = df["Preis"].ewm(span=12, adjust=False).mean()
exp2 = df["Preis"].ewm(span=26, adjust=False).mean()
df["MACD"] = exp1 - exp2
df["MACDs"] = df["MACD"].ewm(span=9, adjust=False).mean()

# BUY-/SELL Signale
df["Signal"] = 0
df.loc[(df["MACD"] > df["MACDs"]) & (df["RSI"] < 70), "Signal"] = 1
    
df.loc[(df["MACD"] < df["MACDs"]) & (df["RSI"] > 30), "Signal"] = -1

# Chart
st.subheader("📈 Kursverlauf mit EMA & Signalen")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Preis"], mode='lines', name='Preis'))
fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode='lines', name='EMA20'))
fig.add_trace(go.Scatter(x=df[df["Signal"] == 1].index, y=df[df["Signal"] == 1]["Preis"],
                         mode='markers', name='BUY', marker=dict(color='green', size=8)))
fig.add_trace(go.Scatter(x=df[df["Signal"] == -1].index, y=df[df["Signal"] == -1]["Preis"],
                         mode='markers', name='SELL', marker=dict(color='red', size=8)))
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# RSI & MACD
st.subheader("📉 RSI")
st.line_chart(df[["RSI"]].dropna())

st.subheader("📈 MACD & Signal")
st.line_chart(df[["MACD", "MACDs"]].dropna())

# Aktuelle Werte
st.subheader("🧭 Letzte Werte")
st.metric("Letzter Preis", f"{df['Preis'].iloc[-1]:.2f}")
st.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")
st.metric("MACD", f"{df['MACD'].iloc[-1]:.4f}")
st.metric("EMA20", f"{df['EMA20'].iloc[-1]:.2f}")

st.success("✅ CSV-Demo-Modus aktiv. Daten & Indikatoren erfolgreich geladen.")
