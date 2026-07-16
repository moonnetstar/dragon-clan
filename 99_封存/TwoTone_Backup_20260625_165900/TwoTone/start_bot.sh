
#!/bin/bash

# 載入 .env 環境變數
source ~/Desktop/龍族報告/99_ARCHIVE/TwoTone_Backup_20260625_165900/TwoTone/.env

export PORT=8077 # Flask 要用正確 port

# 啟動 ngrok 隧道 (在背景)
ngrok http "$PORT" &
NGROK_PID=$!
sleep 3

echo ">>> Starting Flask app.py on $PORT..."
python3 app.py
