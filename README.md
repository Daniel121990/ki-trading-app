 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index 4a8b4ca24d9ea72b9a6b83ee5ecce04c71cd1227..b610106f1d0d71351de22d22d9960f10d31bbb80 100644
--- a/README.md
+++ b/README.md
@@ -1,20 +1,21 @@
 # KI-Trading-App
 
 Live-Trading-Analyse für Gold, Tesla, NVIDIA, XRP u.a.
 Funktionen:
 - Live-Charts (1-Minuten)
 - EMA, RSI, MACD
 - Signal-Anzeige BUY/SELL (folgt)
 - Prognose der nächsten 3 Candles (folgt)
 
 ## Ausführen lokal
 ```bash
 pip install -r requirements.txt
 streamlit run app.py
 ```
 
 ## Deployment mit Streamlit Cloud
 1. Forke dieses Repo
 2. Gehe zu https://streamlit.io/cloud
 3. Verknüpfe deinen GitHub-Account
-4. Wähle dein Repo aus und deploye
+4. Wähle dein Repo aus und deploye
+
 
EOF
)
