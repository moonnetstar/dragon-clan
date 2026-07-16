#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TwoTone LINE Bot 自動守護腳本 (Watchdog)
- 每 5 分鐘由 cron 呼叫
- 檢查 localhost:8081/healthz 是否活著
- 若掛掉：重啟 Flask + ngrok，並 TG 通知勞大
- 若 ngrok 隧道斷掉：重建隧道
"""
import os
import sys
import time
import json
import subprocess
import urllib.request
import urllib.error

PROJECT_DIR = os.path.expanduser("~/Desktop/龍族報告/01_專案/TwoTone_Project")
VENV_PY = os.path.join(PROJECT_DIR, "venv", "bin", "python3")
APP_PORT = 8081
NGROK_AUTH = "3EeVaYI1Qt8BLL3WiQjrZS1znnq_NrL6B2SPrekVPRSdH639"
TG_SCRIPT = os.path.expanduser("~/Desktop/龍族報告/04_資源/Market_Data/send_tg.py")
TG_CHAT = "793529884"
SIGN = "🌹 桃樂絲 Dorothy"


def send_tg(msg: str):
    try:
        subprocess.run(
            ["python3", TG_SCRIPT, TG_CHAT, msg],
            check=False, timeout=20
        )
    except Exception as e:
        print(f"[WARN] TG 發送失敗: {e}")


def is_port_listening(port: int) -> bool:
    out = subprocess.run(
        f"lsof -i :{port} | awk 'NR!=1 {{print $2}}'",
        shell=True, capture_output=True, text=True
    )
    return bool(out.stdout.strip())


def is_health_ok() -> bool:
    try:
        with urllib.request.urlopen(f"http://localhost:{APP_PORT}/healthz", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def ngrok_tunnel_alive() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=5) as r:
            data = json.load(r)
            return len(data.get("tunnels", [])) > 0
    except Exception:
        return False


def kill_port(port: int):
    subprocess.run(
        f"lsof -i :{port} | awk 'NR!=1 {{print $2}}' | xargs kill -9 2>/dev/null",
        shell=True, capture_output=True, text=True
    )


def start_flask():
    kill_port(APP_PORT)
    subprocess.Popen(
        [VENV_PY, "app.py"],
        cwd=PROJECT_DIR,
        stdout=open(os.path.join(PROJECT_DIR, "flask.log"), "a"),
        stderr=subprocess.STDOUT,
    )


def start_ngrok():
    # 先殺掉舊 ngrok
    subprocess.run("pkill -f 'ngrok http 8081' 2>/dev/null", shell=True)
    time.sleep(1)
    subprocess.Popen(
        f"ngrok http {APP_PORT} --authtoken {NGROK_AUTH}",
        shell=True,
        stdout=open("/tmp/ngrok.log", "a"),
        stderr=subprocess.STDOUT,
    )


def main():
    restarted = False

    # 1. 檢查 Flask
    if not is_health_ok():
        print("[WATCHDOG] Flask 未回應，嘗試重啟...")
        start_flask()
        restarted = True
        time.sleep(6)

    # 2. 檢查 ngrok 隧道
    if not ngrok_tunnel_alive():
        print("[WATCHDOG] ngrok 隧道斷開，嘗試重建...")
        start_ngrok()
        restarted = True
        time.sleep(4)

    # 3. 最終確認
    if is_health_ok() and ngrok_tunnel_alive():
        if restarted:
            send_tg(f"{SIGN}\n🔧 TwoTone LINE Bot 已自動修復並恢復運作！")
            print("[WATCHDOG] 修復完成，已通知勞大")
        else:
            print("[WATCHDOG] 一切正常，無需動作")
    else:
        send_tg(f"{SIGN}\n⚠️ TwoTone LINE Bot 自動修復失敗，請勞大手動檢查！")
        print("[WATCHDOG] 修復失敗")


if __name__ == "__main__":
    main()
