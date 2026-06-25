import urllib.request, urllib.parse, json, re

# Read config
with open('/Users/moonstar/.hermes/config.yaml') as f:
    content = f.read()

# Find token under telegram section
match = re.search(r'telegram:.*?token:\s*([^\s\n]+)', content, re.DOTALL)
token = match.group(1).strip().strip('"').strip("'") if match else None

if not token:
    print('No token found')
    exit(1)

print(f'Using token: {token[:15]}...')

# Send Telegram message
chat_id = '793529884'
text = '📈 【和碩(4938) 漲價警報】\n\n⏰ 時間：2026-06-24 10:10 (盤中)\n💰 現價：82.70\n📊 漲跌：+2.30 (+2.86%)\n📋 昨收：80.40\n🔺 開盤：80.30\n📈 最高：82.70\n📉 最低：80.10\n📦 成交量：4,950,000張\n💎 市值：221.805B\n\n⚠️ 較昨收漲幅 +2.86%，已超過 2% 設定閾值！'

url = f'https://api.telegram.org/bot{token}/sendMessage'
data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')

try:
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
        print(f'Telegram response: {result}')
        if result.get('ok'):
            print('SUCCESS: Telegram message sent!')
        else:
            print(f'FAILED: {result}')
except Exception as e:
    print(f'Error: {e}')
