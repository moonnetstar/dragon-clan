#!/usr/bin/env python3
"""Dragon Clan Resource Report Generator."""
import subprocess
import re


def run(cmd):
    r = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=30
    )
    return r.stdout.strip()


def main():
    ts_main = run('date "+%Y-%m-%d %H:%M:%S CST"')

    print("=" * 72)
    print("  Dragon Clan Resource Monitor")
    print("=" * 72)
    print("*** Report generated at:", ts_main, "***\n")

    # System info
    cpu_brand = run('sysctl -n machdep.cpu.brand_string').strip()
    ncpu_str = run('sysctl -n hw.ncpu')
    ncpu = re.search(r'(\d+)', ncpu_str.split('/')[-1]).groups(0)
