// lib/screens/add_stock_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../models/portfolio_model.dart';
import '../models/stock.dart';

class AddStockScreen extends StatefulWidget {
  const AddStockScreen({super.key});

  @override
  State<AddStockScreen> createState() => _AddStockScreenState();
}

class _AddStockScreenState extends State<AddStockScreen> {
  final _formKey = GlobalKey<FormState>();
  final _codeCtrl = TextEditingController();
  final _nameCtrl = TextEditingController();
  final _costCtrl = TextEditingController();
  final _sharesCtrl = TextEditingController();
  DateTime _buyDate = DateTime.now();

  // 預設股票清單
  final _presetStocks = [
    {'code': '2330.TW', 'name': '台積電'},
    {'code': '4938.TW', 'name': '和碩'},
    {'code': '3376.TW', 'name': '新日興'},
    {'code': '3019.TW', 'name': '亞光'},
    {'code': '6121.TWO', 'name': '新普'},
    {'code': '2454.TW', 'name': '聯發科'},
    {'code': '2317.TW', 'name': '鴻海'},
    {'code': '2382.TW', 'name': '廣達'},
    {'code': '0050.TW', 'name': '元大台灣50'},
    {'code': '0056.TW', 'name': '元大高股息'},
    {'code': '00713.TW', 'name': '元大高息低波'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('新增持股'),
        actions: [
          TextButton(
            onPressed: _save,
            child: const Text('儲存', style: TextStyle(fontSize: 16)),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 快速選擇
            const Text('快速選擇', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _presetStocks.map((s) {
                return ActionChip(
                  label: Text(s['name']!),
                  onPressed: () {
                    _codeCtrl.text = s['code']!;
                    _nameCtrl.text = s['name']!;
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // 股票代碼
            TextFormField(
              controller: _codeCtrl,
              decoration: const InputDecoration(
                labelText: '股票代碼',
                hintText: '例如：2330.TW',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? '請輸入股票代碼' : null,
            ),
            const SizedBox(height: 16),

            // 股票名稱
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(
                labelText: '股票名稱',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? '請輸入股票名稱' : null,
            ),
            const SizedBox(height: 16),

            // 買入價格
            TextFormField(
              controller: _costCtrl,
              decoration: const InputDecoration(
                labelText: '買入價格',
                border: OutlineInputBorder(),
                prefixText: 'NT\$ ',
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[\d.]'))],
              validator: (v) {
                if (v?.isEmpty ?? true) return '請輸入買入價格';
                if (double.tryParse(v!) == null) return '請輸入有效數字';
                return null;
              },
            ),
            const SizedBox(height: 16),

            // 股數
            TextFormField(
              controller: _sharesCtrl,
              decoration: const InputDecoration(
                labelText: '持有股數',
                border: OutlineInputBorder(),
                suffixText: '股',
              ),
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              validator: (v) {
                if (v?.isEmpty ?? true) return '請輸入股數';
                if (int.tryParse(v!) == null) return '請輸入有效數字';
                return null;
              },
            ),
            const SizedBox(height: 16),

            // 買入日期
            ListTile(
              title: const Text('買入日期'),
              subtitle: Text('${_buyDate.year}/${_buyDate.month.toString().padLeft(2, '0')}/${_buyDate.day.toString().padLeft(2, '0')}'),
              trailing: const Icon(Icons.calendar_today),
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: _buyDate,
                  firstDate: DateTime(2020),
                  lastDate: DateTime.now(),
                );
                if (date != null) setState(() => _buyDate = date);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;

    final stock = Stock(
      code: _codeCtrl.text.trim(),
      name: _nameCtrl.text.trim(),
      cost: double.parse(_costCtrl.text),
      shares: int.parse(_sharesCtrl.text),
      buyDate: _buyDate,
    );

    context.read<PortfolioModel>().addStock(stock);
    Navigator.pop(context);
  }

  @override
  void dispose() {
    _codeCtrl.dispose();
    _nameCtrl.dispose();
    _costCtrl.dispose();
    _sharesCtrl.dispose();
    super.dispose();
  }
}
