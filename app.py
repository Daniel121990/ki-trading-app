import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
import streamlit as st

# 🕒 Simuliere 1-Minuten-Daten der letzten Stunde
now = datetime.datetime.now()
timestamps = pd.date_range(end=now, periods=60, freq='T')
close_prices = np.cumsum(np.random.randn(60)) + 30000  # Beispiel: BTC-Schlusskurse
data = pd.DataFrame({'Timestamp': timestamps, 'Close': close_prices})
data.set_index('Timestamp', inplace=True)

# 📊 Indikatoren berechnen
def calculate_ema(series, period=20):
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data['EMA20'] = calculate_ema(data['Close'])
data['RSI'] = calculate_rsi(data['Close'])

# 📈 Chart
st.set_page_config(layout="wide", page_title="Simulierter BTC Chart")
st.title("📈 KI Trading App – Simulierter BTC-Kurs mit RSI & EMA")

fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], mode='lines', name='EMA20'))

fig.update_layout(title="📉 Kursverlauf – 1-Minuten-Kerzen", height=400, xaxis_title="Zeit", yaxis_title="Preis (USD)")
st.plotly_chart(fig, use_container_width=True)

# 🔍 Werte farblich anzeigen
def get_color(val, low, high):
    if pd.isna(val): return "gray"
    if val < low: return "red"
    if val > high: return "green"
    return "white"

rsi_val = round(data["RSI"].iloc[-1], 2)
ema_val = round(data["EMA20"].iloc[-1], 2)
close_val = round(data["Close"].iloc[-1], 2)

st.markdown(f"- **Letzter Schlusskurs:** <span style='color:white'>{close_val} USD</span>", unsafe_allow_html=True)
st.markdown(f"- **EMA20:** <span style='color:{get_color(ema_val, 0, float('inf'))}'>{ema_val}</span>", unsafe_allow_html=True)
st.markdown(f"- **RSI:** <span style='color:{get_color(rsi_val, 30, 70)}'>{rsi_val}</span>", unsafe_allow_html=True)

st.success("✅ Simulierte Kursdaten wurden erfolgreich geladen.")
