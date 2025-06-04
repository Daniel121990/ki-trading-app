 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index b677e14c896fd4db11fa7d6e89a8a222fefcf345..9821054aeb4d89abfdaee02b0192dca6ebd529fe 100644
--- a/app.py
+++ b/app.py
@@ -1,201 +1,41 @@
- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
-diff --git a/app.py b/app.py
-index 19d5edfd3c7017a1901b82ca71774793056240f9..9821054aeb4d89abfdaee02b0192dca6ebd529fe 100644
---- a/app.py
-+++ b/app.py
-@@ -1,151 +1,41 @@
-- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
--diff --git a/app.py b/app.py
--index 0d0768423dc40a0e17cbc9e0ec3340e9a73516d3..3f7f4d5ae628d2352a281ca7f26f5ca141648ac6 100644
----- a/app.py
--+++ b/app.py
--@@ -1,72 +1,71 @@
--+import streamlit as st
--+import pandas as pd
--+import plotly.graph_objects as go
--+import yfinance as yf
-- 
--- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
---diff --git a/app.py b/app.py
---index 8b137891791fe96927ad78e64b0aad7bded08bdc..0c09b820ecd23837bc3aa0e1dab115d22f4c125a 100644
------ a/app.py
---+++ b/app.py
---@@ -1 +1,62 @@
---+import streamlit as st
---+import pandas as pd
---+import plotly.graph_objects as go
---+import yfinance as yf
--- 
---+from zielchecker import compute_ema, compute_rsi, compute_macd, forecast_prices
---+
---+TICKER = "^GDAXI"  # GER40/DAX40 index
---+
---+
---+def load_data(ticker: str) -> pd.DataFrame:
---+    return yf.download(ticker, interval="1m", period="1d")
---+
---+
---+def main():
---+    st.title("GER40 Trading Dashboard")
---+
---+    data_load_state = st.text("Loading data...")
---+    data = load_data(TICKER)
---+    data_load_state.text("Loading data... done!")
---+
---+    if data.empty:
---+        st.error("No data retrieved. Please check your internet connection or ticker symbol.")
---+        return
---+
---+    data['EMA12'] = compute_ema(data, 12)
---+    data['EMA26'] = compute_ema(data, 26)
---+    macd_df = compute_macd(data)
---+    data['MACD'] = macd_df['MACD']
---+    data['MACDSignal'] = macd_df['Signal']
---+    data['RSI'] = compute_rsi(data)
---+    data['Signal'] = ["BUY" if ema12 > ema26 else "SELL" for ema12, ema26 in zip(data['EMA12'], data['EMA26'])]
---+
---+    st.subheader("Latest data")
---+    st.dataframe(data.tail())
---+
---+    fig = go.Figure(data=[go.Candlestick(x=data.index,
---+                                         open=data['Open'],
---+                                         high=data['High'],
---+                                         low=data['Low'],
---+                                         close=data['Close'],
---+                                         name='Candles')])
---+    fig.add_trace(go.Scatter(x=data.index, y=data['EMA12'],
---+                             line=dict(color='blue', width=1), name='EMA12'))
---+    fig.add_trace(go.Scatter(x=data.index, y=data['EMA26'],
---+                             line=dict(color='orange', width=1), name='EMA26'))
---+    st.plotly_chart(fig, use_container_width=True)
---+
---+    st.subheader("Indicators")
---+    st.line_chart(data[['RSI']])
---+    st.line_chart(data[['MACD', 'MACDSignal']])
---+
---+    st.subheader("Current Signal")
---+    st.write(data['Signal'].iloc[-1])
---+
---+    forecast = forecast_prices(data['Close'], steps=3)
---+    st.subheader("Next 3 Candle Forecast")
---+    st.write(forecast)
---+
---+
---+if __name__ == "__main__":
---+    main()
--- 
---EOF
---)
--+from zielchecker import compute_ema, compute_rsi, compute_macd, forecast_prices
--+
--+TICKER = "^GDAXI"  # GER40/DAX40 index
--+
--+
--+def load_data(ticker: str) -> pd.DataFrame:
--+    """Load intraday data for the given ticker."""
--+    return yf.download(ticker, interval="1m", period="1d")
--+
--+
--+def main() -> None:
--+    st.title("GER40 Trading Dashboard")
--+
--+    data_load_state = st.text("Loading data...")
--+    data = load_data(TICKER)
--+    data_load_state.text("Loading data... done!")
--+
--+    if data.empty:
--+        st.error("No data retrieved. Please check your internet connection or ticker symbol.")
--+        return
--+
--+    data["EMA12"] = compute_ema(data, 12)
--+    data["EMA26"] = compute_ema(data, 26)
--+    macd_df = compute_macd(data)
--+    data["MACD"] = macd_df["MACD"]
--+    data["MACDSignal"] = macd_df["Signal"]
--+    data["RSI"] = compute_rsi(data)
--+    data["Signal"] = ["BUY" if ema12 > ema26 else "SELL" for ema12, ema26 in zip(data["EMA12"], data["EMA26"])]
--+
--+    st.subheader("Latest data")
--+    st.dataframe(data.tail())
--+
--+    fig = go.Figure(
--+        data=[
--+            go.Candlestick(
--+                x=data.index,
--+                open=data["Open"],
--+                high=data["High"],
--+                low=data["Low"],
--+                close=data["Close"],
--+                name="Candles",
--+            )
--+        ]
--+    )
--+    fig.add_trace(
--+        go.Scatter(x=data.index, y=data["EMA12"], line=dict(color="blue", width=1), name="EMA12")
--+    )
--+    fig.add_trace(
--+        go.Scatter(x=data.index, y=data["EMA26"], line=dict(color="orange", width=1), name="EMA26")
--+    )
--+    st.plotly_chart(fig, use_container_width=True)
--+
--+    st.subheader("Indicators")
--+    st.line_chart(data[["RSI"]])
--+    st.line_chart(data[["MACD", "MACDSignal"]])
--+
--+    st.subheader("Current Signal")
--+    st.write(data["Signal"].iloc[-1])
--+
--+    forecast = forecast_prices(data["Close"], steps=3)
--+    st.subheader("Next 3 Candle Forecast")
--+    st.write(forecast)
--+
--+
--+if __name__ == "__main__":
--+    main()
-- 
--EOF
--)
-+import streamlit as st
-+import pandas as pd
-+import plotly.graph_objects as go
-+import yfinance as yf
-+
-+TICKER = "^GDAXI"  # GER40 / DAX index
-+
-+
-+def load_data(ticker: str) -> pd.DataFrame:
-+    """Return 1 day of 1‑minute data for the given ticker."""
-+    return yf.download(ticker, interval="1m", period="1d")
-+
-+
-+def main() -> None:
-+    st.title("GER40 Chart")
-+
-+    status = st.empty()
-+    status.text("Loading data …")
-+    data = load_data(TICKER)
-+    status.text("")
-+
-+    if data.empty:
-+        st.error("No data returned from Yahoo Finance.")
-+        return
-+
-+    fig = go.Figure(
-+        data=[
-+            go.Candlestick(
-+                x=data.index,
-+                open=data["Open"],
-+                high=data["High"],
-+                low=data["Low"],
-+                close=data["Close"],
-+            )
-+        ]
-+    )
-+    st.plotly_chart(fig, use_container_width=True)
-+
-+
-+if __name__ == "__main__":
-+    main()
- 
-EOF
-)
+import streamlit as st
+import pandas as pd
+import plotly.graph_objects as go
+import yfinance as yf
+
+TICKER = "^GDAXI"  # GER40 / DAX index
+
+
+def load_data(ticker: str) -> pd.DataFrame:
+    """Return 1 day of 1‑minute data for the given ticker."""
+    return yf.download(ticker, interval="1m", period="1d")
+
+
+def main() -> None:
+    st.title("GER40 Chart")
+
+    status = st.empty()
+    status.text("Loading data …")
+    data = load_data(TICKER)
+    status.text("")
+
+    if data.empty:
+        st.error("No data returned from Yahoo Finance.")
+        return
+
+    fig = go.Figure(
+        data=[
+            go.Candlestick(
+                x=data.index,
+                open=data["Open"],
+                high=data["High"],
+                low=data["Low"],
+                close=data["Close"],
+            )
+        ]
+    )
+    st.plotly_chart(fig, use_container_width=True)
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
