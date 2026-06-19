// lib/screens/stock_detail_screen.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/stock.dart';

class StockDetailScreen extends StatelessWidget {
  final Stock stock;
  final int index;

  const StockDetailScreen({super.key, required this.stock, required this.index});

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat('#,##0.0');
    final fmtPct = NumberFormat('+#,##0.00;-#,##0.00');
    final isUp = stock.changePercent >= 0;
    final color = isUp ? Colors.red[600] : Colors.green[600];

    return Scaffold(
      appBar: AppBar(
        title: Text(stock.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () {
              Navigator.pop(context, true);
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 價格大卡
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(stock.code, style: TextStyle(color: Colors.grey[600])),
                  const SizedBox(height: 8),
                  Text('${fmt.format(stock.currentPrice)}', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: color)),
                  const SizedBox(height: 4),
                  Text('${isUp ? '+' : ''}${stock.changePercent.toStringAsFixed(2)}%', style: TextStyle(color: color, fontSize: 16)),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: stock.profitLossPercent >= 0 ? Colors.red[50] : Colors.green[50],
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '損益 ${fmtPct.format(stock.profitLossPercent / 100)}',
                      style: TextStyle(color: stock.profitLossPercent >= 0 ? Colors.red[700] : Colors.green[700], fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 基本資料
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('基本資料', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  _infoRow('買入成本', '${fmt.format(stock.cost)}'),
                  _infoRow('持有股數', '${stock.shares}'),
                  _infoRow('買入日期', DateFormat('yyyy/MM/dd').format(stock.buyDate)),
                  _infoRow('總成本', 'NT\$ ${fmt.format(stock.totalCost)}'),
                  _infoRow('總市值', 'NT\$ ${fmt.format(stock.totalValue)}'),
                  _infoRow('總損益', 'NT\$ ${fmt.format(stock.profitLoss)}'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 技術指標
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('技術指標', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  _infoRow('52週最高', '${fmt.format(stock.high52w)}'),
                  _infoRow('52週最低', '${fmt.format(stock.low52w)}'),
                  _infoRow('MA5', stock.ma5 > 0 ? '${fmt.format(stock.ma5)}' : 'N/A'),
                  _infoRow('MA20', stock.ma20 > 0 ? '${fmt.format(stock.ma20)}' : 'N/A'),
                  _infoRow('MA60', stock.ma60 > 0 ? '${fmt.format(stock.ma60)}' : 'N/A'),
                  _infoRow('RSI(14)', '${stock.rsi.toStringAsFixed(1)}'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // AI 建議
          Card(
            color: Theme.of(context).colorScheme.primaryContainer,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(children: [
                    const Icon(Icons.psychology, size: 20),
                    const SizedBox(width: 8),
                    const Text('桃樂絲 AI 建議', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ]),
                  const SizedBox(height: 12),
                  Text(stock.trendSignal, style: const TextStyle(fontSize: 16)),
                  const SizedBox(height: 8),
                  Text(_getAdvice(stock), style: const TextStyle(fontSize: 14)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[600])),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  String _getAdvice(Stock s) {
    if (s.rsi > 75) return '⚠️ RSI 偏高，短線可能回檔。建議觀察或分批獲利了結。';
    if (s.rsi < 25) return '💡 RSI 偏低，可能反彈。可留意買點。';
    if (s.currentPrice > s.ma5 && s.ma5 > s.ma20) return '📈 多頭排列，趨勢健康，可續抱。';
    if (s.currentPrice < s.ma5 && s.ma5 < s.ma20) return '📉 空頭排列，趨勢偏弱，留意停損。';
    return '➡️ 中性整理，等待方向明朗。';
  }
