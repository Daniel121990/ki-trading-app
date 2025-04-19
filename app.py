import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Live Bitcoin Kurs (BTCUSDT) – 1-Minuten-Aktualisierung")

# Initialisierung der Session-Daten
if "data" not in st.session_state:
    st.session_state.data = []

# Funktion: BTC-Preis von Binance holen
def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)

    try:
        data = response.json()
        price = float(data["price"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        return {"Zeit": timestamp, "Preis (USDT)": price}
    except (KeyError, ValueError, TypeError):
        st.error("⚠️ Fehler beim Abrufen des Bitcoin-Preises. Binance-Antwort ungültig.")
        return None

# Neuen Preis holen
new_data = get_btc_price()
if new_data:
    st.session_state.data.append(new_data)

# DataFrame erzeugen
df = pd.DataFrame(st.session_state.data)

# Anzeige: Tabelle
st.subheader("📋 Aktuelle Preistabelle")
st.dataframe(df.tail(20), use_container_width=True)

# Anzeige: Liniendiagramm
st.subheader("📊 Live-Preisverlauf")
fig = px.line(df, x="Zeit", y="Preis (USDT)", markers=True)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Hinweis + automatische Aktualisierung
st.info("🔁 Die Seite wird alle 60 Sekunden automatisch aktualisiert.")
time.sleep(60)
st.experimental_rerun()
