#!/usr/bin/env python3
# 🐉 龍族「本地深層思考」路由 (Local Deep Think)
# 把深層推理任務導向本機 Qwen2.5-14B-Instruct-8bit @ localhost:8083 (MLX)
# 模式：單一 MLX 常駐（勞大決定 2026-07-13：不雙切，直接跑 MLX）
#   4bit 在本機長生成會卡死 → 改用 8bit 修復（已實測 200/300 tokens 穩定）
#   假設 8083 已經由 mlx_server_launcher.sh big 啟動，本腳本不自治啟停
# ── 用法 ──
#   python3 local_think.py "問題"                 # 預設 max_tokens=200
#   python3 local_think.py --max-tokens 400 "問題"
#   python3 local_think.py --check                # 只檢查健康
# ──────────
import sys, json, argparse, urllib.request, urllib.error

QWEN_URL = "http://localhost:8083/v1/chat/completions"
REQUEST_TIMEOUT = 300  # 8bit 14B 長生成較慢，給足 5 分鐘
MODEL_TAG = "qwen2.5-14b-instruct-8bit (本地 MLX)"

def check_health():
    try:
        with urllib.request.urlopen(QWEN_URL.replace("/v1/chat/completions", "/health"), timeout=5) as r:
            return r.status == 200
    except Exception:
        return False

def think(prompt, max_tokens=200):
    payload = {"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(QWEN_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
        resp = json.loads(r.read().decode())
    return resp["choices"][0]["message"]["content"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="?", default="")
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check:
        ok = check_health()
        print("healthy" if ok else "DOWN")
        sys.exit(0 if ok else 1)

    if not args.prompt:
        print("用法: python3 local_think.py '問題' [--max-tokens N]")
        sys.exit(1)
    if not check_health():
        print("⚠️ 本地 14B-8bit (8083) 未啟動，請執行: bash mlx_server_launcher.sh big")
        sys.exit(1)

    print(f"🧠 本地深層思考 [{MODEL_TAG}]")
    try:
        print(think(args.prompt, args.max_tokens))
    except urllib.error.URLError as e:
        print(f"連線失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"推理錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
