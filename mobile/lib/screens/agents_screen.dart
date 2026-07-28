import 'package:flutter/material.dart';

class AgentsScreen extends StatelessWidget {
  const AgentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final agents = [
      {'name': 'Architect Agent', 'type': 'architect', 'status': 'idle', 'icon': Icons.architecture},
      {'name': 'Executor Agent', 'type': 'executor', 'status': 'running', 'icon': Icons.play_circle},
      {'name': 'Reviewer Agent', 'type': 'reviewer', 'status': 'idle', 'icon': Icons.rate_review},
      {'name': 'Testing Agent', 'type': 'testing', 'status': 'idle', 'icon': Icons.science},
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Agents'), actions: [IconButton(icon: const Icon(Icons.add), onPressed: () {})]),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: agents.length,
        itemBuilder: (context, index) {
          final a = agents[index];
          final isRunning = a['status'] == 'running';
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(child: Icon(a['icon'] as IconData)),
              title: Text(a['name'] as String, style: const TextStyle(fontWeight: FontWeight.w600)),
              subtitle: Text('${a['type']} \u2022 ${a['status']}'),
              trailing: isRunning
                  ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.play_arrow),
              onTap: () {},
            ),
          );
        },
      ),
    );
  }
}