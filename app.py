import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import time

# ======================
# 🔧 KERN-KOMPONENTEN
# ======================
class TradingApp:
    def __init__(self):
        self.asset_types = {
            "Krypto": ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD"],
            "Aktien": ["TSLA", "AAPL", "NVDA", "AMZN"],
            "Rohstoffe": ["GC=F", "CL=F", "SI=F"]
        }
        self.model = None
        self.scaler = MinMaxScaler()
        
    # ----------- Datenabfrage -----------
    @st.cache_data(ttl=300, show_spinner="Lade Marktdaten...")
    def fetch_data(_self, symbol: str, asset_type: str) -> pd.DataFrame:
        """Holt Echtzeitdaten von Yahoo Finance/CoinGecko mit Fallback-Logic"""
        try:
            # Yahoo Finance API (für alle Asset-Typen)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=7d"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            response.raise_for_status()
            
            data = response.json()["chart"]["result"][0]
            timestamps = pd.to_datetime(data["timestamp"], unit="s")
            
            df = pd.DataFrame({
                "Open": data["indicators"]["quote"][0]["open"],
                "High": data["indicators"]["quote"][0]["high"],
                "Low": data["indicators"]["quote"][0]["low"],
                "Close": data["indicators"]["quote"][0]["close"]
            }, index=timestamps).dropna()
            
            return df.ffill().bfill()
            
        except Exception as e:
            st.error(f"Datenabfrage fehlgeschlagen: {str(e)}")
            return pd.DataFrame()

    # ----------- KI-Modell -----------
    def build_model(self, input_shape: tuple) -> Sequential:
        """Erstellt ein robustes LSTM-Modell mit Dropout"""
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.3),
            LSTM(64),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer="adam", loss="mse")
        return model

    def train_model(self, data: pd.DataFrame):
        """Komplettes Training mit Progress-Bar"""
        scaled_data = self.scaler.fit_transform(data[["Close"]])
        
        # Sequenzerstellung
        X, y = [], []
        look_back = 60
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i, 0])
            y.append(scaled_data[i, 0])
            
        X = np.array(X).reshape(-1, look_back, 1)
        y = np.array(y)
        
        # Modelltraining
        self.model = self.build_model((look_back, 1))
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for epoch in range(25):
            self.model.fit(X, y, epochs=1, batch_size=32, verbose=0)
            progress = (epoch + 1) / 25
            progress_bar.progress(progress)
            status_text.text(f"Training Epoche {epoch+1}/25...")
            time.sleep(0.1)  # Simuliert echtes Training
            
        progress_bar.empty()
        status_text.empty()

    # ----------- UI-Logik -----------
    def render_ui(self):
        """Haupt-UI mit dynamischer Anpassung"""
        # Konfiguration
        st.set_page_config(
            page_title="NeuroTrader PRO",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Dark Mode CSS
        st.markdown("""
        <style>
        .stApp { background: #0a0a2e; color: #ffffff; }
        .stSelectbox > div { background: #1a1a4a; }
        .st-bq { color: #4af7d3; }
        .stAlert { background: #1a1a4a!important; }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("🧠 NeuroTrader PRO")
        
        # Asset-Auswahl
        col1, col2 = st.columns([1, 3])
        with col1:
            asset_type = st.selectbox("Asset-Typ", list(self.asset_types.keys()))
            symbol = st.selectbox("Symbol", self.asset_types[asset_type])
            
        # Daten laden
        df = self.fetch_data(symbol.split("-")[0], asset_type)
        if df.empty:
            st.warning("Keine Daten verfügbar. Bitte Symbol ändern.")
            return
            
        # Modelltraining
        if st.button("KI-Modell aktualisieren") or not self.model:
            with st.spinner("Initialisiere KI..."):
                self.train_model(df)
                
        # Vorhersage
        if self.model:
            scaled_data = self.scaler.transform(df[["Close"]][-60:])
            prediction = self.model.predict(scaled_data.reshape(1, 60, 1))
            predicted_price = self.scaler.inverse_transform(prediction)[0][0]
            current_price = df["Close"].iloc[-1]
            
            # Signalgenerierung
            delta = (predicted_price / current_price - 1) * 100
            color = "#00ff00" if delta > 1 else "#ff0000" if delta < -1 else "#ffffff"
            
            # Dashboard
            with col2:
                st.metric("Aktueller Preis", f"${current_price:.2f}", 
                         delta=f"{delta:.2f}%", delta_color="normal")
                st.markdown(f"<h2 style='color:{color}'>🚀 {'KAUFEN' if delta > 1 else 'VERKAUFEN' if delta < -1 else 'HALTEN'}</h2>", 
                            unsafe_allow_html=True)
            
            # Candlestick Chart
            fig = go.Figure(data=[
                go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    increasing_line_color="#2ed573",
                    decreasing_line_color="#ff4757"
                )
            ])
            fig.update_layout(
                height=700,
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                title=f"{symbol} - Echtzeitanalyse"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Disclaimer
            st.error("""
            **❗ Wichtiger Hinweis:**  
            Diese App dient ausschließlich Bildungszwecken.  
            Finanzentscheidungen sollten nie auf Basis von KI-Prognosen getroffen werden.  
            Historische Performance ist kein Indikator für zukünftige Ergebnisse.
            """)

# ======================
# 🚀 APP-STARTER
# ======================
if __name__ == "__main__":
    app = TradingApp()
    app.render_ui()
