import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final stats = [
      {'label': 'Active Agents', 'value': '3', 'icon': Icons.smart_toy, 'color': Colors.indigo},
      {'label': 'Workflows', 'value': '12', 'icon': Icons.account_tree, 'color': Colors.teal},
      {'label': 'Executions', 'value': '147', 'icon': Icons.play_circle, 'color': Colors.orange},
      {'label': 'Cost (MTD)', 'value': '\$42.50', 'icon': Icons.attach_money, 'color': Colors.green},
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('SuperDev'), actions: [
        IconButton(icon: const Icon(Icons.notifications_outlined), onPressed: () {}),
      ]),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Welcome back!', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text('All systems operational', style: TextStyle(color: Colors.grey.shade600)),
          const SizedBox(height: 20),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: 1.5, crossAxisSpacing: 12, mainAxisSpacing: 12),
            itemCount: stats.length,
            itemBuilder: (context, index) {
              final s = stats[index];
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Icon(s['icon'] as IconData, color: s['color'] as Color, size: 28),
                      Text(s['value'] as String, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                      Text(s['label'] as String, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                    ],
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 20),
          Text('Recent Activity', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                ListTile(leading: const Icon(Icons.check_circle, color: Colors.green), title: const Text('CI/CD Pipeline completed'), subtitle: Text('2 min ago', style: TextStyle(fontSize: 12, color: Colors.grey.shade600))),
                const Divider(height: 1),
                ListTile(leading: const Icon(Icons.play_circle, color: Colors.blue), title: const Text('Code Review started'), subtitle: Text('15 min ago', style: TextStyle(fontSize: 12, color: Colors.grey.shade600))),
                const Divider(height: 1),
                ListTile(leading: const Icon(Icons.error, color: Colors.red), title: const Text('Data Pipeline failed'), subtitle: Text('1 hour ago', style: TextStyle(fontSize: 12, color: Colors.grey.shade600))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}