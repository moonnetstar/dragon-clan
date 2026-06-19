// lib/models/stock.dart
class Stock {
  final String code;
  final String name;
  final double cost;
  final int shares;
  final DateTime buyDate;
  double currentPrice;
  double changePercent;
  double high52w;
  double low52w;
  double ma5;
  double ma20;
  double ma60;
  double rsi;

  Stock({
    required this.code,
    required this.name,
    required this.cost,
    required this.shares,
    required this.buyDate,
    this.currentPrice = 0,
    this.changePercent = 0,
    this.high52w = 0,
    this.low52w = 0,
    this.ma5 = 0,
    this.ma20 = 0,
    this.ma60 = 0,
    this.rsi = 50,
  });

  double get totalCost => cost * shares;
  double get totalValue => currentPrice * shares;
  double get profitLoss => totalValue - totalCost;
  double get profitLossPercent => cost > 0 ? (currentPrice - cost) / cost * 100 : 0;

  String get trendSignal {
    if (rsi > 75) return '超買 ⚠️';
    if (rsi < 25) return '超賣 💡';
    if (currentPrice > ma5 && ma5 > ma20) return '多頭 📈';
    if (currentPrice < ma5 && ma5 < ma20) return '空頭 📉';
    return '中性 ➡️';
  }

  Map<String, dynamic> toJson() => {
    'code': code,
    'name': name,
    'cost': cost,
    'shares': shares,
    'buyDate': buyDate.toIso8601String(),
  };

  factory Stock.fromJson(Map<String, dynamic> json) => Stock(
    code: json['code'] ?? '',
    name: json['name'] ?? '',
    cost: (json['cost'] ?? 0).toDouble(),
    shares: json['shares'] ?? 0,
    buyDate: DateTime.tryParse(json['buyDate'] ?? '') ?? DateTime.now(),
  );
}
