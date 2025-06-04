import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

st.set_page_config(page_title="🧠 NeuroTrader PRO", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0a0a2e; color: white; }
h1 { color: #4af7d3; }
</style>
""", unsafe_allow_html=True)

class NeuroTrader:
    def __init__(self):
        self.asset_types = {
            "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD"],
            "Aktien": ["TSLA", "AAPL", "AMZN", "NVDA"],
            "Rohstoffe": ["GC=F", "CL=F", "SI=F"],
            "Indizes": ["^GDAXI"]
        }
        self.scaler = MinMaxScaler()
        self.model = RandomForestRegressor(n_estimators=100)

    @st.cache_data(ttl=300)
    def fetch_data(_self, symbol: str) -> pd.DataFrame:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=7d"
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

    def run_zielchecker(self, symbol):
        st.subheader("🎯 Zielchecker")
        df = self.fetch_data(symbol)
        if df.empty:
            st.warning("⚠️ Keine Kursdaten verfügbar.")
            return

        aktueller = df["Close"].iloc[-1]
        zielwert = st.number_input("Kursziel eingeben (€)", value=float(aktueller), key="ziel_input")

        if st.button("Ziel prüfen", key="ziel_button"):
            if len(df) < 200:
                st.warning("⚠️ Mindestens 200 Datenpunkte erforderlich.")
                return

            ema50 = df["Close"].ewm(span=50).mean()
            ema200 = df["Close"].ewm(span=200).mean()
            trend = "Aufwärts" if ema50.iloc[-1] > ema200.iloc[-1] else "Abwärts"
            support = df["Low"].rolling(window=20).min().iloc[-1]
            resistance = df["High"].rolling(window=20).max().iloc[-1]
            wahrscheinlichkeit = 0.7 if support <= zielwert <= resistance else 0.3

            st.metric("Wahrscheinlichkeit", f"{wahrscheinlichkeit * 100:.0f}%")
            st.metric("Trendrichtung", trend)
            st.metric("Support", f"{support:.2f}")
            st.metric("Widerstand", f"{resistance:.2f}")

    def render_ui(self):
        st.title("🧠 NeuroTrader PRO")

        view = st.selectbox("Modul wählen", ["Live-Chart", "Zielchecker"])

        col1, col2 = st.columns([1, 3])
        with col1:
            asset_type = st.selectbox("Kategorie", list(self.asset_types.keys()))
            symbol = st.selectbox("Symbol", self.asset_types[asset_type])

        if view == "Zielchecker":
            self.run_zielchecker(symbol)
            return

        df = self.fetch_data(symbol)
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

        with col2:
            st.metric("Aktueller Preis", f"${current:.2f}", f"{delta:.2f}%")
            st.markdown(f"<h2 style='color:{color}'>{trend}</h2>", unsafe_allow_html=True)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color="#2ed573",
            decreasing_line_color="#ff4757",
            name="Preis"
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
            title=f"{symbol} – Echtzeit KI-Trading"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.error("""
        ❗ Hinweis: Diese App ist keine Finanzberatung.  
        Prognosen sind spekulativ. Handel nur mit eigenem Risiko!
        """)

if __name__ == "__main__":
    app = NeuroTrader()
    app.render_ui()
