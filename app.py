 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index c36c54610ca5f474e4559836ee0e352bf53b0cbe..6a69ed1e517679ee9ee554eca940d4a7d313f18f 100644
--- a/app.py
+++ b/app.py
@@ -1,22 +1,30 @@
 import streamlit as st
 import yfinance as yf
 import pandas as pd
 import pandas_ta as ta
 
-st.set_page_config(layout="wide")
-st.title("KI-Trading App – Live Analyse & Prognose")
+def main() -> None:
+    """Render the trading dashboard."""
+    st.set_page_config(layout="wide")
+    st.title("KI-Trading App – Live Analyse & Prognose")
 
-asset = st.selectbox("Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"])
-data = yf.download(asset, period="1d", interval="1m")
+    asset = st.selectbox(
+        "Wähle ein Asset", ["XAUUSD", "TSLA", "NVDA", "XRP-USD"]
+    )
+    data = yf.download(asset, period="1d", interval="1m")
 
-data["EMA20"] = ta.ema(data["Close"], length=20)
-data["RSI"] = ta.rsi(data["Close"], length=14)
-macd = ta.macd(data["Close"])
-data["MACD"] = macd["MACD_12_26_9"]
-data["MACDs"] = macd["MACDs_12_26_9"]
+    data["EMA20"] = ta.ema(data["Close"], length=20)
+    data["RSI"] = ta.rsi(data["Close"], length=14)
+    macd = ta.macd(data["Close"])
+    data["MACD"] = macd["MACD_12_26_9"]
+    data["MACDs"] = macd["MACDs_12_26_9"]
 
-st.line_chart(data[["Close", "EMA20"]].dropna())
-st.line_chart(data[["RSI"]].dropna())
-st.line_chart(data[["MACD", "MACDs"]].dropna())
+    st.line_chart(data[["Close", "EMA20"]].dropna())
+    st.line_chart(data[["RSI"]].dropna())
+    st.line_chart(data[["MACD", "MACDs"]].dropna())
 
-st.success("KI-Signale & Candle-Prognose folgen im Ausbau")
+    st.success("KI-Signale & Candle-Prognose folgen im Ausbau")
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
