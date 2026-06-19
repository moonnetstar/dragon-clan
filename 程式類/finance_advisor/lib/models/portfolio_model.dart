// lib/models/portfolio_model.dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'stock.dart';
import '../services/stock_api_service.dart';

class PortfolioModel extends ChangeNotifier {
  List<Stock> _stocks = [];
  bool _isLoading = false;
  String _lastUpdate = '';
  double _cashBalance = 0;

  List<Stock> get stocks => _stocks;
  bool get isLoading => _isLoading;
  String get lastUpdate => _lastUpdate;
  double get cashBalance => _cashBalance;

  double get totalCost => _stocks.fold(0, (sum, s) => sum + s.totalCost);
  double get totalValue => _stocks.fold(0, (sum, s) => sum + s.totalValue);
  double get totalProfitLoss => totalValue - totalCost;
  double get totalProfitLossPercent => totalCost > 0 ? totalProfitLoss / totalCost * 100 : 0;
  double get totalAssets => totalValue + cashBalance;

  PortfolioModel() {
    _loadDefaultPortfolio();
    loadPortfolio();
  }

  void _loadDefaultPortfolio() {
    _stocks = [
      Stock(code: '2330.TW', name: '台積電', cost: 1825, shares: 1000, buyDate: DateTime(2025, 1, 15)),
      Stock(code: '4938.TW', name: '和碩', cost: 69.8, shares: 900, buyDate: DateTime(2025, 2, 10)),
      Stock(code: '3376.TW', name: '新日興', cost: 179, shares: 1000, buyDate: DateTime(2025, 3, 5)),
      Stock(code: '3019.TW', name: '亞光', cost: 164.5, shares: 100, buyDate: DateTime(2025, 1, 20)),
      Stock(code: '6121.TWO', name: '新普', cost: 345, shares: 1000, buyDate: DateTime(2025, 4, 1)),
    ];
    _cashBalance = 25400;
  }

  Future<void> loadPortfolio() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final stocksJson = prefs.getString('stocks');
      final cash = prefs.getDouble('cashBalance');
      if (stocksJson != null) {
        final List<dynamic> decoded = jsonDecode(stocksJson);
        _stocks = decoded.map((e) => Stock.fromJson(e)).toList();
      }
      if (cash != null) _cashBalance = cash;
      notifyListeners();
    } catch (e) {
      debugPrint('載入失敗: $e');
    }
  }

  Future<void> savePortfolio() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final stocksJson = jsonEncode(_stocks.map((e) => e.toJson()).toList());
      await prefs.setString('stocks', stocksJson);
      await prefs.setDouble('cashBalance', _cashBalance);
    } catch (e) {
      debugPrint('儲存失敗: $e');
    }
  }

  Future<void> refreshPrices() async {
    _isLoading = true;
    notifyListeners();

    try {
      final codes = _stocks.map((s) => s.code).toList();
      final prices = await StockApiService.fetchMultiplePrices(codes);
      
      for (var stock in _stocks) {
        final data = prices[stock.code];
        if (data != null) {
          stock.currentPrice = data['price'] ?? 0;
          stock.changePercent = data['changePercent'] ?? 0;
          stock.high52w = data['high52w'] ?? 0;
          stock.low52w = data['low52w'] ?? 0;
          stock.ma5 = data['ma5'] ?? 0;
          stock.ma20 = data['ma20'] ?? 0;
          stock.ma60 = data['ma60'] ?? 0;
          stock.rsi = data['rsi'] ?? 50;
        }
      }
      
      _lastUpdate = DateTime.now().toString().substring(11, 19);
      await savePortfolio();
    } catch (e) {
      debugPrint('刷新價格失敗: $e');
    }

    _isLoading = false;
    notifyListeners();
  }

  void addStock(Stock stock) {
    _stocks.add(stock);
    savePortfolio();
    notifyListeners();
  }

  void removeStock(int index) {
    if (index >= 0 && index < _stocks.length) {
      _stocks.removeAt(index);
      savePortfolio();
      notifyListeners();
    }
  }

  void updateStock(int index, Stock stock) {
    if (index >= 0 && index < _stocks.length) {
      _stocks[index] = stock;
      savePortfolio();
      notifyListeners();
    }
  }
}
