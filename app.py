from binance.client import Client
import pandas as pd
import datetime

client = Client()

# Hole OHLCV Daten von Binance (1-Minuten-Kerzen, ohne API-Key nutzbar für öffentliche Daten)
def get_binance_ohlcv(symbol="XRPUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

    return df
