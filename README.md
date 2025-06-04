 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index 5e16e67caa0876f2264adbe4958b84cf5aae908f..6c368c364a47cb52a1a469972548cd772b564028 100644
--- a/README.md
+++ b/README.md
@@ -1,31 +1,23 @@
- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
-diff --git a/README.md b/README.md
-index 4a8b4ca24d9ea72b9a6b83ee5ecce04c71cd1227..b610106f1d0d71351de22d22d9960f10d31bbb80 100644
---- a/README.md
-+++ b/README.md
-@@ -1,20 +1,21 @@
- # KI-Trading-App
- 
- Live-Trading-Analyse für Gold, Tesla, NVIDIA, XRP u.a.
- Funktionen:
- - Live-Charts (1-Minuten)
- - EMA, RSI, MACD
- - Signal-Anzeige BUY/SELL (folgt)
- - Prognose der nächsten 3 Candles (folgt)
- 
- ## Ausführen lokal
- ```bash
- pip install -r requirements.txt
- streamlit run app.py
- ```
- 
- ## Deployment mit Streamlit Cloud
- 1. Forke dieses Repo
- 2. Gehe zu https://streamlit.io/cloud
- 3. Verknüpfe deinen GitHub-Account
--4. Wähle dein Repo aus und deploye
-+4. Wähle dein Repo aus und deploye
-+
- 
-EOF
-)
+# KI-Trading-App
+
+A simple Streamlit dashboard for analyzing the GER40 (DAX40) index. It pulls
+latest intraday data from Yahoo Finance and displays common technical
+indicators.
+
+## Features
+- Live 1‑minute candlestick chart for the GER40
+- Exponential Moving Averages (EMA), Relative Strength Index (RSI) and MACD
+- Simple BUY/SELL signal using EMA crossover
+- Forecast of the next three candles based on a linear trend model
+
+## Local Usage
+```bash
+pip install -r requirements.txt
+streamlit run app.py
+```
+
+## Deployment with Streamlit Community Cloud
+1. Fork this repository
+2. Go to https://streamlit.io/cloud
+3. Connect your GitHub account
+4. Select your fork and deploy
 
EOF
)
