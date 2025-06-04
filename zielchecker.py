 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/zielchecker.py b/zielchecker.py
index a35d8e6f5b3b9c3d6b5f38762099385fe85f4fcd..7064d58534f779bb5e06a018d87f9ce3defbd117 100644
--- a/zielchecker.py
+++ b/zielchecker.py
@@ -1,35 +1,34 @@
 import streamlit as st
 import pandas as pd
 import numpy as np
 import requests
 from datetime import datetime
 from sklearn.ensemble import RandomForestRegressor
 from sklearn.preprocessing import MinMaxScaler
 import plotly.graph_objects as go
 
-st.set_page_config(page_title="🧠 NeuroTrader PRO", layout="wide")
 
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
             "Indizes": ["^GDAXI"]
         }
         self.scaler = MinMaxScaler()
         self.model = RandomForestRegressor(n_estimators=100)
 
     @st.cache_data(ttl=300)
     def fetch_data(_self, symbol: str) -> pd.DataFrame:
         try:
             url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=7d"
             headers = {"User-Agent": "Mozilla/5.0"}
             r = requests.get(url, headers=headers, timeout=10)
diff --git a/zielchecker.py b/zielchecker.py
index a35d8e6f5b3b9c3d6b5f38762099385fe85f4fcd..7064d58534f779bb5e06a018d87f9ce3defbd117 100644
--- a/zielchecker.py
+++ b/zielchecker.py
@@ -145,27 +144,28 @@ class NeuroTrader:
         signal_color = "#00ff00" if "KAUFEN" in trend else "#ff0000" if "VERKAUFEN" in trend else "#ffffff"
         fig.add_trace(go.Scatter(
             x=[df.index[-1]],
             y=[current],
             mode="markers+text",
             marker=dict(color=signal_color, size=14, symbol="circle"),
             text=[trend],
             textposition="top center",
             name="Signal"
         ))
 
         fig.update_layout(
             template="plotly_dark",
             height=600,
             xaxis_rangeslider_visible=False,
             title=f"{symbol} – Echtzeit KI-Trading"
         )
         st.plotly_chart(fig, use_container_width=True)
 
         st.error("""
         ❗ Hinweis: Diese App ist keine Finanzberatung.  
         Prognosen sind spekulativ. Handel nur mit eigenem Risiko!
         """)
 
 if __name__ == "__main__":
+    st.set_page_config(page_title="🧠 NeuroTrader PRO", layout="wide")
     app = NeuroTrader()
     app.render_ui()
 
EOF
)
