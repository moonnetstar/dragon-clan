#!/usr/bin/env python3
"""Dragon Clan Resource Monitor — Quick Snapshot (Run for Cron)"""
import psutil, shutil, subprocess, os, json, urllib.request
from datetime import datetime

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
log_dir = os.path.expanduser('~/Desktop/龍族報告/03_作業/監控/logs')
os.makedirs(log_dir, exist_ok=True)

# Gather all metrics in one go for consistency
vm = psutil.virtual_memory()
sw = psutil.swap_memory()
disk = shutil.disk_usage('/')
load = psutil.getloadavg()
uptime_out = subprocess.run('uptime', shell=True, capture_output=True, text=True).stdout.strip()
up_part = uptime_out.split('up',1)[1].strip() if 'up' in uptime_out else ''

gpu_raw = subprocess.run(['system_profiler','SPDisplaysDataType'], capture_output=True,text=True).stdout
for line in gpu_raw.split('\n'):
    if 'Chipset Model' in line:
        gpu_raw = line.split(': ',1)[1].strip()

# Ollama models & count
model_count = 0
models_info = []
try:
    with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5) as resp:
        data = json.loads(resp.read())
        model_count = len(data.get('models', []))
        for m in data.get('models', []):
            models_info.append({
                'name': m['name'],
                'size_gb': round(m.get('size', 0) / (1024**3), 0)
            })
except Exception as e:
    pass

swap_pct = sw.percent
if swap_pct >= 90 or vm.percent >= 95:
    status = '🔴 CRITICAL'
elif swap_pct >= 75 or vm.percent >= 80:
    status = '🟡 WARNING'
else:
    status = '🟢 NORMAL'

swapbar = '=' * min(int(swap_pct/3), 33)

# ps top consumers (RSS > 100MB)
ps_rows = []
try:
    ps_out = subprocess.run('ps -rco pid,%mem,rss,args', shell=True, capture_output=True, text=True).stdout.strip()
    for line in ps_out.split('\n')[1:]:
        parts = line.split(None, 4) if len(line.split()) >= 5 else []
        if len(parts) == 5 and int(parts[3]) > 102400:  # RSS > 100MB
            ps_rows.append(parts)
except: pass

# Build log content
lines = []
lines.append('============================================================')
lines.append(f'Dragon Clan Resource Monitor — {now} CST')
lines.append(f'Status: {status}')
lines.append('============================================================')
lines.append('')
lines.append(f'📊 System Overview ({now[:10]}):')
lines.append(f'  Memory:    {vm.percent:.1f}% ({vm.used/1024**3:.1f}GB / {vm.total/1024**3:.1f}GB) | Available: {vm.available/1024**3:.1f}GB (~{vm.available/vm.total*100:.0f}% free)')
lines.append(f'  Swap:      {sw.percent:.1f}% ({sw.used/1024**3:.1f}GB / {sw.total/1024**3:.1f}GB) [{swapbar}] ⚠️ HIGH')
lines.append('')
if ps_rows:
    lines.append(f'  Top RSS consumers (>100MB): ')
    for row in ps_rows[:5]:
        pid, mpercent, rss_kb, _, cmd = row
        try:
            rss_mb = int(rss_kb) / 1024
            lines.append(f'    PID={pid} rss={rss_mb:.0f}MB mem={mpercent}% {cmd}')
        except ValueError:
            pass

lines.append('')
lines.append(f'  Disk:      {disk.used/disk.total*100:.1f}% ({disk.used/1024**3:.1f}GB used / {disk.total/1024**3:.1f}GB) | Free: {disk.free/1024**3:.1f}GB ✅')
lines.append(f'  Load Avg:  {load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}')
lines.append(f'  Uptime:    {up_part.split(",")[0].strip()}')
lines.append('')
lines.append(f'🎮 GPU: {gpu_raw or "unknown"} (Apple Silicon Unified Memory)')
lines.append('')
if vm.percent >= 90:
    lines.append(f'💥 MEMORY PRESSURE: ⚠️ CRITICAL - Memory ≥ 90%, swap is heavy ({swap_pct:.1f}%)')
    lines.append('   → Model inference will be slow due to I/O swapping')
    lines.append('   → No memory headroom for new models or context expansion')
else:
    lines.append(f'💥 MEMORY PRESSURE: Normal')

lines.append('')
lines.append(f'🤖 Ollama Registry ({model_count} models):')
for mi in models_info[:10]:
    lines.append(f'  • {mi["name"]:<50} ~{int(mi["size_gb"])}GB')
if len(models_info) > 10:
    rest = len(models_info) - 10
    lines.append(f'  ... and {rest} more models ({sum(m["size_gb"] for m in models_info if not "size" in m)} GB total)')

lines.append('')
lines.append('🎯 RECOMMENDATIONS:')
if swap_pct >= 90:
    lines.append('  🚨 [URGENT] Unload large unused models to reduce swap pressure immediately.')
if model_count > 15:
    lines.append(f'  📦 [RECOMMENDED] Trim Ollama registry from {model_count} models — reclaim SSD space.')

lines.append('============================================================')
lines.append(f'Generated: {now} CST by Dorobot Monitor')
content = '\n'.join(lines) + '\n'

log_file = os.path.join(log_dir, f'resource_monitor.log.{now[:10]}.md')
with open(log_file, 'w', encoding='utf-8') as f:
    f.write(content)

# Print concise summary to stdout
print(f'✅ LOGGED → {log_file}')
print('=== RESOURCE MONITOR SUMMARY ===')
print(f'Status : {status}')
free_gb = (vm.total - vm.used) / 1024 ** 3
print(f'Memory  : {vm.percent:.1f}% ({swapbar}) [{free_gb:.1f}GB free]')
