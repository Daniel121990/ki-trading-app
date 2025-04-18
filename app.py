import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse & Prognose")

# Kategorien
asset_categories = {
    "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "BNB-USD", "SOL-USD", "ADA-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "TRX-USD",
               "MATIC-USD", "LTC-USD", "SHIB-USD", "BCH-USD", "LINK-USD", "XLM-USD", "ATOM-USD", "ETC-USD", "NEAR-USD", "HBAR-USD"],

    "Aktien": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "V", "JNJ",
               "JPM", "WMT", "UNH", "PG", "XOM", "MA", "HD", "CVX", "PFE", "INTC"],

    "Rohstoffe": ["XAUUSD", "XAGUSD", "CL=F", "BZ=F", "NG=F", "KC=F", "CC=F", "CT=F", "ZC=F", "ZS=F",
                   "ZW=F", "HG=F", "PA=F", "PL=F", "SB=F", "HO=F", "RB=F", "LBS=F", "ZR=F", "ZO=F"]
}

# Kategorie und Asset-Auswahl
selected_category = st.selectbox("Wähle eine Kategorie", list(asset_categories.keys()))
assets = asset_categories[selected_category]
asset = st.selectbox("🔎 Wähle ein Asset", assets)

st.markdown(f"📍 Gewähltes Asset: **{asset}**")

try:
    data = yf.download(asset, period="1d", interval="1m")
    if data is None or data.empty:
        st.error("❌ Daten ungültig oder leer.")
    else:
        # Technische Indikatoren
        data["EMA20"] = ta.ema(data["Close"], length=20)
        data["RSI"] = ta.rsi(data["Close"], length=14)
        macd = ta.macd(data["Close"])
        if macd is not None and "MACD_12_26_9" in macd.columns:
            data["MACD"] = macd["MACD_12_26_9"]
            data["Signal"] = macd["MACDs_12_26_9"]
        else:
            st.warning("⚠️ MACD konnte nicht berechnet werden – Spalte fehlt oder Daten unvollständig.")

        # Chart
        st.subheader("📊 Kursverlauf (1-Minuten-Kerzen)")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index,
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close'],
                                     name='Candles'))
        fig.update_layout(xaxis_rangeslider_visible=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Indikatoren-Werte mit Farbe
        def color_value(value, good_range, neutral_range):
            if value >= good_range[0] and value <= good_range[1]:
                return f"<span style='color:green'><b>{value:.2f}</b></span>"
            elif value >= neutral_range[0] and value <= neutral_range[1]:
                return f"<span style='color:white'>{value:.2f}</span>"
            else:
                return f"<span style='color:red'><b>{value:.2f}</b></span>"

        st.markdown("""
        ### 🔍 Indikatoren
        """, unsafe_allow_html=True)
        rsi_val = data['RSI'].iloc[-1] if 'RSI' in data.columns else None
        ema_val = data['EMA20'].iloc[-1] if 'EMA20' in data.columns else None
        macd_val = data['MACD'].iloc[-1] if 'MACD' in data.columns else None

        st.markdown(f"- **RSI**: {color_value(rsi_val, (55, 70), (45, 55))}" if rsi_val else "- RSI: n/a", unsafe_allow_html=True)
        st.markdown(f"- **EMA20**: {color_value(ema_val, (0, float('inf')), (0, float('inf')))}" if ema_val else "- EMA20: n/a", unsafe_allow_html=True)
        st.markdown(f"- **MACD**: {color_value(macd_val, (0, float('inf')), (-0.5, 0))}" if macd_val else "- MACD: n/a", unsafe_allow_html=True)

        st.success("✅ Live-Daten und Indikatoren geladen.")

except Exception as e:
    st.error(f"Fehler beim Laden oder Berechnen der Daten: {e}")
