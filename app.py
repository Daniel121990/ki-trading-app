import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go
import joblib
import os

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
            "Rohstoffe": ["GC=F", "CL=F", "SI=F"]
        }
        self.scaler = MinMaxScaler()
        self.model = RandomForestRegressor(n_estimators=100)
        self.signals = []

    @st.cache_data(ttl=300)
    def fetch_data(_self, symbol: str, interval: str = "1m") -> pd.DataFrame:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range=60d"
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

    def train_model(self, df: pd.DataFrame, symbol: str):
        data = self.scaler.fit_transform(df[["Close"]])
        lookback = 60
        X, y = [], []
        for i in range(lookback, len(data)):
            X.append(data[i-lookback:i].flatten())
            y.append(data[i, 0])
        self.model.fit(X, y)
        joblib.dump(self.model, f"model_{symbol}.pkl")
        joblib.dump(self.scaler, f"scaler_{symbol}.pkl")

    def load_model(self, symbol: str):
        if os.path.exists(f"model_{symbol}.pkl") and os.path.exists(f"scaler_{symbol}.pkl"):
            self.model = joblib.load(f"model_{symbol}.pkl")
            self.scaler = joblib.load(f"scaler_{symbol}.pkl")
            return True
        return False

    def predict(self, df: pd.DataFrame) -> float:
        last_seq = self.scaler.transform(df[["Close"]][-60:]).flatten().reshape(1, -1)
        pred_scaled = self.model.predict(last_seq)[0]
        return self.scaler.inverse_transform([[pred_scaled]])[0][0]

    def compute_indicators(self, df: pd.DataFrame):
        df['RSI'] = df['Close'].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / \
                    df['Close'].diff().abs().rolling(14).mean() * 100
        df['EMA'] = df['Close'].ewm(span=21).mean()
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        return df

    def analyze_signal(self, df: pd.DataFrame, prediction: float, current: float):
        reason = []
        if df['RSI'].iloc[-1] > 70:
            reason.append("RSI über 70")
        if df['MACD'].iloc[-1] < 0:
            reason.append("MACD negativ")
        if current > df['EMA'].iloc[-1]:
            reason.append("Kurs über EMA")

        delta = (prediction / current - 1) * 100
        if delta > 1:
            signal = "KAUFEN"
        elif delta < -1:
            signal = "VERKAUFEN"
        else:
            signal = "HALTEN"

        self.signals.append({"Signal": signal, "Korrekt": (signal == "KAUFEN" and prediction > current)
                                                          or (signal == "VERKAUFEN" and prediction < current)})
        if len(self.signals) > 5:
            self.signals.pop(0)

        return signal, reason, delta

    def compute_performance_table(self, df: pd.DataFrame):
        today = df['Close'].iloc[-1]
        one_day = df['Close'].iloc[-2] if len(df) > 1 else today
        one_week = df['Close'].shift(3900).dropna().iloc[-1] if len(df) > 3900 else today
        one_month = df['Close'].shift(18000).dropna().iloc[-1] if len(df) > 18000 else today
        one_year = df['Close'].shift(93600).dropna().iloc[-1] if len(df) > 93600 else today

        return pd.DataFrame({
            "Zeitraum": ["Heute", "Woche", "Monat", "Jahr"],
            "Veränderung": [
                f"{(today/one_day - 1)*100:.2f}%",
                f"{(today/one_week - 1)*100:.2f}%",
                f"{(today/one_month - 1)*100:.2f}%",
                f"{(today/one_year - 1)*100:.2f}%"
            ]
        })

    def render_ui(self):
        st.title("🧠 NeuroTrader PRO")

        col1, col2 = st.columns([1, 3])
        with col1:
            asset_type = st.selectbox("Kategorie", list(self.asset_types.keys()))
            symbol = st.selectbox("Symbol", self.asset_types[asset_type])
            interval = st.selectbox("Intervall", ["1m", "5m", "15m"])

        df = self.fetch_data(symbol, interval)
        if df.empty:
            st.warning("⚠️ Keine Daten verfügbar.")
            return

        df = self.compute_indicators(df)

        # Always show chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color="#2ed573", decreasing_line_color="#ff4757"))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Analyze Button
        if st.button("🔍 KI-Signal analysieren"):
            if not self.load_model(symbol):
                self.train_model(df, symbol)
            prediction = self.predict(df)
            current = df['Close'].iloc[-1]
            signal, reason, delta = self.analyze_signal(df, prediction, current)

            signal_color = "#00ff00" if signal == "KAUFEN" else "#ff0000" if signal == "VERKAUFEN" else "#ffffff"
            st.metric("Aktueller Preis", f"${current:.2f}", f"{delta:.2f}%")
            st.markdown(f"<h2 style='color:{signal_color}'>{signal}</h2>", unsafe_allow_html=True)
            if reason:
                st.info("Begründung: " + ", ".join(reason))
            quote = sum(s['Korrekt'] for s in self.signals) / len(self.signals) * 100 if self.signals else 0
            st.success(f"Trefferquote: {quote:.0f}% der letzten {len(self.signals)} Signale")

            # Performance Tabelle
            performance_df = self.compute_performance_table(df)
            st.markdown("### Performance (Veränderung)")
            st.dataframe(performance_df, use_container_width=True)

            st.error("""
            ❗ Hinweis: Diese App ist keine Finanzberatung.  
            Prognosen sind spekulativ. Handel nur mit eigenem Risiko!
            """)

if __name__ == "__main__":
    app = NeuroTrader()
    app.render_ui()
