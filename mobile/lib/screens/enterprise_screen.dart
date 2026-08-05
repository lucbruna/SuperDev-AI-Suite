import 'package:flutter/material.dart';
import 'enterprise/erp_screen.dart';
import 'enterprise/crm_screen.dart';
import 'enterprise/pdv_screen.dart';
import 'enterprise/inventory_screen.dart';
import 'enterprise/finance_screen.dart';

class EnterpriseScreen extends StatelessWidget {
  const EnterpriseScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return DefaultTabController(
      length: 5,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Enterprise Suite'),
          bottom: TabBar(
            isScrollable: true,
            tabs: [
              Tab(
                child: Row(
                  children: [
                    const Icon(Icons.inventory_2, size: 18),
                    const SizedBox(width: 6),
                    Text('ERP', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
              Tab(
                child: Row(
                  children: [
                    const Icon(Icons.people, size: 18),
                    const SizedBox(width: 6),
                    Text('CRM', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
              Tab(
                child: Row(
                  children: [
                    const Icon(Icons.point_of_sale, size: 18),
                    const SizedBox(width: 6),
                    Text('PDV', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
              Tab(
                child: Row(
                  children: [
                    const Icon(Icons.inventory, size: 18),
                    const SizedBox(width: 6),
                    Text('Inventory', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
              Tab(
                child: Row(
                  children: [
                    const Icon(Icons.account_balance, size: 18),
                    const SizedBox(width: 6),
                    Text('Finance', style: theme.textTheme.labelLarge),
                  ],
                ),
              ),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            ErpScreen(),
            CrmScreen(),
            PdvScreen(),
            InventoryScreen(),
            FinanceScreen(),
          ],
        ),
      ),
    );
  }
}
