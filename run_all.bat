@echo off
title PictExpress - Windows Launcher
chcp 65001 > nul


cd /d "%~dp0"

echo 🚀 LANCEMENT DU SYSTÈME...


echo 🐍 Démarrage du serveur FastAPI en arrière-plan...
start "PictExpress Server" /d "%~dp0" cmd /k "chcp 65001 > nul && call environnement_scolaire\Scripts\activate && uvicorn serveur_api:app --reload"
:: remplacer 'environnement_scolaire' par votre nom de variable d'environnement

echo 🖥️ Préparation de l'interface Flutter...
cd pictexpress_app

if not exist pubspec.yaml (
    echo ❌ ERREUR : pubspec.yaml introuvable dans %cd%
    pause
    exit
)

echo 🚀 Lancement de l'application (L'écran de chargement va prendre le relais)...

call flutter run -d windows

pause