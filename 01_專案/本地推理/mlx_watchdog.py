#!/usr/bin/env python3
# 🐉 龍族 14B-8bit 看門狗 (watchdog)
# 每分鐘由 cron 呼叫：檢查 localhost:8083 健康，掉了就自動重啟 14B-8bit。
# 重啟用 terminal(background) 等價方式：nohup 不行(被 Hermes 擋)，改用 launchd-safe
# 後台拉起 (setsid + &)。重啟記錄寫 watchdog.log。
# 作者：桃樂絲 Dorothy 🌹
import urllib.request, subprocess, os, datetime, sys

PORT = 8083
URL = f"http://localhost:{PORT}/health"
LAUNCHER = os.path.expanduser(
    "~/Desktop/龍族報告/01_專案/本地推理/mlx_server_launcher.sh")
LOG = os.path.expanduser(
    "~/Desktop/龍族報告/01_專案/本地推理/watchdog.log")


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with open(LOG, "a") as f:
            f.write(line)
    except Exception:
        pass
    print(line, end="")


def is_healthy():
    try:
        with urllib.request.urlopen(URL, timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


def restart():
    log("⚠️ 8083 無回應 → 自動重啟 14B-8bit")
    # 先清掉任何殘留的 8083 server (精確 PID，避免自殺式 pkill)
    try:
        out = subprocess.run(["pgrep", "-f", "mlx_lm server.*8083"],
                             capture_output=True, text=True)
        for pid in out.stdout.split():
            subprocess.run(["kill", "-9", pid.strip()],
                           capture_output=True)
    except Exception:
        pass
    # 背景拉起：macOS 無 setsid，用 start_new_session=True 脫離 cron 父行程
    try:
        subprocess.Popen(
            ["bash", LAUNCHER, "big"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True)
        log("✅ 重啟指令已發出 (bash mlx_server_launcher.sh big)")
    except Exception as e:
        log(f"❌ 重啟失敗: {e}")


def main():
    if is_healthy():
        # 靜默成功：不寫 log（避免 log 爆量），只偶爾印
        sys.exit(0)
    else:
        restart()


if __name__ == "__main__":
    main()
