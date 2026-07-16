# 龍族記憶快照包（Memory Snapshot）

建立時間：2026-07-16 14:58
建立者：桃樂絲 Dorothy

## 用途
當 ~/.hermes 整個遺失（系統重置、環境變動、Hermes 重裝）時，
從此包恢復桃樂絲的記憶與龍族身份設定，避免偏好/規則/身分丟失。

## 內容
- `MEMORY_20260716.md` — 桃樂絲的完整記憶條目（來自 ~/.hermes/memories/MEMORY.md）
- `soul.md` — 身份核心定義（勞大是老闆、桃樂絲是 ZOO 開發等）
- `identity_restore.sh` — 身份恢復腳本（bash alias: laoda/whoami）
- `雙切模式配置_20260626_101018.md` — 龍族成員深度模型錯開配置

## 恢復方式
1. 將 MEMORY_YYYYMMDD.md 內容複製回 ~/.hermes/memories/MEMORY.md
2. 將 soul.md 複製回 ~/.hermes/soul.md
3. 將 identity_restore.sh 複製回 ~/.hermes/scripts/ 並 chmod +x
4. 執行 identity_restore.sh 建立 alias

## 注意
此目錄（03_作業/備份/）已被主倉庫 .gitignore 排除，不會進 git 自動追蹤。
如需備份到遠端，請手動處理或單獨 git add -f。
