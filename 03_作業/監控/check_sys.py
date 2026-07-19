#!/usr/bin/env python3
"""Dragon Clan system resource monitoring - macOS."""
import subprocess, os, json, re
from datetime import datetime

def run(cmd):
    return (subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout or '').strip()

# Timestamps
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')

# CPU cores
cpu_cores = run('sysctl -n hw.ncpu').strip()

# Memory from top command
top_out    = run('top -l 1')
mem_used_gb, mem_pct = None, None
for line in top_out.splitlines():
    if 'Phys' in line and ('Mem' in line or 'Compress' in line):
        m_mem   = re.search(r'([\d,]+)\s*MB\s+used', line)
        m_total = re.search(r'out (\d+)\s*M', line)
        if m_mem:
            mem_used_mb    = int(m_mem.group(1).replace(',',''))
            mem_used_gb     = round(mem_used_mb/1024, 1)
            total_mb       = int(m_total.group(1)) if m_total else (mem_used_mb * 3 // 2)
            mem_pct         = round(mem_used_mb / total_mb * 100, 1)
        break

# Disk free
disk_free = run("df -h / | awk 'NR==2{print $4}'").strip()

# Top processes by CPU and Memory (using proper Python subprocess instead of shell tricks)
try:
    cmd_cpu   = ['ps', '-eo', 'pid,comm,pcpu,rss', '--sort=-%cpu', '|', 'head', '-n8', '|', 'tail', '-n7']
except Exception as e:
    cmd_cpu    = []

# Fallback - use a simple shell command string instead
top_cpu_raw   = run('ps aux --sort=-pcpu | head -6')

# Ollama loaded models
ollama_tags  = run('curl -s http://localhost:11434/api/tags')
models_list  = []
try:
    data        = json.loads(ollama_tags) if ollama_tags else {}
    models_list  = data.get('models', [])
except (json.JSONDecodeError, AttributeError):
    models_list   = []

# Build report lines
L          = []
L.append('=' * 70)
L.append(f'Dragon Clan Resource Monitor - {now_str}')
L.append('='*70) 

# System section
L.append('── SYSTEM ──────────────────')   
L.append(f'CPU Cores:      {cpu_cores} cores')
if mem_used_gb is not None and total_mb:
    L.append(f'Memory Usage:   ~{total_mb/1024:.0f} GB system, {mem_used_gb} GB used ({mem_pct}%)')
else:
    L.append('Memory:         Could not determine (top output failed)')

L.append(f'Disk Available:  ~{disk_free}') 

# Top processes by CPU  
L.append('── Top Processes by CPU ──────────────') 
cpu_lines     = top_cpu_raw.strip().splitlines()
if len(cpu_lines) > 1:  
    header      = cpu_lines[0]
    for line in cpu_lines[1:4]:    # take top 3
        parts     = line.split()  
        if len(parts) >= 8:    
            user, pid, cpu, mem_kb, comm   = parts[0], parts[1], parts[2], parts[7], parts[-1]
            rss_mb   = int(mem_kb) / 1024 if mem_kb.isdigit() else '-'  
            L.append(f'  {comm:<25s} PID={pid:>7s} User={user:<8s} CPU={cpu:>5s}% RSS={rss_mb:.0f}MB')
else:  
    # Try alternative format  
    alt_raw       = run("ps -eo pid,%mem,rss,nlwp,comm --sort=-%mem | head -6")  
    for al in alt_raw.strip().splitlines()[1:4]:      
        parts       = al.split()     
        if len(parts) >= 5:
            num, pct, rss_val, threads, name     = int(parts[0]), parts[1], parts[2], parts[3], parts[-1]
            L.append(f'  {name:<25s} RSS={rss_val:>7s}KB MEM={pct}% PID={num}')

# Ollama models  
L.append('── Ollama Loaded Models ──────────') 
for model in (models_list or [])[:8]:
    md        = model.get('details', {}) or {}
    parent     = md.get('parent_model','') or 'latest'
    tag       = f'{model["name"]}:{parent.split(":")[0]}' 
    size_mb    = int(model.get('size', 0) / (1 << 20)) if model.get('size') else '?'  
    L.append(f'  {tag} (~{size_mb} MB)' if isinstance(size_mb,int) else f'{model["name"]}')

est_total_gb   = sum(int((m.get('size', 0) or 0)/(1 << 20)) for m in (models_list or [])) / 1024

L.append('='*70) 
report   = '\n'.join(L)
print(report)  

# Save to log file  
log_dir       = os.path.expanduser('~/Desktop/龍族報告/03_作業/監控/')   
os.makedirs(log_dir, exist_ok=True) 
log_file      = os.path.join(log_dir,'resource_monitor.log')
with open(log_file, 'a', encoding='utf-8') as f:    
    f.write('\n' + report + '\n\n')  

print(f'\n✅ Logged to {log_file}')
