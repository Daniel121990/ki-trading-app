import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Live Bitcoin Kurs (BTCUSDT) – 1-Minuten-Aktualisierung")

# Daten speichern in der Session
if "data" not in st.session_state:
    st.session_state.data = []

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    price = float(response.json()["price"])
    timestamp = datetime.now().strftime("%H:%M:%S")
    return {"Zeit": timestamp, "Preis (USDT)": price}

# Neuen Kurs holen und speichern
new_data = get_btc_price()
st.session_state.data.append(new_data)

# DataFrame erzeugen
df = pd.DataFrame(st.session_state.data)

# Zeige Tabelle
st.subheader("📋 Aktuelle Preistabelle")
st.dataframe(df.tail(20), use_container_width=True)

# Zeige Liniendiagramm
st.subheader("📊 Live-Preisverlauf")
fig = px.line(df, x="Zeit", y="Preis (USDT)", markers=True)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Hinweis + Auto-Refresh
st.info("🔁 Seite lädt alle 60 Sekunden neu für aktuellen Kurs...")
time.sleep(60)
st.experimental_rerun()
