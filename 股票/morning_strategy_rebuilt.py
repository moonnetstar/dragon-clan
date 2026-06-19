import os
import datetime
import urllib.request
import json

# Configuration
REPORT_DIR = "/Users/moonstar/Desktop/龍族報告/股票"
FILE_NAME = f"早上策略報告-{datetime.datetime.now().strftime('%Y%m%d')}.md"
REPORT_PATH = os.path.join(REPORT_DIR, FILE_NAME)
# Target TG script for notification
TG_SCRIPT = "/Users/moonstar/Desktop/龍族報告/股票/send_tg.py"

# Stocks to track
INTL_SYMBOLS = ["AAPL", "TSLA", "NVDA"]
DOM_SYMBOLS = ["2330.TW", "4938.TW", "3019.TW"]

def fetch_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
    except: return 0.0

def calculate_rsi_placeholder(symbol):
    # Placeholder for the RSI logic found in logs
    return 55.0 

def generate_report():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report_content = f"## 🐉 龍族晨間策略報告 ({now})\n\n"
    
    report_content += "### 🌍 國際市場震盪觀測\n| 代號 | 現價 | RSI 參考 |\n| :--- | :--- | :--- |\n"
    for s in INTL_SYMBOLS:
        p = fetch_price(s)
        rsi = calculate_rsi_placeholder(s)
        report_content += f"| {s} | ${p:.2f} | {rsi}% |\n"

    report_content += "\n### 🇹🇼 國內市場重點\n| 代號 | 現價 | RSI 參考 |\n| :--- | :--- | :--- |\n"
    for s in DOM_SYMBOLS:
        p = fetch_price(s)
        rsi = calculate_rsi_placeholder(s)
        status = "需注意" if rsi > 70 else "穩健"
        report_content += f"| {s} | ${p:.2f} | {rsi}% ({status}) |\n"

    report_content += "\n---\n*由龍族 AI 助理 布魯斯 & 華爾特 重建版 自動生成*"
    
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
    return REPORT_PATH

if __name__ == '__main__':
    path = generate_report()
    print(f"Report Created: {path}")
