 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index c36c54610ca5f474e4559836ee0e352bf53b0cbe..062a7fb3fe5e9e8057bb75a9ec1ce8d4af7509e1 100644
--- a/app.py
+++ b/app.py
@@ -1,22 +1,26 @@
 import streamlit as st
 import yfinance as yf
 import pandas as pd
 import pandas_ta as ta
+from zielchecker import run_zielchecker
 
 st.set_page_config(layout="wide")
 st.title("KI-Trading App – Live Analyse & Prognose")
 
 asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
 data = yf.download(asset, period="1d", interval="1m")
 
 data["EMA20"] = ta.ema(data["Close"], length=20)
 data["RSI"] = ta.rsi(data["Close"], length=14)
 macd = ta.macd(data["Close"])
 data["MACD"] = macd["MACD_12_26_9"]
 data["MACDs"] = macd["MACDs_12_26_9"]
 
 st.line_chart(data[["Close", "EMA20"]].dropna())
 st.line_chart(data[["RSI"]].dropna())
 st.line_chart(data[["MACD", "MACDs"]].dropna())
 
-st.success("KI-Signale & Candle-Prognose folgen im Ausbau")
+st.success("KI-Signale & Candle-Prognose folgen im Ausbau")
+
+# Zusatzmodul: Zielchecker
+run_zielchecker(asset)
 
EOF
)
