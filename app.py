import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

# --- Kategorien & Assets
st.subheader("📂 Kategorie wählen")
kategorien = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD"],
    "Aktien": ["AAPL", "TSLA", "NVDA"],
    "Rohstoffe": ["GC=F", "SI=F", "CL=F"]
}

kategorie = st.selectbox("Kategorie", list(kategorien.keys()))

suchbegriff = st.text_input("🔍 Suche nach Asset (z.B. TSLA)", "")

verfuegbare_assets = kategorien[kategorie]
if suchbegriff:
    verfuegbare_assets = [a for a in verfuegbare_assets if suchbegriff.upper() in a.upper()]

asset = st.selectbox("Asset auswählen", verfuegbare_assets)
interval = st.selectbox("Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"], index=0)

st.markdown(f"### 📍 Gewähltes Asset: <span style='color:lightgreen'>{asset}</span>", unsafe_allow_html=True)

# --- Daten holen + absichern
try:
    data = yf.download(asset, period="1d", interval=interval)
    if data is None or data.empty:
        st.error("❌ Keine Daten gefunden – bitte anderes Asset oder Intervall wählen.")
        st.stop()

    data.reset_index(inplace=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join(col).strip() for col in data.columns.values]
    else:
        data.columns = [str(col) for col in data.columns]

    close_col = next((col for col in data.columns if "Close" in col), None)
    if close_col is None:
        st.warning("⚠️ Indikatoren konnten nicht berechnet werden: 'Close'")
        st.stop()

    data["EMA20"] = ta.ema(data[close_col], length=20)
    data["RSI"] = ta.rsi(data[close_col], length=14)
    macd = ta.macd(data[close_col])

    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
        data["MACDs"] = macd["MACDs_12_26_9"]
    else:
        st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

    # BUY-/SELL Signale berechnen
    data["Signal"] = 0
    data.loc[(data["MACD"] > data["MACDs"]) & (data["RSI"] < 70), "Signal"] = 1  # BUY
    data.loc[(data["MACD"] < data["MACDs"]) & (data["RSI"] > 30), "Signal"] = -1  # SELL

except Exception as e:
    st.error(f"❌ Fehler beim Datenabruf oder Berechnung: {e}")
    st.stop()

# --- Chart mit Signalen
st.subheader("📈 Kursverlauf mit EMA & BUY-/SELL-Signalen")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data["Datetime"], y=data[close_col], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=data["Datetime"], y=data["EMA20"], mode='lines', name='EMA20'))
fig.add_trace(go.Scatter(x=data[data["Signal"] == 1]["Datetime"], y=data[data["Signal"] == 1][close_col],
                         mode='markers', name='BUY', marker=dict(color='green', size=8)))
fig.add_trace(go.Scatter(x=data[data["Signal"] == -1]["Datetime"], y=data[data["Signal"] == -1][close_col],
                         mode='markers', name='SELL', marker=dict(color='red', size=8)))
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# --- RSI
st.subheader("📉 RSI")
if "RSI" in data.columns:
    st.line_chart(data[["RSI"]].dropna())
else:
    st.warning("⚠️ RSI konnte nicht angezeigt werden.")

# --- MACD & Signal
st.subheader("📈 MACD & Signal")
if "MACD" in data.columns and "MACDs" in data.columns:
    st.line_chart(data[["MACD", "MACDs"]].dropna())
else:
    st.warning("⚠️ MACD konnte nicht dargestellt werden.")

# --- Indikatorwerte anzeigen
st.subheader("🧭 Indikatorwerte (aktuell)")
st.metric("Schlusskurs", f"{data[close_col].iloc[-1]:.2f}")
st.metric("RSI", f"{data['RSI'].iloc[-1]:.2f}")
st.metric("MACD", f"{data['MACD'].iloc[-1]:.4f}")
st.metric("EMA20", f"{data['EMA20'].iloc[-1]:.2f}")

st.success("✅ KI-Analyse aktiv. Nächster Schritt: Candle-Prognose & Trefferquote.")
