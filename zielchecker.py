 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/zielchecker.py b/zielchecker.py
index a35d8e6f5b3b9c3d6b5f38762099385fe85f4fcd..193dca2952b76e2abe053682a3c69f910e6ccaf4 100644
--- a/zielchecker.py
+++ b/zielchecker.py
@@ -1,30 +1,28 @@
 import streamlit as st
 import pandas as pd
-import numpy as np
 import requests
-from datetime import datetime
 from sklearn.ensemble import RandomForestRegressor
 from sklearn.preprocessing import MinMaxScaler
 import plotly.graph_objects as go
 
 st.set_page_config(page_title="🧠 NeuroTrader PRO", layout="wide")
 
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
 
EOF
)
