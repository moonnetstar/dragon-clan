# ☁️ 雲端 Hermes Agent 調查報告

調查時間：2026-07-13 10:55
調查者：🌹 桃樂絲 Dorothy（依勞大指示，委派布魯斯執行）
結論：✅ Hermes Agent 官方支援雲端部署，非僅限本機

---

## 官方文檔明確說法（hermes-agent.nousresearch.com/docs）

> "It lives wherever you put it — a $5 VPS, a GPU cluster, or serverless
> infrastructure (Daytona, Modal) that costs nearly nothing when idle.
> Talk to it from Telegram while it works on a cloud VM you never SSH
> into yourself. It's not tied to your laptop."

白話：Hermes Agent 可以裝在任何雲端（VPS / Daytona / Modal），從 Telegram
遠端指揮，不用自己管那台 VM。

---

## 推薦的雲端部署方案

### 方案 A：Daytona（最推薦，一鍵起 VM）
- 雲端開發環境，註冊後一鍵開 Ubuntu VM
- 在 VM 上跑 `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
- 跑 `hermes setup --portal` 完成 OAuth
- 之後從 Telegram 指揮這台雲端 Hermes
- 優點：有持久硬碟、24h 不掉、適合當「龍族雲端大腦」

### 方案 B：Modal（serverless，近乎零成本）
- 閒置不收費，呼叫才計費
- 適合跑短期任務型 agent（如部署腳本）
- 缺點：非 24h 常駐，不適合當常駐統計中心

### 方案 C：$5 VPS（DigitalOcean / Linode / Hetzner）
- 最傳統、最可控
- 一個月約 $5，24h 常駐
- 適合把雙音符統計中心 + 雲端 Hermes 都放上去

---

## 對龍族的意義

1. **解決「停電客人連不上」**：雲端 Hermes 不被動，統計中心也能搬上 VPS
2. **一鍵生成雲端**：在雲端 Hermes 裡下指令，它直接在雲端 VM 上寫程式、
   部署服務，完全不依賴勞大這台 Mac
3. **Telegram 指揮**：勞大用手機 Telegram 就能讓雲端 Hermes 幹活

---

## 布魯斯後續任務
- [ ] 實際註冊 Daytona 或開 $5 VPS，安裝 Hermes Agent
- [ ] 驗證從 Telegram 指揮雲端 Hermes 可行
- [ ] 把雙音符統計中心遷移到雲端 Hermes 所在的 VM
- [ ] 寫一份「龍族雲端部署 SOP」

🌹 桃樂絲 Dorothy
