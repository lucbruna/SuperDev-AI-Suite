import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const SuperDevApp());
}

class SuperDevApp extends StatelessWidget {
  const SuperDevApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SuperDev',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
