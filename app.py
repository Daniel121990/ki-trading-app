import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Live Bitcoin Kurs (BTCUSDT) – 1-Minuten-Aktualisierung")

if "data" not in st.session_state:
    st.session_state.data = []

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)

    try:
        data = response.json()

        # Fehlerbehandlung, falls kein 'price' im JSON vorhanden ist
        if "price" not in data:
            st.error(f"❌ Binance hat keinen 'price' geliefert: {data}")
            return None

        price = float(data["price"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        return {"Zeit": timestamp, "Preis (USDT)": price}

    except Exception as e:
        st.error(f"⚠️ Fehler beim Verarbeiten der Binance-Antwort: {e}")
        return None

# Neue Kursdaten holen und speichern
new_data = get_btc_price()
if new_data:
    st.session_state.data.append(new_data)

# Tabelle anzeigen
df = pd.DataFrame(st.session_state.data)
st.subheader("📋 Aktuelle Preistabelle")
st.dataframe(df.tail(20), use_container_width=True)

# Diagramm anzeigen
st.subheader("📊 Preisentwicklung")
fig = px.line(df, x="Zeit", y="Preis (USDT)", markers=True)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Automatische Aktualisierung
st.info("🔁 Seite wird alle 60 Sekunden aktualisiert...")
time.sleep(60)
st.experimental_rerun()
