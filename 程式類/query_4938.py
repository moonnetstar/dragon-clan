import urllib.request, json

url = "https://query1.finance.yahoo.com/v8/finance/chart/4938.TW?range=1d&interval=1m"
req = urllib.request.Request(url)
req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        d = json.load(resp)
        r = d["chart"]["result"][0]
        m = r["meta"]
        q = r["indicators"]["quote"][0]
        p = [c for c in q.get("close", []) if c is not None]
        print(f"Price: {m['regularMarketPrice']}")
        print(f"Currency: {m['currency']}")
        print(f"Today's prices count: {len(p)}")
        if p:
            print(f"Largest: {max(p)}")
            print(f"Smallest: {min(p)}")
            print(f"Latest price: {p[-1]}")
except Exception as e:
    print(f"Error: {e}")
