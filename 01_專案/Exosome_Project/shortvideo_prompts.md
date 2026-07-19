# Exosome 面泌體 短影音腳本庫 (DragonCommerce 品牌模組)

適用平台：TikTok / Instagram Reels / 小紅書 / 抖音 / LINE 動態
標準規格：9:16 豎屏, 5-10 秒, 1080x1920

---

## A. 產品展示 (Product Showcase)
**AI 影片 prompt (kling):**
> A luxury skincare serum bottle (Exosome essence) rotating slowly on a minimalist white pedestal, soft studio light, dewy droplets, macro close-up of the golden liquid, premium cosmetic commercial style, 9:16 vertical, slow motion.

**字幕腳本 (5s):**
| 時間 | 字幕 |
|--|--|
| 0-1.5s | 面泌體精華 · 看得見的修復力 |
| 1.5-3s | 外泌體技術 直達肌底 |
| 3-5s | 一滴喚醒年輕光 |

---

## B. 科普 (Science / Education)
**AI 影片 prompt (minimax/hailuo):**
> Animated 3D microscopic view of exosomes (small glowing vesicles) traveling through skin layers and delivering repair signals to cells, clean medical infographic style, blue and white palette, 9:16 vertical.

**字幕腳本 (10s):**
| 時間 | 字幕 |
|--|--|
| 0-2s | 什麼是外泌體？ |
| 2-5s | 奈米級信使 傳遞修復指令 |
| 5-7s | 喚醒休眠細胞 |
| 7-10s | 面泌體 = 肌膚的重新開機鍵 |

---

## C. 品牌故事 (Brand Story)
**AI 影片 prompt (luma):**
> Cinematic slow-motion of a woman touching her glowing cheek by a window at golden hour, soft bokeh, emotional and warm, premium skincare brand film, 9:16 vertical, dreamy atmosphere.

**字幕腳本 (10s):**
| 時間 | 字幕 |
|--|--|
| 0-3s | 每道細紋 都是時間的詩 |
| 3-6s | 面泌體 溫柔接住歲月 |
| 6-10s | Exosome · 讓光回來 |

---

## D. 前後對比 (Before / After)
**AI 影片 prompt (kling-i2v, 輸入 product_main.jpg):**
> The skincare product image transforms: left side shows dull tired skin texture, right side smoothly transitions to radiant glowing skin, split-screen reveal effect, soft light sweep, 9:16 vertical.

**字幕腳本 (5s):**
| 時間 | 字幕 |
|--|--|
| 0-2s | 28 天前 vs 28 天後 |
| 2-5s | 差別 看得見 |

---

## 本地 ffmpeg 實做版 (無 FAL_KEY 備案)
當 FAL_KEY 不可用時，用 `scripts/make_slideshow.py` 把 product_main.jpg + 字幕 + 音樂合成 9:16 短片。
指令：
```bash
python3 scripts/make_slideshow.py \
  --image images/product_main.jpg \
  --script shortvideo_prompts.md \
  --direction A \
  --out videos/exosome_A_local.mp4
```

## 驗證標準
生成後必須：
1. 檔案 > 1MB
2. ffprobe 確認時長正確 (5s / 10s)
3. 歸檔到 videos/，並發 TG 通知 (chat_id: 793529884, 署名 🌹 桃樂絲 Dorothy)
