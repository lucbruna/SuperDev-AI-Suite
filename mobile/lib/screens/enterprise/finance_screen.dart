import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../models/enterprise.dart';
import '../../providers/enterprise_provider.dart';
import '../../widgets/loading_widget.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/status_badge.dart';
import '../../widgets/chart_widget.dart';

class FinanceScreen extends StatefulWidget {
  const FinanceScreen({super.key});

  @override
  State<FinanceScreen> createState() => _FinanceScreenState();
}

class _FinanceScreenState extends State<FinanceScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<EnterpriseProvider>().loadInvoices();
      context.read<EnterpriseProvider>().loadCashFlow();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _showPaymentForm(Invoice invoice) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _PaymentFormWidget(invoice: invoice),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Column(
        children: [
          TabBar(
            controller: _tabController,
            tabs: [
              Tab(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.receipt, size: 18),
                    const SizedBox(width: 6),
                    Text('Invoices', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
              Tab(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.show_chart, size: 18),
                    const SizedBox(width: 6),
                    Text('Cash Flow', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _InvoicesView(onPay: _showPaymentForm),
                _CashFlowView(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InvoicesView extends StatelessWidget {
  final void Function(Invoice invoice) onPay;

  const _InvoicesView({required this.onPay});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    if (provider.isLoadingInvoices) {
      return const LoadingWidget(message: 'Loading invoices...');
    }

    if (provider.error != null) {
      return AppErrorWidget(
        message: provider.error!,
        onRetry: () => provider.loadInvoices(),
      );
    }

    if (provider.invoices.isEmpty) {
      return const EmptyStateWidget(
        message: 'No invoices',
        icon: Icons.receipt_outlined,
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadInvoices(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.invoices.length,
        itemBuilder: (context, index) {
          final invoice = provider.invoices[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Invoice #${invoice.invoiceNumber}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      StatusBadge(status: invoice.status),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (invoice.customerName != null)
                    Text(
                      'Customer: ${invoice.customerName}',
                      style: theme.textTheme.bodyMedium,
                    ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Issued: ${_formatDate(invoice.issueDate)}',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface.withOpacity(0.6),
                        ),
                      ),
                      Text(
                        '\$${invoice.amount.toStringAsFixed(2)}',
                        style: theme.textTheme.titleLarge?.copyWith(
                          color: AppTheme.tealAccent,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  if (invoice.status == 'pending' ||
                      invoice.status == 'overdue') ...[
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () => onPay(invoice),
                        icon: const Icon(Icons.payment, size: 18),
                        label: const Text('Register Payment'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.successGreen,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/'
        '${date.month.toString().padLeft(2, '0')}/'
        '${date.year}';
  }
}

class _CashFlowView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final provider = context.watch<EnterpriseProvider>();

    if (provider.cashFlow.isEmpty) {
      return SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            CashFlowChart(
              inflows: [0],
              outflows: [0],
              labels: ['No Data'],
            ),
          ],
        ),
      );
    }

    final inflows = provider.cashFlow.map((e) => e.inflow).toList();
    final outflows = provider.cashFlow.map((e) => e.outflow).toList();
    final labels = provider.cashFlow.map((e) {
      return '${e.date.month}/${e.date.day}';
    }).toList();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          CashFlowChart(
            inflows: inflows,
            outflows: outflows,
            labels: labels,
          ),
          const SizedBox(height: 24),
          _buildBalanceSummary(context),
        ],
      ),
    );
  }

  Widget _buildBalanceSummary(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    final totalInflow = provider.cashFlow.fold<double>(
        0.0, (sum, e) => sum + e.inflow);
    final totalOutflow = provider.cashFlow.fold<double>(
        0.0, (sum, e) => sum + e.outflow);
    final balance = totalInflow - totalOutflow;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Summary', style: theme.textTheme.titleLarge),
            const SizedBox(height: 12),
            _summaryRow(theme, 'Total Inflow', '\$${totalInflow.toStringAsFixed(2)}',
                AppTheme.successGreen),
            const SizedBox(height: 8),
            _summaryRow(theme, 'Total Outflow', '\$${totalOutflow.toStringAsFixed(2)}',
                AppTheme.errorRed),
            const Divider(height: 24),
            _summaryRow(
                theme,
                'Net Balance',
                '\$${balance.toStringAsFixed(2)}',
                balance >= 0 ? AppTheme.successGreen : AppTheme.errorRed),
          ],
        ),
      ),
    );
  }

  Widget _summaryRow(
      ThemeData theme, String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: theme.textTheme.bodyLarge),
        Text(
          value,
          style: theme.textTheme.titleMedium?.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

class _PaymentFormWidget extends StatefulWidget {
  final Invoice invoice;
  const _PaymentFormWidget({required this.invoice});

  @override
  State<_PaymentFormWidget> createState() => _PaymentFormWidgetState();
}

class _PaymentFormWidgetState extends State<_PaymentFormWidget> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _referenceController = TextEditingController();
  String _method = 'cash';

  @override
  void initState() {
    super.initState();
    _amountController.text = widget.invoice.amount.toStringAsFixed(2);
  }

  @override
  void dispose() {
    _amountController.dispose();
    _referenceController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    final data = {
      'invoice_id': widget.invoice.id,
      'amount': double.tryParse(_amountController.text) ?? 0.0,
      'method': _method,
      if (_referenceController.text.isNotEmpty)
        'reference': _referenceController.text.trim(),
    };
    context.read<EnterpriseProvider>().registerPayment(data);
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
                'Register Payment',
                style: theme.textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Invoice #${widget.invoice.invoiceNumber}',
                style: theme.textTheme.bodyLarge,
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _amountController,
                decoration: const InputDecoration(
                  labelText: 'Amount *',
                  prefixText: '\$',
                ),
                keyboardType: TextInputType.number,
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Required';
                  if (double.tryParse(v) == null || double.parse(v) <= 0) {
                    return 'Enter a valid amount';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _method,
                decoration: const InputDecoration(labelText: 'Payment Method'),
                items: const [
                  DropdownMenuItem(value: 'cash', child: Text('Cash')),
                  DropdownMenuItem(
                      value: 'credit_card', child: Text('Credit Card')),
                  DropdownMenuItem(
                      value: 'debit_card', child: Text('Debit Card')),
                  DropdownMenuItem(value: 'bank_transfer', child: Text('Bank Transfer')),
                  DropdownMenuItem(value: 'pix', child: Text('PIX')),
                ],
                onChanged: (v) => setState(() => _method = v ?? 'cash'),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _referenceController,
                decoration: const InputDecoration(labelText: 'Reference'),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submit,
                  child: const Text('Register Payment'),
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
