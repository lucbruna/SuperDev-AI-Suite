import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../models/enterprise.dart';
import '../../providers/enterprise_provider.dart';
import '../../widgets/loading_widget.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/status_badge.dart';

class ErpScreen extends StatefulWidget {
  const ErpScreen({super.key});

  @override
  State<ErpScreen> createState() => _ErpScreenState();
}

class _ErpScreenState extends State<ErpScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<EnterpriseProvider>().loadProducts();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearch(String query) {
    context.read<EnterpriseProvider>().loadProducts(search: query);
  }

  void _showProductForm({Product? product}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _ProductFormWidget(product: product),
    );
  }

  void _showProductDetail(Product product) {
    showDialog(
      context: context,
      builder: (ctx) => _ProductDetailDialog(product: product),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search products...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _onSearch('');
                        },
                      )
                    : null,
              ),
              onChanged: _onSearch,
            ),
          ),
          Expanded(
            child: _buildContent(theme, provider),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showProductForm(),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildContent(ThemeData theme, EnterpriseProvider provider) {
    if (provider.isLoadingProducts) {
      return const LoadingWidget(message: 'Loading products...');
    }

    if (provider.error != null) {
      return AppErrorWidget(
        message: provider.error!,
        onRetry: () => provider.loadProducts(),
      );
    }

    if (provider.products.isEmpty) {
      return const EmptyStateWidget(
        message: 'No products found',
        icon: Icons.inventory_2_outlined,
        actionLabel: 'Add Product',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadProducts(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: provider.products.length,
        itemBuilder: (context, index) {
          final product = provider.products[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => _showProductDetail(product),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        color: AppTheme.tealAccent.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(
                          product.name.isNotEmpty
                              ? product.name[0].toUpperCase()
                              : '?',
                          style: theme.textTheme.headlineMedium?.copyWith(
                            color: AppTheme.tealAccent,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            product.name,
                            style: theme.textTheme.titleMedium,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            product.sku != null
                                ? 'SKU: ${product.sku}'
                                : product.category ?? 'No category',
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
                          '\$${product.price.toStringAsFixed(2)}',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: AppTheme.tealAccent,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Stock: ${product.stockQuantity}',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: product.stockQuantity < 10
                                ? AppTheme.errorRed
                                : theme.colorScheme.onSurface
                                    .withOpacity(0.6),
                          ),
                        ),
                      ],
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
}

class _ProductDetailDialog extends StatelessWidget {
  final Product product;
  const _ProductDetailDialog({required this.product});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppTheme.tealAccent.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      product.name.isNotEmpty
                          ? product.name[0].toUpperCase()
                          : '?',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        color: AppTheme.tealAccent,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(product.name, style: theme.textTheme.titleLarge),
                      if (product.sku != null)
                        Text('SKU: ${product.sku}',
                            style: theme.textTheme.bodyMedium),
                    ],
                  ),
                ),
                StatusBadge(
                    status: product.isActive ? 'Active' : 'Inactive'),
              ],
            ),
            const Divider(height: 32),
            _detailRow(theme, 'Price',
                '\$${product.price.toStringAsFixed(2)}'),
            if (product.costPrice != null)
              _detailRow(theme, 'Cost Price',
                  '\$${product.costPrice!.toStringAsFixed(2)}'),
            _detailRow(theme, 'Stock', '${product.stockQuantity} units'),
            if (product.category != null)
              _detailRow(theme, 'Category', product.category!),
            if (product.description != null &&
                product.description!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  product.description!,
                  style: theme.textTheme.bodyMedium,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _detailRow(ThemeData theme, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: theme.textTheme.bodyMedium),
          Text(value,
              style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _ProductFormWidget extends StatefulWidget {
  final Product? product;
  const _ProductFormWidget({this.product});

  @override
  State<_ProductFormWidget> createState() => _ProductFormWidgetState();
}

class _ProductFormWidgetState extends State<_ProductFormWidget> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _skuController;
  late final TextEditingController _priceController;
  late final TextEditingController _costPriceController;
  late final TextEditingController _stockController;
  late final TextEditingController _categoryController;
  late final TextEditingController _descriptionController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.product?.name ?? '');
    _skuController = TextEditingController(text: widget.product?.sku ?? '');
    _priceController = TextEditingController(
        text: widget.product?.price.toString() ?? '');
    _costPriceController = TextEditingController(
        text: widget.product?.costPrice?.toString() ?? '');
    _stockController = TextEditingController(
        text: widget.product?.stockQuantity.toString() ?? '0');
    _categoryController =
        TextEditingController(text: widget.product?.category ?? '');
    _descriptionController =
        TextEditingController(text: widget.product?.description ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _skuController.dispose();
    _priceController.dispose();
    _costPriceController.dispose();
    _stockController.dispose();
    _categoryController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    final data = {
      'name': _nameController.text.trim(),
      if (_skuController.text.isNotEmpty) 'sku': _skuController.text.trim(),
      'price': double.tryParse(_priceController.text) ?? 0.0,
      if (_costPriceController.text.isNotEmpty)
        'cost_price': double.tryParse(_costPriceController.text),
      'stock_quantity': int.tryParse(_stockController.text) ?? 0,
      if (_categoryController.text.isNotEmpty)
        'category': _categoryController.text.trim(),
      if (_descriptionController.text.isNotEmpty)
        'description': _descriptionController.text.trim(),
    };

    final provider = context.read<EnterpriseProvider>();
    if (widget.product != null) {
      provider.updateProduct(widget.product!.id, data);
    } else {
      provider.createProduct(data);
    }
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
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
              Text(
                widget.product != null ? 'Edit Product' : 'New Product',
                style: theme.textTheme.headlineMedium,
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Product Name *'),
                validator: (v) =>
                    v == null || v.trim().isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _skuController,
                      decoration: const InputDecoration(labelText: 'SKU'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _priceController,
                      decoration: const InputDecoration(
                        labelText: 'Price *',
                        prefixText: '\$',
                      ),
                      keyboardType: TextInputType.number,
                      validator: (v) =>
                          v == null || v.isEmpty ? 'Required' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _costPriceController,
                      decoration: const InputDecoration(
                        labelText: 'Cost Price',
                        prefixText: '\$',
                      ),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _stockController,
                      decoration:
                          const InputDecoration(labelText: 'Stock Quantity'),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _categoryController,
                decoration: const InputDecoration(labelText: 'Category'),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Description'),
                maxLines: 3,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submit,
                  child: Text(widget.product != null
                      ? 'Update Product'
                      : 'Create Product'),
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
