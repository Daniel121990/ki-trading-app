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
# 🔧 KONFIGURATION & DESIGN
# -------------------------------
st.set_page_config(layout="wide", page_title="💰 KI-Trading PRO", page_icon="🚀")
st.markdown("""
    <style>
    .stApp {background: #0a0a2e; color: white;}
    h1 {color: #4af7d3; border-bottom: 2px solid #4af7d3;}
    .stSelectbox div {background: #1a1a4a;}
    .stAlert {background: #1a1a4a!important;}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 🌐 DATENABFRAGE (Mit Caching & Fehlerbehandlung)
# -------------------------------
@st.cache_data(ttl=300, show_spinner="Lade Echtzeitdaten...")
def get_data(symbol: str, asset_type: str) -> pd.DataFrame:
    try:
        # Krypto (CoinGecko)
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
        
        # Aktien & Rohstoffe (Yahoo Finance)
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
            return df.dropna().astype(float)
    
    except Exception as e:
        st.error(f"🚨 Fehler: {str(e)}")
        return pd.DataFrame()

# -------------------------------
# 🧠 KI-MODELL (Mit Fortschrittsbalken)
# -------------------------------
def create_model(data: pd.DataFrame):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[["Close"]])
    
    # Sequenzerstellung
    X, y = [], []
    look_back = 60
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i-look_back:i, 0])
        y.append(scaled_data[i, 0])
    
    X = np.array(X).reshape(-1, look_back, 1)
    y = np.array(y)
    
    # Modellarchitektur
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(look_back, 1)),
        LSTM(64),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    
    # Training mit Fortschrittsbalken
    progress_bar = st.progress(0)
    for epoch in range(20):
        model.fit(X, y, epochs=1, batch_size=32, verbose=0)
        progress_bar.progress((epoch + 1) / 20)
    
    return model, scaler

# -------------------------------
# 📈 HAUPTAPP
# -------------------------------
st.title("🚀 KI-Trading PRO")
with st.expander("ℹ️ Signal-Erklärung"):
    st.markdown("""
    - **🚀 KAUFEN**: Vorhersage >1% über aktuellem Preis  
    - **🔥 VERKAUFEN**: Vorhersage <1% unter aktuellem Preis  
    - **🛑 HALten**: Innerhalb ±1% Schwankung  
    """)

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
df = get_data(symbol, asset_type)
if df.empty:
    st.warning("⚠️ Keine Daten verfügbar. Bitte Asset wechseln.")
    st.stop()

# Modelltraining
if "model" not in st.session_state or st.session_state.last_symbol != symbol:
    with st.spinner("Trainiere KI-Modell..."):
        st.session_state.model, st.session_state.scaler = create_model(df)
        st.session_state.last_symbol = symbol

# Vorhersage
scaled_data = st.session_state.scaler.transform(df[["Close"]][-60:])
prediction = st.session_state.model.predict(scaled_data.reshape(1, 60, 1))
predicted_price = st.session_state.scaler.inverse_transform(prediction)[0][0]
current_price = df["Close"].iloc[-1]

trend = "🚀 KAUFEN" if predicted_price > current_price * 1.01 else \
        "🔥 VERKAUFEN" if predicted_price < current_price * 0.99 else "🛑 HALten"

# -------------------------------
# 📊 DASHBOARD
# -------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Aktuell", f"${current_price:.2f}")
col2.metric("Prognose", f"${predicted_price:.2f}", f"{(predicted_price/current_price-1)*100:.2f}%")
col3.markdown(f"### <span style='color: {'#00ff00' if 'KAUFEN' in trend else '#ff0000' if 'VERKAUFEN' in trend else '#ffffff'}'>\
             {trend}</span>", unsafe_allow_html=True)

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
fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# ⚠️ DISCLAIMER
# -------------------------------
st.error("""
**❗ Wichtig:**  
- **Keine Finanzberatung!** Nur zu Demonstrationszwecken.  
- **KI-Prognosen sind unsicher** – immer eigenes Research durchführen.  
- **Risikohinweis:** Bis zu 100% Verlust möglich.  
""")
