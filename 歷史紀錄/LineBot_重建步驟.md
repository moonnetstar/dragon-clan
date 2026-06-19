# 🚀 LineBot 重建步驟報告 (SOP)
## 目的：快速復原 LINE Bot 訊息接收與推送功能

### 第一階段：環境檢查
1. 確認 `python --version` 為 3.10+。
2. 確認 `.env` 檔案中包含 `CHANNEL_ACCESS_TOKEN` 與 `CHANNEL_SECRET`。

### 第二階段：依賴安裝
```bash
pip install line-bot-sdk flask python-dotenv
```

### 第三階段：Webhook 設定 (ngrok)
1. 在終端機執行: `ngrok http 5000`
2. 將產生的 `https://....ngrok-free.app` 複製到 LINE Developers 控制台的 Webhook URL。

### 第四階段：測試與驗證
- 發送一則訊息給 Bot，檢查終端機是否有輸出內容。
