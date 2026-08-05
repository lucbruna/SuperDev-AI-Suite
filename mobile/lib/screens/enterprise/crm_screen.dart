import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../models/enterprise.dart';
import '../../providers/enterprise_provider.dart';
import '../../widgets/loading_widget.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/status_badge.dart';

class CrmScreen extends StatefulWidget {
  const CrmScreen({super.key});

  @override
  State<CrmScreen> createState() => _CrmScreenState();
}

class _CrmScreenState extends State<CrmScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<EnterpriseProvider>().loadLeads();
      context.read<EnterpriseProvider>().loadPipeline();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _showLeadForm() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _LeadFormWidget(),
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
                    const Icon(Icons.timeline, size: 18),
                    const SizedBox(width: 6),
                    Text('Pipeline', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
              Tab(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.people, size: 18),
                    const SizedBox(width: 6),
                    Text('Leads', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _PipelineView(),
                _LeadsView(),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showLeadForm,
        child: const Icon(Icons.add),
      ),
    );
  }
}

class _PipelineView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    if (provider.isLoadingPipeline) {
      return const LoadingWidget(message: 'Loading pipeline...');
    }

    if (provider.pipeline.isEmpty) {
      return const EmptyStateWidget(
        message: 'No pipeline data',
        icon: Icons.timeline,
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.pipeline.length,
      itemBuilder: (context, index) {
        final stage = provider.pipeline[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: _stageColor(index),
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          stage.name,
                          style: theme.textTheme.titleLarge,
                        ),
                      ],
                    ),
                    Text(
                      '\$${stage.totalValue.toStringAsFixed(0)}',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: AppTheme.tealAccent,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ...stage.opportunities.map((opp) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              opp.title,
                              style: theme.textTheme.bodyMedium,
                            ),
                          ),
                          if (opp.value != null)
                            Text(
                              '\$${opp.value!.toStringAsFixed(0)}',
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _stageColor(int index) {
    const colors = [
      AppTheme.infoBlue,
      AppTheme.warningAmber,
      AppTheme.tealAccent,
      AppTheme.successGreen,
      AppTheme.primaryLight,
    ];
    return colors[index % colors.length];
  }
}

class _LeadsView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<EnterpriseProvider>();

    if (provider.isLoadingLeads) {
      return const LoadingWidget(message: 'Loading leads...');
    }

    if (provider.error != null) {
      return AppErrorWidget(
        message: provider.error!,
        onRetry: () => provider.loadLeads(),
      );
    }

    if (provider.leads.isEmpty) {
      return const EmptyStateWidget(
        message: 'No leads yet',
        icon: Icons.people_outline,
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadLeads(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.leads.length,
        itemBuilder: (context, index) {
          final lead = provider.leads[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => _showLeadDetail(context, lead),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppTheme.infoBlue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(
                          lead.name.isNotEmpty
                              ? lead.name[0].toUpperCase()
                              : '?',
                          style: theme.textTheme.headlineMedium?.copyWith(
                            color: AppTheme.infoBlue,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(lead.name, style: theme.textTheme.titleMedium),
                          if (lead.company != null)
                            Text(
                              lead.company!,
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
                        StatusBadge(status: lead.status),
                        if (lead.estimatedValue != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            '\$${lead.estimatedValue!.toStringAsFixed(0)}',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AppTheme.tealAccent,
                            ),
                          ),
                        ],
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

  void _showLeadDetail(BuildContext context, Lead lead) {
    final theme = Theme.of(context);
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(lead.name, style: theme.textTheme.titleLarge),
                  ),
                  StatusBadge(status: lead.status),
                ],
              ),
              const Divider(height: 24),
              if (lead.email != null)
                _detailRow(theme, Icons.email, lead.email!),
              if (lead.phone != null)
                _detailRow(theme, Icons.phone, lead.phone!),
              if (lead.company != null)
                _detailRow(theme, Icons.business, lead.company!),
              if (lead.source != null)
                _detailRow(theme, Icons.source, lead.source!),
              if (lead.estimatedValue != null)
                _detailRow(theme, Icons.attach_money,
                    '\$${lead.estimatedValue!.toStringAsFixed(2)}'),
              if (lead.notes != null && lead.notes!.isNotEmpty) ...[
                const SizedBox(height: 12),
                Text('Notes', style: theme.textTheme.titleMedium),
                const SizedBox(height: 4),
                Text(lead.notes!, style: theme.textTheme.bodyMedium),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _detailRow(ThemeData theme, IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 18, color: theme.colorScheme.onSurface.withOpacity(0.6)),
          const SizedBox(width: 8),
          Text(text, style: theme.textTheme.bodyMedium),
        ],
      ),
    );
  }
}

class _LeadFormWidget extends StatefulWidget {
  @override
  State<_LeadFormWidget> createState() => _LeadFormWidgetState();
}

class _LeadFormWidgetState extends State<_LeadFormWidget> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _companyController = TextEditingController();
  final _valueController = TextEditingController();
  final _notesController = TextEditingController();
  String _source = 'website';
  String _status = 'new';

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _companyController.dispose();
    _valueController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    final data = {
      'name': _nameController.text.trim(),
      if (_emailController.text.isNotEmpty)
        'email': _emailController.text.trim(),
      if (_phoneController.text.isNotEmpty)
        'phone': _phoneController.text.trim(),
      if (_companyController.text.isNotEmpty)
        'company': _companyController.text.trim(),
      'source': _source,
      'status': _status,
      if (_valueController.text.isNotEmpty)
        'estimated_value': double.tryParse(_valueController.text),
      if (_notesController.text.isNotEmpty)
        'notes': _notesController.text.trim(),
    };
    context.read<EnterpriseProvider>().createLead(data);
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
              Text('New Lead', style: theme.textTheme.headlineMedium),
              const SizedBox(height: 24),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Name *'),
                validator: (v) =>
                    v == null || v.trim().isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(labelText: 'Email'),
                      keyboardType: TextInputType.emailAddress,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _phoneController,
                      decoration: const InputDecoration(labelText: 'Phone'),
                      keyboardType: TextInputType.phone,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _companyController,
                decoration: const InputDecoration(labelText: 'Company'),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _source,
                      decoration: const InputDecoration(labelText: 'Source'),
                      items: const [
                        DropdownMenuItem(value: 'website', child: Text('Website')),
                        DropdownMenuItem(value: 'referral', child: Text('Referral')),
                        DropdownMenuItem(value: 'social', child: Text('Social Media')),
                        DropdownMenuItem(value: 'email', child: Text('Email')),
                        DropdownMenuItem(value: 'phone', child: Text('Phone')),
                        DropdownMenuItem(value: 'other', child: Text('Other')),
                      ],
                      onChanged: (v) => setState(() => _source = v ?? 'website'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _status,
                      decoration: const InputDecoration(labelText: 'Status'),
                      items: const [
                        DropdownMenuItem(value: 'new', child: Text('New')),
                        DropdownMenuItem(
                            value: 'contacted', child: Text('Contacted')),
                        DropdownMenuItem(
                            value: 'qualified', child: Text('Qualified')),
                        DropdownMenuItem(value: 'lost', child: Text('Lost')),
                      ],
                      onChanged: (v) => setState(() => _status = v ?? 'new'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _valueController,
                decoration: const InputDecoration(
                  labelText: 'Estimated Value',
                  prefixText: '\$',
                ),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _notesController,
                decoration: const InputDecoration(labelText: 'Notes'),
                maxLines: 3,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submit,
                  child: const Text('Create Lead'),
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
