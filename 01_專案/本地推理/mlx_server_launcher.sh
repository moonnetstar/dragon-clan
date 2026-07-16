#!/bin/bash
# 🐉 龍族 MLX 本地推理 Server 啟動器
# 模式：單一 MLX 常駐（勞大決定 2026-07-13：不雙切，直接跑 MLX）
#   small : Qwen2.5-1.5B-4bit   @ 8080 (輕量備用)
#   big   : Qwen2.5-14B-8bit    @ 8083 (深層思考主引擎；4bit 長生成會卡死，已棄用)
# 用途：本機 M4 GPU 推理，繞過 OpenRouter API 額度/冷卻
# 作者：桃樂絲 Dorothy 🌹

set -e
date "+📅 啟動時間: %Y-%m-%d %H:%M:%S %Z"

HF_HUB=~/.cache/huggingface/hub
MLX_PY=~/Desktop/MLX_LM/bin/python3
# 優先用 hermes venv (mlx_lm 0.31.3, 當前服務實際使用)；若不在則用 Desktop/MLX_LM (0.29.1 舊)
if [ -x "$HOME/.hermes/hermes-agent/venv/bin/python3" ]; then
  MLX_PY="$HOME/.hermes/hermes-agent/venv/bin/python3"
fi
MODEL_15B="$HF_HUB/models--mlx-community--Qwen2.5-1.5B-Instruct-4bit/snapshots/8b403126fc14f14cfc99bb4cfa72ecbc129ea677"
# 14B-8bit 模型目錄（扁平 local 結構，由 dl_8bit.sh 維護；port 8083 避開 Xcode 佔用的 8082）
MODEL_14B8="$HF_HUB/models--mlx-community--Qwen2.5-14B-Instruct-8bit-local"

usage() {
  echo "用法: $0 [small|big]"
  echo "  small : 啟動 Qwen2.5-1.5B (port 8080, 輕量備用)"
  echo "  big   : 啟動 Qwen2.5-14B-8bit (port 8083, 深層思考主引擎)"
  exit 1
}

[ -z "$1" ] && usage

case "$1" in
  small)
    echo "🚀 啟動 Qwen2.5-1.5B-Instruct-4bit @ port 8080"
    "$MLX_PY" -m mlx_lm server --model "$MODEL_15B" --port 8080 --host 0.0.0.0
    ;;
  big)
    # 確認權重檔存在（safetensors），否則拒絕啟動
    if ! find "$MODEL_14B8" -name "*.safetensors" 2>/dev/null | grep -q .; then
      echo "❌ 14B-8bit 權重尚未下載完成（找不到 .safetensors），請先執行："
      echo "   bash dl_8bit.sh"
      exit 1
    fi
    echo "🚀 啟動 Qwen2.5-14B-Instruct-8bit @ port 8083 (model: $MODEL_14B8)"
    "$MLX_PY" -m mlx_lm server --model "$MODEL_14B8" --port 8083 --host 0.0.0.0
    ;;
  *)
    usage
    ;;
esac
