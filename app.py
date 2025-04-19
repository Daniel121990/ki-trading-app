import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Live Bitcoin Preis (BTC/USDT) – 1-Minuten-Intervalle")

# Leere Liste zur Speicherung der Daten
if "price_data" not in st.session_state:
    st.session_state.price_data = []

def get_live_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    price = float(response.json()["price"])
    timestamp = datetime.now().strftime("%H:%M:%S")
    return timestamp, price

# Hole neuen Preis + speichere ihn
timestamp, price = get_live_price()
st.session_state.price_data.append({"Zeit": timestamp, "Preis (USDT)": price})

# In DataFrame umwandeln
df = pd.DataFrame(st.session_state.price_data)

# Tabelle anzeigen
st.subheader("Preisentwicklung (Live-Tabelle)")
st.dataframe(df.tail(20), use_container_width=True)

# Chart anzeigen
st.subheader("Live-Preisverlauf")
fig = px.line(df, x="Zeit", y="Preis (USDT)", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Auto-Reload alle 60 Sekunden
st.info("Aktualisiere alle 60 Sekunden...")
time.sleep(60)
st.experimental_rerun()
