#!/usr/bin/env python3
import json
import sys
import traceback

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yfinance', 'pandas', 'numpy', '--break-system-packages'])
    import yfinance as yf
    import pandas as pd
    import numpy as np

def get_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_ma(series, period):
    return series.rolling(window=period).mean()

def analyze_stock(ticker_str, name):
    try:
        t = yf.Ticker(ticker_str)
        hist = t.history(period='1y')
        if hist.empty or len(hist) < 5:
            return {"error": f"No data for {ticker_str}", "name": name, "ticker": ticker_str}
        
        current = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change_pct = ((current - prev_close) / prev_close) * 100
        
        ma5 = get_ma(hist['Close'], 5).iloc[-1]
        ma10 = get_ma(hist['Close'], 10).iloc[-1]
        ma20 = get_ma(hist['Close'], 20).iloc[-1]
        rsi14 = get_rsi(hist['Close'], 14).iloc[-1]
        
        high_52w = hist['Close'].tail(252).max() if len(hist) >= 252 else hist['Close'].max()
        low_52w = hist['Close'].tail(252).min() if len(hist) >= 252 else hist['Close'].min()
        
        return {
            "ticker": ticker_str,
            "name": name,
            "current": round(current, 2),
            "prev_close": round(prev_close, 2),
            "change_pct": round(change_pct, 2),
            "change_val": round(current - prev_close, 2),
            "ma5": round(ma5, 2) if not pd.isna(ma5) else None,
            "ma10": round(ma10, 2) if not pd.isna(ma10) else None,
            "ma20": round(ma20, 2) if not pd.isna(ma20) else None,
            "rsi14": round(rsi14, 2) if not pd.isna(rsi14) else None,
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "volume": int(hist['Volume'].iloc[-1]),
            "vol_ma5": int(hist['Volume'].tail(5).mean()),
            "error": None
        }
    except Exception as e:
        return {"error": str(e), "name": name, "ticker": ticker_str}

def analyze_gold():
    results = {}
    for ticker_str, name in [("GC=F", "黃金期貨"), ("^TNX", "美10年期公債殖利率"), ("DX-Y.NYB", "美元指數")]:
        try:
            t = yf.Ticker(ticker_str)
            hist = t.history(period='1y')
            if hist.empty:
                results[name] = {"error": "No data", "ticker": ticker_str}
                continue
            
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change_pct = ((current - prev_close) / prev_close) * 100
            
            # Recent (1 month ~ 21 trading days)
            recent = hist['Close'].tail(21)
            mid = hist['Close'].tail(63)
            long_ = hist['Close'].tail(252)
            
            results[name] = {
                "ticker": ticker_str,
                "current": round(current, 4),
                "prev_close": round(prev_close, 4),
                "change_pct": round(change_pct, 2),
                "change_val": round(current - prev_close, 4),
                "ma1m": round(recent.mean(), 4),
                "ma3m": round(mid.mean(), 4),
                "ma12m": round(long_.mean(), 4),
                "high1m": round(recent.max(), 4),
                "low1m": round(recent.min(), 4),
                "high3m": round(mid.max(), 4),
                "low3m": round(mid.min(), 4),
                "high12m": round(long_.max(), 4),
                "low12m": round(long_.min(), 4),
                "ma5": round(get_ma(hist['Close'], 5).iloc[-1], 4),
                "ma10": round(get_ma(hist['Close'], 10).iloc[-1], 4),
                "ma20": round(get_ma(hist['Close'], 20).iloc[-1], 4),
                "rsi14": round(get_rsi(hist['Close'], 14).iloc[-1], 2),
                "error": None
            }
        except Exception as e:
            results[name] = {"error": str(e), "ticker": ticker_str}
    return results

def get_index_data():
    results = {}
    for ticker_str, name in [("^TWII", "加權指數"), ("^GSPC", "S&P 500"), ("^IXIC", "NASDAQ")]:
        try:
            t = yf.Ticker(ticker_str)
            hist = t.history(period='3mo')
            if hist.empty:
                continue
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change_pct = ((current - prev) / prev) * 100
            results[name] = {
                "current": round(current, 2),
                "change_pct": round(change_pct, 2),
                "ticker": ticker_str
            }
        except:
            pass
    return results

def get_hot_us_stocks():
    """Fetch data hot US stocks for recommendation."""
    candidates = [
        ("NVDA", "輝達"), ("MSFT", "微軟"), ("AAPL", "蘋果"),
        ("GOOG", "谷歌"), ("AMZN", "亞馬遜"), ("META", "Meta"),
        ("TSLA", "特斯拉"), ("AMD", "AMD"), ("TSM", "台積電ADR"),
        ("SMH", "費城半導體ETF"), ("AVGO", "博通"),
    ]
    results = []
    for ticker_str, name in candidates:
        try:
            t = yf.Ticker(ticker_str)
            hist = t.history(period='3mo')
            if hist.empty or len(hist) < 20:
                continue
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change_pct = ((current - prev) / prev) * 100
            ma5 = get_ma(hist['Close'], 5).iloc[-1]
            ma10 = get_ma(hist['Close'], 10).iloc[-1]
            ma20 = get_ma(hist['Close'], 20).iloc[-1]
            rsi = get_rsi(hist['Close'], 14).iloc[-1]
            vol_ratio = hist['Volume'].iloc[-1] / hist['Volume'].tail(20).mean() if hist['Volume'].tail(20).mean() > 0 else 1
            
            results.append({
                "ticker": ticker_str,
                "name": name,
                "current": round(current, 2),
                "change_pct": round(change_pct, 2),
                "ma5": round(ma5, 2) if not pd.isna(ma5) else None,
                "ma10": round(ma10, 2) if not pd.isna(ma10) else None,
                "ma20": round(ma20, 2) if not pd.isna(ma20) else None,
                "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
                "vol_ratio": round(vol_ratio, 2),
            })
        except:
            pass
    return results

def get_hot_tw_stocks():
    """Fetch data for hot TW stocks for recommendation."""
    candidates = [
        ("2454.TW", "聯發科"), ("2379.TW", "瑞昱"), ("3034.TW", "聯詠"),
        ("2303.TW", "聯電"), ("2308.TW", "台達電"), ("2412.TW", "中華電"),
        ("6415.TW", "矽力"), ("3260.TW", "威鋒電子"), ("6531.TW", "愛普"),
        ("3548.TW", "兆利"), ("2344.TW", "華邦電"), ("8069.TW", "元太"),
        ("4919.TW", "唐欣"), ("6715.TW", "嘉基"), ("3661.TW", "世芯"),
        ("3008.TW", "大立光"),
    ]
    results = []
    for ticker_str, name in candidates:
        try:
            t = yf.Ticker(ticker_str)
            hist = t.history(period='3mo')
            if hist.empty or len(hist) < 20:
                continue
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change_pct = ((current - prev) / prev) * 100
            ma5 = get_ma(hist['Close'], 5).iloc[-1]
            ma10 = get_ma(hist['Close'], 10).iloc[-1]
            ma20 = get_ma(hist['Close'], 20).iloc[-1]
            rsi = get_rsi(hist['Close'], 14).iloc[-1]
            vol_ratio = hist['Volume'].iloc[-1] / hist['Volume'].tail(20).mean() if hist['Volume'].tail(20).mean() > 0 else 1
            
            results.append({
                "ticker": ticker_str,
                "name": name,
                "current": round(current, 2),
                "change_pct": round(change_pct, 2),
                "ma5": round(ma5, 2) if not pd.isna(ma5) else None,
                "ma10": round(ma10, 2) if not pd.isna(ma10) else None,
                "ma20": round(ma20, 2) if not pd.isna(ma20) else None,
                "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
                "vol_ratio": round(vol_ratio, 2),
            })
        except:
            pass
    return results

# ===== MAIN =====
output = {}

# 勞勞持股
portfolio = {
    "台積電": {"ticker": "2330.TW", "cost": 1825, "qty": 100},
    "和碩": {"ticker": "4938.TW", "cost": 69.8, "qty": 1000},
    "新日興": {"ticker": "3376.TW", "cost": 179, "qty": 100},
    "亞光": {"ticker": "3019.TW", "cost": 164.5, "qty": 200},
    "新普": {"ticker": "6121.TWO", "cost": 345, "qty": 100},
}

output["portfolio"] = {}
for name, info in portfolio.items():
    data = analyze_stock(info["ticker"], name)
    data["cost"] = info["cost"]
    data["qty"] = info["qty"]
    if data.get("error"):
        output["portfolio"][name] = data
        continue
    total_cost = info["cost"] * info["qty"]
    total_value = data["current"] * info["qty"]
    profit = total_value - total_cost
    profit_pct = (profit / total_cost) * 100
    data["total_cost"] = total_cost
    data["total_value"] = round(total_value, 2)
    data["profit"] = round(profit, 2)
    data["profit_pct"] = round(profit_pct, 2)
    output["portfolio"][name] = data

# 黃金相關
output["gold"] = analyze_gold()

# 指數
output["indices"] = get_index_data()

# 候選股票
output["tw_candidates"] = get_hot_tw_stocks()
output["us_candidates"] = get_hot_us_stocks()

print(json.dumps(output, ensure_ascii=False, indent=2))
