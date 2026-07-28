import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Account', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Colors.grey)),
          const SizedBox(height: 8),
          ListTile(title: const Text('Profile'), leading: const Icon(Icons.person), onTap: () {}),
          ListTile(title: const Text('Notifications'), leading: const Icon(Icons.notifications), trailing: Switch(value: true, onChanged: (_) {}), onTap: () {}),
          const Divider(),
          const Text('AI Providers', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Colors.grey)),
          const SizedBox(height: 8),
          ListTile(title: const Text('OpenAI'), subtitle: const Text('Connected'), leading: const Icon(Icons.cloud), trailing: const Icon(Icons.check_circle, color: Colors.green)),
          ListTile(title: const Text('Anthropic'), subtitle: const Text('Not connected'), leading: const Icon(Icons.cloud_outlined), onTap: () {}),
          const Divider(),
          const Text('About', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Colors.grey)),
          const SizedBox(height: 8),
          ListTile(title: const Text('Version'), subtitle: const Text('1.0.0'), leading: const Icon(Icons.info)),
        ],
      ),
    );
  }
}