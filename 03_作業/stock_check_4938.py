import json, datetime

with open('/tmp/yahoo_4938.json') as f:
    data = json.load(f)

meta = data['chart']['result'][0]['meta']
q = data['chart']['result'][0]['indicators']['quote'][0]

print("=== 華爾特 和碩(4938.TW) 即時股價查詢 ===\n")

latest = len(q['close']) - 1
day_open = q['open'][1] if len(q['open']) > 1 else None
day_high = q['high'][1] if day_high := (q['high'][latest]) is not None else q.get('high', [])[-1]
day_low_val_pos = latest
print(f"Symbol: {meta['symbol']}")
print(f"Currency: {meta['currency']}")

# Extract data carefully
for i, key in enumerate(['open','high','low','close']):
    vals = q.get(key, [None])
    if len(vals) > 1:
        raw_idx = len(vals)-1
    elif i < len(vals):
        raw_idx = i
    else:
        continue

print(f"Latest timestamps:", q['timestamp'])
print("Data:")

# Manual extraction - indices depend on array length (previous day + today)
# chartPreviousClose is the close of previous trading session
prev_close = meta.get('chartPreviousClose', 'N/A')
today_close_val = None
for ci, val in enumerate(q['close']):
    if val is not None:
        # The last non-None value is today's
        pass

# Last element is today
today_close = q['close'][-1]
day_high_v = q['high'][-1]
day_low_v = q['low'][-1]
day_vol = q['volume'][-1]
day_open_val = q['open'][-1] if len(q['open']) > 1 else None

# Previous day's data
if len(q['close']) >= 2:
    prev_day_close = q['close'][0]
else:
    prev_day_close = today_close

print(f"Today open: {day_open_val}")
print(f"Today high: {day_high_v}")
print(f"Today low: {day_low_v}")
print(f"Today volume: {day_vol:+,}" if isinstance(day_vol,(int,float)) else f"Volume: N/A")
print(f"prevClose (API): {prev_close}")

market_time = meta.get('regularMarketTime')
if market_time:
    dt = datetime.datetime.fromtimestamp(market_time, tz=datetime.timezone(datetime.timedelta(hours=8)))
    print(f"regMarketTime Tp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
is_weekday = now.weekday() < 5
now_t = now.time()
wh_start = datetime.time(9, 0)
wh_end = datetime.time(13, 30)
in_trade_time = is_weekday and wh_start <= now_t <= wh_end

print(f"Now CST: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Weekday: {'Mon-Fri' if is_weekday else 'Weekend'}, Trading: {in_trade_time}")

wh_status = ""
if not is_weekday:
    wh_status = "Non-trading (Sat/Sun)"
elif now_t < wh_start:
    wh_status = f"Before 09:00 open, now {now_t.strftime('%H:%M')}"
else:
    wh_status = f"After lunch close 13:30, now {now_t.strftime('%H:%M')}"

print(f"Trading check (09:00-13:30 Taipei): NOT trading - {wh_status}")

# Compare with last recorded price
last_price = 84.5
pct_change = (today_close - last_price) / last_price * 100 if today_close else None
print(f"\nLatest close: {today_close}")
print(f"Last recorded: {last_price}")
if pct_change is not None:
    print(f"Change vs record: {pct_change:+.2f}%")

# Day high/low from current session data (latest row)
dh = day_high_v[-1] if isinstance(day_high_v, list) else day_high_v
dl = day_low_v[-1] if isinstance(day_low_v, list) else day_low_v
print(f"Current candle: High={dh}, Low={dl}")
