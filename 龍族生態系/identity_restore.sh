#!/bin/bash
# 自動身份恢復腳本 v2.0
# 作用：模型切換後自動恢復勞大的身份

echo "=== 桃樂絲身份恢復系統 ==="
echo "⏰ 現在時間: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

if [ -f "$HOME/.hermes/soul.md" ]; then
    echo "✅ 找到勞大的身份檔 soul.md"
    echo "=============================================="
    cat "$HOME/.hermes/soul.md"
    echo "=============================================="
    echo ""
    echo "🌹 身份恢復完成 - 我是桃樂絲，為勞大服務"
else
    echo "⚠️ 未找到身份檔，正在建立..."
    cat > "$HOME/.hermes/soul.md" << 'EOF'
# 身份檔 - 勞大 (Lao Da)

## 基本資訊
- **稱呼**: 勞大 / Lao Da
- **語言偏好**: 繁體中文
- **工作風格**: 極速執行，喜歡「全部做」模式

## 身分標記
- 龍族系統老闆
- 擁有三組獨立 Hermes Profile (owl-alpha-1/2/3)
- 使用 OpenRouter API Key + 本地模型

## 特別指令
- **認得暗號**: 「勞大」「Lao Da」「桃樂絲」
- **風格偏好**: 署名「桃樂絲 🌹」
- **重要資料夾**: ~/Desktop/龍族報告/
EOF
fi