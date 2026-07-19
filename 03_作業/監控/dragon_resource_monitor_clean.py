#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dragon Clan Resource Monitor — clean rewrite."""

import datetime, json, re, subprocess, sys,\
    os, urllib.request


def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,\
                           text=True, timeout=15)
        return (r.stdout or '').strip()
    except Exception:
        return 'ERR'


ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CST")

# ─── CPU cores + load ---/n  #   ncpu = int(run('sysctl -n hw.ncpu\') or run)
ncpu_str = run('sysctl -n hw.ncpu')
try:
    ncpu = int(re.search(r'\d+', ncpu_str).group())
except (AttributeError, ValueError):
    ncpu = 1

load_raw = run('sysctl -n vm.loadavg'):
loads = []