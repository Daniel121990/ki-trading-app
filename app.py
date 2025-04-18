import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta

st.set_page_config(layout="wide")
st.title("📈 KI-Trading App – Live Analyse")

# Auswahlbereich
st.subheader("🔎 Kategorienwahl")
category = st.selectbox("Kategorie wählen", ["Krypto", "Aktien", "Rohstoffe"])

search_term = st.text_input("🔍 Suche nach Asset (z. B. TSLA, BTCUSDT)", "BTCUSDT")

interval = st.selectbox("🕒 Zeitintervall", ["1m", "5m", "15m", "1h", "4h", "1d"])

# Binance-API für Live-Daten
def fetch_binance_klines(symbol="BTCUSDT", interval="1m", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

# Daten abrufen
data = fetch_binance_klines(symbol=search_term, interval=interval)

if data is not None and not data.empty:
    st.success(f"📍 Live-Daten geladen: {search_term.upper()} – Intervall: {interval}")
    st.dataframe(data.tail(20))

    # Technische Indikatoren
    try:
        data["EMA20"] = ta.ema(data["close"], length=20)
        data["RSI"] = ta.rsi(data["close"], length=14)
    except Exception as e:
        st.warning("⚠️ Indikatoren konnten nicht berechnet werden.")

    # Indikatoren als Farbwerte anzeigen
    st.markdown("### 📊 Technische Indikatoren (Live)")
    col1, col2 = st.columns(2)

    def style_value(val, low, high):
        if val < low:
            return f":red[{val:.2f}]"
        elif val > high:
            return f":green[{val:.2f}]"
        else:
            return f":white[{val:.2f}]"

    if "RSI" in data.columns:
        rsi = data["RSI"].dropna().iloc[-1]
        with col1:
            st.markdown(f"**RSI:** {style_value(rsi, 30, 70)}")
    if "EMA20" in data.columns:
        ema = data["EMA20"].dropna().iloc[-1]
        close = data["close"].iloc[-1]
        with col2:
            diff = close - ema
            st.markdown(f"**Abstand EMA20:** {style_value(diff, -5, 5)}")

    # Candle Chart über Altair
    import altair as alt
    st.markdown("### 🕯️ Live-Candlestick Chart")

    candle_df = data.copy().reset_index()
    candle_df["date"] = candle_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    base = alt.Chart(candle_df).encode(x="date:T")

    rule = base.mark_rule().encode(
        y="high:Q",
        y2="low:Q"
    )

    bar = base.mark_bar().encode(
        y="open:Q",
        y2="close:Q",
        color=alt.condition("datum.open <= datum.close",
                            alt.value("#00FF00"),  # Grün für steigende Kerzen
                            alt.value("#FF3131"))  # Rot für fallende Kerzen
    )

    chart = (rule + bar).properties(width=900, height=400)
    st.altair_chart(chart, use_container_width=True)

else:
    st.error("❌ Daten konnten nicht geladen werden. Bitte Symbol prüfen.")
