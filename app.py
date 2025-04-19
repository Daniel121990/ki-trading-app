import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px

# Layout
st.set_page_config(layout="wide")
st.title("📈 Live Bitcoin Kurs (BTCUSDT) – 1-Minuten-Aktualisierung")

# Initialisiere Session-Daten
if "data" not in st.session_state:
    st.session_state.data = []

# Funktion: BTC-Preis von Binance holen (mit Fehlerprüfung)
def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)

    try:
        data = response.json()

        # Debug-Ausgabe (kannst du auch rausnehmen)
        st.write("Binance API Antwort:", data)

        if "price" not in data:
            st.error(f"❌ Binance hat keinen 'price' geliefert: {data}")
            return None

        price = float(data["price"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        return {"Zeit": timestamp, "Preis (USDT)": price}

    except Exception as e:
        st.error(f"⚠️ Fehler beim Verarbeiten der Binance-Antwort: {e}")
        return None

# Abrufen & Speichern der aktuellen Kursdaten
new_data = get_btc_price()
if new_data:
    st.session_state.data.append(new_data)

# DataFrame erstellen
df = pd.DataFrame(st.session_state.data)

# Anzeige: Tabelle
st.subheader("📋 Aktuelle Preistabelle")
st.dataframe(df.tail(20), use_container_width=True)

# Anzeige: Live-Liniendiagramm
st.subheader("📊 Preisentwicklung")
fig = px.line(df, x="Zeit", y="Preis (USDT)", markers=True)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Auto-Reload mit Hinweis
st.info("🔁 Die Seite lädt automatisch alle 60 Sekunden neu...")
time.sleep(60)
st.experimental_rerun()
