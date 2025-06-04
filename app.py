# === app.py ===
import streamlit as st
from zielchecker import run_zielchecker
import pandas as pd
import requests
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import numpy as np

st.set_page_config(page_title="📊 NeuroTrader PRO", layout="wide")

# ===================== DATENABFRAGE =====================
def get_chart_data(symbol="^GDAXI", interval="5m", range_="1d"):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        data = r.json()["chart"]["result"][0]
        ts = pd.to_datetime(data["timestamp"], unit="s")
        q = data["indicators"]["quote"][0]
        df = pd.DataFrame(q, index=ts)[["open", "high", "low", "close"]]
        df.columns = ["Open", "High", "Low", "Close"]
        return df.dropna()
    except Exception as e:
        st.error(f"Datenabruf fehlgeschlagen: {e}")
        return pd.DataFrame()

# ===================== KI MODELL =====================
class SimplePredictor:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = RandomForestRegressor(n_estimators=100)

    def train(self, df):
        data = self.scaler.fit_transform(df[["Close"]])
        X, y = [], []
        lookback = 60
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i].flatten())
            y.append(data[i, 0])
        self.model.fit(X, y)

    def predict(self, df):
        if len(df) < 60:
            return None
        last_seq = self.scaler.transform(df[["Close"]][-60:]).flatten().reshape(1, -1)
        pred_scaled = self.model.predict(last_seq)[0]
        return self.scaler.inverse_transform([[pred_scaled]])[0][0]

# ===================== UI =====================
st.title("📊 NeuroTrader PRO")
modul = st.selectbox("Modul auswählen:", [
    "Live-Chart & KI-Prognose",
    "Zielchecker"
])

if modul == "Live-Chart & KI-Prognose":
    symbol = st.selectbox("Asset wählen", ["^GDAXI", "BTC-USD", "ETH-USD", "TSLA"])
    df = get_chart_data(symbol)
    if df.empty:
        st.warning("⚠️ Keine Kursdaten verfügbar – eventuell Symbol falsch oder Internetproblem.")
    else:
        model = SimplePredictor()
        model.train(df)
        prediction = model.predict(df)
        aktueller = df["Close"].iloc[-1]
        delta = (prediction / aktueller - 1) * 100 if prediction else 0
        trend = "🚀 KAUFEN" if delta > 1 else "🔥 VERKAUFEN" if delta < -1 else "🛑 HALTEN"
        farbe = "#00ff00" if "KAUFEN" in trend else "#ff0000" if "VERKAUFEN" in trend else "#ffffff"

        st.metric("Aktueller Kurs", f"{aktueller:.2f}", f"{delta:.2f}%")
        st.markdown(f"<h3 style='color:{farbe}'>{trend}</h3>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color="#00ff00",
            decreasing_line_color="#ff0000"
        ))
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[aktueller],
            mode="markers+text",
            marker=dict(color=farbe, size=14),
            text=[trend],
            textposition="top center"
        ))
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)

elif modul == "Zielchecker":
    run_zielchecker("^GDAXI")
