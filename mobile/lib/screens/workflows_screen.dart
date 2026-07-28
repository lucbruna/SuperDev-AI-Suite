import 'package:flutter/material.dart';

class WorkflowsScreen extends StatelessWidget {
  const WorkflowsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final workflows = [
      {'name': 'CI/CD Pipeline', 'status': 'running', 'steps': 3, 'done': 2},
      {'name': 'Code Review', 'status': 'idle', 'steps': 4, 'done': 0},
      {'name': 'Data Pipeline', 'status': 'failed', 'steps': 3, 'done': 1},
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Workflows'), actions: [IconButton(icon: const Icon(Icons.add), onPressed: () {})]),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: workflows.length,
        itemBuilder: (context, index) {
          final w = workflows[index];
          final isRunning = w['status'] == 'running';
          final isFailed = w['status'] == 'failed';
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
                      Text(w['name'] as String, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                      Chip(
                        label: Text(w['status'] as String, style: const TextStyle(fontSize: 12)),
                        backgroundColor: isRunning ? Colors.green.shade100 : isFailed ? Colors.red.shade100 : Colors.grey.shade200,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  LinearProgressIndicator(
                    value: (w['done'] as int) / (w['steps'] as int),
                    backgroundColor: Colors.grey.shade200,
                    color: isFailed ? Colors.red : Colors.green,
                  ),
                  const SizedBox(height: 4),
                  Text('${w['done']}/${w['steps']} steps completed', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}