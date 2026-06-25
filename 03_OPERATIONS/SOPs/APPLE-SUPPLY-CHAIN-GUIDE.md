# 華爾特蘋果供應鏈監控系統 — 使用說明
========================================

Novabridge — 工程師布魯斯 建立
最後更新：2026-06-03

## 系統概述

本系統每日自動監控 Apple 相關事件（WWDC、財報、新產品發表）
及勞勞持有的 5 檔蘋果供應鏈股票新聞，分析對投資組合的潛在影響。

## 勞勞的持股

| 代號 | 名稱   | 預估持倉金額 |
|------|--------|------------|
| 2330 | 台積電  | 83,760 元  |
| 4938 | 和碩    | 83,760 元  |
| 3376 | 新日興  | 83,760 元  |
| 3019 | 亞光    | 83,760 元  |
| 6121 | 新普    | 83,760 元  |
|      | **合計** | **418,800 元** |

警示門檻：5% = **20,940 元**

## 檔案位置

| 檔案 | 路徑 |
|------|------|
| 主程式 | `/Users/moonstar/line-bot/apple_supply_chain_monitor.py` |
| 報告目錄 | `/Users/moonstar/line-bot/reports/` |
| 狀態檔 | `/Users/moonstar/line-bot/.apple_monitor_state.json` |
| 環境變數 | `/Users/moonstar/line-bot/.env` |
| 本說明檔 | `~/Desktop/APPLE-SUPPLY-CHAIN-GUIDE.md` |

## 使用方式

### 每日自動執行（cronjob）
已設定每天 09:00 (台灣時間) 自動執行。

### 手動執行

```bash
# 正常模式（抓取即時新聞 + 推播 LINE）
cd /Users/moonstar/line-bot
python3 apple_supply_chain_monitor.py

# 測試模式（用模擬資料，不推播）
python3 apple_supply_chain_monitor.py --test --dry-run

# 只產生報告，不推播 LINE
python3 apple_supply_chain_monitor.py --dry-run

# WWDC 特別監控模式
python3 apple_supply_chain_monitor.py --wwdc
```

## 推播格式

```
【華爾特蘋果快報】
事件：Apple WWDC 2026 發表 AI 新功能
影響：
  - 台積電（2330）：正面，預估影響金額 +2,014 元
  - 和碩（4938）：正面，預估影響金額 +535 元
  - 新日興（3376）：正面，預估影響金額 +1,833 元
  - 亞光（3019）：正面，預估影響金額 +1,010 元
  - 新普（6121）：正面，預估影響金額 +1,783 元
組合總影響：+7,175 元
操作建議：請人工確認
```

## 警示規則

- 當預估波動 **超過 20,940 元**（總組合 5%）時，報告標註 ⚠️ 警告
- 預估波動以「金額」呈現，而非百分比
- 影響方向分：正面 / 負面 / 中性

## 新聞來源

- Google News RSS（中文）
- 關鍵字：台積電、和碩、新日興、亞光、新普（搭配 Apple / 蘋果）
- 每週追蹤：Apple WWDC、財報、新產品發表

## LINE 推播設定

推播需要 `LINE_CHANNEL_TOKEN`，設定於 `/Users/moonstar/line-bot/.env`：
```
LINE_CHANNEL_TOKEN=你的ChannelAccessToken
```

若未設定 Token，系統只會產生報告檔案，跳過 LINE 推播。（不影響監控運作）

## Cronjob 資訊

- 排程：每天 09:00 (台灣時間)
- 指令：`cd /Users/moonstar/line-bot && python3 apple_supply_chain_monitor.py`
- 日誌：終端機輸出 / reports/ 目錄下的報告檔案

## WWDC 特別注意

- WWDC 2026：2026-06-09
- 前後一週建議每日關注 `apple_supply_chain_monitor.py --wwdc` 輸出
- WWDC 後 48 小時內預期供應鏈波動較大

## 維護事项

1. **更新持倉金額**：編輯 `POSITION_VALUES` 字典
2. **新增監控股票**：在 `HOLDINGS` 和 `supplier_keywords` 新增
3. **調整警示門檻**：修改 `THRESHOLD_AMOUNT`
4. **報告留存**：reports/ 目錄自動保留最近 30 天

## 關於

- 系統名稱：華爾特蘋果供應鏈監控系統 v1.0
- 開發者：布魯斯 @ Novabridge
- 使用者：勞勞
- 授權：Novabridge 內部使用
