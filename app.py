# 📂 app.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

# -------------------------------
# 🔧 UI & DESIGN
# -------------------------------
st.set_page_config(layout="wide", page_title="💰 KI-Trading PRO", page_icon="🚀")
st.markdown("""
    <style>
    .stApp {background-color: #0a0a2e; color: white;}
    h1 {color: #4af7d3; border-bottom: 2px solid #4af7d3;}
    .stSelectbox div {background: #1a1a4a;}
    .stAlert {background: #1a1a4a!important;}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 🌐 DATENABFRAGE
# -------------------------------
@st.cache_data(ttl=300)
def get_data(symbol: str, asset_type: str) -> pd.DataFrame:
    try:
        if asset_type == "Krypto":
            coin_id = {
                "BTC/USD": "bitcoin", "ETH/USD": "ethereum",
                "XRP/USD": "ripple", "SOL/USD": "solana"
            }.get(symbol, "ripple")
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=["Time", "Open", "High", "Low", "Close"])
            df["Time"] = pd.to_datetime(df["Time"], unit="ms")
            df.set_index("Time", inplace=True)
            return df.astype(float)
        else:
            symbol_clean = symbol.split(" ")[0]
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol_clean}?interval=2m"
            response = requests.get(url, headers={"User-Agent": ""}, timeout=10)
            response.raise_for_status()
            data = response.json()
            prices = data["chart"]["result"][0]["indicators"]["quote"][0]
            timestamps = data["chart"]["result"][0]["timestamp"]
            df = pd.DataFrame({
                "Open": prices["open"],
                "High": prices["high"],
                "Low": prices["low"],
                "Close": prices["close"]
            }, index=pd.to_datetime(timestamps, unit="s"))
            df = df[df["Close"].notnull()]
            return df.astype(float)
    except Exception as e:
        st.error(f"🚨 Fehler beim Laden: {e}")
        return pd.DataFrame()

# -------------------------------
# 🧠 KI-MODELL
# -------------------------------
def create_model(data: pd.DataFrame):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data[["Close"]])

    X, y = [], []
    look_back = 60
    for i in range(look_back, len(scaled)):
        X.append(scaled[i-look_back:i, 0])
        y.append(scaled[i, 0])

    X = np.array(X).reshape(-1, look_back, 1)
    y = np.array(y)

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(look_back, 1)),
        LSTM(64),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")

    progress = st.progress(0)
    for epoch in range(20):
        model.fit(X, y, epochs=1, batch_size=32, verbose=0)
        progress.progress((epoch + 1) / 20)

    return model, scaler

# -------------------------------
# 📈 START DER APP
# -------------------------------
st.title("🚀 KI-Trading PRO")
with st.expander("ℹ️ Signal-Erklärung"):
    st.markdown("""
    - **🚀 KAUFEN**: Prognose > 1 % über aktuellem Preis  
    - **🔥 VERKAUFEN**: Prognose < 1 % unter aktuellem Preis  
    - **🛑 HALten**: Innerhalb ±1 % Spanne
    """)

# Auswahl
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

# Daten holen
df = get_data(symbol, asset_type)
if df.empty:
    st.warning("⚠️ Keine Daten verfügbar.")
    st.stop()

# Modell laden/trainieren
if "model" not in st.session_state or st.session_state.get("last_symbol") != symbol:
    with st.spinner("Trainiere Modell..."):
        st.session_state.model, st.session_state.scaler = create_model(df)
        st.session_state.last_symbol = symbol

# Prognose berechnen
scaled_last = st.session_state.scaler.transform(df[["Close"]][-60:])
prediction = st.session_state.model.predict(scaled_last.reshape(1, 60, 1))
predicted_price = st.session_state.scaler.inverse_transform(prediction)[0][0]
current_price = df["Close"].iloc[-1]

trend = "🚀 KAUFEN" if predicted_price > current_price * 1.01 else \
        "🔥 VERKAUFEN" if predicted_price < current_price * 0.99 else "🛑 HALten"

# Anzeige
col1, col2, col3 = st.columns(3)
col1.metric("Aktuell", f"${current_price:.2f}")
col2.metric("Prognose", f"${predicted_price:.2f}", f"{(predicted_price/current_price - 1)*100:.2f}%")
col3.markdown(f"### <span style='color: {'#00ff00' if 'KAUFEN' in trend else '#ff0000' if 'VERKAUFEN' in trend else '#ffffff'}'>{trend}</span>", unsafe_allow_html=True)

# Chart
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
fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Disclaimer
st.error("""
**❗ Hinweis:**  
- Dieses Tool stellt keine Finanzberatung dar.  
- Prognosen der KI können falsch sein.  
- Investitionen sind mit Risiko verbunden.
""")
