import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# 🔧 Konfiguration
st.set_page_config(layout="wide", page_title="XRP KI-Trading App")
st.markdown("""
    <style>
    .stApp {background-color: #0e1117; color: white;}
    .st-bq {color: #ff4b4b;}
    </style>
    """, unsafe_allow_html=True)
st.title("🚀 XRP KI-Trading App (Mit Echtzeit-Signalen)")

# 🌐 API-Funktionen (OHNE API-Key!)
@st.cache_data(ttl=60)
def get_xrp_data():
    # CoinGecko API (XRP/USD)
    url = "https://api.coingecko.com/api/v3/coins/ripple/market_chart?vs_currency=usd&days=30&interval=hourly"
    data = requests.get(url).json()
    df = pd.DataFrame(data['prices'], columns=['Time', 'Close'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df.set_index('Time', inplace=True)
    return df

# 🧠 KI-Modell (LSTM)
def create_lstm_model(data):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[['Close']])
    
    X, y = [], []
    look_back = 24  # 24 Stunden
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i-look_back:i, 0])
        y.append(scaled_data[i, 0])
    
    X = np.array(X).reshape(-1, look_back, 1)
    y = np.array(y)
    
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(look_back, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=15, batch_size=32, verbose=0)
    return model, scaler

# 📈 Technische Indikatoren
def add_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).apply(lambda x: (np.where(x < 0, -x, 0).mean() / np.where(x > 0, x, 0).mean())))
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    return df

# 🎯 Signalgenerierung
def generate_signal(model, scaler, data):
    look_back = 24
    scaled_data = scaler.transform(data[['Close']][-look_back:])
    prediction = model.predict(np.array([scaled_data]))
    predicted_price = scaler.inverse_transform(prediction)[0][0]
    current_price = data['Close'].iloc[-1]
    
    if predicted_price > current_price * 1.03:
        return "🚀 STRONG BUY", predicted_price, "#00FF00"
    elif predicted_price > current_price:
        return "📈 BUY", predicted_price, "#90EE90"
    elif predicted_price < current_price * 0.97:
        return "🔥 STRONG SELL", predicted_price, "#FF0000"
    else:
        return "🛑 HOLD", predicted_price, "#FFFFFF"

# 🖥️ Hauptprogramm
df = get_xrp_data()
df = add_indicators(df)

if 'model' not in st.session_state:
    st.session_state.model, st.session_state.scaler = create_lstm_model(df)

signal, price, color = generate_signal(st.session_state.model, st.session_state.scaler, df)

# 📊 Dashboard
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### 🧠 **KI-Empfehlung**  \n<span style='color:{color}; font-size: 24px'>{signal}</span>", unsafe_allow_html=True)
    st.markdown(f"- **Vorhergesagter Preis:** ${price:.4f}")
    st.markdown(f"- **Aktueller Preis:** ${df['Close'].iloc[-1]:.4f}")

with col2:
    st.markdown("### 📊 Technische Indikatoren")
    st.markdown(f"- **RSI:** {df['RSI'].iloc[-1]:.1f} ({'Überkauft 🚨' if df['RSI'].iloc[-1] > 70 else 'Überverkauft 💰' if df['RSI'].iloc[-1] < 30 else 'Neutral'})")
    st.markdown(f"- **MACD:** {df['MACD'].iloc[-1]:.4f}")
    st.markdown(f"- **Volatilität (24h):** {df['Close'].pct_change().std()*100:.2f}%")

# 🕯️ Candlestick-Chart
fig = go.Figure(data=[
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#2ED573',
        decreasing_line_color='#FF4757'
    )
])
fig.update_layout(height=500, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
