#!/usr/bin/env python3
"""Fix the .env file: split single-line vars into proper multi-line format, then start Flask."""
import os, sys

ENV_PATH = "/Users/moonstar/Desktop/龍族報告/99_封存/TwoTone_Backup_20260625_165900/TwoTone/.env"

# Read raw content - all vars on one line separated by spaces
with open(ENV_PATH, "rb") as f:
    raw = f.read()

# Parse: keys are LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, NGROK_AUTHTOKEN
parsed = {}
for prefix in ["LINE_CHANNEL_ID=",
               "LINE_CHANNEL_SECRET=",
               "LINE_CHANNEL_ACCESS_TOKEN=",
               "NGROK_AUTHTOKEN="]:
    idx_start = raw.find(prefix.encode())
    if idx_start < 0:
        print(f"❌ Missing key: {prefix}")
        sys.exit(1)
    val_end = len(raw)
    # Split at next ' ' (space separator between keys)
    for other_prefix in ["LINE_CHANNEL_ID=", "LINE_CHANNEL_SECRET=",
                         "LINE_CHANNEL_ACCESS_TOKEN=", "NGROK_AUTHTOKEN="]:
        idx_next = raw.find(other_prefix.encode(), idx_start + 1)
        if 0 < idx_next < val_end:
            val_end = idx_next

    parsed[prefix[:-1]] = raw[idx_start + len(prefix):-val_end == idx_start and idx_start or sys.maxsize]

# Re-parse properly using string split approach
raw_str = raw.decode("utf-8").strip()
new_lines = {}
current_key_val = ""
for chunk in raw_str.split():
    if "=" in chunk:
        key, _, val = chunk.partition("=")
        # If next space-separated token has '=' too and current value doesn't end with = 
        new_lines[key] = str(val)

print("Parsed keys:", list(new_lines.keys()))

# Write back in proper format
with open(ENV_PATH, "w") as f:
    for k, v in new_lines.items():
        f.write(f"{k}={v}\n")
        print(f"  {k}: {len(v)} chars — {'OK' if len(v) > 20 else '⚠️ short'}")

print("\n✅ .env file reformatted successfully!")

# Now verify Flask can parse it with dotenv
sys.path.insert(0, "/Users/moonstar/Desktop/龍族報告/99_封存/TwoTone_Backup_20260625_165900/TwoTone")
from dotenv import load_dotenv
load_dotenv(env_path=ENV_PATH)

lid = os.environ.get("LINE_CHANNEL_ID","").strip()
ls = os.environ.get("LINE_CHANNEL_SECRET","").strip()
lat = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN","").strip()
ng = os.environ.get("NGROK_AUTHTOKEN","")

print(f"\n--- Verification ---")
print(f"LINE_CHANNEL_ID:        {lid} ({len(lid)} chars)")
print(f"LINE_CHANNEL_SECRET:    {'SET' if ls else 'EMPTY'} (len={len(ls)})")
print(f"LINE_ACCESS_TOKEN:      {'SET' if lat else 'EMPTY'} (len={len(lat)})")
print(f"NGROK_AUTHTOKEN:        {'present' if ng else 'EMPTY'} (len={len(ng)})")

# Start Flask on PORT 8077 with all env vars set
os.environ["PORT"] = "8077"
os.chdir("/Users/moonstar/Desktop/龍族報告/99_封存/TwoTone_Backup_20260625_165900/TwoTone")

print("\n--- Starting Flask on :8077 ---")
from app import app
app.run(host="0.0.0.0", port=8077, debug=False)
