#!/usr/bin/env python3
"""Dragon Clan system resource monitoring — macOS."""
import subprocess, os, re

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

now = run('date "+%Y-%m-%d %H:%M:%S CST"')

# CPU cores
cpu_cores = run('sysctl -n hw.ncpu').strip()

# RAM info via top
vm_top   = run('top -l 1')
used_mb  = total_mb = None
for line in vm_top.splitlines():
    if 'Phys Mem' in line and 'out' in line:
        m = re.search(r'(\d+)M\s*used', line)
        total_match = re.search(r'out (\d+)M', line)
        if m and total_match:
            used_mb  = int(m.group(1))
            total_mb = int(total_match.group(1))
break  # noqa

if used_mb is None:
    # Fallback: parse sysctl + vm_map info
    hw_mem = run('sysctl -n hw.memsize')
    total_mb_raw = hw_mem.split(':')[1].strip()
    total_mb = int(total_mem_str) / (1024 ** 1)   # already bytes -> MB

# disk free  
disk_free = run('df -h / | awk NR==2{print $4}').strip().lstrip()

top_cpu_raw = run("""ps -eo pid,user,pcpu,pmem,rss%,"""'comm --sort=-%cpu | grep -v PID | head -7'""")
top_mem_raw = run("""ps -eo pid,user,pcpu,pmem,rss%,"""'comm --sort=-%mem | grep -v PID | head -5'""")

# Ollama loaded models
ollama_out = run('curl -s http://localhost:11434/models')
import json as _json
try:
    models = _json.loads(ollama_out) if ollama_out else []
except Exception:
    models = []

total_ram_est_mb = sum(m.get('size', 0) for m in models) / (1024**2) * len(models) if not isinstance(models, list) else 'N/A'

# Build report  
lines = []
lines.append('='*70)
lines.append(f'Dragon Clan Resource Monitor — {now}')
lines.append('='*70)
lines.append('')
lines.append('── System Summary ──────────────')
lines.append(f'Cores: {cpu_cores} | RAM: ~{total_mb/1024:.1f} GB total / {used_mb/1024:.1f} GB used ({used_mb/total_mb*100:.1f}%) ')
lines.append(f'Disk: {disk_free}')

if models:
    lines.append('')
    lines.append(f'── Loaded Models ────────────────')
    for m in models[:8]:   # show only recent
        tag = f"{m['name']}:{m.get('details',{}).get('parent_model','').split(':')[0] if isinstance(m.get('details'),dict) else ''}".strip()
        lines.append(f'  {tag}')

lines.append('='*70)

text = '\n'.join(lines) 
print(text)

# Append to log  
log_path = os.path.expanduser('~/Desktop/龍族報告/03_作業/監控/resource_monitor.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
with open(log_path, 'a', encoding='utf-8') as f:
    f.write(text + '\n\n')

print('\n>> Logged to:', log_path)
