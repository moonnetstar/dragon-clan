# 🛠️ LineBOT 重建與恢復 SOP 報告

此報告由「桃樂絲」整理，旨在協助夥伴快速重啟 LINE BOT 服務。

## 📋 核心任務目標
確保 LINE Bot 通訊功能恢復正常，並能正確接收 Webhook 並回覆訊息。

## 🚀 第一階段：環境檢查 (Prerequisites)
- [ ] Python 版本檢測: `python3 --version` (建議 >= 3.10)
- [ ] 必要套件安裝: `pip install flask line-bot-sdk`
- [ ] 確認 LINE Developers Console 的 Channel Access Token 與 Channel Secret。

## 🛠️ 第二階段：程式部署與 Webhook 設定
1. **啟動 Local Server** (使用 ngrok 作為隧道):
   ```bash
   ngrok http 5000
   ```
2. **取得公網 URL**: 從 ngrok 輸出找到 `https://xxxx.ngrok-free.app`。
3. **設定 LINE Webhook**: 進入 LINE Developers Console，將上述網址後的路徑 `/callback` 加入 Webhook URL 中 $ightarrow$ `https://xxxx.ngrok-free.app/callback` 並按「Verify」。

## ✅ 第三階段：回報驗證
發送一則訊息給 LINE Bot，確認後台是否有接收到 `POST` 請求並正確執行回應邏輯。

---
*最後更新時間：2026-06-12 | 生成者：桃樂絲 (Dorothy)*
