import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'main.dart';

class LoadingScreen extends StatefulWidget {
  @override
  _LoadingScreenState createState() => _LoadingScreenState();
}

class _LoadingScreenState extends State<LoadingScreen> {
  String _statusMessage = "Initialisation du système...";
  double _progress = 0.0;
  bool _isServerReady = false;

  @override
  void initState() {
    super.initState();
    _startLoadingSequence();
  }

  void _updateStatus(String msg, double prog) {
    if (mounted) {
      setState(() {
        _statusMessage = msg;
        _progress = prog;
      });
    }
  }

  Future<void> _startLoadingSequence() async {
    await Future.delayed(Duration(seconds: 2));
    _updateStatus("Chargement du moteur spaCy (NLP)...", 0.2);

    await Future.delayed(Duration(seconds: 3));
    _updateStatus("Chargement de l'Ontologie Géométrique...", 0.4);

    _updateStatus("Réveil du serveur Whisper (IA)...", 0.6);

    int attempts = 0;
    while (!_isServerReady) {
      try {
        // Remplacer par 10.0.2.2 si émulateur Android, ou IP locale
        final response = await http
            .get(Uri.parse('http://127.0.0.1:8000/'))
            .timeout(Duration(seconds: 2));

        if (response.statusCode == 200) {
          _isServerReady = true;
        }
      } catch (e) {
        attempts++;
        if (attempts > 5)
          _updateStatus(
            "Le serveur prend un peu de temps (Whisper est lourd)...",
            0.7,
          );
        await Future.delayed(Duration(seconds: 2));
      }
    }

    _updateStatus("Système prêt !", 1.0);
    await Future.delayed(Duration(milliseconds: 500));
    _transitionToHome();
  }

  void _transitionToHome() {
    Navigator.pushReplacement(
      context,
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) => MainScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          var curve = Curves.easeInOutCubic;
          var fadeAnimation = Tween(
            begin: 0.0,
            end: 1.0,
          ).animate(CurvedAnimation(parent: animation, curve: curve));
          var scaleAnimation = Tween(
            begin: 0.8,
            end: 1.0,
          ).animate(CurvedAnimation(parent: animation, curve: curve));

          return FadeTransition(
            opacity: fadeAnimation,
            child: ScaleTransition(scale: scaleAnimation, child: child),
          );
        },
        transitionDuration: Duration(milliseconds: 800),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TweenAnimationBuilder(
              tween: Tween<double>(begin: 0, end: 1),
              duration: Duration(seconds: 2),
              builder: (context, double value, child) {
                return Opacity(
                  opacity: value,
                  child: Icon(
                    Icons.auto_awesome,
                    size: 80,
                    color: Colors.blueAccent,
                  ),
                );
              },
            ),
            SizedBox(height: 40),
            Text(
              "PictExpress",
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                letterSpacing: 2,
              ),
            ),
            SizedBox(height: 20),
            Container(
              width: 250,
              height: 6,
              child: LinearProgressIndicator(
                value: _progress,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blueAccent),
              ),
            ),
            SizedBox(height: 20),
            Text(
              _statusMessage,
              style: TextStyle(
                color: Colors.grey[600],
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
