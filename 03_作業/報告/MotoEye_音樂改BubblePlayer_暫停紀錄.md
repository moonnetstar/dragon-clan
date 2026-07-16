# MotoEye HUD APK 修改 — 工作暫停紀錄

## 日期
2026-07-16

## 當前狀態
- 手機已安裝 **v21**（高德還原版，能正常看高德地圖 + 點終點跳 Google Maps App）
- v21 已備份：`~/Desktop/龍族報告/01_專案/MotoEye_HUD/備份/MotoEye_A_GoogleMap_v21_高德還原備份_20260716_130922.apk`
  - MD5: `2e623a4d06953f875dd07231967e5b66`
- 工作目錄 smali 專案：`/tmp/A_fix/`（已還原高德，WebViewActivity 保留 DOM Storage）
- 原始反編專案：`/tmp/orig_full/`（乾淨對照用）

## 已完成
- v1-v20：嘗試把導航主頁改成 Google WebView（全部失敗：VerifyError / 閃退 / 白屏）
- v21：還原高德 → **成功**，地圖正常顯示，點終點正常跳 Google Maps App
- 確認「導航地圖」流程：點按鈕 → startNaviPage() → (需連藍牙) → MainFunctionActivity → 切到 NavigateFragment(tab index 2)
- 確認音樂入口：lyAlbum → AlbumStartActivity → AlbumListNewFragment → 點項目開 VideoPlayActivity（傳 VIDEO_PATH = MediaDataBean.path）

## 暫停中的任務（等車上實測後決定）
**目標**：把 MotoEye 裡的「音樂」功能改為連接手機上的 **Bubble Player App**（套件名 `com.songs.bubble.player`）

### 已查到的關鍵資訊
- 音樂列表點擊邏輯鏈：
  `AlbumListNewAdapter$2.onClick` → `onItemClickListener.onItemClick()` 
  → `AlbumListNewFragment$4.onItemClick` → `access$1100()` 
  → `AlbumListNewFragment` line 678: `new Intent(VideoPlayActivity)` + `putExtra("VIDEO_PATH", path)` + `startActivity`
- `VideoPlayActivity` 用 `VideoView.setVideoPath(String)` 播放 → path 是可直接播放的路徑（本地或 http）
- `MediaDataBean.path`：音樂/影片檔案路徑（來自主機 FTP 或已下載本地）
- **Bubble Player (`com.songs.bubble.player`) 未註冊 `ACTION_VIEW` audio/video intent-filter** → 不能純靠 ACTION_VIEW + URI 開，需確認其啟動方式

### 待確認（勞大車上實測後回答）
1. 點 MotoEye 音樂時，檔案是已在手機本地（藍牙/WiFi 傳來）還是 streaming？
2. Bubble Player 平時怎麼收音樂（掃本地檔？連網路源？）
3. 是否有必要改（實測後若原本就能用就不改）

### 預計改法（待確認後實施）
在 `AlbumListNewFragment` line 678 之前插入：
```
Intent i = new Intent(Intent.ACTION_VIEW);
i.setPackage("com.songs.bubble.player");
i.setData(Uri.fromFile(new File(mediaData.path)));  // 或 FileProvider/content URI
i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
try { startActivity(i); } catch (ActivityNotFoundException e) { /* fallback 原 VideoPlayActivity */ }
```
需處理：Bubble Player 不接受 ACTION_VIEW 時的備用方案 + path 是 http 還是本地檔的判斷。

## 工具/路徑備忘
- JAVA_HOME: `~/android-toolchain/jdk/jdk-17.0.14+7/Contents/Home`
- apktool: `/tmp/apktool.jar`（v2.11.1）
- build-tools: `~/android-toolchain/android-sdk/build-tools/34.0.0`（zipalign/apksigner）
- adb: `~/android-toolchain/android-sdk/platform-tools/adb`
- keystore: `~/Desktop/龍族報告/01_專案/MotoEye_HUD/bruce_moto.keystore`（alias bruce, pwd Dragon2026!）
- 原始 APK: `~/Desktop/龍族報告/01_專案/MotoEye_HUD/MotoEye.apk`
- dex 注入流程：apktool d → 改 smali → apktool b → 抽出 classes3.dex → Python 注入原始 APK（.so 保持 STORED）→ zipalign -p 4 → apksigner sign → adb install -r
- 華為 WebView 為 com.huawei.webview 114.0.5.302；WindowManager$LayoutParams(IIII) 不存在（需用 (II)+手設 type/flags）
