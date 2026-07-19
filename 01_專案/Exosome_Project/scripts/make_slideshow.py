#!/usr/bin/env python3
"""
Exosome 本地短影音實做 (無 FAL_KEY 備案)
把產品圖 + 字幕 + 背景音樂 合成 9:16 豎屏短片。

依賴: ffmpeg (靜態版路徑見 FFMPEG 常數)
用法:
  python3 make_slideshow.py --image images/product_main.jpg --direction A \
      --out videos/exosome_A_local.mp4
方向: A=產品展示 B=科普 C=品牌故事 D=前後對比
"""
import argparse
import os
import subprocess
import sys

# 靜態 ffmpeg 路徑 (龍族備援)
FFMPEG = os.path.expanduser(
    "~/Desktop/龍族報告/02_素材/tools/ffmpeg"
)

# 各方向字幕 (timestamp, text)
SUBTITLES = {
    "A": [
        (0.0, "面泌體精華 · 看得見的修復力"),
        (1.5, "外泌體技術 直達肌底"),
        (3.0, "一滴喚醒年輕光"),
    ],
    "B": [
        (0.0, "什麼是外泌體？"),
        (2.0, "奈米級信使 傳遞修復指令"),
        (5.0, "喚醒休眠細胞"),
        (7.0, "面泌體 = 肌膚的重新開機鍵"),
    ],
    "C": [
        (0.0, "每道細紋 都是時間的詩"),
        (3.0, "面泌體 溫柔接住歲月"),
        (6.0, "Exosome · 讓光回來"),
    ],
    "D": [
        (0.0, "28 天前 vs 28 天後"),
        (2.0, "差別 看得見"),
    ],
}

DURATION = {"A": 10, "B": 13, "C": 10, "D": 7}


def build_filter(image, direction):
    dur = DURATION[direction]
    # 縮放圖到 1080x1920 (9:16), 置中, 加底色
    base = (
        f"scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,"
    )
    # 字幕 drawtext 堆疊 (輪播, 不重疊, 固定底部位置)
    subs = SUBTITLES[direction]
    n = len(subs)
    draw_parts = []
    fontcolor = "white"
    for i, (ts, txt) in enumerate(subs):
        # 結束時間 = 下一句開始 (或影片結尾), 確保區間不重疊
        te = subs[i + 1][0] if i + 1 < n else dur
        # 淡入淡出 0.3s
        fade = f"alpha='if(lt(t,{ts}+0.3),((t-{ts})/0.3),if(gt(t,{te}-0.3),(({te}-t)/0.3),1))'"
        draw_parts.append(
            f"drawtext=text='{txt}':fontcolor={fontcolor}:fontsize=64:"
            f"x=(w-text_w)/2:y=h-text_h-220:box=1:boxcolor=black@0.45:boxborderw=24:"
            f"enable='between(t,{ts},{te})':{fade}"
        )
    draw = ",".join(draw_parts)
    # 緩慢 zoom 增加質感
    zoom = "zoompan=z='min(zoom+0.0008,1.12)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
    vf = f"{base}{zoom},{draw}"
    return vf, dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--direction", required=True, choices=list(SUBTITLES.keys()))
    ap.add_argument("--out", required=True)
    ap.add_argument("--music", help="可選背景音樂 mp3")
    args = ap.parse_args()

    if not os.path.exists(args.image):
        print(f"ERROR: 圖片不存在 {args.image}")
        sys.exit(1)
    if not os.path.exists(FFMPEG):
        print(f"ERROR: ffmpeg 不存在 {FFMPEG}")
        sys.exit(1)

    vf, dur = build_filter(args.image, args.direction)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", args.image,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-t", str(dur),
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-b:v", "4M", "-maxrate", "6M", "-bufsize", "8M",
        "-g", "30", "-c:a", "aac", "-b:a", "128k", "-shortest",
        args.out,
    ]
    if args.music:
        # 若提供音樂則用音樂替代靜音
        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-i", args.image,
            "-i", args.music,
            "-t", str(dur),
            "-vf", vf,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", "-map", "0:v:0", "-map", "1:a:0",
            args.out,
        ]

    print(f"[run] {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:\n", r.stderr[-2000:])
        sys.exit(1)

    size = os.path.getsize(args.out)
    print(f"[OK] 產出 {args.out} ({size//1024} KB, {dur}s)")
    if size < 1_000_000:
        print("WARN: 檔案 < 1MB, 可能異常")


if __name__ == "__main__":
    main()
