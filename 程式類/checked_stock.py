import json
from datetime import datetime

now = datetime(2026, 7, 12, 13, 0, 20)  # CST
weekday = now.weekday()  # Mon=0 Sun=6

print(f"Current time: {now.strftime('%Y-%m-%d %H:%M')} CST")
days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
print(f"Weekday: {days[weekday]} = {weekday}")

if weekday >= 5:  # Sat/Sun
    print("RESULT: Non-trading time (weekend)")
elif now.hour <= 8 or now.hour > 13 or (now.hour == 13 and now.minute > 30):
    print("RESULT: Not yet trading hours / market closed")
else:
    print(f"Trading hours - pulling price of last close: N/A (API failed)")
