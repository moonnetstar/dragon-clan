# 🐉 龍族 MLX 本地推理 (DragonBrain Local)

## 模式：單一 14B-8bit 常駐（2026-07-13 定案，2026-07-16 重建於中文目錄）
勞大決定「不雙切，直接跑 MLX」。經實測與修復：
- **Qwen2.5-14B-Instruct-4bit**：短生成可用，但長生成(>15 tokens)在本機卡死
  （mlx-lm 0.31.3 + macOS 26.5.1 環境 bug）→ **已棄用**。
- **Qwen2.5-14B-Instruct-8bit**：換量化繞開 bug，**200/300 tokens 長生成穩定**
  （32s/46s）→ **現為深層思考主引擎 @ 8083**。

## 服務狀態
| 模型 | Port | 用途 | 狀態 |
|------|------|------|------|
| Qwen2.5-14B-Instruct-8bit | 8083 | 深層思考主引擎 | ✅ 常駐 |
| Qwen2.5-1.5B-Instruct-4bit | 8080 | 輕量備用（預設關） | ⏸️ 備用 |

## 啟動
```bash
# 深層思考主引擎 (14B-8bit @ 8083)
bash ./mlx_server_launcher.sh big

# 輕量備用 (1.5B @ 8080，需要時)
bash ./mlx_server_launcher.sh small
```

## 本地推理路由
```bash
# 深層思考（導向 14B-8bit @ 8083）
python3 local_think.py "用三點說明本地 LLM 的價值"
python3 local_think.py --max-tokens 400 "詳細分析..."
python3 local_think.py --check          # 健康檢查
```

或 curl：
```bash
curl http://localhost:8083/v1/chat/completions -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}],"max_tokens":200}'
```

## 權重檔
- 14B-8bit：`~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-14B-Instruct-8bit-local/`
  （3 shards 共 15.7GB，由 `dl_8bit.sh` 單進程順序下載）
- 1.5B-4bit：HF hub snapshots 結構

## 重要坑（已寫入技能 local-llm-setup）
1. **下載**：`hf download` 卡死 → 用 `curl` 直連 CDN；單進程順序寫 + `.part` 暫存；
   **絕不能設 `--max-time` 小於單 shard 下載時間**（否則 curl 超時重試從頭寫，永遠下不完）。
2. **自殺式 pkill**：`pkill -f "Qwen2.5-14B"` 會連自己下載一起殺 → 只用精確 PID。
3. **M4 GPU 壞狀態**：反覆啟停 MLX 會搞壞 GPU context → 只能重啟 Mac。
4. **14B-4bit 長生成卡死**：mlx-lm 0.31.3 + macOS 26.5.1 環境 bug → **改用 8bit 修復**。
5. **保熱**：14B 閒置會被 macOS page-out（RSS 掉到數十 MB），但 8bit 冷喚回長生成仍穩定，
   無需保熱 cron（4bit 才需要）。

---
🐉 作者：桃樂絲 Dorothy 🌹 ｜ 重建：2026-07-16（中文目錄 01_專案/本地推理）
