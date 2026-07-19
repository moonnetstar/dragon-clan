============================================================
Dragon Clan Resource Monitor — 2026-07-18 19:21:33 CST
Status: 🔴 CRITICAL
============================================================

📊 System Overview (2026-07-18):
  Memory:    92.5% (25.6GB / 32.0GB) | Available: 2.4GB (~8% free)
  Swap:      95.2% (17.1GB / 18.0GB) [===============================] ⚠️ HIGH


  Disk:      23.8% (442.3GB used / 1858.2GB) | Free: 1415.9GB ✅
  Load Avg:  1.12 / 1.16 / 1.25
  Uptime:    5 days

🎮 GPU: Apple M4 (Apple Silicon Unified Memory)

💥 MEMORY PRESSURE: ⚠️ CRITICAL - Memory ≥ 90%, swap is heavy (95.2%)
   → Model inference will be slow due to I/O swapping
   → No memory headroom for new models or context expansion

🤖 Ollama Registry (18 models):
  • ollama-launch/Qwen3.6-35B-A3B:latest               ~17GB
  • ollama-launch/qwen3:8b                             ~5GB
  • ollama-launch/Sornith-1.0-35b-Q4:latest            ~20GB
  • ollama-launch/phi3:mini                            ~2GB
  • Qwen27B:latest                                     ~19GB
  • dragon_walter:latest                               ~16GB
  • dragon_dorothy:latest                              ~16GB
  • dragon_edith:latest                                ~1GB
  • dragon_bruce:latest                                ~2GB
  • Sornith-1.0-35b-Q4:latest                          ~20GB
  ... and 8 more models (176.0 GB total)

🎯 RECOMMENDATIONS:
  🚨 [URGENT] Unload large unused models to reduce swap pressure immediately.
  📦 [RECOMMENDED] Trim Ollama registry from 18 models — reclaim SSD space.
============================================================
Generated: 2026-07-18 19:21:33 CST by Dorobot Monitor
