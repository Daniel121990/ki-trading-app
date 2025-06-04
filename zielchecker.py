import streamlit as st
import pandas as pd
import requests

def get_chart_data(symbol="^GDAXI", interval="1h", range_="1mo"):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()["chart"]["result"][0]
        ts = pd.to_datetime(data["timestamp"], unit="s")
        q = data["indicators"]["quote"][0]
        df = pd.DataFrame(q, index=ts)[["open", "high", "low", "close"]]
        df.columns = ["Open", "High", "Low", "Close"]
        return df.dropna()
    except Exception as e:
        st.error(f"Datenabruf fehlgeschlagen: {e}")
        return pd.DataFrame()

def run_zielchecker(asset: str) -> None:
    st.subheader("🎯 Zielchecker")

    df = get_chart_data(asset)
    if df.empty:
        st.warning("⚠️ Keine Kursdaten verfügbar.")
        return

    aktueller = df["Close"].iloc[-1]
    zielwert = st.number_input("Kursziel eingeben (€)", value=float(aktueller), key="ziel_input")

    if st.button("Ziel prüfen", key="ziel_button"):
        if len(df) < 200:
            st.warning("⚠️ Mindestens 200 Datenpunkte erforderlich.")
            return

        ema50 = df["Close"].ewm(span=50).mean()
        ema200 = df["Close"].ewm(span=200).mean()
        trend = "Aufwärts" if ema50.iloc[-1] > ema200.iloc[-1] else "Abwärts"
        support = df["Low"].rolling(window=20).min().iloc[-1]
        resistance = df["High"].rolling(window=20).max().iloc[-1]
        wahrscheinlichkeit = 0.7 if support <= zielwert <= resistance else 0.3

        st.metric("Wahrscheinlichkeit", f"{wahrscheinlichkeit * 100:.0f}%")
        st.metric("Trendrichtung", trend)
        st.metric("Support", f"{support:.2f}")
        st.metric("Widerstand", f"{resistance:.2f}")
