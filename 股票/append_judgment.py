filepath = '和碩追蹤-20260603.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

judgment = """### 📋 追蹤判斷 (10:50)
- RSI 84.54 > 74 ✅ 超買區
- 股價 101.0 >= 100 ✅
- 創今日新高 ❌（今日高 102.5，現價 101.0 尚未突破）
- **結論：** 10:15 已發第一批 TG 通知（RSI 85.4、創高 102.5），本次 RSI 與價格均未超越上次通知值，不重複發送。持續觀察是否再突破 102.5。
- 📌 第一批通知已發，等待創新高或明顯變化再發第二批。

---"""

content = content.rstrip()
if content.endswith('---'):
    content = content[:-3].rstrip() + '\n\n' + judgment + '\n'
else:
    content += '\n\n' + judgment + '\n'

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
