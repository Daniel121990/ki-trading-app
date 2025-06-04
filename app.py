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
            "Spezialmodule": ["GER40-Hebelstrategie", "Zielchecker", "Signal-Analyse"]
        }
        self.scaler = MinMaxScaler()
        self.model = RandomForestRegressor(n_estimators=100)

    @st.cache_data(ttl=300)
    def fetch_data(_self, symbol: str) -> pd.DataFrame:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
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
        st.title("🧠 NeuroTrader PRO")

        col1, col2 = st.columns([1, 3])
        with col1:
            asset_type = st.selectbox("Kategorie", list(self.asset_types.keys()))
            symbol = st.selectbox("Symbol", self.asset_types[asset_type])

        if asset_type == "Spezialmodule":
            if symbol == "GER40-Hebelstrategie":
                st.subheader("GER40-Hebelstrategie")
                kapital = st.number_input("Kapital (€)", min_value=0.0)
                hebel = st.number_input("Hebel", min_value=1.0)
                stop = st.number_input("Stop-Loss in %", min_value=0.0)
                ziel = st.number_input("Take-Profit in %", min_value=0.0)
                if st.button("Strategie berechnen"):
                    risiko = kapital * (stop / 100)
                    pot_gewinn = kapital * (ziel / 100)
                    st.success(f"Risiko: {risiko:.2f} €, Potenzieller Gewinn: {pot_gewinn:.2f} €")
                df = self.fetch_data("^GDAXI")
                if not df.empty:
                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            elif symbol == "Zielchecker":
                st.subheader("Zielchecker")
                kursziel = st.number_input("Kursziel eingeben")
                df = self.fetch_data("^GDAXI")
                if not df.empty:
                    aktueller_kurs = df["Close"].iloc[-1]
                    delta = (aktueller_kurs - kursziel) / kursziel * 100
                    st.metric("Aktueller Kurs", f"{aktueller_kurs:.2f}", f"{delta:.2f}%")
                    if st.button("Ziel prüfen"):
                        if aktueller_kurs >= kursziel:
                            st.success("Ziel erreicht oder überschritten!")
                        else:
                            st.info("Ziel noch nicht erreicht.")

            elif symbol == "Signal-Analyse":
                st.subheader("Signal-Analyse")
                uploaded_file = st.file_uploader("CSV-Datei mit Signalen hochladen", type="csv")
                if uploaded_file is not None:
                    df = pd.read_csv(uploaded_file)
                    st.write("Vorschau:", df.head())
                    treffer = df[df['Signal'] == df['Ergebnis']].shape[0]
                    gesamt = df.shape[0]
                    quote = (treffer / gesamt) * 100 if gesamt > 0 else 0
                    st.success(f"Trefferquote: {quote:.2f}%")

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
        trend = "🚀 KAUFEN" if delta > 1 else "🔥 VERKAUFEN" if delta < -1 else "🚫 HALTEN"
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
        signal_color = color
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[current],
            mode="markers+text",
            marker=dict(color=signal_color, size=14, symbol="circle"),
            text=[trend],
            textposition="top center",
            name="Signal"
        ))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False,
                          title=f"{symbol} – Echtzeit KI-Trading")
        st.plotly_chart(fig, use_container_width=True)

        st.error("""
        ❗ Hinweis: Diese App ist keine Finanzberatung.  
        Prognosen sind spekulativ. Handel nur mit eigenem Risiko!
        """)

if __name__ == "__main__":
    app = NeuroTrader()
    app.render_ui()
