#!/usr/bin/env python3
"""
🐉 每日資源報告生成器
由 Cron Job 定時執行，生成資源使用報告並發送到 Telegram
"""

import subprocess
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path.home() / "Desktop" / "龍族報告/03_作業/Monitoring"
REPORT_DIR = Path.home() / "Desktop" / "龍族報告/03_作業/Reports"
LOG_FILE = LOG_DIR / "resource_log.csv"

def generate_daily_report():
    """分析 CSV 日誌，生成每日報告"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if not LOG_FILE.exists():
        return None
    
    # 讀取昨天的數據
    rows = []
    with open(LOG_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["timestamp"].startswith(yesterday):
                rows.append(row)
    
    if not rows:
        return None
    
    # 統計
    mem_values = [float(r["memory_used_pct"]) for r in rows]
    cpu_values = [float(r["cpu_load_1m"]) for r in rows]
    swap_values = [float(r["swap_gb"]) for r in rows]
    model_values = [float(r["ollama_total_gb"]) for r in rows]
    
    report = f"""📊 龍族每日資源報告 ({yesterday})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥️ 系統資源
  記憶體使用率:
    平均: {sum(mem_values)/len(mem_values):.1f}%
    最高: {max(mem_values):.1f}%
    最低: {min(mem_values):.1f}%
  
  CPU 負載 (1m):
    平均: {sum(cpu_values)/len(cpu_values):.1f}
    最高: {max(cpu_values):.1f}
  
  Swap 使用:
    平均: {sum(swap_values)/len(swap_values):.2f}GB
    最高: {max(swap_values):.2f}GB

🤖 Ollama 模型
  平均佔用: {sum(model_values)/len(model_values):.1f}GB
  最高佔用: {max(model_values):.1f}GB

📈 取樣點數: {len(rows)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # 存檔
    report_path = REPORT_DIR / f"每日資源報告_{yesterday.replace('-', '')}.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    return report

if __name__ == "__main__":
    report = generate_daily_report()
    if report:
        print(report)
    else:
        print("無資料可生成報告")
