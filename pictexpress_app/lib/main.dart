import 'package:flutter/material.dart';

import 'screens/teacher_screen.dart';
import 'screens/child_screen.dart';

// DESIGN: set at build time via --dart-define=SERVER_URL=http://192.168.x.x:8000
// Exported so TeacherScreen and ChildScreen can both reference it.
const String serverUrl = String.fromEnvironment(
  'SERVER_URL',
  defaultValue: 'http://127.0.0.1:8000',
);

void main() {
  runApp(const PictExpressApp());
}

class PictExpressApp extends StatelessWidget {
  const PictExpressApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PictExpress',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: const Color(0xFFF0F4F8),
        primarySwatch: Colors.blueGrey,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'PictExpress',
                style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.blueGrey),
              ),
              const SizedBox(height: 8),
              const Text(
                'Qui êtes-vous ?',
                style: TextStyle(fontSize: 20, color: Colors.black54),
              ),
              const SizedBox(height: 60),
              _RoleButton(
                label: "Je suis le maître",
                icon: Icons.school,
                color: Colors.blueAccent,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const TeacherScreen()),
                ),
              ),
              const SizedBox(height: 24),
              _RoleButton(
                label: "Je suis l'élève",
                icon: Icons.child_care,
                color: Colors.orange,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const ChildScreen()),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RoleButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _RoleButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 280,
      height: 90,
      child: ElevatedButton.icon(
        icon: Icon(icon, size: 36),
        label: Text(label, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          elevation: 4,
        ),
        onPressed: onTap,
      ),
    );
  }
}
