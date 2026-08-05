import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../models/enterprise.dart';
import '../../providers/enterprise_provider.dart';
import '../../widgets/loading_widget.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/status_badge.dart';

class InventoryScreen extends StatefulWidget {
  const InventoryScreen({super.key});

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<EnterpriseProvider>().loadStockLevels();
    });
  }

  void _showMovementForm() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _StockMovementFormWidget(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    return Scaffold(
      body: Column(
        children: [
          if (provider.lowStockItems.isNotEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              color: AppTheme.errorRed.withOpacity(0.15),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber, color: AppTheme.errorRed),
                  const SizedBox(width: 8),
                  Text(
                    '${provider.lowStockItems.length} items low on stock',
                    style: TextStyle(color: AppTheme.errorRed),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: _showMovementForm,
                    child: const Text('Restock'),
                  ),
                ],
              ),
            ),
          Expanded(
            child: _buildContent(theme, provider),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showMovementForm,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildContent(ThemeData theme, EnterpriseProvider provider) {
    if (provider.isLoadingStock) {
      return const LoadingWidget(message: 'Loading inventory...');
    }

    if (provider.error != null) {
      return AppErrorWidget(
        message: provider.error!,
        onRetry: () => provider.loadStockLevels(),
      );
    }

    if (provider.stockItems.isEmpty) {
      return const EmptyStateWidget(
        message: 'No stock items',
        icon: Icons.inventory_outlined,
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadStockLevels(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.stockItems.length,
        itemBuilder: (context, index) {
          final item = provider.stockItems[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: item.isLowStock
                          ? AppTheme.errorRed.withOpacity(0.1)
                          : AppTheme.successGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      item.isLowStock
                          ? Icons.inventory_2
                          : Icons.check_circle,
                      color: item.isLowStock
                          ? AppTheme.errorRed
                          : AppTheme.successGreen,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.productName,
                          style: theme.textTheme.titleMedium,
                        ),
                        if (item.sku != null)
                          Text(
                            'SKU: ${item.sku}',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: theme.colorScheme.onSurface
                                  .withOpacity(0.6),
                            ),
                          ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '${item.currentQuantity}',
                        style: theme.textTheme.headlineMedium?.copyWith(
                          color: item.isLowStock
                              ? AppTheme.errorRed
                              : AppTheme.successGreen,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (item.minimumQuantity != null)
                        Text(
                          'min: ${item.minimumQuantity}',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurface.withOpacity(0.5),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _StockMovementFormWidget extends StatefulWidget {
  @override
  State<_StockMovementFormWidget> createState() =>
      _StockMovementFormWidgetState();
}

class _StockMovementFormWidgetState extends State<_StockMovementFormWidget> {
  final _formKey = GlobalKey<FormState>();
  final _quantityController = TextEditingController();
  final _reasonController = TextEditingController();
  String _type = 'in';

  @override
  void dispose() {
    _quantityController.dispose();
    _reasonController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    final data = {
      'product_id': 0,
      'type': _type,
      'quantity': int.tryParse(_quantityController.text) ?? 0,
      'reason': _reasonController.text.trim(),
    };
    context.read<EnterpriseProvider>().registerStockMovement(data);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
        left: 24,
        right: 24,
        top: 24,
      ),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Stock Movement', style: theme.textTheme.headlineMedium),
              const SizedBox(height: 24),
              DropdownButtonFormField<String>(
                value: _type,
                decoration: const InputDecoration(labelText: 'Movement Type'),
                items: const [
                  DropdownMenuItem(value: 'in', child: Text('Stock In')),
                  DropdownMenuItem(value: 'out', child: Text('Stock Out')),
                  DropdownMenuItem(value: 'adjustment', child: Text('Adjustment')),
                ],
                onChanged: (v) => setState(() => _type = v ?? 'in'),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<int>(
                decoration: const InputDecoration(labelText: 'Product'),
                items: provider.stockItems.map((item) {
                  return DropdownMenuItem(
                    value: item.id,
                    child: Text(item.productName),
                  );
                }).toList(),
                onChanged: (v) {},
                validator: (v) => v == null ? 'Select a product' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _quantityController,
                decoration: const InputDecoration(labelText: 'Quantity *'),
                keyboardType: TextInputType.number,
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Required';
                  if (int.tryParse(v) == null || int.parse(v) <= 0) {
                    return 'Enter a valid quantity';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _reasonController,
                decoration: const InputDecoration(labelText: 'Reason'),
                maxLines: 2,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submit,
                  child: const Text('Register Movement'),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
