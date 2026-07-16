// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/portfolio_model.dart';
import '../models/stock.dart';
import 'stock_detail_screen.dart';
import 'add_stock_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PortfolioModel>().refreshPrices();
    });
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      const _PortfolioTab(),
      const _StocksTab(),
      const _SettingsTab(),
    ];

    return Scaffold(
      body: SafeArea(child: pages[_selectedIndex]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (i) => setState(() => _selectedIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: '總覽'),
          NavigationDestination(icon: Icon(Icons.list_outlined), selectedIcon: Icon(Icons.list), label: '持股'),
          NavigationDestination(icon: Icon(Icons.settings_outlined), selectedIcon: Icon(Icons.settings), label: '設定'),
        ],
      ),
    );
  }
}

// ========== 總覽頁面 ==========
class _PortfolioTab extends StatelessWidget {
  const _PortfolioTab();

  @override
  Widget build(BuildContext context) {
    return Consumer<PortfolioModel>(
      builder: (context, model, _) {
        final fmt = NumberFormat('#,##0');
        final fmtPct = NumberFormat('+#,##0.00%;-#,##0.00%');
        final isUp = model.totalProfitLoss >= 0;

        return RefreshIndicator(
          onRefresh: model.refreshPrices,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 標題
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('桃樂絲理財顧問', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  if (model.isLoading)
                    const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  else
                    Text('更新: ${model.lastUpdate}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                ],
              ),
              const SizedBox(height: 20),

              // 總資產卡片
              Card(
                elevation: 4,
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    gradient: LinearGradient(
                      colors: [Theme.of(context).colorScheme.primary, Theme.of(context).colorScheme.primaryContainer],
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('總資產', style: TextStyle(color: Colors.white70, fontSize: 14)),
                      const SizedBox(height: 8),
                      Text('NT\$ ${fmt.format(model.totalAssets)}', style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Icon(isUp ? Icons.trending_up : Icons.trending_down, color: Colors.white, size: 20),
                          const SizedBox(width: 4),
                          Text('損益 ${fmt.format(model.totalProfitLoss)}', style: const TextStyle(color: Colors.white)),
                          const SizedBox(width: 12),
                          Text('(${fmtPct.format(model.totalProfitLossPercent / 100)})', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // 持股列表
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('我的持股', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.add_circle_outline),
                    onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AddStockScreen())),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              ...model.stocks.asMap().entries.map((entry) {
                final i = entry.key;
                final s = entry.value;
                return _StockCard(stock: s, onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => StockDetailScreen(stock: s, index: i)));
                });
              }),
            ],
          ),
        );
      },
    );
  }
}

// ========== 持股卡片 ==========
class _StockCard extends StatelessWidget {
  final Stock stock;
  final VoidCallback onTap;

  const _StockCard({required this.stock, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isUp = stock.changePercent >= 0;
    final color = isUp ? Colors.red[600] : Colors.green[600];
    final fmt = NumberFormat('#,##0.0');

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(onTap: onTap, child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(stock.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  Text(stock.code, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                ]),
                Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                  Text('${fmt.format(stock.currentPrice)}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
                  Text('${isUp ? '+' : ''}${stock.changePercent.toStringAsFixed(2)}%', style: TextStyle(color: color, fontSize: 12)),
                ]),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('成本 ${fmt.format(stock.cost)} × ${stock.shares}股', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                Text(
                  '${stock.profitLossPercent >= 0 ? '+' : ''}${stock.profitLossPercent.toStringAsFixed(1)}%',
                  style: TextStyle(color: stock.profitLossPercent >= 0 ? Colors.red[600] : Colors.green[600], fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('市值 ${fmt.format(stock.totalValue)}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                Text(stock.trendSignal, style: const TextStyle(fontSize: 12)),
              ],
            ),
          ],
        ),
      )),
    );
  }
}

// ========== 持股列表頁面 ==========
class _StocksTab extends StatelessWidget {
  const _StocksTab();

  @override
  Widget build(BuildContext context) {
    return Consumer<PortfolioModel>(
      builder: (context, model, _) {
        return Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('持股明細', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  Row(children: [
                    IconButton(
                      icon: const Icon(Icons.refresh),
                      onPressed: model.refreshPrices,
                    ),
                    IconButton(
                      icon: const Icon(Icons.add),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AddStockScreen())),
                    ),
                  ]),
                ],
              ),
            ),
            Expanded(
              child: model.stocks.isEmpty
                  ? const Center(child: Text('尚未新增持股'))
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: model.stocks.length,
                      itemBuilder: (context, i) {
                        final s = model.stocks[i];
                        return _StockCard(stock: s, onTap: () {
                          Navigator.push(context, MaterialPageRoute(builder: (_) => StockDetailScreen(stock: s, index: i)));
                        });
                      },
                    ),
            ),
          ],
        );
      },
    );
  }
}

// ========== 設定頁面 ==========
class _SettingsTab extends StatelessWidget {
  const _SettingsTab();

  @override
  Widget build(BuildContext context) {
    return Consumer<PortfolioModel>(
      builder: (context, model, _) {
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text('設定', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            Card(
              child: Column(children: [
                ListTile(
                  leading: const Icon(Icons.attach_money),
                  title: const Text('現金餘額'),
                  subtitle: Text('NT\$ ${NumberFormat('#,##0').format(model.cashBalance)}'),
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.refresh),
                  title: const Text('重新載入預設值'),
                  onTap: () {
                    model.savePortfolio();
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('已重新載入')));
                  },
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('關於'),
                  subtitle: const Text('桃樂絲理財顧問 v1.0.0\n工程師布魯斯 製作'),
                ),
              ]),
            ),
          ],
        );
      },
    );
  }
}
