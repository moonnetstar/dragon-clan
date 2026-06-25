# Meridian Bridge LINE Bot MVP

## 一、LINE Developers 設定（免費）

1. 到 https://developers.line.biz 註冊（用你的 LINE 帳號）
2. 建立 Provider → Create a new provider
3. 建立 Channel → Messaging API
4. 取得：
   - Channel Access Token（長字串）
   - Channel Secret（短字串）
5. 關閉「自動回覆訊息」（我們自己處理）
6. Webhook URL 填：`https://你的ngrok網址/callback`
7. 開啟「Use webhook」

## 二、安裝（本機 Mac）

```bash
cd ~/line-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 三、設定 Token

兩種方式選一種：

方式 A：環境變數（推薦）
```bash
export LINE_CHANNEL_TOKEN="你的ChannelAccessToken"
export LINE_CHANNEL_SECRET="你的ChannelSecret"
```

方式 B：直接改 app.py 第 10-11 行

## 四、啟動 Bot（終端機開兩個視窗）

視窗 1 — 啟動 Bot：
```bash
cd ~/line-bot
source .venv/bin/activate
python app.py
```

視窗 2 — 啟動 ngrok（讓 LINE 找得到你的本機）：
```bash
ngrok http 5000
```

ngrok 會產生一個公開網址，例如：
`https://xxxx-xx-xx-xx.ngrok-free.app`

把這個網址 + `/callback` 填入 LINE Developers 的 Webhook URL。

## 五、測試

1. 用你的手機掃描 LINE Developers 頁面上的 QR Code
2. 傳一則訊息給 Bot
3. 你應該會收到回覆

## 六、下一步（串接 Agent）

目前 Bot 只是框架。下一步是把收到的訊息轉給桃樂絲（CEO agent），
再把 agent 的回覆傳回 LINE。

Token 拿到後找我（布魯斯），我幫你串完整版。
