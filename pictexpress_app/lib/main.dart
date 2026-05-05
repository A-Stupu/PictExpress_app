import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

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
      home: const MainScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({Key? key}) : super(key: key);

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  bool _isRecording = false;
  List<String> _pictogrammes = [];
  String _texteCompris = "";

  // Outil d'enregistrement natif
  final AudioRecorder _audioRecorder = AudioRecorder();

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      // 1. ARRÊT DE L'ENREGISTREMENT
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
      });

      if (path != null) {
        await _envoyerAudioAuServeur(path);
      }
    } else {
      // 2. DÉMARRAGE DE L'ENREGISTREMENT
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

  // Fonction magique qui envoie l'audio à Python
  Future<void> _envoyerAudioAuServeur(String audioPath) async {
    // L'adresse locale de votre ordinateur
    var uri = Uri.parse('http://127.0.0.1:8000/api/transcrire');

    var request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('file', audioPath));

    try {
      var response = await request.send();
      if (response.statusCode == 200) {
        var responseData = await response.stream.bytesToString();
        var json = jsonDecode(responseData);

        setState(() {
          // On récupère la liste des pictos renvoyée par Python
          _pictogrammes = List<String>.from(json['pictogrammes']);
          _texteCompris = json['texte_compris'];
        });
      }
    } catch (e) {
      print("Erreur de connexion avec le serveur : $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PictExpress'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 1,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              icon: const Icon(
                Icons.help_outline,
                size: 32,
                color: Colors.blueGrey,
              ),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const HelpScreen()),
                );
              },
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Affichage du texte compris par Whisper
            if (_texteCompris.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  'Entendu : "$_texteCompris"',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),

            // Affichage des Pictogrammes
            Container(
              height: 200,
              alignment: Alignment.center,
              child: _pictogrammes.isEmpty
                  ? Text(
                      _isRecording
                          ? 'Écoute en cours...'
                          : 'Appuyez pour parler',
                      style: const TextStyle(
                        fontSize: 24,
                        color: Colors.black54,
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: _pictogrammes
                          .map(
                            (nomFichier) => Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10.0,
                              ),
                              child: Image.network(
                                // On va chercher l'image sur notre serveur Python !
                                'http://127.0.0.1:8000/pictogrammes/$nomFichier',
                                width:
                                    120, // Taille de l'image (plus lisible pour l'enfant)
                                height: 120,
                                fit: BoxFit.contain,
                                // Petite sécurité : si l'image manque, on affiche une icône d'erreur grise
                                errorBuilder: (context, error, stackTrace) =>
                                    const Icon(
                                      Icons.broken_image,
                                      size: 80,
                                      color: Colors.grey,
                                    ),
                              ),
                            ),
                          )
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

class HelpScreen extends StatelessWidget {
  const HelpScreen({Key? key}) : super(key: key);

  Widget _buildNeedButton(
    BuildContext context,
    String text,
    String emoji,
    Color bgColor,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 20.0),
      child: SizedBox(
        width: double.infinity,
        height: 100,
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: bgColor,
            foregroundColor: Colors.black87,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
          ),
          onPressed: () {
            ScaffoldMessenger.of(
              context,
            ).showSnackBar(SnackBar(content: Text('Demande : $text')));
          },
          child: Row(
            children: [
              Text(emoji, style: const TextStyle(fontSize: 50)),
              const SizedBox(width: 20),
              Expanded(
                child: Text(
                  text,
                  style: const TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w600,
                  ),
                ),
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
              _buildNeedButton(
                context,
                'Répéter',
                '🔁',
                Colors.lightBlue.shade100,
              ),
              _buildNeedButton(
                context,
                'Faire une pause',
                '⏸️',
                Colors.orange.shade100,
              ),
              _buildNeedButton(
                context,
                'Je me sens mal',
                '🤕',
                Colors.red.shade100,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
