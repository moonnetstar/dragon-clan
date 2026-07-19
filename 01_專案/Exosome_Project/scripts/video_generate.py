#!/usr/bin/env python3
"""
Exosome 短影音生成腳本 (DragonCommerce 品牌模組)
依賴: fal_client (pip install fal-client), FAL_KEY 環境變數

用法:
  文生影片:
    python3 video_generate.py --prompt "..." --model kling --duration 5 --aspect 9:16 --out exosome_A.mp4
  圖生影片:
    python3 video_generate.py --prompt "..." --model kling-i2v --image product.png --duration 5 --out exosome_D.mp4

模型對照:
  kling      -> 文生影片 (動作自然, 首選產品/對比)
  kling-i2v  -> 圖生影片 (輸入 --image)
  luma       -> 文生影片 (夢幻流暢, 品牌故事/氛圍)
  minimax    -> 文生影片 (動態強, 科普動畫)
  hailuo     -> 文生影片 (動態強, 科普動畫)
"""
import argparse
import os
import sys
import time

try:
    import fal_client
except ImportError:
    print("ERROR: fal_client 未安裝 -> pip install fal-client")
    sys.exit(1)


# fal.ai 各模型端點
ENDPOINTS = {
    "kling": "fal-ai/kling-video/v1/standard/text-to-video",
    "kling-i2v": "fal-ai/kling-video/v1/standard/image-to-video",
    "luma": "fal-ai/luma-dream-machine/dream-machine/v1/text-to-video",
    "minimax": "fal-ai/minimax/video-01/text-to-video",
    "hailuo": "fal-ai/hailuo-01/standard/text-to-video",
}

ASPECT_MAP = {
    "9:16": "9:16",
    "16:9": "16:9",
    "1:1": "1:1",
}


def on_queue_update(update):
    if hasattr(update, "status") and update.status:
        print(f"[queue] {update.status}", flush=True)
    if hasattr(update, "logs") and update.logs:
        for log in update.logs:
            print(f"[log] {log.message}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="影片描述 prompt")
    ap.add_argument("--model", required=True, choices=list(ENDPOINTS.keys()))
    ap.add_argument("--image", help="圖生影片用的驅動圖 (kling-i2v)")
    ap.add_argument("--duration", type=int, default=5, choices=[5, 10])
    ap.add_argument("--aspect", default="9:16", choices=list(ASPECT_MAP.keys()))
    ap.add_argument("--out", required=True, help="輸出 mp4 路徑")
    args = ap.parse_args()

    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY 環境變數為空。請先 export FAL_KEY=<key>")
        sys.exit(1)

    endpoint = ENDPOINTS[args.model]
    print(f"[info] model={args.model} endpoint={endpoint} duration={args.duration}s aspect={args.aspect}")

    if args.model == "kling-i2v":
        if not args.image or not os.path.exists(args.image):
            print("ERROR: kling-i2v 需要 --image 且檔案存在")
            sys.exit(1)
        # 上傳圖片到 fal storage
        print("[info] 上傳圖片到 fal storage ...", flush=True)
        image_url = fal_client.upload_file(args.image)
        arguments = {
            "prompt": args.prompt,
            "input_image_urls": [image_url],
            "duration": args.duration,
            "aspect_ratio": args.aspect,
        }
    else:
        arguments = {
            "prompt": args.prompt,
            "duration": args.duration,
            "aspect_ratio": args.aspect,
        }

    print("[info] 提交生成任務 (排隊中, 可能 1-5 分鐘) ...", flush=True)
    t0 = time.time()
    result = fal_client.run(endpoint, arguments=arguments, on_queue_update=on_queue_update)
    elapsed = int(time.time() - t0)
    print(f"[info] 完成, 耗時 {elapsed}s", flush=True)

    # 取出影片 URL
    video_url = None
    if isinstance(result, dict):
        video_url = result.get("video", {}).get("url") or result.get("url") or result.get("output")
    if not video_url:
        print("ERROR: 無法從結果取得影片 URL")
        print(result)
        sys.exit(1)

    # 下載
    print(f"[info] 下載影片 {video_url} -> {args.out}", flush=True)
    os.system(f'curl -L -o "{args.out}" "{video_url}"')
    if os.path.exists(args.out) and os.path.getsize(args.out) > 1_000_000:
        print(f"[OK] 影片已產出: {args.out} ({os.path.getsize(args.out)//1024} KB)")
    else:
        print(f"WARN: 輸出檔案異常, 請檢查 {args.out}")


if __name__ == "__main__":
    main()
