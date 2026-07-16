import yfinance as yf
from datetime import datetime
import json

def get_stock_data():
    ticker_symbol = "4938.TW"
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(period='5d')
        if hist.empty or len(hist) < 2:
            return {"error": "Could not fetch sufficient data for 4938.TW"}
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        change_val = current_price - prev_close
        change_pct = (change_val / prev_close) * 100
        return {
            "current": round(float(current_price), 2),
            "prev_close": round(float(prev_close), 2),
            "change_val": round(float(change_val), 2),
            "change_pct": round(float(change_pct), 2),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(json.dumps(get_stock_data()))
