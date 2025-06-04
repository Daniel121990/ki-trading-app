import streamlit as st
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

st.set_page_config(page_title="📊 GER40 NeuroTrader", layout="wide")

st.title("📊 GER40 Spezialmodule")

# Daten holen
def get_ger40_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^GDAXI?interval=5m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()["chart"]["result"][0]
        ts = pd.to_datetime(data["timestamp"], unit="s")
        quotes = data["indicators"]["quote"][0]
        df = pd.DataFrame(quotes, index=ts)[["open", "high", "low", "close"]]
        df.columns = ["Open", "High", "Low", "Close"]
        return df.dropna()
    except:
        return pd.DataFrame()

# Modul-Auswahl
modul = st.selectbox("Modul auswählen", [
    "Bitte wählen...",
    "GER40-Hebelstrategie",
    "Zielchecker",
    "Signal-Analyse"
])

# Hebelstrategie
if modul == "GER40-Hebelstrategie":
    st.subheader("GER40-Hebelstrategie")
    kapital = st.number_input("Kapital (€)", value=1000.0)
    hebel = st.number_input("Hebel", value=2.0)
    stop = st.number_input("Stop-Loss (%)", value=2.0)
    ziel = st.number_input("Take-Profit (%)", value=4.0)
    if st.button("Berechnen"):
        risiko = kapital * (stop / 100)
        gewinn = kapital * (ziel / 100)
        st.success(f"Risiko: {risiko:.2f} € / Gewinnchance: {gewinn:.2f} €")
    df = get_ger40_data()
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"]
        )])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# Zielchecker
elif modul == "Zielchecker":
    st.subheader("Zielchecker (GER40)")
    ziel = st.number_input("Kursziel eingeben (€)")
    df = get_ger40_data()
    if not df.empty:
        aktueller = df["Close"].iloc[-1]
        delta = ((aktueller - ziel) / ziel) * 100
        st.metric("Aktueller Kurs", f"{aktueller:.2f} €", f"{delta:.2f} %")
        if st.button("Ziel prüfen"):
            if aktueller >= ziel:
                st.success("🎯 Ziel erreicht!")
            else:
                st.info("⏳ Noch nicht erreicht.")

# Signal-Analyse
elif modul == "Signal-Analyse":
    st.subheader("Signal-Analyse")
    file = st.file_uploader("CSV hochladen (Signal & Ergebnis)", type="csv")
    if file:
        df = pd.read_csv(file)
        st.write(df.head())
        try:
            treffer = df[df["Signal"] == df["Ergebnis"]].shape[0]
            quote = (treffer / len(df)) * 100
            st.success(f"Trefferquote: {quote:.2f} %")
        except:
            st.error("⚠️ Spalten 'Signal' und 'Ergebnis' fehlen?")
