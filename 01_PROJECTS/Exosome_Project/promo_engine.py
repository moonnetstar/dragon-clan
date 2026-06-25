def calc(prices):
    if len(prices)<3: return sum(prices), False, 0.0
    return sum(prices)*0.8, True, min(prices)
print(calc([3980,358_80,1580]))