#!/usr/bin/env python3
import time, sys
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
current_time_local = datetime.now(tz)
print(f"台北時間：{current_time_local.strftime('%Y-%m-%d %H:%M:%S')} 星期{'一二三四五六日'[current_time_local.weekday()]}")
print(f">> Yahoo API recently rate-limited, retrying with yfinance...")

try:
    import yfinance as yf
    
    ticker = yf.Ticker("4938.TW")
    
    # Get history for 2 days - to get latest quote or previous close
    hist_2d = ticker.history(period="2d", interval="1m")
    
    if not hist_2d.empty:
        last_close_time = hist_2d.index[-1]
        latest_price = float(hist_2d['Close'].iloc[-1])
        
        # Get market regular market previous close - better estimate from prev row
        if len(hist_2d) >= 2:
            for i in range(len(hist_2d)-1, -1, -1):
                ts = hist_2d.index[i]
                local_ts = ts.tz_convert(tz) if ts.tzinfo else tz.localize(ts.replace(tzinfo=tz))
                # skip overnight hours (after 5:30pm previous day or before 9am current/day)
                if local_ts.hour >= 14 and i < len(hist_2d)-1:
                    continue
                latest_price = float(hist_2d['Close'].iloc[i])
                
        print(f"yfinance API OK - Latest price: {latest_price} NGD")
    else:
        print("hist empty!")

except Exception as e:
    print(f"Error checking via yfinance: {e}")

