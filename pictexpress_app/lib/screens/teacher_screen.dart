import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import '../main.dart' show serverUrl;

class TeacherScreen extends StatefulWidget {
  const TeacherScreen({Key? key}) : super(key: key);

  @override
  State<TeacherScreen> createState() => _TeacherScreenState();
}

class _TeacherScreenState extends State<TeacherScreen> {
  bool _isRecording = false;
  List<String> _pictogrammes = [];
  String _texteCompris = "";

  final AudioRecorder _audioRecorder = AudioRecorder();

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
      });
      if (path != null) {
        await _envoyerAudioAuServeur(path);
      }
    } else {
      if (await _audioRecorder.hasPermission()) {
        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.pcm16bits),
          path: 'enregistrement.wav',
        );
        setState(() {
          _isRecording = true;
          _pictogrammes = [];
          _texteCompris = "";
        });
      }
    }
  }

  Future<void> _envoyerAudioAuServeur(String audioPath) async {
    var uri = Uri.parse('$serverUrl/api/transcrire');
    var request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('file', audioPath));

    try {
      var response = await request.send();
      if (response.statusCode == 200) {
        var responseData = await response.stream.bytesToString();
        var json = jsonDecode(responseData);
        setState(() {
          _pictogrammes = List<String>.from(json['pictogrammes']);
          _texteCompris = json['texte_compris'];
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur serveur : $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PictExpress — Enseignant'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 1,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              icon: const Icon(Icons.help_outline, size: 32, color: Colors.blueGrey),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const HelpScreen()),
              ),
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (_texteCompris.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  'Entendu : "$_texteCompris"',
                  style: const TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
                ),
              ),
            Container(
              height: 200,
              alignment: Alignment.center,
              child: _pictogrammes.isEmpty
                  ? Text(
                      _isRecording ? 'Écoute en cours...' : 'Appuyez pour parler',
                      style: const TextStyle(fontSize: 24, color: Colors.black54),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: _pictogrammes
                          .map((nomFichier) => Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 10.0),
                                child: Image.network(
                                  '$serverUrl/pictogrammes/$nomFichier',
                                  width: 120,
                                  height: 120,
                                  fit: BoxFit.contain,
                                  errorBuilder: (_, __, ___) =>
                                      const Icon(Icons.broken_image, size: 80, color: Colors.grey),
                                ),
                              ))
                          .toList(),
                    ),
            ),
            const SizedBox(height: 50),
            GestureDetector(
              onTap: _toggleRecording,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: _isRecording ? Colors.redAccent : Colors.blueAccent,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black26,
                      blurRadius: _isRecording ? 20 : 10,
                      spreadRadius: _isRecording ? 5 : 2,
                    ),
                  ],
                ),
                child: const Icon(Icons.mic, color: Colors.white, size: 60),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// HelpScreen kept here as it belongs to the teacher flow
class HelpScreen extends StatelessWidget {
  const HelpScreen({Key? key}) : super(key: key);

  Widget _buildNeedButton(BuildContext context, String text, IconData icon, Color bgColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 20.0),
      child: SizedBox(
        width: double.infinity,
        height: 100,
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: bgColor,
            foregroundColor: Colors.black87,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          ),
          onPressed: () => ScaffoldMessenger.of(context)
              .showSnackBar(SnackBar(content: Text('Demande : $text'))),
          child: Row(
            children: [
              Icon(icon, size: 44),
              const SizedBox(width: 20),
              Expanded(
                child: Text(text,
                    style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w600)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mes besoins'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildNeedButton(context, 'Répéter', Icons.replay, Colors.lightBlue.shade100),
              _buildNeedButton(context, 'Faire une pause', Icons.pause_circle_outline, Colors.orange.shade100),
              _buildNeedButton(context, 'Je me sens mal', Icons.sentiment_dissatisfied, Colors.red.shade100),
            ],
          ),
        ),
      ),
    );
  }
}
