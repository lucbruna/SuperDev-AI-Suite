import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../models/enterprise.dart';
import '../../providers/enterprise_provider.dart';
import '../../widgets/loading_widget.dart';

class PdvScreen extends StatefulWidget {
  const PdvScreen({super.key});

  @override
  State<PdvScreen> createState() => _PdvScreenState();
}

class _PdvScreenState extends State<PdvScreen> {
  final List<_CartItem> _cart = [];
  String _selectedPayment = 'cash';
  double _discount = 0.0;
  bool _showCart = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<EnterpriseProvider>().loadProducts();
    });
  }

  double get _subtotal =>
      _cart.fold(0.0, (sum, item) => sum + item.subtotal);

  double get _total => (_subtotal - _discount).clamp(0, double.infinity);

  void _addToCart(Product product) {
    setState(() {
      final existing = _cart.where((c) => c.product.id == product.id).firstOrNull;
      if (existing != null) {
        existing.quantity++;
      } else {
        _cart.add(_CartItem(product: product));
      }
    });
  }

  void _removeFromCart(int index) {
    setState(() {
      _cart.removeAt(index);
    });
  }

  void _updateQuantity(int index, int delta) {
    setState(() {
      final item = _cart[index];
      item.quantity = (item.quantity + delta).clamp(1, 999);
    });
  }

  Future<void> _completeSale() async {
    if (_cart.isEmpty) return;
    final provider = context.read<EnterpriseProvider>();
    final saleData = {
      'items': _cart
          .map((c) => {
                'product_id': c.product.id,
                'product_name': c.product.name,
                'quantity': c.quantity,
                'unit_price': c.product.price,
                'subtotal': c.subtotal,
              })
          .toList(),
      'total_amount': _total,
      'discount_amount': _discount,
      'payment_method': _selectedPayment,
      'status': 'completed',
    };

    final order = await provider.registerSale(saleData);
    if (order != null && mounted) {
      setState(() {
        _cart.clear();
        _discount = 0.0;
        _showCart = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Sale #${order.orderNumber} completed!'),
          backgroundColor: AppTheme.successGreen,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    return Scaffold(
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: theme.colorScheme.primary.withOpacity(0.1),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Point of Sale',
                        style: theme.textTheme.titleLarge,
                      ),
                      Text(
                        '${_cart.length} items in cart',
                        style: theme.textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppTheme.tealAccent.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      Text(
                        'Total',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: AppTheme.tealAccent,
                        ),
                      ),
                      Text(
                        '\$${_total.toStringAsFixed(2)}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: AppTheme.tealAccent,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          if (_showCart)
            _buildCartView(theme)
          else
            _buildCatalogView(theme, provider),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => setState(() => _showCart = !_showCart),
                    icon: Icon(_showCart ? Icons.grid_view : Icons.shopping_cart),
                    label: Text(_showCart ? 'Catalog' : 'Cart (${_cart.length})'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _cart.isEmpty ? null : _completeSale,
                    icon: const Icon(Icons.check),
                    label: const Text('Complete Sale'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.successGreen,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCatalogView(ThemeData theme, EnterpriseProvider provider) {
    if (provider.isLoadingProducts) {
      return const Expanded(child: LoadingWidget(message: 'Loading products...'));
    }

    if (provider.products.isEmpty) {
      return const Expanded(
        child: Center(child: Text('No products available')),
      );
    }

    return Expanded(
      child: GridView.builder(
        padding: const EdgeInsets.all(12),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          childAspectRatio: 0.8,
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
        ),
        itemCount: provider.products.length,
        itemBuilder: (context, index) {
          final product = provider.products[index];
          return Card(
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => _addToCart(product),
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.tealAccent.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        product.name.isNotEmpty
                            ? product.name[0].toUpperCase()
                            : '?',
                        style: theme.textTheme.headlineMedium?.copyWith(
                          color: AppTheme.tealAccent,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      product.name,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '\$${product.price.toStringAsFixed(2)}',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: AppTheme.tealAccent,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCartView(ThemeData theme) {
    if (_cart.isEmpty) {
      return const Expanded(
        child: Center(child: Text('Cart is empty')),
      );
    }

    return Expanded(
      child: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _cart.length,
              itemBuilder: (context, index) {
                final item = _cart[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.product.name,
                                style: theme.textTheme.titleMedium,
                              ),
                              Text(
                                '\$${item.product.price.toStringAsFixed(2)} ea',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: AppTheme.tealAccent,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.remove_circle_outline),
                              onPressed: item.quantity > 1
                                  ? () => _updateQuantity(index, -1)
                                  : () => _removeFromCart(index),
                              color: AppTheme.errorRed,
                            ),
                            Text(
                              '${item.quantity}',
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.add_circle_outline),
                              onPressed: () => _updateQuantity(index, 1),
                              color: AppTheme.successGreen,
                            ),
                          ],
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '\$${item.subtotal.toStringAsFixed(2)}',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    Text('Discount', style: theme.textTheme.bodyLarge),
                    const Spacer(),
                    SizedBox(
                      width: 100,
                      child: TextField(
                        decoration: const InputDecoration(
                          prefixText: '\$',
                          isDense: true,
                        ),
                        keyboardType: TextInputType.number,
                        onChanged: (v) {
                          setState(() {
                            _discount = double.tryParse(v) ?? 0.0;
                          });
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Text('Payment', style: theme.textTheme.bodyLarge),
                    const Spacer(),
                    DropdownButton<String>(
                      value: _selectedPayment,
                      items: const [
                        DropdownMenuItem(value: 'cash', child: Text('Cash')),
                        DropdownMenuItem(
                            value: 'credit_card', child: Text('Credit Card')),
                        DropdownMenuItem(
                            value: 'debit_card', child: Text('Debit Card')),
                        DropdownMenuItem(value: 'pix', child: Text('PIX')),
                        DropdownMenuItem(value: 'other', child: Text('Other')),
                      ],
                      onChanged: (v) =>
                          setState(() => _selectedPayment = v ?? 'cash'),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Total', style: theme.textTheme.headlineMedium),
                    Text(
                      '\$${_total.toStringAsFixed(2)}',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        color: AppTheme.tealAccent,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CartItem {
  final Product product;
  int quantity;

  _CartItem({required this.product, this.quantity = 1});

  double get subtotal => product.price * quantity;
}
