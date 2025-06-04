import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="DAX Test", layout="wide")
st.title("📈 DAX (GER40) Live-Chart – Minimale Version")

# Kursdaten holen
def get_dax():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^GDAXI?interval=5m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()["chart"]["result"][0]
        ts = pd.to_datetime(data["timestamp"], unit="s")
        q = data["indicators"]["quote"][0]
        df = pd.DataFrame(q, index=ts)[["open", "high", "low", "close"]]
        df.columns = ["Open", "High", "Low", "Close"]
        return df
    except Exception as e:
        st.error(f"Fehler beim Datenabruf: {e}")
        return pd.DataFrame()

# Chart anzeigen
df = get_dax()
if not df.empty:
    st.success("Daten erfolgreich geladen ✅")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"]
    )])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Keine Daten empfangen – Internetverbindung prüfen?")
