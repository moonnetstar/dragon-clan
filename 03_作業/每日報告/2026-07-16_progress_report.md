# 🐉 龍族每日工作報告 — 2026-07-16

> 生成時間：2026-07-17 11:21 CST（補單，涵蓋 7/13→7/16 主要工作）
> 作者：桃樂絲 Dorothy 🌹

## 📌 本日重點
本地 MLX 深層思考引擎完成**根本性修復並上線無人值守監控**。

## ✅ 已完成任務

### 1. 14B 長生成卡死 — 根因確診 + 修復
- **問題**：Qwen2.5-14B-Instruct-4bit 在本機（mlx-lm 0.31.3 + macOS 26.5.1）短生成可用，但**任何 >15 tokens 的長生成直接卡死**（即便重啟 Mac、權重完整載入也一樣）。
- **根因**：4bit 量化的長序列生成 bug（環境層，非設定、非 GPU 壞狀態、無新版可升）。
- **修復**：改用 **Qwen2.5-14B-Instruct-8bit**（走不同 code path）→ 實測 200 tokens / 32s、300 tokens / 46s **穩定**。權重 15.7GB（3 shards）已下載至 `~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-14B-Instruct-8bit-local/`。

### 2. 單一 MLX 模式定案
- 勞大決定「不雙切，直接跑 MLX」。
- 現役：**14B-8bit @ 8083（深層思考主引擎）**；1.5B @ 8080 關閉備用。
- 路由腳本 `local_think.py` 指向 8083，實測端到端 OK。

### 3. 桌面資料夾中文更名 — 影響與補救
- 勞大將所有資料夾改中文（`01_PROJECTS`→`01_專案` 等）。
- **影響**：原 `MLX_Local_Inference` 專案資料夾（啟動腳本+路由）在更名中遺失。
- **補救**：在 `01_專案/本地推理/` 重建完整套件（launcher / local_think.py / dl_8bit.sh / README.md）。
- 說明：`Desktop/MLX_LM` 是舊 Python venv（非專案）；14B 權重在 `~/.cache/` 不受桌面更名影響，服務照常。

### 4. 看門狗 cron 上線（無人值守自動重啟）
- 新增 `mlx_watchdog.py`：每分鐘檢查 8083，掉線自動重啟並寫 log。
- cron job `5430258dc6dd` 已註冊（每分鐘，`local` 模式靜默）。
- 實測：殺掉 14B → watchdog 50 秒內自動帶回（新 PID 33678）。✅
- 修正坑：macOS 無 `setsid` → 改用 `start_new_session=True`；launcher 指定 hermes venv python 避免 cron 環境找不到 `mlx_lm`。

## 🔧 當前系統狀態（7/17 11:21 實測）
| 服務 | Port | 狀態 |
|------|------|------|
| 14B-8bit (深層思考) | 8083 | ✅ 活 (PID 33678, health ok) |
| 1.5B-4bit | 8080 | ⏸️ 關（備用） |
| TwoTone LINE Bot | 8081 | ⏸️ 關 |
| Ollama 模型 | — | Qwen27B / dragon_walter / dragon_dorothy / Qwen3.6-35B-A3B 等已裝 |
| 看門狗 cron | — | ✅ job 5430258dc6dd 每分鐘 |

## 📁 本日產出檔案
```
~/Desktop/龍族報告/01_專案/本地推理/
├── mlx_server_launcher.sh   # big→14B-8bit@8083 (用 hermes venv python)
├── local_think.py           # 深層思考路由
├── dl_8bit.sh               # 權重下載 (15.7GB, 單進程順序)
├── mlx_watchdog.py          # 看門狗 (自動重啟)
├── README.md                # 定案說明
└── watchdog.log             # 重啟記錄
```

## ⏭️ 待辦 / 未決
- [ ] 7/14、7/15 每日報告缺口（未補）
- [ ] 確認 `05_DAILY_REPORTS/` 是否要統一收每日報告（目前實際放在 `03_作業/每日報告/`）
- [ ] 中文更名後其他舊腳本是否還有路徑斷裂（如 TwoTone、股票 cron 指向舊路徑）

## 🧠 關鍵學習（已寫入技能 local-llm-setup）
1. 14B-4bit 長生成卡死 → **8bit 修復**（已證實）
2. 下載絕不能設 `--max-time` < 單 shard 下載時間（否則 curl 重試從頭寫，永遠下不完）
3. macOS 無 `setsid`，背景拉起用 `start_new_session=True`
4. cron 環境 PATH 不含 venv → launcher 須用絕對 python 路徑

---
🌹 桃樂絲 Dorothy
