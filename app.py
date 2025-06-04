import streamlit as st
import pandas as pd
import numpy as np

# ==== INDIKATOREN UND SIGNAL-LOGIK ====

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    exp1 = series.ewm(span=12).mean()
    exp2 = series.ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd, signal

def calculate_indicators(df):
    df['EMA20'] = df['close'].ewm(span=20).mean()
    df['EMA50'] = df['close'].ewm(span=50).mean()
    df['RSI'] = compute_rsi(df['close'])
    df['MACD'], df['SignalLine'] = compute_macd(df['close'])
    return df

def detect_ger40_signals(df):
    signals = []
    for i in range(1, len(df)):
        if df['EMA20'][i] > df['EMA50'][i] and df['RSI'][i] > 50 and df['MACD'][i] > df['SignalLine'][i]:
            signals.append("KAUFEN")
        elif df['EMA20'][i] < df['EMA50'][i] and df['RSI'][i] < 50 and df['MACD'][i] < df['SignalLine'][i]:
            signals.append("VERKAUFEN")
        else:
            signals.append("HALTEN")
    signals.insert(0, "HALTEN")
    return signals

def zielchecker(df, zielkurs):
    letzter_kurs = df["close"].iloc[-1]
    trend = "Long" if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] else "Short"
    max_high = df["high"].rolling(window=20).max().iloc[-1]
    min_low = df["low"].rolling(window=20).min().iloc[-1]
    dist = abs(zielkurs - letzter_kurs)
    spread = max_high - min_low
    wahrscheinlichkeit = max(0, min(100, 100 - (dist / spread) * 100))
    return {
        "aktueller_kurs": letzter_kurs,
        "trend": trend,
        "wahrscheinlichkeit": round(wahrscheinlichkeit, 2),
        "widerstand_oben": max_high,
        "unterstützung_unten": min_low
    }

# ==== STREAMLIT UI ====

st.set_page_config(page_title="GER40 Hebelstrategie + Zielchecker", layout="wide")

st.title("📊 GER40-Hebelstrategie & Zielchecker")

# === DATEN EINLESEN ===
# Ersetze diese CSV durch deine Live-Datenquelle
try:
    df = pd.read_csv("ger40_minute_data.csv")  # Muss Spalten: time, open, high, low, close, volume enthalten
except:
    st.error("⚠️ Datenquelle nicht gefunden. Bitte lade eine Datei 'ger40_minute_data.csv' hoch.")
    st.stop()

df = calculate_indicators(df)
df["TradeSignal"] = detect_ger40_signals(df)

# === SIGNALAUSGABE ===
st.subheader("📈 Aktuelles Handelssignal")
signal = df["TradeSignal"].iloc[-1]
st.metric("Signal", signal)

col1, col2, col3 = st.columns(3)
col1.metric("RSI", f"{round(df['RSI'].iloc[-1],1)}")
col2.metric("MACD", round(df["MACD"].iloc[-1], 2))
col3.metric("EMA20 / EMA50", f"{round(df['EMA20'].iloc[-1],2)} / {round(df['EMA50'].iloc[-1],2)}")

# === VERLAUF ===
with st.expander("🔍 Letzte Signale ansehen"):
    st.dataframe(df[["time", "close", "TradeSignal"]].tail(50))

# === ZIELCHECKER ===
st.divider()
st.subheader("🎯 Zielchecker GER40")

zielkurs = st.number_input("Zielkurs eingeben (z. B. 24150)", min_value=0.0, value=round(df["close"].iloc[-1] + 100, 2))
check = zielchecker(df, zielkurs)

c1, c2, c3 = st.columns(3)
c1.metric("Aktueller Kurs", round(check["aktueller_kurs"], 2))
c2.metric("Trendrichtung", check["trend"])
c3.metric("Wahrscheinlichkeit", f"{check['wahrscheinlichkeit']} %")

st.write(f"📍 **Widerstand oben:** {round(check['widerstand_oben'], 2)}")
st.write(f"📍 **Unterstützung unten:** {round(check['unterstützung_unten'], 2)}")

# === HINWEIS ===
st.info("🔄 Für Live-Daten kann eine API (z. B. Yahoo Finance oder Finnhub) angebunden werden.")
