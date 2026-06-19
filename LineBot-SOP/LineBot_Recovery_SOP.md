# 🛠️ LINE Bot 重建與復原 SOP (龍族專用)

當環境異常或需要重新部署時，請依此步驟操作。

## 1. 環境檢查 (Environment)
- **Python**: 3.11+
- **必要套件**: `pip install line-bot-sdk flask python-dotenv`
- **關鍵檔案**: `.env` (存放 Channel Access Token 與 Secret)

## 2. 重建代碼步驟
1. **建立專案目錄** 並將程式腳本 (`app.py`) 放好。
2. **設定 Webhook 地址**: 使用 `ngrok http 5000` 開啟隧道，並拿到新的 URL $\rightarrow$ 更新至 LINE Developers 控制台的 Webhook URL。
3. **伺服器啟動**: `python app.py`

## 3. 自動化驗證 (Testing)
- 直接從 LINE App 發送訊息給 Bot，觀察控制台 Log 是否正常解析 JSON。
