#!/usr/bin/env python3
import yfinance as yf
ticker = yf.Ticker("4938.TW")
info = ticker.fast_info
print(f"Current price: {info.last_price}")
print(f"Previous close: {info.previous_close}")
