#!/usr/bin/env python3
"""Dragon Clan Resource Monitor - system + Ollama status report."""

import datetime as Dt, json, os, re
import subprocess as sub


def run_cmd(cmd):
    """Run shell command safely. Returns stdout or empty string."""
    try:
        r = sub.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10,
        )
        return (r.stdout or "").strip()
    except Exception:
        return ""


def parse_memory():
    """Aggregate memory from vm_stat pages. Apple Silicon uses 16384-byte pages."""
    active = wireddown = 0
    for line in run_cmd("vm_stat").splitlines():
        pm = re.match(r"\s*Pages\s+(.+?):\s+(\d+)\.?\s*\.", line, re.IGNORECASE)
        if not pm:
            continue
        key = pm.group(1).strip().replace(" ", "")
        val = int(pm.group(2))
        if key == "Active":
            active = val
        elif key == "Wireddown":
            wireddown = val
        # Also handle lowercase variants from vm_stat output
        if key == "active":
            active = val
        elif key == "wireddown":
            wireddown = val

    psb = 16384
    used_gb = (active + wireddown) * psb / (1024.0 ** 3)

    total_bytes_raw = int(run_cmd("sysctl -n hw.memsize") or "0")
    total_gb_actual = round(total_bytes_raw / (1024 ** 3), 1) if total_bytes_raw else 0

    return {"total_gb": total_gb_actual, "used_gb": round(used_gb, 2)}


def parse_cpu():
    """Get CPU core count and load averages."""
    ncpu_str = run_cmd("sysctl -n hw.ncpu").strip()
    cores = int(ncpu_str) if ncpu_str.isdigit else 1

    try:
        loads = list(os.getloadavg())
    except Exception:
        ut = run_cmd("uptime") or ""
        nums = [float(x.strip()) for x in re.findall(r"[0-9.]+", ut)[:3]]
        loads = nums if len(nums) >= 2 else []

    return {"cores": cores, "loads": loads}


def parse_disk():
    """Get root filesystem usage from df -h /.

    macOS output format:
      Filesystem   Size  Used Avail Capacity iused   ifree %iused  Mounted on
      /dev/disk3s1s1  1.8Ti  13Gi  1.4Ti       1%     459k  4.3G       0%   /

    Column positions: [0]=Fs [1]=Size [2]=Used [3]=Avail [4]=Cap %
                     [5]=iused [6]=ifree [7]%%iuse [8]=Mounted on
    """
    out_lines = run_cmd("df -h /").splitlines()
    if len(out_lines) < 2:
        return {"pct": "?", "used": "-", "total": "-"}

    parts = out_lines[1].split()
    if len(parts) >= 5:
        pct_str = str(parts[4])
        used_str = str(parts[2])
        total_str = str(parts[1])
    else:
        return {"pct": "?", "used": "-", "total": "-"}

    return {"pct": pct_str, "used": used_str, "total": total_str}


def get_ollama_models():
    """List Ollama models and deduplicate by base name."""
    out = run_cmd("ollama list") or ""
    entries = [l for l in out.splitlines() if l.strip()]

    seen_base = set()
    dragon_models = []

    for line in entries:
        m_match = re.match(
            r"(\S+)\s+(\S+)\s+([\d.]+\s*[MGTP]?B)\s+(.+)", line
        )
        if not m_match:
            continue

        name_raw = m_match.group(1)
        size_str = m_match.group(3).strip()

        normalized = (re.sub(r"^ollama-launch/", "", name_raw)).rsplit(":", 1)[0]
        seen_base.add(normalized)

        if "dragon_" in name_raw.lower():
            dragon_models.append((name_raw, size_str))

    return {
        "count": len(entries),
        "unique_names": len(seen_base),
        "models": dragon_models,
    }


def status_assessment(cpu_info):
    """Determine overall system health from CPU load."""
    cores = cpu_info["cores"]
    loads = cpu_info.get("loads", [])

    if not cores or not loads:
        return "CHECK - could not determine system load"

    load_1m = loads[0]
    ratio = (load_1m / cores) if cores > 0 else 0
    pct = round(ratio * 100)

    if ratio > 3.5:
        return "WARN: CPU high load (load={:.1f}, cores={} ~{}/core)".format(
            load_1m, cores, pct
        )
    elif ratio > 1.5:
        return "CAUTION: CPU moderate load (load={:.1f}, cores={} ~{}/core)".format(
            load_1m, cores, pct
        )
    else:
        return ("CPU NORMAL (load={:.1f} / {} cores = {}/core)").format(
            load_1m, cores, pct)


def main():
    ts = Dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S CST")

    mem_stats  = parse_memory()
    cpu_info   = parse_cpu()
    disk_data  = parse_disk()
    ollama     = get_ollama_models()

    sep = "=" * 60

    # Build report
    rlines = []
    rlines.append(sep)
    rlines.append("Dragon Clan Resource Monitor | {}".format(ts))
    rlines.append(sep)
    rlines.append("")

    cores     = cpu_info["cores"]
    loads_list = cpu_info["loads"]

    # --- CPU row ---
    if cores > 0 and len(loads_list) >= 2:
        pct_val = round(loads_list[0] / cores * 100)
        rlines.append("CPU: {} core(s), Load Avg (1/5/15min): {:.2f} / {:.2f} / {:.2f} (~{}/core)".format(
            cores, loads_list[0], loads_list[1], loads_list[2], pct_val))

    # --- status row via CPU assessment ---
    status_text = status_assessment(cpu_info)
    rlines.append("")
    rlines.append(status_text)

    # --- Memory row ---
    rlines.append("")
    rlines.append("Memory:")
    rlines.append("  Total: {} GB | Used (Active+Wireddown): {:.2f} GB".format(
        mem_stats["total_gb"], mem_stats["used_gb"]))

    # --- Disk row ---
    disk_pct = disk_data.get("pct", "?")
    if disk_pct and "%" in str(disk_pct):
        rlines.append("")
        rlines.append("Disk (/): {} used ({}/{} bytes) -- OK".format(
            disk_pct, disk_data["used"], disk_data["total"]))

    # --- Ollama models row ---
    if ollama.get("models"):
        rlines.append("")
        rlines.append(
            "Ollama Models: {} total, {} unique base names, {} Dragon Clan".format(
                ollama["count"], ollama["unique_names"], len(ollama["models"])
            )
        )
        for dm_name, dm_size in sorted(set(ollama["models"])):
            rlines.append("  * {} ({})".format(dm_name, dm_size))

    # --- Join and print report ---
    report = "\n".join(rlines) + "\n"
    print(report)

    # --- Append to log file ---
    home_dir = os.environ.get("HOME", "/Users/moonstar")
    log_dir = os.path.join(
        home_dir, "Desktop", "龍族報告", "03_作業", "監控")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "resource_monitor.log")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n" + report)


if __name__ == "__main__":
    main()
