 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index 3a3f4de13bdac96aaf67e473ab482b25396acdc2..833a1447e6e4917e4965da947ba1bbf93f2b08f0 100644
--- a/app.py
+++ b/app.py
@@ -1,28 +1,28 @@
 # === app.py ===
 import streamlit as st
-from zielchecker import run_zielchecker
+from zielchecker import NeuroTrader
 import pandas as pd
 import requests
 import plotly.graph_objects as go
 from sklearn.ensemble import RandomForestRegressor
 from sklearn.preprocessing import MinMaxScaler
 import numpy as np
 
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
 
diff --git a/app.py b/app.py
index 3a3f4de13bdac96aaf67e473ab482b25396acdc2..833a1447e6e4917e4965da947ba1bbf93f2b08f0 100644
--- a/app.py
+++ b/app.py
@@ -70,26 +70,27 @@ if modul == "Live-Chart & KI-Prognose":
         farbe = "#00ff00" if "KAUFEN" in trend else "#ff0000" if "VERKAUFEN" in trend else "#ffffff"
 
         st.metric("Aktueller Kurs", f"{aktueller:.2f}", f"{delta:.2f}%")
         st.markdown(f"<h3 style='color:{farbe}'>{trend}</h3>", unsafe_allow_html=True)
 
         fig = go.Figure()
         fig.add_trace(go.Candlestick(
             x=df.index,
             open=df["Open"], high=df["High"],
             low=df["Low"], close=df["Close"],
             increasing_line_color="#00ff00",
             decreasing_line_color="#ff0000"
         ))
         fig.add_trace(go.Scatter(
             x=[df.index[-1]],
             y=[aktueller],
             mode="markers+text",
             marker=dict(color=farbe, size=14),
             text=[trend],
             textposition="top center"
         ))
         fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
         st.plotly_chart(fig, use_container_width=True)
 
 elif modul == "Zielchecker":
-    run_zielchecker("^GDAXI")
+    trader = NeuroTrader()
+    trader.run_zielchecker("^GDAXI")
 
EOF
)
