#!/usr/bin/env python3
"""
🐉 Dragon Clan Agent Scheduler (龍族 Agent 任務調度器)
根據資源可用度和優先級，決定是否允許 Agent 執行任務

設計原則：
1. 高優先級任務可搶佔低優先級資源
2. 記憶體不足時拒絕新任務
3. 模型卸載/載入自動化
4. 提供 REST API 供 Agent 查詢/申請資源
"""

import subprocess
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════
MEMORY_TOTAL_GB = 32.0
MEMORY_RESERVED_GB = 4.0  # 系統保留
MEMORY_AVAILABLE_GB = MEMORY_TOTAL_GB - MEMORY_RESERVED_GB

# Agent 資源配額
AGENTS = {
    "owl-alpha-1": {
        "name": "桃樂絲",
        "priority": 3,        # high
        "max_memory_gb": 12,
        "max_concurrent": 2,
        "preemptible": False,  # 不可被搶佔
    },
    "owl-alpha-2": {
        "name": "布魯斯",
        "priority": 2,        # medium
        "max_memory_gb": 8,
        "max_concurrent": 1,
        "preemptible": True,
    },
    "owl-alpha-3": {
        "name": "華爾特",
        "priority": 2,        # medium
        "max_memory_gb": 8,
        "max_concurrent": 1,
        "preemptible": True,
    },
    "default": {
        "name": "通用",
        "priority": 1,        # low
        "max_memory_gb": 4,
        "max_concurrent": 1,
        "preemptible": True,
    },
}

# 任務佇列
task_queue = []
active_tasks = {}  # agent_id -> [task_info]
lock = threading.Lock()

# ═══════════════════════════════════════════════
# 資源管理
# ═══════════════════════════════════════════════

class ResourceManager:
    def __init__(self):
        self.total_memory = MEMORY_AVAILABLE_GB
        self.allocated = {}  # agent_id -> GB
        
    def get_free_memory(self):
        """取得目前可用記憶體"""
        result = subprocess.run(["vm_stat"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        mem_stats = {}
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                val = val.strip().replace(".", "").replace(" ", "")
                try:
                    mem_stats[key.strip()] = int(val) * 16384
                except:
                    pass
        
        active = mem_stats.get("Pages active", 0)
        wired = mem_stats.get("Pages wired", 0)
        compressor = mem_stats.get("Pages stored in compressor", 0)
        used_gb = (active + wired + compressor) / (1024**3)
        
        return MEMORY_TOTAL_GB - used_gb
    
    def get_ollama_memory(self):
        """估算 Ollama 模型佔用"""
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        total = 0
        for line in result.stdout.strip().split("\n")[1:]:
            if line.strip():
                cols = line.split()
                if len(cols) >= 4:
                    try:
                        size_str = cols[2] + " " + cols[3]
                        if "GB" in size_str:
                            total += float(size_str.replace("GB", "").strip()) * 1.2
                    except:
                        pass
        return total
    
    def can_allocate(self, agent_id, request_gb):
        """檢查是否可以分配資源"""
        agent = AGENTS.get(agent_id)
        if not agent:
            return False, "未知 Agent"
        
        # 檢查並行數
        current_tasks = len(active_tasks.get(agent_id, []))
        if current_tasks >= agent["max_concurrent"]:
            return False, f"已達最大並行數 ({agent['max_concurrent']})"
        
        # 檢查 Agent 配額
        current_alloc = self.allocated.get(agent_id, 0)
        if current_alloc + request_gb > agent["max_memory_gb"]:
            return False, f"超出 Agent 配額 ({agent['max_memory_gb']}GB)"
        
        # 檢查系統可用
        free = self.get_free_memory()
        ollama_mem = self.get_ollama_memory()
        truly_free = free - ollama_mem
        
        if request_gb > truly_free:
            # 嘗試搶佔低優先級
            if self._try_preempt(agent_id, request_gb - truly_free):
                return True, "資源已通過搶佔釋放"
            return False, f"系統可用記憶體不足 (需要 {request_gb:.1f}GB, 可用 {truly_free:.1f}GB)"
        
        return True, "OK"
    
    def _try_preempt(self, requester_id, need_gb):
        """嘗試搶佔低優先級 Agent 的資源"""
        requester = AGENTS[requester_id]
        freed = 0
        
        # 按優先級低到高排序
        candidates = sorted(
            self.allocated.items(),
            key=lambda x: AGENTS.get(x[0], {}).get("priority", 0)
        )
        
        for agent_id, alloc_gb in candidates:
            if agent_id == requester_id:
                continue
            agent = AGENTS.get(agent_id)
            if not agent or not agent.get("preemptible"):
                continue
            if agent["priority"] >= requester["priority"]:
                continue
            
            # 搶佔此 Agent
            freed += alloc_gb
            self.allocated[agent_id] = 0
            # 通知該 Agent 需要釋放資源 (在實際應用中透過 API)
            
            if freed >= need_gb:
                return True
        
        return False
    
    def allocate(self, agent_id, task_id, memory_gb):
        """分配資源給 Agent"""
        with lock:
            self.allocated[agent_id] = self.allocated.get(agent_id, 0) + memory_gb
            if agent_id not in active_tasks:
                active_tasks[agent_id] = []
            active_tasks[agent_id].append({
                "task_id": task_id,
                "memory_gb": memory_gb,
                "started_at": datetime.now().isoformat(),
            })
    
    def release(self, agent_id, task_id):
        """釋放資源"""
        with lock:
            tasks = active_tasks.get(agent_id, [])
            for i, t in enumerate(tasks):
                if t["task_id"] == task_id:
                    mem = t["memory_gb"]
                    tasks.pop(i)
                    self.allocated[agent_id] = max(0, self.allocated.get(agent_id, 0) - mem)
                    return True
            return False
    
    def get_status(self):
        """取得完整資源狀態"""
        free = self.get_free_memory()
        ollama = self.get_ollama_memory()
        return {
            "timestamp": datetime.now().isoformat(),
            "memory": {
                "total_gb": MEMORY_TOTAL_GB,
                "available_system_gb": round(free, 2),
                "ollama_models_gb": round(ollama, 2),
                "truly_free_gb": round(free - ollama, 2),
            },
            "allocations": {
                agent_id: {
                    "agent_name": AGENTS[agent_id]["name"],
                    "allocated_gb": alloc,
                    "max_gb": AGENTS[agent_id]["max_memory_gb"],
                    "active_tasks": len(active_tasks.get(agent_id, [])),
                    "priority": AGENTS[agent_id]["priority"],
                }
                for agent_id, alloc in self.allocated.items()
            },
            "queue_length": len(task_queue),
        }


# 全域資源管理器
resource_mgr = ResourceManager()

# ═══════════════════════════════════════════════
# HTTP API Server
# ═══════════════════════════════════════════════

class AgentHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """自定義日誌格式"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_GET(self):
        if self.path == "/status":
            self._send_json(resource_mgr.get_status())
        elif self.path == "/agents":
            self._send_json({
                id: {"name": a["name"], "priority": a["priority"], "max_memory_gb": a["max_memory_gb"]}
                for id, a in AGENTS.items()
            })
        else:
            self._send_json({"error": "not found"}, 404)
    
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        
        if self.path == "/allocate":
            agent_id = body.get("agent_id")
            task_id = body.get("task_id", f"task-{int(time.time())}")
            memory_gb = body.get("memory_gb", 2)
            
            ok, msg = resource_mgr.can_allocate(agent_id, memory_gb)
            if ok:
                resource_mgr.allocate(agent_id, task_id, memory_gb)
                self._send_json({"ok": True, "task_id": task_id, "message": msg})
            else:
                self._send_json({"ok": False, "message": msg}, 429)
        
        elif self.path == "/release":
            agent_id = body.get("agent_id")
            task_id = body.get("task_id")
            released = resource_mgr.release(agent_id, task_id)
            self._send_json({"ok": released})
        
        elif self.path == "/schedule":
            """智能排程：根據優先級和資源決定是否可執行"""
            agent_id = body.get("agent_id")
            memory_gb = body.get("memory_gb", 2)
            priority_override = body.get("priority_override")
            
            agent = AGENTS.get(agent_id, AGENTS["default"])
            effective_priority = priority_override or agent["priority"]
            
            ok, msg = resource_mgr.can_allocate(agent_id, memory_gb)
            self._send_json({
                "ok": ok,
                "agent": agent["name"],
                "priority": effective_priority,
                "message": msg,
                "suggestion": "等待資源釋放" if not ok else "可以執行",
            })
        
        else:
            self._send_json({"error": "not found"}, 44)


def run_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), AgentHandler)
    print(f"🐉 Dragon Agent Scheduler running on :{port}")
    print(f"   GET  /status  - 資源狀態")
    print(f"   GET  /agents  - Agent 列表")
    print(f"   POST /allocate - 申請資源")
    print(f"   POST /release  - 釋放資源")
    print(f"   POST /schedule - 排程查詢")
    server.serve_forever()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run_server(args.port)
