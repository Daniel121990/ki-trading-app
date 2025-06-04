import streamlit as st
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
st.title("📊 NeuroTrader PRO – GER40 & mehr")
modul = st.selectbox("Modul auswählen:", [
    "Live-Chart & KI-Prognose",
    "GER40-Hebelstrategie",
    "Zielchecker",
    "Signal-Analyse (CSV)"
])

if modul == "Live-Chart & KI-Prognose":
    symbol = st.selectbox("Asset wählen", ["^GDAXI", "BTC-USD", "ETH-USD", "TSLA"])
    df = get_chart_data(symbol)
    if not df.empty:
        st.success("Daten geladen ✅")
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

elif modul == "GER40-Hebelstrategie":
    st.subheader("💹 GER40-Hebelstrategie")
    kapital = st.number_input("Kapital (€)", value=1000.0)
    hebel = st.number_input("Hebel", value=2.0)
    stop = st.number_input("Stop-Loss (%)", value=2.0)
    ziel = st.number_input("Take-Profit (%)", value=4.0)
    if st.button("Berechnen"):
        risiko = kapital * (stop / 100)
        pot_gewinn = kapital * (ziel / 100)
        st.success(f"Risiko: {risiko:.2f} €, Gewinnchance: {pot_gewinn:.2f} €")
    df = get_chart_data("^GDAXI")
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"]
        )])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

elif modul == "Zielchecker":
    st.subheader("🎯 Zielchecker")
    df = get_chart_data("^GDAXI")
    if not df.empty:
        aktueller = df["Close"].iloc[-1]
        zielwert = st.number_input("Kursziel (€)", value=aktueller)
        if st.button("Ziel prüfen"):
            support = df["Low"].rolling(20).min().iloc[-1]
            resistance = df["High"].rolling(20).max().iloc[-1]
            wahrscheinlichkeit = 0.7 if support <= zielwert <= resistance else 0.3
            trend = "Aufwärts" if df["Close"].rolling(50).mean().iloc[-1] > df["Close"].rolling(200).mean().iloc[-1] else "Abwärts"
            st.metric("Wahrscheinlichkeit", f"{wahrscheinlichkeit * 100:.0f}%")
            st.metric("Trend", trend)
            st.metric("Support", f"{support:.2f}")
            st.metric("Widerstand", f"{resistance:.2f}")

elif modul == "Signal-Analyse (CSV)":
    st.subheader("📂 Signal-Analyse")
    file = st.file_uploader("CSV hochladen mit 'Signal' & 'Ergebnis'", type="csv")
    if file:
        df = pd.read_csv(file)
        st.write("📄 Vorschau:", df.head())
        if "Signal" in df.columns and "Ergebnis" in df.columns:
            treffer = df[df["Signal"] == df["Ergebnis"]].shape[0]
            gesamt = len(df)
            quote = (treffer / gesamt) * 100 if gesamt > 0 else 0
            st.success(f"Trefferquote: {quote:.2f}%")
        else:
            st.error("❌ Spalten 'Signal' und 'Ergebnis' fehlen.")

st.info("Hinweis: Keine Finanzberatung. Nutzung auf eigenes Risiko.")
