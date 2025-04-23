import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# -------------------------------
# 🔧 KONFIGURATION & DESIGN
# -------------------------------
st.set_page_config(layout="wide", page_title="💰 KI-Trading App PRO", page_icon="🚀")
st.markdown("""
    <style>
    .stApp {background: #0a0a2e; color: white;}
    h1 {color: #4af7d3; border-bottom: 2px solid #4af7d3;}
    .stSelectbox div {background: #1a1a4a;}
    .st-bq {font-size: 18px;}
    .stAlert {background: #1a1a4a!important;}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 🌐 API-FUNKTIONEN (Echtzeit & Ohne Key)
# -------------------------------
def get_data(symbol, asset_type):
    # Krypto (CoinGecko)
    if asset_type == "Krypto":
        coin_id = {
            "BTC/USD": "bitcoin", 
            "ETH/USD": "ethereum",
            "XRP/USD": "ripple",
            "SOL/USD": "solana"
        }.get(symbol, "ripple")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=1"
        data = requests.get(url).json()
        df = pd.DataFrame(data, columns=["Time", "Open", "High", "Low", "Close"])
        df["Time"] = pd.to_datetime(df["Time"], unit="ms")
        df.set_index("Time", inplace=True)
        return df.astype(float)
    
    # Aktien & Rohstoffe (Yahoo Finance)
    elif asset_type == "Aktien" or asset_type == "Rohstoffe":
        interval = "2m" if asset_type == "Aktien" else "1d"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}"
        data = requests.get(url, headers={"User-Agent": ""}).json()
        prices = data["chart"]["result"][0]["indicators"]["quote"][0]
        timestamps = data["chart"]["result"][0]["timestamp"]
        df = pd.DataFrame({
            "Open": prices["open"],
            "High": prices["high"],
            "Low": prices["low"],
            "Close": prices["close"]
        }, index=pd.to_datetime(timestamps, unit="s"))
        return df.dropna()

# -------------------------------
# 🧠 KI-MODELL (LSTM für Vorhersage)
# -------------------------------
def create_model(data):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[["Close"]])
    
    X, y = [], []
    look_back = 60
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i-look_back:i, 0])
        y.append(scaled_data[i, 0])
    
    X = np.array(X).reshape(-1, look_back, 1)
    y = np.array(y)
    
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(look_back, 1)),
        LSTM(64),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=20, batch_size=32, verbose=0)
    return model, scaler

# -------------------------------
# 📈 DASHBOARD & VISUALISIERUNG
# -------------------------------
st.title("🚀 KI-Trading App PRO")
st.markdown("**Wähle ein Asset und erhalte Echtzeit-KI-Signale**")

# Asset-Auswahl
col1, col2 = st.columns(2)
with col1:
    asset_type = st.selectbox("Kategorie", ["Krypto", "Aktien", "Rohstoffe"])
    
assets = {
    "Krypto": ["BTC/USD", "ETH/USD", "XRP/USD", "SOL/USD"],
    "Aktien": ["TSLA", "AAPL", "AMZN", "NVDA"],
    "Rohstoffe": ["GC=F (Gold)", "CL=F (Öl)", "SI=F (Silber)"]
}[asset_type]

with col2:
    symbol = st.selectbox("Asset", assets)

# Daten laden
df = get_data(symbol.split(" ")[0], asset_type)
if df.empty:
    st.error("⚠️ Keine Daten gefunden. Bitte anderes Asset wählen.")
    st.stop()

# KI-Modell erstellen
if "model" not in st.session_state or st.session_state.last_symbol != symbol:
    with st.spinner("🧠 KI-Modell trainiert..."):
        st.session_state.model, st.session_state.scaler = create_model(df)
        st.session_state.last_symbol = symbol

# Vorhersage
scaled_data = st.session_state.scaler.transform(df[["Close"]][-60:])
prediction = st.session_state.model.predict(np.array([scaled_data]))
predicted_price = st.session_state.scaler.inverse_transform(prediction)[0][0]
current_price = df["Close"].iloc[-1]

trend = "🚀 KAUFEN" if predicted_price > current_price * 1.01 else \
        "🔥 VERKAUFEN" if predicted_price < current_price * 0.99 else "🛑 HALten"

# -------------------------------
# 📊 VISUALISIERUNGEN
# -------------------------------
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Aktueller Preis", f"${current_price:.2f}")
col2.metric("KI-Prognose", f"${predicted_price:.2f}", delta=f"{(predicted_price/current_price-1)*100:.2f}%")
col3.markdown(f"### <span style='color: {'#00ff00' if 'KAUFEN' in trend else '#ff0000'}'>{trend}</span>", unsafe_allow_html=True)

# Candlestick-Chart
fig = go.Figure(data=[
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing_line_color="#2ed573",
        decreasing_line_color="#ff4757"
    )
])
fig.update_layout(
    title=f"{symbol} – Letzte 24 Stunden",
    height=600,
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# ⚠️ DISCLAIMER
# -------------------------------
st.markdown("---")
st.error("""
**❗ Wichtiger Hinweis:**  
- **Keine Finanzberatung!** Diese App dient nur Demonstrationszwecken.  
- **KI-Prognosen sind unzuverlässig** – immer eigene Recherche durchführen.  
- **Kryptowährungen sind hochriskant** – nur mit Geld handeln, dessen Verlust du verkraften kannst.  
""")
