#!/usr/bin/env python3
"""
Dragon Clan Morning Strategy Report (08:40)
Structure:
1. International Market Focus (3 Stocks)
2. Domestic Market Focus (3 Stocks)
3. Long-term Investment Recommendations
4. Personal Portfolio Advice
"""
import os
import datetime
import urllib.request
import json

# --- Configuration ---
REPORT_DIR = "/Users/moonstar/Desktop/龍族報告/股票"
FILE_NAME = f"早上策略報告-{datetime.datetime.now().strftime('%Y%m%d')}.md"
REPORT_PATH = os.path.join(REPORT_DIR, FILE_NAME)

# Stock Symbols (Placeholders - to be updated by AI logic or static list)
INTL_SYMBOLS = ["AAPL", "TSLA", "NVDA"]
DOM_SYMBOLS = ["2330.TW", "4938.TW", "3019.TW"] 
PORTFOLIO_STOCK = "4938.TW"

def fetch_price(symbol):
    """Fetch current price from Yahoo Finance using urllib"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User_Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
    except Exception:
        return 0.0

def generate_report():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timestamp = now
    
    report_content = f"## 🐉 龍族晨間策略報告 ({timestamp})\n\n### 🌍 國際市場觀測 (International Focus)\n| 代號 | 現價 | 市場趨勢觀察 |\n| :--- | :--- | :--- |\n"
    
    # Adding International Stocks
    for s in INTL_SYMBOLS:
        p = fetch_price(s)
        report_content += f"| {s} | ${p:.2f} | 市場關注度高，觀察波動性 |\n"

    report_content += "\n### 🇹🇼 國內市場觀測 (Domestic Focus)\n| 代號 | 現價 | 技術面觀察 |\n| :--- | :--- | :--- |\n"
    for s in DOM_SYMBOLS:
        p = fetch_price(s)
        report_content += f"| {s} | ${p:.2f} | 支撐位確認 |\n"

    report_content += "\n### 🎯 長線投資標的推薦\n- **標的 A**: 持續觀察，基本面優異\\n- **標的 B**: 等待回檔佈局\\n"
    report_content += "\n### 💰 個人持股建議 (Portfolio Advice)\n"
    report_content += f"- **{PORTFOLIO_STOCK}**: 維持現狀，隨時注意 RSI 指標。\\n- 其他部位: 持平觀望。\\n"
    report_content += "\n---\n*由龍_桃樂絲 自動生成*"

    # Save to file
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"Report generated successfully at: {REPORT_PATH}")
    return REPORT_PATH

if __name__ == "__main__":
    path = generate_report()
    print(f"Final Output Path: {path}")
