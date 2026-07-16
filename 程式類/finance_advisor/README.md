# 桃樂絲理財顧問 App

**工程師布魯斯 製作 | 2026-06-03**

## 功能特色

- 📊 **即時報價** — Yahoo Finance API 即時股價
- 💰 **損益計算** — 自動計算每檔持股損益、報酬率
- 📈 **技術指標** — MA5/MA20/MA60、RSI、趨勢判斷
- 🤖 **AI 建議** — 根據技術面給出買賣建議
- 📱 **跨平台** — iOS + Android 一套程式碼

## 安裝方式

### 環境需求
- Flutter SDK 3.0+
- Dart SDK 3.0+
- Xcode（iOS 開發）
- Android Studio（Android 開發）

### 步驟

```bash
# 1. 進入專案目錄
cd finance_advisor

# 2. 安裝依賴
flutter pub get

# 3. 執行模擬器
flutter run

# 4. 建置 APK（Android）
flutter build apk --release

# 5. 建置 iOS
flutter build ios --release
```

### 安裝到手机

**Android：**
1. 開啟手機「開發者選項」→ 啟用「USB 偵錯」
2. 用 USB 連接手機
3. 執行 `flutter run`

**iOS（需要 Apple Developer 帳號）：**
1. 用 Xcode 打開 `ios/Runner.xcworkspace`
2. 設定 Signing & Capabilities
3. 連接手機後執行 `flutter run`

## 專案結構

```
finance_advisor/
├── lib/
│   ├── main.dart                    # 入口
│   ├── models/
│   │   ├── stock.dart               # 股票資料模型
│   │   └── portfolio_model.dart     # 投資組合管理
│   ├── screens/
│   │   ├── home_screen.dart         # 主頁面（總覽、持股列表、設定）
│   │   ├── stock_detail_screen.dart # 持股詳情
│   │   └── add_stock_screen.dart    # 新增持股
│   └── services/
│       └── stock_api_service.dart   # Yahoo Finance API
├── pubspec.yaml
└── README.md
```

## 預設持股

已內建勞勞的持股組合作為預設值：
- 台積電 2330.TW（1000股，成本1825）
- 和碩 4938.TW（900股，成本69.8）
- 新日興 3376.TW（1000股，成本179）
- 亞光 3019.TW（100股，成本164.5）
- 新普 6121.TWO（1000股，成本345）
- 現金餘額：25,400 元

## 注意事項

- 股價資料來源為 Yahoo Finance，可能有 15-20 分鐘延遲
- 此 App 僅供參考，投資有風險
- 建議搭配桃樂絲每日報告使用

---

— 工程師布魯斯
