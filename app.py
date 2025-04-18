# 📊 KI-Trading App – Live Analyse & Prognose (modernes Design mit BUY/SELL Feld)

import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# 🌙 Dunkles Layout und modernes Panel
st.set_page_config(layout="wide", page_title="KI-Trading App")
st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .st-bb, .st-at, .st-emotion-cache-1avcm0n {background-color: #0e1117;}
        .buy-box {background-color: #16c784; color: white; padding: 12px; border-radius: 10px; text-align: center;}
        .sell-box {background-color: #ea3943; color: white; padding: 12px; border-radius: 10px; text-align: center;}
        .big-value {font-size: 22px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 KI-Trading App – Live Analyse & Prognose")

# ✅ Kategorien und Top-Auswahl
categories = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD", "ADA-USD", "AVAX-USD", "DOGE-USD", "BNB-USD"],
    "Aktien": [
        "Apple (AAPL)", "Tesla (TSLA)", "Nvidia (NVDA)", "Microsoft (MSFT)", "Amazon (AMZN)", "Google (GOOGL)",
        "Meta (META)", "Alibaba (BABA)", "Netflix (NFLX)", "Intel (INTC)", "JP Morgan (JPM)", "Visa (V)",
        "UnitedHealth (UNH)", "Disney (DIS)", "Pfizer (PFE)", "Coca-Cola (KO)", "Merck (MRK)",
        "ExxonMobil (XOM)", "Walmart (WMT)", "Nike (NKE)"
    ],
    "Rohstoffe": ["Gold (GC=F)", "Silber (SI=F)", "Öl (CL=F)", "Gas (NG=F)", "Kupfer (HG=F)", "Mais (ZC=F)", "Soja (ZS=F)", "Kaffee (KC=F)", "Zucker (SB=F)", "Rindfleisch (LE=F)"]
}

# Kategorie- und Asset-Auswahl
col1, col2, col3 = st.columns([2, 3, 2])
with col1:
    category = st.selectbox("🧭 Wähle eine Kategorie", list(categories.keys()))

asset_list = categories[category]
with col2:
    search = st.text_input("🔎 Suche nach Asset (z.B. TSLA, ETH-USD)", "")
    filtered_assets = [a for a in asset_list if search.upper() in a.upper()] or asset_list

with col3:
    timeframe = st.selectbox("⏳ Zeitintervall", ["1m", "5m", "15m", "1h", "1d"])

symbol = st.selectbox("📈 Wähle ein Asset", filtered_assets)
symbol_clean = symbol.split("(")[-1].replace(")", "").strip()

st.markdown(f"### 📍 Gewähltes Asset: `{symbol_clean}`")

try:
    data = yf.download(tickers=symbol_clean, interval=timeframe, period="1d")
    if data.empty:
        st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
        st.stop()

    # Technische Indikatoren berechnen
    data["EMA20"] = ta.ema(data["Close"], length=20)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    macd = ta.macd(data["Close"])
    if macd is not None and "MACD_12_26_9" in macd.columns:
        data["MACD"] = macd["MACD_12_26_9"]
    else:
        data["MACD"] = None

    # Kerzenchart
    st.subheader("📉 Kursverlauf (1-Minuten-Kerzen)")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Kerzen"
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Letzter Kurs
    current_price = round(data["Close"].iloc[-1], 2)
    buy_price = round(current_price * 0.999, 2)
    sell_price = round(current_price * 1.001, 2)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='sell-box'><div>SELL</div><div class='big-value'>{sell_price}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='buy-box'><div>BUY</div><div class='big-value'>{buy_price}</div></div>", unsafe_allow_html=True)

    # RSI / EMA / MACD Werte anzeigen
    st.subheader("🔎 Indikatoren")
    def get_color(val, low, high):
        if pd.isna(val): return "white"
        if val < low: return "red"
        if val > high: return "green"
        return "white"

    rsi = round(data["RSI"].iloc[-1], 2)
    ema = round(data["EMA20"].iloc[-1], 2)
    macd_val = round(data["MACD"].iloc[-1], 4) if not pd.isna(data["MACD"].iloc[-1]) else "n/a"

    st.markdown(f"- **RSI:** <span style='color:{get_color(rsi, 30, 70)}'>{rsi}</span>", unsafe_allow_html=True)
    st.markdown(f"- **EMA20:** <span style='color:{get_color(ema, 0, float('inf'))}'>{ema}</span>", unsafe_allow_html=True)
    st.markdown(f"- **MACD:** <span style='color:{get_color(macd_val, 0, float('inf'))}'>{macd_val}</span>", unsafe_allow_html=True)

    st.success("✅ Live Daten und Indikatoren geladen.")

except Exception as e:
    st.error(f"❌ Fehler beim Laden oder Berechnen: {e}")
