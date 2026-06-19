#!/usr/bin/env python3
"""Send Telegram notification for 和碩 stock alert."""
import json, urllib.request, urllib.parse, os, sys

# Get bot token from .env
def get_bot_token():
    env_path = os.path.expanduser("~/.hermes/.env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN=") and not line.startswith("#"):
                return line.split("=", 1)[1]
    return None

def send_telegram(chat_id, text):
    token = get_bot_token()
    if not token:
        print("ERROR: Could not find TELEGRAM_BOT_TOKEN")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
        return result.get("ok", False)

if __name__ == "__main__":
    chat_id = sys.argv[1] if len(sys.argv) > 1 else "793529884"
    message = sys.argv[2] if len(sys.argv) > 2 else "Test message"
    ok = send_telegram(chat_id, message)
    print(f"Sent: {ok}")
