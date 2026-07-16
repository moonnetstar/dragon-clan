#!/bin/bash
# 龍族深度模型下載腳本
# 執行時間: 2026-06-26

echo "🐉 開始下載深度模型..."

echo "📥 1/3 Qwen 2.5-27B（布魯斯-程式/推理）"
ollama pull qwen2.5:27b

echo "📥 2/3 Gemma 2-27B（艾蒂兒-中文/創意）"
ollama pull gemma2:27b

echo "📥 3/3 DeepSeek-R1-27B（備用-深度推理）"
ollama pull deepseek-r1:27b

echo ""
echo "✅ 全部下載完成！"
echo ""
echo "📋 模型清單："
echo "  qwen2.5:27b      → 布魯斯（程式/推理）"
echo "  gemma2:27b       → 艾蒂兒（中文/創意）"
echo "  deepseek-r1:27b → 備用（深度推理）"
echo ""
echo "💡 驗證：ollama list"
