 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index 3a3f4de13bdac96aaf67e473ab482b25396acdc2..6a5679d221140c3115cc8303e56279056aca73c3 100644
--- a/app.py
+++ b/app.py
@@ -1,34 +1,33 @@
 # === app.py ===
 import streamlit as st
 from zielchecker import run_zielchecker
 import pandas as pd
 import requests
 import plotly.graph_objects as go
 from sklearn.ensemble import RandomForestRegressor
 from sklearn.preprocessing import MinMaxScaler
-import numpy as np
 
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
 
 
EOF
)
