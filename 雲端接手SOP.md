# 🐉 龍族雲端接手 SOP

> 當本機離線，雲端 session 接手工作時，請按照此 SOP 操作。

## 第一步：拉取最新狀態

```bash
cd ~/Desktop/龍族報告
git pull origin main
```

## 第二步：檢查待辦事項

```bash
# 查看最近的 commit 了解進度
git log --oneline -10

# 查看工作目錄狀態
git status
```

## 第三步：讀取記憶

- 讀取 `~/.hermes/memories/` 中的記憶檔
- 查看 `~/Desktop/龍族報告/` 中的最新報告
- 檢查是否有未完成的任務

## 第四步：繼續工作

- 完成未完成的任務
- 工作結束前執行 heartbeat：`~/.hermes/scripts/heartbeat.sh`
- 或手動 commit + push：
  ```bash
  cd ~/Desktop/龍族報告
  git add -A
  git commit -m "雲端接手: [描述工作内容]"
  git push origin main
  ```

## 重要規則

1. **每次工作結束前必須 push**，讓下一個 session 能接手
2. **不要覆蓋其他人的工作**，先 pull 再工作
3. **commit 訊息要清楚**，讓接手的人知道做了什麼
4. **重要決策寫入 memory**，不要只寫在 commit 訊息裡

## 緊急聯絡

如果發現系統異常，透過 Telegram 通知勞勞（chat_id: 793529884）
