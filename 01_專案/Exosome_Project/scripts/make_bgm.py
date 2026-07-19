#!/usr/bin/env python3
"""
Exosome 短影音 BGM 生成與混音 (無外部素材/key 備案)
用 ffmpeg 內建濾波器生成柔和 ambient pad 背景音樂, 再疊進影片。

用法:
  python3 make_bgm.py --duration 5 --out bgm_A.mp3
  python3 make_bgm.py --mix videos/exosome_A_local.mp4 --bgm bgm_A.mp3 --out videos/exosome_A_final.mp4
"""
import argparse
import os
import subprocess
import sys

FFMPEG = os.path.expanduser("~/Desktop/龍族報告/02_素材/tools/ffmpeg")


def gen_bgm(duration, out):
    """生成柔和 ambient pad: C大調和弦 (C-E-G) + 低八度 + 輕微顫音 + 淡入淡出"""
    # 頻率: C4=261.63 E4=329.63 G4=392.00 C3=130.81
    # 單一 filtergraph: 每個 sine 標標籤, 再 amix
    filter_complex = (
        f"sine=frequency=261.63:duration={duration}[c];"
        f"sine=frequency=329.63:duration={duration}[e];"
        f"sine=frequency=392.00:duration={duration}[g];"
        f"sine=frequency=130.81:duration={duration}[low];"
        f"[c][e][g][low]amix=inputs=4:duration=longest[a];"
        f"[a]lowpass=f=1200[a];"
        f"[a]volume=0.25[a];"
        f"[a]afade=t=in:st=0:d=1[a];"
        f"[a]afade=t=out:st={max(0,duration-1)}:d=1[aout]"
    )
    cmd = [
        FFMPEG, "-y",
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", str(duration),
        "-c:a", "libmp3lame", "-q:a", "4",
        out,
    ]
    print(f"[run] {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("BGM GEN ERROR:\n", r.stderr[-1500:])
        sys.exit(1)
    print(f"[OK] BGM {out} ({os.path.getsize(out)//1024} KB)")


def mix(video, bgm, out):
    cmd = [
        FFMPEG, "-y",
        "-i", video,
        "-i", bgm,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        out,
    ]
    print(f"[run] {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("MIX ERROR:\n", r.stderr[-1500:])
        sys.exit(1)
    print(f"[OK] 混音 {out} ({os.path.getsize(out)//1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=int, help="生成 BGM 秒數")
    ap.add_argument("--out", help="BGM 輸出 mp3")
    ap.add_argument("--mix", help="待混音影片")
    ap.add_argument("--bgm", help="BGM mp3")
    args = ap.parse_args()

    if not os.path.exists(FFMPEG):
        print(f"ERROR: ffmpeg 不存在 {FFMPEG}")
        sys.exit(1)

    if args.duration and args.out:
        gen_bgm(args.duration, args.out)
    elif args.mix and args.bgm and args.out:
        mix(args.mix, args.bgm, args.out)
    else:
        print("用法: --duration 5 --out bgm.mp3  或  --mix vid.mp4 --bgm bgm.mp3 --out final.mp4")
        sys.exit(1)


if __name__ == "__main__":
    main()
