#!/usr/bin/env python3
"""
和碩 (4938.TW) 股價追蹤腳本 - 2026-06-03
目標：追蹤股價並在 RSI 超買時建議賣出 30%
"""
import json, urllib.request, datetime, os, sys

# === 設定 ===
SYMBOL = "4938.TW"
REPORT_DIR = os.path.expanduser("~/Desktop/龍族報告/股票")
REPORT_FILE = os.path.join(REPORT_DIR, "和碩追蹤-20260603.md")
STOP_LOSS = 85.0
RSI_OVERBOUGHT = 74.0
COST_PRICE = 77.0  # 推算成本 (105 / 1.31 ≈ 77)

os.makedirs(REPORT_DIR, exist_ok=True)

def fetch_data():
    """從 Yahoo Finance 取得股價資料"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval=1d&range=60d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def get_signal(rsi, current_price):
    """根據 RSI 和價格判斷買賣信號"""
    if current_price <= STOP_LOSS:
        return "🔴 停損", f"價格 {current_price} 已觸及停損價 {STOP_LOSS}，建議立即賣出"
    elif rsi >= 80:
        return "🟢 強烈賣出", f"RSI={rsi:.1f} 嚴重超買，價格創 52 週高點附近，建議積極賣出 30%"
    elif rsi >= RSI_OVERBOUGHT:
        return "🟡 建議賣出", f"RSI={rsi:.1f} 已達超買區，建議分批賣出 30%"
    elif rsi >= 60:
        return "⚪ 觀察", f"RSI={rsi:.1f} 偏強，持續觀察"
    else:
        return "⚪ 等待", f"RSI={rsi:.1f} 尚未到超買區，等待更好賣點"

def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S CST")
    
    # 檢查是否在交易時間
    market_open = now.replace(hour=9, minute=0, second=0)
    market_close = now.replace(hour=13, minute=30, second=0)
    
    if now < market_open or now > market_close:
        status = "⏸ 非交易時間 (09:00-13:30)，跳過追蹤"
        print(status)
        # 仍然記錄
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n## {timestamp}\n\n{status}\n\n---\n")
        return
    
    try:
        data = fetch_data()
    except Exception as e:
        error_msg = f"❌ 取得資料失敗: {e}"
        print(error_msg)
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n## {timestamp}\n\n{error_msg}\n\n---\n")
        return
    
    result = data["chart"]["result"][0]
    meta = result["meta"]
    current_price = meta["regularMarketPrice"]
    day_high = meta.get("regularMarketDayHigh", 0)
    day_low = meta.get("regularMarketDayLow", 0)
    volume = meta.get("regularMarketVolume", 0)
    week52_high = meta.get("fiftyTwoWeekHigh", 0)
    week52_low = meta.get("fiftyTwoWeekLow", 0)
    
    closes = result["indicators"]["quote"][0]["close"]
    timestamps = result["timestamp"]
    valid = [(t, c) for t, c in zip(timestamps, closes) if c is not None]
    price_list = [c for _, c in valid]
    
    rsi = calc_rsi(price_list)
    signal, advice = get_signal(rsi, current_price)
    
    # 計算報酬
    profit_pct = ((current_price - COST_PRICE) / COST_PRICE) * 100
    
    # 產生報告
    report = f"""## {timestamp}

### 📊 即時行情
| 項目 | 數值 |
|------|------|
| 現價 | **{current_price}** 元 |
| 今日高點 | {day_high} 元 |
| 今日低點 | {day_low} 元 |
| 成交量 | {volume:,} 張 |
| 52週高點 | {week52_high} 元 |
| 52週低點 | {week52_low} 元 |

### 📈 技術指標
| 指標 | 數值 | 狀態 |
|------|------|------|
| RSI(14) | **{rsi:.2f}** | {'🔴 嚴重超買' if rsi >= 80 else '🟡 超買' if rsi >= 74 else '⚪ 正常'} |
| 成本價 | {COST_PRICE} 元 | - |
| 目前獲利 | **{profit_pct:.1f}%** | {'✅ 已達目標' if profit_pct >= 30 else '⏳ 持續獲利中'} |
| 停損價 | {STOP_LOSS} 元 | 距停損 {((current_price - STOP_LOSS) / current_price * 100):.1f}% |

### 🎯 操作建議
**{signal}** — {advice}

> 目標：賣出 30% 持倉。目前獲利 {profit_pct:.1f}%，RSI={rsi:.1f} 已達超買區。

---
"""
    
    # 寫入報告
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(report)
    
    # 輸出摘要
    print(f"=== 和碩 (4938) 追蹤報告 ===")
    print(f"時間: {timestamp}")
    print(f"現價: {current_price} 元")
    print(f"RSI: {rsi:.2f}")
    print(f"獲利: {profit_pct:.1f}%")
    print(f"信號: {signal}")
    print(f"建議: {advice}")
    print(f"報告已寫入: {REPORT_FILE}")

if __name__ == "__main__":
    main()
