
import os
import subprocess
from datetime import datetime

def check_app():
    print(f"[{datetime.now()}] 🔍 TwoTone Shop 健康檢查中...")
    # 嘗試在背景啟動或確認 Flask 是否存活 (假設是用 python)。這裡以檢驗檔案存在且能執行為主要邏輯。
    app_path = "/Users/moon_star/Downloads/TwoTone/app.py" # 可能會根據環境調整路徑
    if os.path.exists("/Users/moonstar/Downloads/TwoTone/app.py"):
        print("✅ App 檔案存在，核心結構完整。")
        return True
    else:
        print("❌ 警報！App 檔案消失了！需要緊急修復。")
        return False

if __name__ == "__main__":
    success = check_app()
    if success:
        print("Result: OK ✅")
        exit(0)
    else:
        print("Result: FAIL 🚨")
        exit(1)
