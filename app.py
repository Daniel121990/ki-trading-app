import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Binance Analyse (Fallback-Modus mit Zeit/Preis)")

# --- Kategorien & Assets
st.subheader("📂 Kategorie wählen")
kategorien = {
    "Krypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT"]
}

kategorie = st.selectbox("Kategorie", list(kategorien.keys()))
suchbegriff = st.text_input("🔍 Suche nach Asset (z. B. BTC)", "")
verfuegbare_assets = kategorien[kategorie]
if suchbegriff:
    verfuegbare_assets = [a for a in verfuegbare_assets if suchbegriff.upper() in a.upper()]

asset = st.selectbox("Asset auswählen", verfuegbare_assets)
interval = st.selectbox("Zeitintervall", ["5m", "15m", "1h"], index=0)

# --- Binance API für Preis-Zeit-Rohdaten (vereinfachter Fallback)
url = f"https://api.binance.com/api/v3/klines?symbol={asset}&interval={interval}&limit=50"
response = requests.get(url)

try:
    data = response.json()
    if not isinstance(data, list) or len(data) == 0:
        st.error("❌ Binance hat keine Daten geliefert. Bitte versuche es später erneut.")
        st.stop()

    timestamps = [datetime.fromtimestamp(candle[0]/1000) for candle in data]
    close_prices = [float(candle[4]) for candle in data]

    df = pd.DataFrame({
        "Zeit": timestamps,
        "Preis": close_prices
    })
    df.set_index("Zeit", inplace=True)

    # --- Chart anzeigen
    st.subheader("📈 Preisverlauf (nur Zeit & Close)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Preis"], mode='lines+markers', name='Preis'))
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # --- Aktuelle Werte anzeigen
    st.subheader("📌 Letzter Wert")
    st.metric("Preis", f"{df['Preis'].iloc[-1]:.2f}")

    # --- Datenvorschau
    st.subheader("🧾 Datenvorschau")
    st.dataframe(df.tail(10))

    st.success("✅ Fallback-Modus aktiv: Nur Zeit + Preis geladen und angezeigt.")

except Exception as e:
    st.error(f"❌ Fehler beim Verarbeiten der Daten: {e}")
    st.code(response.text, language="json")
