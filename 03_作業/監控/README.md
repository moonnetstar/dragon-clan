# 🐉 龍族多 Agent 資源管理方案

> 建立時間：2026-06-30
> 平台：Apple M4 / 32GB 統一記憶體 / macOS
> 狀態：✅ 監控運作中 | Docker 方案待部署

---

## 📁 檔案結構

```
03_作業/監控/
├── dragon_resource_monitor.py    # 即時資源監控腳本（已上線）
├── agent_scheduler.py            # Agent 任務調度器（API 模式）
├── daily_resource_report.py      # 每日資源報告生成器
├── docker-compose.yml            # Docker 編排方案（未來遷移用）
├── prometheus.yml                # Prometheus 配置
├── dragon_alerts.yml             # 告警規則
└── README.md                     # 本文件
```

---

## 🎯 資源配額設計

| Agent | 角色 | 優先級 | 最大記憶體 | 最大並行 | 可搶佔 |
|-------|------|--------|-----------|---------|--------|
| owl-alpha-1 | 桃樂絲 (CEO) | 🔴 High | 12GB | 2 | ❌ |
| owl-alpha-2 | 布魯斯 (工程) | 🟡 Medium | 8GB | 1 | ✅ |
| owl-alpha-3 | 華爾特 (財經) | 🟡 Medium | 8GB | 1 | ✅ |
| default | 通用 | 🟢 Low | 4GB | 1 | ✅ |

**總量：32GB 統一記憶體，保留 4GB 給系統，28GB 供 Agent 使用**

---

## 🔧 使用方式

### 1. 即時監控（手動）
```bash
# 完整報告
python3 ~/Desktop/龍族報告/03_作業/監控/dragon_resource_monitor.py

# 簡短摘要
python3 ~/Desktop/龍族報告/03_作業/監控/dragon_resource_monitor.py --summary

# 持續監控（每 30 秒）
python3 ~/Desktop/龍族報告/03_作業/監控/dragon_resource_monitor.py -i 30
```

### 2. 自動監控（Cron Job）
- Job ID: `479345f99be2`
- 頻率：每 10 分鐘
- 行為：有風險時發送 TG 告警，無風險時靜默

### 3. Agent 調度器 API
```bash
# 啟動
python3 agent_scheduler.py --port 8080

# 查詢狀態
curl http://localhost:8080/status

# 申請資源
curl -X POST http://localhost:8080/allocate \
  -d '{"agent_id":"owl-alpha-1","memory_gb":3}'

# 釋放資源
curl -X POST http://localhost:8080/release \
  -d '{"agent_id":"owl-alpha-1","task_id":"task-xxx"}'

# 排程查詢
curl -X POST http://localhost:8080/schedule \
  -d '{"agent_id":"owl-alpha-2","memory_gb":4}'
```

---

## 🐳 Docker 部署（未來方案）

當需要遷移到 Linux 伺服器時：

```bash
cd ~/Desktop/龍族報告/03_作業/監控
docker compose up -d

# 監控 Dashboard
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

### Docker 資源隔離
- **ollama-server**: 限制 20GB 記憶體 / 8 CPU
- **agent-dorothy**: 限制 12GB / 4 CPU
- **agent-bruce**: 限制 8GB / 3 CPU
- **agent-walter**: 限制 8GB / 3 CPU
- **monitoring stack**: 限制 2GB 總計

---

## ⚠️ 告警門檻

| 指標 | 警告 | 嚴重 |
|------|------|------|
| 記憶體使用率 | > 85% | > 90% |
| Swap 使用 | > 1GB | > 2GB |
| CPU 負載 (1m) | > 8 (80% 核心數) | > 9.5 |
| 可用記憶體 (扣模型) | < 6GB | < 4GB |
| 任務佇列 | > 5 | > 10 |

---

## 📊 數據儲存

- **即時快照**: `latest_snapshot.json`
- **歷史日誌**: `resource_log.csv`
- **每日報告**: `Reports/每日資源報告_YYYYMMDD.md`

---

## 🔮 未來優化

1. **模型自動卸載**: 當記憶體壓力大時，自動 `ollama rm` 閒置模型
2. **預測性調度**: 根據歷史數據預測高負載時段
3. **GPU 監控**: 遷移到有獨立 GPU 的機器後，加入 `nvidia-smi` 監控
4. **自動擴展**: 整合 Kubernetes HPA 自動擴展 Agent 實例

---

桃樂絲 🌹 | 2026-06-30
