#!/usr/bin/env python3
"""Fetch latest price for 和碩 (4938.TW) from Yahoo Finance.

Strategy: do one request, retry once after a short backoff on HTTP 429.
Returns stdout line 'PRICE=<number>' or 'ERROR=<msg>'.
"""
import json, sys, time, urllib.request, urllib.error

URL = "https://query1.finance.yahoo.com/v8/finance/chart/4938.TW?range=1d&interval=5m"


def _fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode())


def main():
    try:
        data = _fetch()
    except urllib.error.HTTPError as e:
        print(f"ERROR:{e.code} {e.reason}")
        # Try once with backoff on 429
        if e.code != 429:
            sys.exit(1)
        time.sleep(8)
        try:
            data = _fetch()
        except urllib.error.HTTPError as e2:
            print(f"ERROR:{e2.code} {e2.reason}")
            sys.exit(1)

    result = data["chart"]["result"][0]
    q = result["indicators"]["quote"][0].get("close") or []
    closes = [x for x in q if x is not None]

    meta = (data["chart"]["result"][0]["meta"]) or {}
    prev_close = float(meta.get("previousClose", 0) or 0)
    cur = meta.get("regularMarketPrice")
    opened = meta.get("regularMarketOpen")

    if closes:
        print(f"PRICE={closes[-1]} PREV_CLOSE={prev_close} OPENED={opened}")
    elif cur is not None and prev_close > 0:
        print(f"PRICE={cur:.4f} PREV_CLOSE={prev_close:.4f}")
    else:
        print("ERROR:no-data")


if __name__ == "__main__":
    main()
