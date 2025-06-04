 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/zielchecker.py
index 0000000000000000000000000000000000000000..948a6451671a1fdf20f4446b5001a9d3b2e4204d 100644
--- a//dev/null
+++ b/zielchecker.py
@@ -0,0 +1,41 @@
+import streamlit as st
+import yfinance as yf
+import pandas_ta as ta
+
+
+def run_zielchecker(asset: str) -> None:
+    """Simple probability helper for a price target."""
+
+    st.subheader("Zielchecker")
+
+    try:
+        data = yf.download(asset, period="1mo", interval="1h")
+    except Exception as err:
+        st.error(f"Daten konnten nicht geladen werden: {err}")
+        return
+
+    if data.empty:
+        st.warning("Keine Daten ver\xFCgbar")
+        return
+
+    target = st.number_input(
+        "Kursziel eingeben",
+        value=float(data["Close"].iloc[-1]),
+        key="target_input",
+    )
+
+    if st.button("Check Ziel", key="zielcheck_btn"):
+        if len(data) < 20:
+            st.warning("Nicht genug Daten f\xFCr Analyse")
+            return
+        ema50 = ta.ema(data["Close"], length=50)
+        ema200 = ta.ema(data["Close"], length=200)
+        trend = "Aufwärts" if ema50.iloc[-1] > ema200.iloc[-1] else "Abwärts"
+        support = data["Low"].rolling(window=20).min().iloc[-1]
+        resistance = data["High"].rolling(window=20).max().iloc[-1]
+        probability = 0.7 if support <= target <= resistance else 0.3
+
+        st.metric("Wahrscheinlichkeit", f"{probability * 100:.0f}%")
+        st.metric("Trendrichtung", trend)
+        st.metric("Support", f"{support:.2f}")
+        st.metric("Resistance", f"{resistance:.2f}")
 
EOF
)
