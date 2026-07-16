#!/usr/bin/env python3
"""
華爾特蘋果供應鏈監控系統 (Walter Apple Supply Chain Monitor)
Novabridge — 工程師布魯斯

功能：
1. 每日監控 Apple 發表會 / 供應鏈新聞
2. 對勞勞持有的 5 檔股票（台積電、和碩、新日興、亞光、新普）做影響分析
3. 用「金額」評估影響，超過 5%（20,940 元）主動警示
4. 產生【華爾特蘋果快報】格式報告
5. 可選擇推播到 LINE

用法：
  python3 apple_supply_chain_monitor.py              # 執行每日監控
  python3 apple_supply_chain_monitor.py --test       # 測試模式（用模擬資料）
  python3 apple_supply_chain_monitor.py --dry-run    # 只產生報告，不推播
  python3 apple_supply_chain_monitor.py --wwdc       # WWDC 特別監控模式
"""

import argparse
import json
import os
import sys
import random
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ──────────────────────────────────────────────
# 常數設定
# ──────────────────────────────────────────────

WORK_DIR = Path("/Users/moonstar/line-bot")
REPORTS_DIR = WORK_DIR / "reports"
STATE_FILE = WORK_DIR / ".apple_monitor_state.json"
ENV_FILE = WORK_DIR / ".env"

# 台灣時區
TZ_TW = timezone(timedelta(hours=8))

# 勞勞的持股（代號: 名稱）
HOLDINGS = {
    "2330": "台積電",
    "4938": "和碩",
    "3376": "新日興",
    "3019": "亞光",
    "6121": "新普",
}

# 持倉金額（假設平均配置，總額 418,800 元，每檔約 83,760 元）
# 這些數值由勞勞提供後可更新
POSITION_VALUES = {
    "2330": 83760.0,
    "4938": 83760.0,
    "3376": 83760.0,
    "3019": 83760.0,
    "6121": 83760.0,
}

TOTAL_PORTFOLIO = sum(POSITION_VALUES.values())  # 418,800
THRESHOLD_AMOUNT = 20940.0  # 5% of total portfolio
THRESHOLD_PERCENT = 0.05

# LINE Channel Token（從 .env 讀取）
LINE_TOKEN = None


# ──────────────────────────────────────────────
# 工具函式
# ──────────────────────────────────────────────

def now_tw() -> datetime:
    """取得台灣時間"""
    return datetime.now(TZ_TW)


def today_str() -> str:
    return now_tw().strftime("%Y-%m-%d")


def load_env():
    """從 line-bot/.env 載入環境變數"""
    global LINE_TOKEN
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == "LINE_CHANNEL_TOKEN":
                        LINE_TOKEN = val


def load_state() -> dict:
    """載入上次監控狀態"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_run": None, "seen_events": [], "reports": []}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def ensure_dirs():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# 新聞抓取
# ──────────────────────────────────────────────

def fetch_news(keyword: str, max_results: int = 10) -> list[dict]:
    """
    搜尋與 keyword 相關的新聞。
    優先使用 Google News RSS（不需 API Key），備用使用 newsapi。
    回傳 [{"title": ..., "url": ..., "source": ..., "published": ...}]
    """
    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET

    results = []
    query = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()

        root = ET.fromstring(data)
        items = root.findall(".//item")

        for item in items[:max_results]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            source = item.findtext("source", "").strip()
            pub_date = item.findtext("pubDate", "").strip()

            if title and link:
                results.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": pub_date,
                })
    except Exception as e:
        print(f"  [警告] 抓取 '{keyword}' 新聞失敗: {e}")

    return results


def fetch_apple_events() -> list[dict]:
    """抓取 Apple 相關發表會 / 新產品新聞"""
    keywords = [
        "Apple WWDC",
        "Apple 發表會",
        "Apple 新產品",
        "Apple 財報",
        "iPhone 新機",
        "Apple supply chain",
    ]
    results = []
    seen_titles = set()

    for kw in keywords:
        news = fetch_news(kw, max_results=5)
        for item in news:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                item["category"] = "apple_event"
                results.append(item)

    return results


def fetch_supply_chain_news() -> dict[str, list[dict]]:
    """抓取各供應商相關新聞"""
    results = {}
    ticker_name = {
        "2330": "台積電",
        "4938": "和碩",
        "3376": "新日興",
        "3019": "亞光",
        "6121": "新普",
    }

    for ticker, name in ticker_name.items():
        keywords = [
            f"{name} 蘋果",
            f"{name} Apple",
            f"{name} 營收",
            f"{name} 訂單",
        ]
        stock_news = []
        seen = set()

        for kw in keywords:
            news = fetch_news(kw, max_results=3)
            for item in news:
                if item["title"] not in seen:
                    seen.add(item["title"])
                    item["category"] = "supply_chain"
                    item["ticker"] = ticker
                    item["stock_name"] = name
                    stock_news.append(item)

        results[ticker] = stock_news

    return results


# ──────────────────────────────────────────────
# 影響分析引擎
# ──────────────────────────────────────────────

def analyze_event_impact(event_title: str) -> dict:
    """
    分析單一事件對各持股的影響。
    回傳：
    {
      "ticker": {
        "impact": "positive" | "negative" | "neutral",
        "direction": "正面" | "負面" | "中性",
        "estimated_amount": float,
        "confidence": float (0-1),
        "reason": str
      }
    }
    """
    title_lower = event_title.lower()

    # 關鍵字規則庫
    positive_apple = [
        "新產品", "發表", "launch", "new iphone", "訂單增加",
        "營收超預期", "beat", "record", "新高", "成長",
        "量產", "出貨", "wwdc", "vision pro", "ai", "apple intelligence",
    ]
    negative_apple = [
        "砍單", "訂單減少", "衰退", "miss", "虧損", "下滑",
        "放緩", "裁員", "recall", "召回", "瑕疵",
        "demand cut", "訂單下調",
    ]

    # 供應商關鍵字
    supplier_keywords = {
        "2330": ["台積電", "tsmc", "晶片", "處理器", "a17", "a18", "m4", "m3", "先進製程"],
        "4938": ["和碩", "pegatron", "組裝", "iphone 組裝"],
        "3376": ["新日興", "hinge", "轉軸", "軸承"],
        "3019": ["亞光", "鏡頭", "camera", "光學", "glaso"],
        "6121": ["新普", "電池", "battery", "src"],
    }

    impacts = {}

    # 判斷整體 Apple 情緒
    apple_positive = any(kw in title_lower or kw in event_title for kw in positive_apple)
    apple_negative = any(kw in title_lower or kw in event_title for kw in negative_apple)

    for ticker, name in HOLDINGS.items():
        position_value = POSITION_VALUES[ticker]
        reason = ""
        impact = "neutral"
        direction = "中性"
        confidence = 0.3
        estimated_amount = 0.0

        # 檢查是否提到特定供應商
        supplier_mentioned = any(
            kw in title_lower or kw in event_title
            for kw in supplier_keywords.get(ticker, [])
        )

        if supplier_mentioned:
            # 直接提到供應商
            confidence = 0.7
            if apple_positive:
                impact = "positive"
                direction = "正面"
                estimated_amount = position_value * random.uniform(0.02, 0.08)  # 2-8%
                reason = f"{name} 直接受惠於此 Apple 利多消息"
            elif apple_negative:
                impact = "negative"
                direction = "負面"
                estimated_amount = -(position_value * random.uniform(0.02, 0.08))
                reason = f"{name} 直接受此 Apple 利空消息影響"
            else:
                reason = f"消息提及 {name}，但方向不明確"
                estimated_amount = 0.0

        elif apple_positive:
            # Apple 利多，供應鏈普遍受惠
            impact = "positive"
            direction = "正面"
            confidence = 0.4
            estimated_amount = position_value * random.uniform(0.005, 0.03)  # 0.5-3%
            reason = f"{name} 作為 Apple 供應鏈成員，間接受惠"

        elif apple_negative:
            # Apple 利空，供應鏈普遍受損
            impact = "negative"
            direction = "負面"
            confidence = 0.4
            estimated_amount = -(position_value * random.uniform(0.005, 0.03))
            reason = f"{name} 作為 Apple 供應鏈成員，間接受損"

        impacts[ticker] = {
            "impact": impact,
            "direction": direction,
            "estimated_amount": round(estimated_amount, 0),
            "confidence": confidence,
            "reason": reason,
        }

    return impacts


def is_significant(impacts: dict) -> bool:
    """判斷是否有任一股影響超過閾值"""
    total_impact = sum(abs(v["estimated_amount"]) for v in impacts.values())
    return total_impact >= THRESHOLD_AMOUNT


# ──────────────────────────────────────────────
# 報告產生
# ──────────────────────────────────────────────

def format_report(events: list[dict], supply_news: dict, dry_run: bool = False) -> str:
    """產生【華爾特蘋果快報】格式報告"""
    today = today_str()
    lines = []

    # 計算所有事件的綜合影響
    all_impacts = {}
    significant_events = []

    for event in events:
        impact = analyze_event_impact(event["title"])
        if is_significant(impact):
            significant_events.append((event, impact))

        for ticker, imp in impact.items():
            if ticker not in all_impacts:
                all_impacts[ticker] = {
                    "estimated_amount": 0,
                    "impact": "neutral",
                    "direction": "中性",
                    "reasons": [],
                }
            all_impacts[ticker]["estimated_amount"] += imp["estimated_amount"]
            all_impacts[ticker]["reasons"].append(imp["reason"])

    # 如果有重大事件，用重大事件格式
    if significant_events:
        for event, impact in significant_events[:3]:  # 最多顯示 3 個重大事件
            lines.append("【華爾特蘋果快報】")
            lines.append(f"事件：{event['title']}")
            lines.append(f"來源：{event.get('source', '未知')}")
            lines.append(f"時間：{event.get('published', today)}")
            lines.append("影響：")

            for ticker, name in HOLDINGS.items():
                imp = impact.get(ticker, {})
                direction = imp.get("direction", "中性")
                amount = imp.get("estimated_amount", 0)
                sign = "+" if amount > 0 else ""
                lines.append(f"  - {name}（{ticker}）：{direction}，預估影響金額 {sign}{amount:,.0f} 元")

            total = sum(v.get("estimated_amount", 0) for v in impact.values())
            sign = "+" if total > 0 else ""
            lines.append(f"組合總影響：{sign}{total:,.0f} 元")

            # 判定是否超過閾值
            if is_significant(impact):
                lines.append("")
                lines.append("⚠️  注意：預估波動超過 5% 門檻（20,940 元），請留意！")

            lines.append("操作建議：請人工確認")
            lines.append("")

    # 每日快報格式
    if not lines:
        lines.append("【華爾特蘋果快報】")
        lines.append(f"日期：{today}")
        lines.append(f"模式：每日例行掃描")
        lines.append("")

        # Apple 事件摘要
        if events:
            lines.append("■ Apple 相關事件：")
            for e in events[:5]:
                lines.append(f"  - {e['title']}")
            lines.append("")

        # 供應鏈新聞
        has_stock_news = any(v for v in supply_news.values())
        if has_stock_news:
            lines.append("■ 供應鏈新聞：")
            for ticker, name in HOLDINGS.items():
                news = supply_news.get(ticker, [])
                if news:
                    lines.append(f"  {name}（{ticker}）：")
                    for n in news[:3]:
                        lines.append(f"    - {n['title']}")
            lines.append("")

        # 綜合影響預估
        lines.append("■ 綜合影響預估：")
        total_portfolio_impact = 0
        for ticker, name in HOLDINGS.items():
            data = all_impacts.get(ticker, {})
            amount = data.get("estimated_amount", 0)
            total_portfolio_impact += amount
            sign = "+" if amount > 0 else ""

            if abs(amount) >= THRESHOLD_AMOUNT * 0.5:
                lines.append(f"  - {name}（{ticker}）：{sign}{amount:,.0f} 元 ⚠️")
            else:
                lines.append(f"  - {name}（{ticker}）：{sign}{amount:,.0f} 元（波動小）")

        sign = "+" if total_portfolio_impact > 0 else ""
        lines.append(f"  組合總影響：{sign}{total_portfolio_impact:,.0f} 元")

        if abs(total_portfolio_impact) >= THRESHOLD_AMOUNT:
            lines.append("")
            lines.append("⚠️  注意：預估波動超過 5% 門檻（20,940 元）！")
        else:
            lines.append("")
            lines.append("✓ 預估波動在正常範圍內。")

        lines.append("操作建議：請人工確認")
        lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# LINE 推播
# ──────────────────────────────────────────────

def send_line_notification(message: str) -> bool:
    """透過 LINE Channel Token 推播通知"""
    load_env()

    if not LINE_TOKEN:
        print("  [LINE] 未設定 LINE_CHANNEL_TOKEN，跳過推播")
        return False

    import urllib.request
    import json

    url = "https://api.line.me/v2/bot/message/broadcast"

    payload = json.dumps({
        "messages": [
            {
                "type": "text",
                "text": message[:5000],  # LINE 上限 5000 字
            }
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_TOKEN}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            if status == 200:
                print("  [LINE] 推播成功")
                return True
            else:
                print(f"  [LINE] 推播失敗，HTTP {status}")
                return False
    except Exception as e:
        print(f"  [LINE] 推播失敗: {e}")
        return False


# ──────────────────────────────────────────────
# 模擬資料（測試用）
# ──────────────────────────────────────────────

def get_test_events() -> list[dict]:
    """產生模擬 Apple 事件"""
    return [
        {
            "title": "Apple WWDC 2026 將發表 AI 新功能 Apple Intelligence 2.0",
            "url": "https://example.com/wwdc2026",
            "source": "蘋果官方",
            "published": datetime.now().isoformat(),
            "category": "apple_event",
        },
        {
            "title": "蘋果 iPhone 17 系列預期採用台積電 2nm 晶片，效能大幅提升",
            "url": "https://example.com/iphone17-tsmc",
            "source": "科技報",
            "published": datetime.now().isoformat(),
            "category": "apple_event",
        },
    ]


def get_test_supply_news() -> dict:
    """產生模擬供應鏈新聞"""
    return {
        "2330": [
            {
                "title": "台積電 5 月營收創歷史新高，AI 訂單強勁",
                "url": "https://example.com/tsmc-revenue",
                "source": "經濟日報",
                "ticker": "2330",
                "stock_name": "台積電",
            },
        ],
        "4938": [
            {
                "title": "和碩取得 Apple Watch Ultra 3 組裝訂單",
                "url": "https://example.com/pegatron-order",
                "source": "工商時報",
                "ticker": "4938",
                "stock_name": "和碩",
            },
        ],
        "3376": [],
        "3019": [
            {
                "title": "亞光接獲 iPhone 17 Pro 潛望式鏡頭訂單",
                "url": "https://example.com/glaso-lens",
                "source": "蘋果日報",
                "ticker": "3019",
                "stock_name": "亞光",
            },
        ],
        "6121": [],
    }


# ──────────────────────────────────────────────
# WWDC 特別模式
# ──────────────────────────────────────────────

def wwdc_mode():
    """WWDC 特別監控模式 - 6/9 WWDC 前後密集監控"""
    today = now_tw().strftime("%Y-%m-%d")
    wwdc_date = "2026-06-09"

    print(f"[WWDC 模式] 今天是 {today}，WWDC 日期是 {wwdc_date}")
    print(f"距離 WWDC 還有...")

    from datetime import date as date_type
    today_date = now_tw().date()
    wwdc = date_type(2026, 6, 9)
    delta = (wwdc - today_date).days

    if delta > 0:
        print(f"  {delta} 天")
        print("  建議：開始密集監控 Apple 相關新聞")
    elif delta == 0:
        print("  ★★★ 今天就是 WWDC！ ★★★")
    else:
        print(f"  WWDC 已過 {abs(delta)} 天")
        print("  建議：持續追蹤 WWDC 後續影響")

    return run_monitor(test_mode=True, dry_run=True)


# ──────────────────────────────────────────────
# 主程式
# ──────────────────────────────────────────────

def run_monitor(test_mode: bool = False, dry_run: bool = False):
    """
    執行每日監控流程
    1. 抓取新聞
    2. 分析影響
    3. 產生報告
    4. 儲存並推播
    """
    ensure_dirs()
    state = load_state()

    print("=" * 60)
    print("華爾特蘋果供應鏈監控系統 v1.0")
    print(f"Novabridge — 工程師布魯斯")
    print(f"執行時間: {now_tw().strftime('%Y-%m-%d %H:%M:%S')} (TW)")
    if test_mode:
        print("模式: 測試模式（使用模擬資料）")
    if dry_run:
        print("模式: Dry Run（不推播）")
    print("=" * 60)
    print()

    # Step 1: 抓取新聞
    print("[1/4] 抓取 Apple 相關事件...")
    if test_mode:
        events = get_test_events()
    else:
        events = fetch_apple_events()
    print(f"      找到 {len(events)} 筆 Apple 事件")

    print("[2/4] 抓取供應商新聞...")
    if test_mode:
        supply_news = get_test_supply_news()
    else:
        supply_news = fetch_supply_chain_news()
    total_news = sum(len(v) for v in supply_news.values())
    print(f"      找到 {total_news} 筆供應商新聞")

    # Step 2: 產生報告
    print("[3/4] 分析影響並產生報告...")
    report = format_report(events, supply_news, dry_run)
    print()

    # 印出報告
    print(report)

    # Step 3: 儲存報告
    report_filename = f"apple_report_{today_str()}.txt"
    report_path = REPORTS_DIR / report_filename
    with open(report_path, "w") as f:
        f.write(report)
    print(f"報告已儲存至: {report_path}")

    # Step 4: 更新狀態
    state["last_run"] = now_tw().isoformat()
    state["reports"].append({
        "date": today_str(),
        "filename": report_filename,
        "events_count": len(events),
        "news_count": total_news,
    })
    # 只保留最近 30 筆
    state["reports"] = state["reports"][-30:]
    save_state(state)

    # Step 5: LINE 推播
    if not dry_run:
        print()
        print("[4/4] 推播到 LINE...")
        send_line_notification(report)
    else:
        print()
        print("[4/4] 跳過推播（dry-run 模式）")

    print()
    print("=" * 60)
    print("監控完成")
    print("=" * 60)

    return report


def main():
    parser = argparse.ArgumentParser(description="華爾特蘋果供應鏈監控系統")
    parser.add_argument("--test", action="store_true", help="測試模式（用模擬資料）")
    parser.add_argument("--dry-run", action="store_true", help="只產生報告，不推播")
    parser.add_argument("--wwdc", action="store_true", help="WWDC 特別監控模式")
    args = parser.parse_args()

    load_env()

    if args.wwdc:
        wwdc_mode()
    else:
        run_monitor(test_mode=args.test, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
