#!/usr/bin/env python3
"""
Dragon Clan Morning Strategy Report Generator
華爾特專用 - 每日晨間策略報告生成器
Version 2.0 - 強化數據品質與格式統一
"""
import os
import datetime
import urllib.request
import json
import time

# === Configuration ===
REPORT_DIR = "/Users/moonstar/Desktop/龍族報告/股票"
FILE_NAME = f"每日股市投資報告_{datetime.datetime.now().strftime('%Y%m%d')}.md"
REPORT_PATH = os.path.join(REPORT_DIR, FILE_NAME)

# === Portfolio Definition ===
PORTFOLIO = [
    {"code": "2330.TW",  "name": "台積電", "shares": 100, "cost": 1825.0},
    {"code": "4938.TW",  "name": "和碩",   "shares": 700, "cost": 69.8},
    {"code": "3376.TW",  "name": "新日興", "shares": 100, "cost": 179.0},
    {"code": "3019.TW",  "name": "亞光",   "shares": 100, "cost": 164.5},
    {"code": "6121.TWO", "name": "新普",   "shares": 100, "cost": 345.0},
    {"code": "0050.TW",  "name": "0050",   "shares": 40,  "cost": None},
    {"code": "0056.TW",  "name": "0056",   "shares": 100, "cost": None},
    {"code": "00713.TW", "name": "00713",  "shares": 200, "cost": None},
]

# === Market Indices ===
INDICES = {
    "^TWII":    "加權指數",
    "^GSPC":    "S&P 500",
    "^IXIC":    "NASDAQ",
    "^SOX":     "費城半導體",
    "DX-Y.NYB": "美元指數",
    "GC=F":     "黃金期貨",
    "^TNX":     "10Y 殖利率",
}

# === International Stocks ===
INTL_STOCKS = ["NVDA", "AAPL", "TSLA", "MSFT", "GOOGL", "AMDA", "META"]

# === Yahoo Finance Fetcher ===
def fetch_yahoo(symbol):
    """Fetch price data from Yahoo Finance API. Returns dict or None."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        return {
            "price": float(meta.get("regularMarketPrice", 0)),
            "prev_close": float(meta.get("chartPreviousClose", 0)),
            "currency": meta.get("currency", ""),
            "symbol": meta.get("symbol", symbol),
        }
    except Exception as e:
        return None

def fetch_rsi_approx(symbol):
    """Approximate RSI from recent closes. Returns float or None."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        closes = [c for c in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c]
        if len(closes) < 15:
            return None
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-15+i] - closes[-15+i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 1)
    except:
        return None

def pct_change(current, previous):
    """Calculate percentage change."""
    if not previous or previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100

def arrow(pct):
    """Return emoji arrow based on percentage."""
    if pct > 1:    return "🔴"
    if pct > 0:    return "🔴"
    if pct < -1:   return "🟢"
    if pct < 0:    return "🟢"
    return "⚪"

def rsi_status(rsi):
    """Return RSI status text."""
    if rsi is None:       return "N/A"
    if rsi >= 80:         return f"{rsi} ⚠️ 過熱"
    if rsi >= 70:         return f"{rsi} 偏強"
    if rsi >= 50:         return f"{rsi} 健康"
    if rsi >= 30:         return f"{rsi} 偏弱"
    return f"{rsi} ⚠️ 超賣"

# === Report Generation ===
def generate_report():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%H:%M")
    lines = []

    # --- Header ---
    lines.append(f"# 🐉 龍族每日股市投資報告 | Walter's Daily Market Intelligence")
    lines.append(f"**日期：** {date_str}  ")
    lines.append(f"**分析官：** 華爾特 (Walter)  ")
    lines.append(f"**狀態：** 即時數據更新中...")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 1: Market Overview ---
    lines.append("## 📊 大盤指數總覽")
    lines.append("")
    lines.append("| 指數 | 現價 | 漲跌 | 漲跌幅 |")
    lines.append("|------|------|------|--------|")

    for sym, name in INDICES.items():
        d = fetch_yahoo(sym)
        time.sleep(0.3)
        if d and d["price"] > 0:
            pct = pct_change(d["price"], d["prev_close"])
            ar = arrow(pct)
            if sym == "^TNX":
                lines.append(f"| {name} | {d['price']:.2f}% | {pct:+.2f} | {ar} |")
            elif sym == "DX-Y.NYB":
                lines.append(f"| {name} | {d['price']:.2f} | {pct:+.2f} | {ar} |")
            elif sym == "GC=F":
                lines.append(f"| 黃金期貨 | ${d['price']:.2f} | {pct:+.2f}% | {ar} |")
            else:
                lines.append(f"| {name} | {d['price']:,.0f} | {pct:+.2f}% | {ar} |")
        else:
            lines.append(f"| {name} | 數據待更新 | — | — |")

    lines.append("")
    lines.append("> 💡 數據來源：Yahoo Finance 即時報價")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 2: Portfolio Overview ---
    lines.append("## 💰 持倉損益總覽")
    lines.append("")
    lines.append("| 股票 | 股數 | 成本 | 現價 | 損益 | 損益% |")
    lines.append("|------|------|------|------|------|-------|")

    total_cost = 0
    total_value = 0

    for stock in PORTFOLIO:
        d = fetch_yahoo(stock["code"])
        time.sleep(0.3)
        if d and d["price"] > 0:
            price = d["price"]
            if stock["cost"] is not None:
                cost_total = stock["cost"] * stock["shares"]
                value_total = price * stock["shares"]
                pnl = value_total - cost_total
                pnl_pct = (pnl / cost_total) * 100
                total_cost += cost_total
                total_value += value_total
                pnl_str = f"+{pnl:,.0f}" if pnl >= 0 else f"{pnl:,.0f}"
                pnl_pct_str = f"+{pnl_pct:.2f}%" if pnl_pct >= 0 else f"{pnl_pct:.2f}%"
                emoji = "🟢" if pnl >= 0 else "🔴"
                lines.append(f"| {stock['name']} ({stock['code'].split('.')[0]}) | {stock['shares']} | {stock['cost']} | {price:.2f} | {emoji} {pnl_str} | {pnl_pct_str} |")
            else:
                value_total = price * stock["shares"]
                total_value += value_total
                lines.append(f"| {stock['name']} | {stock['shares']} | — | {price:.2f} | — | — |")
        else:
            lines.append(f"| {stock['name']} ({stock['code'].split('.')[0]}) | {stock['shares']} | {stock['cost'] or '—'} | 數據待更新 | — | — |")

    lines.append("")
    if total_cost > 0:
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost) * 100
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        lines.append(f"**💎 總持倉損益：** 總成本 NT$ {total_cost:,.0f} | 總市值 NT$ {total_value:,.0f} | {pnl_emoji} 總損益 **{'+' if total_pnl >= 0 else ''}{total_pnl:,.0f}** ({'+' if total_pnl_pct >= 0 else ''}{total_pnl_pct:.2f}%)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 3: International Stocks Quick View ---
    lines.append("## 🌍 國際市場快訊")
    lines.append("")
    lines.append("| 代號 | 現價 | RSI(14) 參考 | 趨勢 |")
    lines.append("|------|------|-------------|------|")

    for sym in INTL_STOCKS[:4]:
        d = fetch_yahoo(sym)
        time.sleep(0.3)
        rsi = fetch_rsi_approx(sym)
        if d and d["price"] > 0:
            pct = pct_change(d["price"], d["prev_close"])
            ar = arrow(pct)
            rsi_s = rsi_status(rsi)
            lines.append(f"| {sym} | ${d['price']:.2f} | {rsi_s} | {ar} {pct:+.2f}% |")
        else:
            lines.append(f"| {sym} | 數據待更新 | — | — |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Section 4: Portfolio Deep Dive ---
    lines.append("## 🔍 持股深度建議")
    lines.append("")

    for stock in PORTFOLIO[:5]:
        d = fetch_yahoo(stock["code"])
        rsi = fetch_rsi_approx(stock["code"])
        time.sleep(0.3)
        code_short = stock["code"].split(".")[0]

        lines.append(f"### {stock['name']} ({code_short})")
        lines.append("")

        if d and d["price"] > 0:
            price = d["price"]
            pct = pct_change(price, d["prev_close"])
            ar = arrow(pct)

            if stock["cost"] is not None:
                pnl = (price - stock["cost"]) * stock["shares"]
                pnl_pct = ((price - stock["cost"]) / stock["cost"]) * 100
                pnl_str = f"+{pnl:,.0f}" if pnl >= 0 else f"{pnl:,.0f}"
                pnl_pct_str = f"+{pnl_pct:.2f}%" if pnl_pct >= 0 else f"{pnl_pct:.2f}%"
                lines.append(f"- **現價：** {price:.2f} | **成本：** {stock['cost']} | **損益：** {pnl_str} ({pnl_pct_str})")
            else:
                lines.append(f"- **現價：** {price:.2f}")

            lines.append(f"- **漲跌幅：** {ar} {pct:+.2f}% | **RSI(14)：** {rsi_status(rsi)}")
            lines.append(f"- **操作建議：** 請參考華爾特 cron 報告中的詳細分析")
        else:
            lines.append("- **現價：** 數據待更新")

        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Section 5: Gold Analysis ---
    lines.append("## 🥇 黃金分析")
    lines.append("")
    gold = fetch_yahoo("GC=F")
    dxy = fetch_yahoo("DX-Y.NYB")
    tnx = fetch_yahoo("^TNX")
    time.sleep(0.3)

    if gold and gold["price"] > 0:
        gold_pct = pct_change(gold["price"], gold["prev_close"])
        ar = arrow(gold_pct)
        lines.append(f"- **黃金期貨：** ${gold['price']:.2f} | {ar} {gold_pct:+.2f}%")
    else:
        lines.append("- **黃金期貨：** 數據待更新")

    if dxy and dxy["price"] > 0:
        dxy_pct = pct_change(dxy["price"], dxy["prev_close"])
        ar = arrow(dxy_pct)
        lines.append(f"- **美元指數：** {dxy['price']:.2f} | {ar} {dxy_pct:+.2f}")
    else:
        lines.append("- **美元指數：** 數據待更新")

    if tnx and tnx["price"] > 0:
        lines.append(f"- **10Y 殖利率：** {tnx['price']:.2f}%")
    else:
        lines.append("- **10Y 殖利率：** 數據待更新")

    lines.append("")
    lines.append("> 💡 完整黃金分析與操作建議，請見華爾特 cron 報告")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Footer ---
    lines.append(f"*報告由龍族財務分析官「華爾特」自動生成 | 數據更新於 {now.strftime('%Y-%m-%d %H:%M')} (GMT+8)*")
    lines.append("")
    lines.append("⚠️ **免責聲明：** 本報告僅供龍族決策參考，不構成直接投資建議。市場有風險，投資需謹慎。")

    # --- Write to file ---
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Report generated: {REPORT_PATH}")
    return REPORT_PATH

if __name__ == "__main__":
    path = generate_report()
    print(f"📄 Output: {path}")
