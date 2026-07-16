import yfinance as yf
import json
import os
from datetime import datetime

# 定義要追蹤的標的
tickers = ["2330.TW", "4938.TW", "SPY", "IXIC", "GC=F"]

def fetch_data():
    data = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1d")
            if not hist.empty:
                data[ticker] = {
                    "price": hist['Close'].iloc[-1],
                    "change": hist['Close'].iloc[-1] - hist['Open'].iloc[0]
                }
        except Exception as e:
            data[ticker] = {"error": str(e)}
    
    # 寫入臨時檔案供華爾特讀取
    output_path = "/Users/moonstar/Desktop/龍族報告/04_資源/Market_Data/market_data_temp.json"
    with open(output_path, 'w') as f:
        json.dump(data, f)
    print(f"Data fetched to {output_path}")

if __name__ == "__main__":
    fetch_data()
