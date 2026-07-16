#!/bin/bash
# 🐉 龍族系統監控 — Ollama 關閉後觀察期 (2026-07-14 起)
# 勞大要求：關閉 Ollama 後觀察幾天，每天回報系統健康。
# 此腳本供 cron 或手動執行，輸出純文字報告。

DATE=$(date "+%Y-%m-%d %H:%M:%S %Z")

# --- 檢查項目 ---
report=""

# 1. Gateway (用 pgrep 精確匹配 python -m hermes_cli.main gateway，或檢查進程)
if pgrep -f "hermes_cli.main gateway run" >/dev/null 2>&1 || pgrep -f "tui_gateway" >/dev/null 2>&1; then
  report="${report}🌐 Gateway: ✅ 活著\n"
else
  report="${report}🌐 Gateway: ❌ 掛了 (需重啟 hermes gateway run)\n"
fi

# 2. MLX 8083
if curl -s --max-time 5 http://127.0.0.1:8083/v1/models >/dev/null 2>&1; then
  report="${report}🔥 MLX 8083: ✅ 活著\n"
else
  report="${report}🔥 MLX 8083: ❌ 掛了 (需重啟 python3 -m mlx_lm server ...)\n"
fi

# 3. Ollama (應保持關閉)
if curl -s --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  report="${report}🐍 Ollama 11434: ⚠️ 意外重啟了！(勞大要求保持關閉)\n"
else
  report="${report}🐍 Ollama 11434: ✅ 關閉中 (符合預期)\n"
fi

# 4. OpenRouter API
if curl -s --max-time 8 https://openrouter.ai/api/v1/models >/dev/null 2>&1; then
  report="${report}🤖 OpenRouter: ✅ 可達\n"
else
  report="${report}🤖 OpenRouter: ⚠️ 異常\n"
fi

# 5. 記憶體壓力
mem_free_pct=$(memory_pressure 2>/dev/null | grep "System-wide memory free percentage" | awk '{print $NF}' | tr -d '%')
if [ -n "$mem_free_pct" ]; then
  report="${report}💾 記憶體自由: ${mem_free_pct}%\n"
fi

# 6. 磁碟
disk_use=$(df -h ~/ | tail -1 | awk '{print $5}')
report="${report}💽 磁碟用量: ${disk_use}\n"

# --- 輸出 ---
echo "🐉 龍族系統健康報告 — ${DATE}"
echo "================================"
echo -e "$report"
echo "================================"

# 若有異常 (❌ 或 ⚠️) 則輸出非 SILENT 標記供 TG 發送
if echo -e "$report" | grep -qE "❌|⚠️"; then
  echo "[ALERT]"
fi
