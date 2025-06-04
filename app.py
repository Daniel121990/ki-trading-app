import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

st.set_page_config(layout="wide")

st.title("KI Trading App – Spezialmodule")

# Dropdown-Menü
module = st.selectbox("Spezialmodul auswählen:", [
    "Bitte Modul auswählen",
    "GER40-Hebelstrategie-Modul",
    "Zielchecker-Modul",
    "Signal-Analyse"
])

# GER40-Modul mit Chart + Strategie
if module == "GER40-Hebelstrategie-Modul":
    st.subheader("GER40-Hebelstrategie")
    col1, col2 = st.columns(2)

    with col1:
        kapital = st.number_input("Kapital (€)", min_value=0.0, step=100.0)
        hebel = st.number_input("Hebel", min_value=1.0, step=0.1)
        stop = st.number_input("Stop-Loss in %", min_value=0.0, step=0.1)
        ziel = st.number_input("Take-Profit in %", min_value=0.0, step=0.1)
        if st.button("Strategie starten"):
            risiko = kapital * (stop / 100)
            pot_gewinn = kapital * (ziel / 100)
            st.success(f"Risiko: {risiko:.2f} €, Potenzieller Gewinn: {pot_gewinn:.2f} €")

    with col2:
        st.write("### GER40 Candlestick-Chart (5-Minuten)")
        df = yf.download("^GDAXI", period="1d", interval="5m")
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

# Zielchecker
elif module == "Zielchecker-Modul":
    st.subheader("Zielchecker")
    zielwert = st.number_input("Kursziel eingeben:", step=1.0)
    aktueller_kurs = yf.download("^GDAXI", period="1d", interval="1m")["Close"][-1]
    st.metric("Aktueller GER40-Kurs", f"{aktueller_kurs:.2f} €")

    if st.button("Ziel überprüfen"):
        if aktueller_kurs >= zielwert:
            st.success("Ziel erreicht oder überschritten!")
        else:
            st.warning("Ziel noch nicht erreicht.")

# Signal-Analyse
elif module == "Signal-Analyse":
    st.subheader("Signal-Analyse")
    st.write("Hier können künftig Signale automatisiert analysiert werden.")
    st.text_area("Signaldaten eingeben oder hochladen", height=150)
    if st.button("Analyse starten"):
        st.info("Signal-Analyse gestartet... (Logik folgt)")
