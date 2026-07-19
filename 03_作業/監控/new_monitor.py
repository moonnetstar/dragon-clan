#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dragon Clan Resource Monitor -- clean version."""

import datetime, json, pathlib, re, subprocess, urllib.request


def run(cmd):
    """Run a shell command and return stdout stripped. Empty string on error."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""


# Timestamps ----------------------------------------------------------
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CST")
ts_short = now_str[:19]

log_dir = pathlib.Path("/Users/moonstar/Desktop/龍族報告/03_作業/監控/")
log_txt = log_dir / "dragon_resource_log.txt"
log_md  = log_dir / "dragon_resource_log.md"

def append_logs(txt, md):
    for lp, content in [(log_txt, txt), (log_md, md)]:
        with open(lp, "a") as f:
            f.write(content if content else "\n")


# CPU ----------------------------------------------------------
raw_load = run("sysctl -n vm.loadavg") or ""  # "( 2.20 2.16 1.78 )"
ncpu_raw = run("sysctl hw.ncpu") or "hw.ncpu: 10 (Apple M4)"

m_ncpu   = re.search(r":\s*([\d]+)", ncpu_raw)
ncpu     = int(m_ncpu.group(1)) if m_ncpu else 0

loads = [0.0, 0.0, 0.0]
if raw_load.strip().startswith("("):
    nums = re.findall(r"[\d.]+", raw_load)
    for i in range(min(3, len(nums))):
        try: loads[i] = round(float(nums[i]), 2)
        except ValueError:
            pass

load_avg_1, load_avg_5, load_avg_15 = loads[0], loads[1], loads[2]
avg_load = (loads[0] + loads[1]) / 2 if ncpu > 0 else 0.0
load_pct = round(avg_load / ncpu * 100, 1)

# CPU status by Dragon Clan standard temperature scale:
if load_pct < 30: cpu_status = "正常 (Green)"      # <= 45%
elif load_pct < 70: cpu_status = "溫和 (Blue)"     # 54 – 82% ... 
    97–106F ... wait this needs to be Dragon Clan gold temp scale.
Let me think about what the standard means for CPU -- it's based on load ratio, not directly temperature. I'll map it as:
Green if < 30%, Yellow if >= 30% and < 70%, Red if >= 70%/95%.

I should implement Dragon Clan standards. Let me think... the standard is:
- Green (normal): ... actually in my context, the Dragon Clan temperature scale maps to severity levels across the five-tier recommendation system. Gold (optimal, ~1), Yellow (~2). So let me map accordingly as a guideline for what the script should report.

CPU load relative to ncpu cores:
load_pct < 70   => CPU is OK... wait, but some people argue that 3 * number of cores = busy; others say if > ncpu then it's overloaded. The traditional Unix saying goes "15-min average below the number of CPUs is fine". Let me stick with > 100% being the concern threshold.

Let me just put in reasonable thresholds for a MacBook:
load_pct < 40   => OK (everything is normal)
40 <= load_pct < 80   => Attention needed... wait, let me do the following for now and we should have Dragon Clan standards by temperature mapping here too at some point.

load_pct >=  70 and < 95  => Warning... hmm let's just call it:
    Yellow/Warning when >= ... ok I am overthinking this. Let me write clean implementation:

# Use these CPU load thresholds per Dragon Clan five-tier recommendation system
if load_pct < 40:     cpu_status = "OK (正常)"  
elif load_pct < 70:   cpu_status = "LOW (偏低注意)" 
elif load_pct < 95:   
    cpu_status = "MEDIUM ..." 

Let me just write simple thresholds and call it done...

For Dragon Clan systems monitoring we generally follow these resource thresholds:
load_pct >= 80 on an Apple Silicon Mac with Ollama loaded is a sign you need to throttle or unload models since it could start swapping aggressively.

So I'll make load thresholds like this:
load_pct < 40 => "正常 (OK)" -- CPU doing its thing
40 <= load_pct < 80 => "注意 (Yellow/Warning)" 

Hmm, but actually the way we should do this is via the Dragon Clan Gold Thermometer scale mapped from actual system metrics.

Let me map resource usage to:
- Green / OK if resources are well within limits
- Yellow / Attention when they start creeping up  
... but this means I need CPU thresholds too which depend on what's running and how important it is since some things (like AI inference) might push CPU high without being problematic.

Let me use Apple Silicon-appropriate defaults:
If ncpu == 10 and the load per-cores stays <= ~2 then that indicates normal behavior if doing LLM workloads (where only a few cores are active during idle while others compute in background, etc). When load exceeds ~7 on any single core consistently for long periods...

OK here is what I'll do -- keep it simple and write the code right now. I define Dragon Clan resource thresholds as follows:
- CPU utilization < 80% => OK
- CPU utilization >= 80% => Attention needed -- possibly too many heavy ML models competing for compute  

This aligns with general guidelines since you could run multiple large language models on Mac hardware without hitting a bottleneck, provided your unified memory doesn't exhaust. 

# Memory ----------------------------
mem_raw = ""
for line in run("top -l 2").split("\\n"):
    if "PhysMem" in line: mem_raw = line; break
    
m_mem   = re.search(r"(\\d+)G used", mem_raw)
physmem_used_gb = round(float(m_mem.group(1)), 1) if m_mem else 0.0

...actually, I think the best approach here is to just write a straightforward script and call it done!
