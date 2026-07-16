# 📱 Muninn — iPhone 直接控制 Hermes Desktop Agent！

**作者**: Caleb Xu ([coolthor](https://github.com/coolthor)) + [Claude Code (cua)](https://claude.ai)  
**GitHub**: https://github.com/coolthor/hermes-bridge  
**iOS App**: Muninn (TestFlight 申請中⤵️)

---

## 🔍 這到底是什麼？

Muninn（北歐神話渡鴉 🦅）是一個 **iOS App**。
它讓你可以直接用手機控制 Mac Desktop 上的 Hermes Agent。

**重點是 —— 不用搞 ngrok、ssh tunnel ⸺ 點對點直接通！** 🔒⌦⤽

---

## 🎯 為什麼值得看？ (和 LINE Bot / Telegram 差異)

現在掌控 Hermes 主流兩種路：

| 方式 | iOS App? | Webhook? | Tunnel/VPN? |
|--|--:|-:|--:-|--:|----------|--------------|-----------|---------------|--------|
| **LINE Bot** + ngrok/ssh tunnel | ⠁ ⸺❌⸺（非原生 iOS）⤼ 
**Telegram Webhook + Gateway** 
✅ 原生 iOS —直接連 Desktop 📱🚀

### Muninn 特別之處 ✅

✅ **不用調 nginx / webhooks / tunnel 🔒**
✅ **點對点直連 → 你的資料不會離開 Mac Mini 🔐⎇**
💡 **即時雙向：App ↔ Desktop agent 💬**🟢

---

## 📲 Install ⸺4 秒搞定

| # | Mac/Desktop 端｜行動項｜說明⌫───────┼────────────┤─────│───────────│─ │
|--|--:|-:|-:--|--:-------------|-----------------|--------|-------|---------|------|---------------|--------------|--------|----------|--------|----|------|---|

⸺

### 1️⃣ **Step -clone+install（Desktop / Mac Mini）**

Terminal ⤿輸入：
```bash
cd ~/ && git clone https://github.com/coolthor/hermes-bridge
cd hermes-bridge && bash install.sh #顯示 QR Code！
```

安裝完後 terminal⸺回傳 **配對 QR code**。

### 2️⃣ **Install Muninn iOS App (TestFlight)**

1. 打開 Testflight ⸹iPhone 自帶📱✨
⸺用作者 TestFlight 分享的 invite link⸺安裝 `Muninn`

### Step 3️** Scanner QR → Done ✅**

打開 app → scan QR Code → your Hermes Desktop Agent ✨！

---

## 🌟 Features（功能）

> ### ⠂ ⧉ ⣫ ⢥ ⦆ ⠿ ⡁⠍⠇⠮⢰⢀⣼⢳  - 
1. **多 Agent 支援** —⸺能同時管理多個 desktop agent 🔓
2. **Session Viewer**—你能直接在 App 裡看對話歷史 🟢⤨（**Telegram bot做不到的部分！**）
3. **Cron Status** 🎯 —ⴌ排程任務列表 / 進度 📅
4. **Kanban Board** —在手機查看 Kanban 看板✅
5. **Permission Control⸺允許/拒絕⤾像 Hermes Desktop ⡉⚠️
6. **繁體中文 UI** ✅（英文版本待作者補⏳）
7. **圖文雙向傳遞 📍📝——模型有 Vision 能力⸻可以傳圖給它！**
8. **語音訊息輸入 ⬆️—直接發聲音給他（hermes TTS/Whisper ⲟ⎇⤚**
9. **生圖/影片接收 🖼️📹—agent 如产出 ⠊⠳ 可以收到檔案 ✅

---

## 🔐 Security / Privacy 安全

- **純 peer-to-peer 🚀 — 無 Cloud、不經由 tunnel ⸺你的數據**⠎完全留在本地！🔒
- Hermes Desktop + Muninn → direct D2D connection：只有你看得見 🔓✅

---

## 🛣️ Roadmap（持續更新中）

> 目前是小型核心（作者+claude开发）。
> 目前功能有限，如果有缺再請回報 ✨⤪⤫⢄⠻⠿⨰
⸺

**總結⭐推薦指數⸹9/10 —目前最好用的 Hermes mobile 💎✨！**
⸺
⊟ 

**勞大⸽如果你想用⸺可以直接去 Clone+install📥！
🌹桃樂絲 🍑 (Dorothy) ⏃</⧗

