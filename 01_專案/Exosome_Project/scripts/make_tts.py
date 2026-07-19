#!/usr/bin/env python3
"""
Exosome 短影音 中文配音 (macOS say 離線 TTS, 免費零 key)
把各方向字幕詞生成語音(aiff->mp3), 再混音進影片取代靜音/並存 BGM。

用法:
  python3 make_tts.py --direction A --voice Meijia --out audio/tts_A.aiff
  python3 make_tts.py --mix videos/exosome_A_local.mp4 --tts audio/tts_A.aiff --bgm audio/bgm_5s.mp3 --out videos/exosome_A_vo.mp4
"""
import argparse
import os
import subprocess
import sys

FFMPEG = os.path.expanduser("~/Desktop/龍族報告/02_素材/tools/ffmpeg")

# 各方向配音文本 (與 shortvideo_prompts.md 字幕一致)
TTS_TEXT = {
    "A": "面泌體精華，看得見的修復力。外泌體技術，直達肌底。一滴喚醒年輕光。",
    "B": "什麼是外泌體？奈米級信使，傳遞修復指令。喚醒休眠細胞。面泌體，等於肌膚的重新開機鍵。",
    "C": "每道細紋，都是時間的詩。面泌體，溫柔接住歲月。Exosome，讓光回來。",
    "D": "二十八天前，對比二十八天後。差別，看得見。",
}

DURATION = {"A": 5, "B": 10, "C": 10, "D": 5}


def gen_tts(text, voice, out, rate=150, pitch_mult=0.89):
    # macOS say -> aiff, 再用 ffmpeg 轉 mp3
    # 沉穩設定: 男聲(Eddy) + rubberband 降調(pitch<0 更低沉) + 低通厚實 + 去回響
    aiff = out.rsplit(".", 1)[0] + ".aiff"
    r1 = subprocess.run(["say", "-v", voice, "-r", str(rate),
                         "-o", aiff, text], capture_output=True, text=True)
    if r1.returncode != 0:
        print("SAY ERR:", r1.stderr[:500])
        sys.exit(1)
    # rubberband: pitch=0.89 約降 2 半音更沉 (倍率, 1.0=原調); lowpass 2800 去刺; 不開回響
    r2 = subprocess.run(
        [FFMPEG, "-y", "-i", aiff,
         "-af", f"rubberband=pitch={pitch_mult},lowpass=f=2800,highpass=f=80",
         "-c:a", "libmp3lame", "-q:a", "4", out],
        capture_output=True, text=True,
    )
    if r2.returncode != 0:
        print("FF ERR:", r2.stderr[:500])
        sys.exit(1)
    os.remove(aiff)
    print(f"[OK] TTS {out} ({os.path.getsize(out)//1024} KB)")


def mix(video, tts, bgm, out):
    if bgm:
        # 語音為主(0.9) + BGM 降低(0.15)
        cmd = [
            FFMPEG, "-y", "-i", video, "-i", tts, "-i", bgm,
            "-filter_complex",
            "[1:a]volume=0.9[voice];[2:a]volume=0.15[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first[a]",
            "-map", "0:v:0", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
            out,
        ]
    else:
        cmd = [
            FFMPEG, "-y", "-i", video, "-i", tts,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
            out,
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("MIX ERR:", r.stderr[:1500])
        sys.exit(1)
    print(f"[OK] 配音影片 {out} ({os.path.getsize(out)//1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--direction", choices=list(TTS_TEXT.keys()),
                     help="生成 TTS 時需要 (A/B/C/D)")
    ap.add_argument("--voice", default="Meijia (中文（台灣）)",
                    help="語音 (預設 Meijia 女聲, 可換 Eddy 男聲)")
    ap.add_argument("--rate", type=int, default=120,
                    help="語速 wpm (預設120, 越慢越小)")
    ap.add_argument("--pitch", type=float, default=0.89,
                    help="降調倍率 (預設0.89約降2半音更沉, 1.0=原調, 0.84更沉)")
    ap.add_argument("--out", help="TTS mp3 輸出")
    ap.add_argument("--mix", help="待混音影片")
    ap.add_argument("--tts", help="TTS mp3")
    ap.add_argument("--bgm", help="可選 BGM mp3")
    args = ap.parse_args()

    if args.direction and args.out and not args.mix:
        gen_tts(TTS_TEXT[args.direction], args.voice, args.out,
                rate=args.rate, pitch_mult=args.pitch)
    elif args.mix and args.tts and args.out:
        mix(args.mix, args.tts, args.bgm, args.out)
    else:
        print("用法: --direction A --out tts.aiff.mp3  或  --mix vid.mp4 --tts tts.mp3 --bgm bgm.mp3 --out final.mp4")
        sys.exit(1)


if __name__ == "__main__":
    main()
