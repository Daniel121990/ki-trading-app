 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/zielchecker.py b/zielchecker.py
index 8b137891791fe96927ad78e64b0aad7bded08bdc..4cabe32859b19ea8c523f12b7910bf374ee39455 100644
--- a/zielchecker.py
+++ b/zielchecker.py
@@ -1 +1,37 @@
+import numpy as np
+import pandas as pd
+from sklearn.linear_model import LinearRegression
 
+
+def compute_ema(data: pd.DataFrame, span: int) -> pd.Series:
+    """Calculate Exponential Moving Average."""
+    return data['Close'].ewm(span=span, adjust=False).mean()
+
+
+def compute_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
+    """Calculate Relative Strength Index."""
+    delta = data['Close'].diff()
+    up = delta.clip(lower=0)
+    down = -delta.clip(upper=0)
+    ma_up = up.rolling(window=period, min_periods=period).mean()
+    ma_down = down.rolling(window=period, min_periods=period).mean()
+    rs = ma_up / ma_down
+    return 100 - (100 / (1 + rs))
+
+
+def compute_macd(data: pd.DataFrame) -> pd.DataFrame:
+    """Calculate MACD line and signal."""
+    ema12 = compute_ema(data, 12)
+    ema26 = compute_ema(data, 26)
+    macd = ema12 - ema26
+    signal = macd.ewm(span=9, adjust=False).mean()
+    return pd.DataFrame({'MACD': macd, 'Signal': signal})
+
+
+def forecast_prices(close: pd.Series, steps: int = 3) -> np.ndarray:
+    """Forecast future prices using a simple linear regression."""
+    close = close.dropna()
+    X = np.arange(len(close)).reshape(-1, 1)
+    model = LinearRegression().fit(X, close.values)
+    future_idx = np.arange(len(close), len(close) + steps).reshape(-1, 1)
+    return model.predict(future_idx)
 
EOF
)
