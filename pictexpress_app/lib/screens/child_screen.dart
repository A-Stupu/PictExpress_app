import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import '../main.dart' show serverUrl;

class ChildScreen extends StatefulWidget {
  const ChildScreen({Key? key}) : super(key: key);

  @override
  State<ChildScreen> createState() => _ChildScreenState();
}

class _ChildScreenState extends State<ChildScreen> {
  bool _loading = true;
  String? _error;

  // Groups returned by GET /needs
  List<Map<String, dynamic>> _physical = [];
  List<Map<String, dynamic>> _mental = [];
  List<Map<String, dynamic>> _helpValidation = [];

  @override
  void initState() {
    super.initState();
    _loadNeeds();
  }

  Future<void> _loadNeeds() async {
    try {
      final resp = await http
          .get(Uri.parse('$serverUrl/needs'))
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        setState(() {
          _physical       = _parseGroup(data['physical']);
          _mental         = _parseGroup(data['mental']);
          _helpValidation = _parseGroup(data['help_validation']);
          _loading = false;
        });
      } else {
        setState(() { _error = 'Erreur ${resp.statusCode}'; _loading = false; });
      }
    } catch (e) {
      setState(() { _error = 'Impossible de charger les pictogrammes'; _loading = false; });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Impossible de charger les pictogrammes')),
        );
      }
    }
  }

  List<Map<String, dynamic>> _parseGroup(dynamic raw) {
    if (raw == null) return [];
    return List<Map<String, dynamic>>.from(
        (raw as List).map((e) => Map<String, dynamic>.from(e)));
  }

  void _showPictogramDialog(Map<String, dynamic> item) {
    final aid = item['arasaac_id'];
    final label = item['label_fr'] ?? item['class_name'];
    final url = '$serverUrl/pictogrammes/$aid.png';

    showDialog(
      context: context,
      builder: (_) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Image.network(
                url,
                width: 220,
                height: 220,
                fit: BoxFit.contain,
                errorBuilder: (_, __, ___) =>
                    const Icon(Icons.broken_image, size: 120, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              Text(
                label,
                style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                ),
                child: const Text('Fermer', style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPictoCard(Map<String, dynamic> item) {
    final aid = item['arasaac_id'];
    final label = item['label_fr'] ?? item['class_name'];
    final url = '$serverUrl/pictogrammes/$aid.png';

    return GestureDetector(
      onTap: () => _showPictogramDialog(item),
      child: Card(
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: Image.network(
                  url,
                  fit: BoxFit.contain,
                  loadingBuilder: (_, child, progress) =>
                      progress == null ? child : const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                  errorBuilder: (_, __, ___) =>
                      const Icon(Icons.broken_image, size: 50, color: Colors.grey),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(String title, Color color, List<Map<String, dynamic>> items) {
    if (items.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 16, 12, 8),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: color.withOpacity(0.4)),
            ),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color.withOpacity(0.9),
              ),
            ),
          ),
        ),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 8),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            childAspectRatio: 0.85,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
          ),
          itemCount: items.length,
          itemBuilder: (_, i) => _buildPictoCard(items[i]),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Je communique'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 1,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null && _physical.isEmpty && _mental.isEmpty && _helpValidation.isEmpty
              ? Center(
                  child: Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 16)))
              : SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildSection("J'ai besoin de...", Colors.orange, _physical),
                      _buildSection("Je me sens...", Colors.purple, _mental),
                      _buildSection("Pour le travail", Colors.teal, _helpValidation),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
    );
  }
}
