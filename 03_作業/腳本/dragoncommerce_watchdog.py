#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雙音符電商統計中心 — 自動守護（雲端版）

狀態：統計中心已永久部署上 Render 雲端
  https://dragoncommerce.onrender.com

本腳本職責：
- 檢查雲端 Render 網址是否活著（永久固定，不怕停電/重啟）
- 若雲端異常 → TG 通知勞大
- 本機 8082 + Cloudflare Tunnel 已退役（雲端上線後不再需要）

如需本地開發測試，直接跑：
  cd ~/Desktop/DragonCommerce && PORT=8082 python3 core/server.py
"""
import os
import subprocess
import urllib.request

CLOUD_URL = "https://dragoncommerce.onrender.com/healthz"
TG_SCRIPT = os.path.expanduser("~/Desktop/龍族報告/04_資源/Market_Data/send_tg.py")
TG_CHAT = "793529884"
SIGN = "🌹 桃樂絲 Dorothy"


def send_tg(msg: str):
    try:
        subprocess.run(["python3", TG_SCRIPT, TG_CHAT, msg], check=False, timeout=20)
    except Exception:
        pass


def is_cloud_up() -> bool:
    try:
        with urllib.request.urlopen(CLOUD_URL, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    if is_cloud_up():
        print("[WD] 雲端統計中心正常 (Render)")
    else:
        print("[WD] 雲端統計中心異常，通知勞大")
        send_tg(f"{SIGN}\n⚠️ 雙音符雲端統計中心 (Render) 無回應，請檢查！")


if __name__ == "__main__":
    main()
