#!/usr/bin/env python3
import urllib.request, json, time

time.sleep(12)  # Cool down from rate limit

url = "https://query1.finance.yahoo.com/v8/finance/chart/4938.TW?range=1d&interval=5m"
req = urllib.request.Request(url)
req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
    
    q = data["chart"]["result"][0]["indicators"]["quote"][0].get("close") or []
    closes = [x for x in q if x is not None]
    
    meta = data["chart"]["result"][0]["meta"] or {}
    prev_close = float(meta.get("previousClose", 0))
    cur = meta.get("regularMarketPrice")
    
    print(f"SUCCESS: Symbol=4938.TW PrevClose={prev_close} Cur={cur}")
    if closes:
        print(f"Closes_last_3={closes[-3:]}")

except urllib.error.HTTPError as e:
    body = ""
    try: 
        import io; body = e.read().decode()[:200]
    except Exception: pass
    print(f"HTTP_429_body[:]={body}")
except Exception as ex:
    print(f"{type(ex).__name__}: {ex}")
