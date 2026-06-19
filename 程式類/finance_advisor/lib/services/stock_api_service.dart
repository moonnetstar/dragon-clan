// lib/services/stock_api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class StockApiService {
  static const String _baseUrl = 'https://query1.finance.yahoo.com/v8/finance/chart';

  static Future<Map<String, dynamic>?> fetchPrice(String code) async {
    try {
      final url = '$_baseUrl/$code?interval=1d&range=60d';
      final response = await http.get(
        Uri.parse(url),
        headers: {'User-Agent': 'Mozilla/5.0'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode != 200) return null;

      final data = jsonDecode(response.body);
      final result = data['chart']?['result']?[0];
      if (result == null) return null;

      final meta = result['meta'];
      final closes = (result['indicators']?['quote']?[0]?['close'] as List?)
          ?.where((e) => e != null)
          .map((e) => (e as num).toDouble())
          .toList() ?? [];

      final price = (meta['regularMarketPrice'] ?? 0).toDouble();
      final prev = (meta['chartPreviousClose'] ?? meta['previousClose'] ?? 0).toDouble();
      final changePercent = prev > 0 ? (price - prev) / prev * 100 : 0;

      // MAs
      double ma5 = 0, ma20 = 0, ma60 = 0;
      if (closes.length >= 5) ma5 = closes.sublist(closes.length - 5).reduce((a, b) => a + b) / 5;
      if (closes.length >= 20) ma20 = closes.sublist(closes.length - 20).reduce((a, b) => a + b) / 20;
      if (closes.length >= 60) ma60 = closes.sublist(closes.length - 60).reduce((a, b) => a + b) / 60;

      // RSI
      double rsi = 50;
      if (closes.length >= 15) {
        double ag = 0, al = 0;
        for (int i = closes.length - 14; i < closes.length; i++) {
          final d = closes[i] - closes[i - 1];
          if (d > 0) ag += d; else al += d.abs();
        }
        ag /= 14; al /= 14;
        rsi = al > 0 ? 100 - (100 / (1 + ag / al)) : 50;
      }

      return {
        'price': price,
        'changePercent': changePercent,
        'high52w': (meta['fiftyTwoWeekHigh'] ?? 0).toDouble(),
        'low52w': (meta['fiftyTwoWeekLow'] ?? 0).toDouble(),
        'ma5': ma5,
        'ma20': ma20,
        'ma60': ma60,
        'rsi': rsi,
      };
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, Map<String, dynamic>>> fetchMultiplePrices(List<String> codes) async {
    final results = <String, Map<String, dynamic>>{};
    for (final code in codes) {
      final data = await fetchPrice(code);
      if (data != null) results[code] = data;
    }
    return results;
  }

  static Future<double> fetchGoldPrice() async {
    try {
      final data = await fetchPrice('GC=F');
      return data?['price'] ?? 0;
    } catch (e) {
      return 0;
    }
  }

  static Future<double> fetchUsdIndex() async {
    try {
      final data = await fetchPrice('DX-Y.NYB');
      return data?['price'] ?? 0;
    } catch (e) {
      return 0;
    }
  }
}
