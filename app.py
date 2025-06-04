import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

st.set_page_config(page_title="🧠 NeuroTrader PRO – GER40", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0a0a2e; color: white; }
h1 { color: #4af7d3; }
</style>
""", unsafe_allow_html=True)

class NeuroTrader:
    def __init__(self):
        self.symbol = "^GDAXI"  # GER40 Index über Yahoo Finance
        self.scaler = MinMaxScaler()
        self.model = RandomForestRegressor(n_estimators=100)

    @st.cache_data(ttl=300)
    def fetch_data(_self) -> pd.DataFrame:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{_self.symbol}?interval=5m&range=7d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)
            data = r.json()["chart"]["result"][0]
            ts = pd.to_datetime(data["timestamp"], unit="s")
            quotes = data["indicators"]["quote"][0]
            df = pd.DataFrame(quotes, index=ts)[["open", "high", "low", "close"]]
            df.columns = ["Open", "High", "Low", "Close"]
            return df.dropna()
        except Exception as e:
            st.error(f"Datenfehler: {e}")
            return pd.DataFrame()

    def train_model(self, df: pd.DataFrame):
        data = self.scaler.fit_transform(df[["Close"]])
        lookback = 60
        X, y = [], []
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i].flatten())
            y.append(data[i, 0])
        self.model.fit(X, y)

    def predict(self, df: pd.DataFrame) -> float:
        last_seq = self.scaler.transform(df[["Close"]][-60:]).flatten().reshape(1, -1)
        pred_scaled = self.model.predict(last_seq)[0]
        return self.scaler.inverse_transform([[pred_scaled]])[0][0]

    def render_ui(self):
        st.title("📈 GER40 Echtzeit KI-Trading")

        df = self.fetch_data()
        if df.empty:
            st.warning("⚠️ Keine Daten verfügbar.")
            return

        with st.spinner("Trainiere Modell..."):
            self.train_model(df)

        prediction = self.predict(df)
        current = df["Close"].iloc[-1]
        delta = (prediction / current - 1) * 100
        trend = "🚀 KAUFEN" if delta > 1 else "🔥 VERKAUFEN" if delta < -1 else "🛑 HALTEN"
        color = "#00ff00" if "KAUFEN" in trend else "#ff0000" if "VERKAUFEN" in trend else "#ffffff"

        st.metric("Aktueller GER40", f"{current:.2f} Punkte", f"{delta:.2f}%")
        st.markdown(f"<h2 style='color:{color}'>{trend}</h2>", unsafe_allow_html=True)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color="#2ed573",
            decreasing_line_color="#ff4757",
            name="GER40"
        ))

        signal_color = "#00ff00" if "KAUFEN" in trend else "#ff0000" if "VERKAUFEN" in trend else "#ffffff"
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[current],
            mode="markers+text",
            marker=dict(color=signal_color, size=14, symbol="circle"),
            text=[trend],
            textposition="top center",
            name="Signal"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False,
            title="GER40 – Echtzeit KI-Prognose"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.error("""
        ❗ Hinweis: Diese App ist keine Finanzberatung.  
        Prognosen sind spekulativ. Handel nur mit eigenem Risiko!
        """)

if __name__ == "__main__":
    app = NeuroTrader()
    app.render_ui()
