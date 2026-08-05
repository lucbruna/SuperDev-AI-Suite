import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../providers/enterprise_provider.dart';
import '../widgets/status_badge.dart';
import 'enterprise_screen.dart';
import 'ai_assistant_screen.dart';
import 'scanner_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    _DashboardTab(),
    EnterpriseScreen(),
    AiAssistantScreen(),
    ScannerScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.business_outlined),
            activeIcon: Icon(Icons.business),
            label: 'Enterprise',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.smart_toy_outlined),
            activeIcon: Icon(Icons.smart_toy),
            label: 'AI',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.qr_code_scanner_outlined),
            activeIcon: Icon(Icons.qr_code_scanner),
            label: 'Scanner',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatefulWidget {
  const _DashboardTab();

  @override
  State<_DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<_DashboardTab> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<EnterpriseProvider>().loadSaleOrders();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authProvider = context.watch<AuthProvider>();
    final enterpriseProvider = context.watch<EnterpriseProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome, ${authProvider.user?.fullName ?? authProvider.user?.username ?? 'User'}',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            Text(
              'SuperDev AI Suite v5.0',
              style: TextStyle(
                fontSize: 12,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => enterpriseProvider.refreshAll(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => enterpriseProvider.refreshAll(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildStatsRow(theme, enterpriseProvider),
              const SizedBox(height: 24),
              Text(
                'Quick Actions',
                style: theme.textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              _buildQuickActions(theme),
              const SizedBox(height: 24),
              Text(
                'Recent Activity',
                style: theme.textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              _buildRecentActivity(theme, enterpriseProvider),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatsRow(ThemeData theme, EnterpriseProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            title: 'Sales',
            value: '\$${provider.saleOrders.fold<double>(0.0, (sum, order) => sum + order.totalAmount).toStringAsFixed(0)}',
            icon: Icons.trending_up,
            color: AppTheme.successGreen,
            theme: theme,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatCard(
            title: 'Leads',
            value: '${provider.leads.length}',
            icon: Icons.people_outline,
            color: AppTheme.infoBlue,
            theme: theme,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActions(ThemeData theme) {
    final actions = [
      _ActionItem(
        icon: Icons.add_shopping_cart,
        label: 'New Sale',
        color: AppTheme.successGreen,
        onTap: () {},
      ),
      _ActionItem(
        icon: Icons.person_add,
        label: 'Add Lead',
        color: AppTheme.infoBlue,
        onTap: () {},
      ),
      _ActionItem(
        icon: Icons.qr_code_scanner,
        label: 'Scan',
        color: AppTheme.warningAmber,
        onTap: () {},
      ),
      _ActionItem(
        icon: Icons.inventory,
        label: 'Stock',
        color: AppTheme.tealAccent,
        onTap: () {},
      ),
      _ActionItem(
        icon: Icons.description,
        label: 'Invoice',
        color: AppTheme.primaryLight,
        onTap: () {},
      ),
      _ActionItem(
        icon: Icons.smart_toy,
        label: 'AI Chat',
        color: AppTheme.tealLight,
        onTap: () {},
      ),
    ];

    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: actions.map((action) {
        return SizedBox(
          width: (MediaQuery.of(context).size.width - 44) / 3,
          child: Card(
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: action.onTap,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: action.color.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(action.icon, color: action.color, size: 24),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      action.label,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildRecentActivity(
      ThemeData theme, EnterpriseProvider provider) {
    final orders = provider.saleOrders.take(5).toList();
    if (orders.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Center(
            child: Text(
              'No recent activity',
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.5),
              ),
            ),
          ),
        ),
      );
    }

    return Column(
      children: orders.map((order) {
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: order.status == 'completed'
                    ? AppTheme.successGreen.withOpacity(0.15)
                    : AppTheme.warningAmber.withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                order.status == 'completed'
                    ? Icons.check_circle
                    : Icons.pending,
                color: order.status == 'completed'
                    ? AppTheme.successGreen
                    : AppTheme.warningAmber,
              ),
            ),
            title: Text(
              'Order #${order.orderNumber}',
              style: theme.textTheme.titleMedium,
            ),
            subtitle: Text(
              order.customerName ?? 'Walk-in Customer',
              style: theme.textTheme.bodyMedium,
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '\$${order.totalAmount.toStringAsFixed(2)}',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                StatusBadge(status: order.status),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final ThemeData theme;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
                const Spacer(),
                Icon(
                  Icons.arrow_upward,
                  color: AppTheme.successGreen,
                  size: 16,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActionItem {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback? onTap;

  _ActionItem({
    required this.icon,
    required this.label,
    required this.color,
    this.onTap,
  });
}
