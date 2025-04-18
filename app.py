import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📊 KI-Trading App – Live Kerzenchart & Analyse")

# Kategorien und Symbole
kategorien = {
    "Krypto": ["BTCUSDT", "XRPUSDT", "ETHUSDT", "BNBUSDT"],
    "Aktien": ["AAPL", "TSLA", "NVDA", "GOOG"],
    "Rohstoffe": ["XAUUSD", "OIL", "SILVER"]
}

kategorie = st.selectbox("📁 Kategorie wählen", list(kategorien.keys()))
suchsymbol = st.text_input("🔎 Suche nach Asset (z.B. TSLA)", "BTCUSDT")

# Intervall-Auswahl
interval = st.selectbox("⏱ Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

# Binance Symbol korrigieren
symbol = suchsymbol.upper().replace("-", "").replace("/", "")

# Funktion zum Abrufen der Binance-Daten
def get_binance_data(symbol, interval="1m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

# Daten abrufen
data = get_binance_data(symbol, interval)

if data is None or data.empty:
    st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
    st.stop()

st.success(f"📍 Daten erfolgreich geladen: {symbol}")
st.dataframe(data.tail(), use_container_width=True)

# Berechne RSI und EMA ohne Diagramm
try:
    rsi_value = round(ta.rsi(data['close'], length=14).iloc[-1], 2)
    ema_value = round(ta.ema(data['close'], length=20).iloc[-1], 2)
except Exception as e:
    rsi_value, ema_value = None, None

# Farbe anhand der Werte
def farbwert(metric, value):
    if metric == "rsi":
        if value is None:
            return ("Keine Daten", "gray")
        elif value < 30:
            return (f"RSI: {value}", "green")
        elif value > 70:
            return (f"RSI: {value}", "red")
        else:
            return (f"RSI: {value}", "white")
    elif metric == "ema":
        if value is None:
            return ("Keine Daten", "gray")
        else:
            return (f"EMA20: {value}", "cyan")

rsi_text, rsi_color = farbwert("rsi", rsi_value)
ema_text, ema_color = farbwert("ema", ema_value)

# Zwei Spalten zur Anzeige
col1, col2 = st.columns(2)
col1.markdown(f"<h4 style='color:{rsi_color}'>{rsi_text}</h4>", unsafe_allow_html=True)
col2.markdown(f"<h4 style='color:{ema_color}'>{ema_text}</h4>", unsafe_allow_html=True)

# Kerzendiagramm zeichnen
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    name="Candlestick"
))
fig.update_layout(
    title=f"📈 Candlestick Chart: {symbol} ({interval})",
    xaxis_title="Zeit",
    yaxis_title="Preis",
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

st.success("✅ Kerzenchart & Indikatorwerte bereit für KI-Prognose")
