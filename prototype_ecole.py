import whisper
import spacy
import speech_recognition as sr
import tempfile
import os

print("Chargement des modèles (cela peut prendre quelques secondes)...")
# 1. Chargement de Whisper (modèle 'small')
modele_whisper = whisper.load_model("small")

# 2. Chargement de spaCy (français)
nlp = spacy.load("fr_core_news_md")

# 3. Notre dictionnaire de pictogrammes temporaire (Mock)
base_pictogrammes = {
    "cahier": "📓 PICTO_CAHIER",
    "manger": "🍽️ PICTO_MANGER",
    "asseoir": "🪑 PICTO_S_ASSEOIR",
    "silence": "🤫 PICTO_SILENCE",
    "dessiner": "🖍️ PICTO_DESSINER",
    "récréation": "⚽ PICTO_COUR",
    "écouter": "👂 PICTO_ECOUTER"
}

# 4. Configuration du microphone
recognizer = sr.Recognizer()

def ecouter_et_analyser():
    with sr.Microphone() as source:
        print("\n" + "="*50)
        print("Réglage du bruit ambiant... Ne parlez pas pendant 1 seconde.")
        recognizer.adjust_for_ambient_noise(source)
        
        print("🟢 PARLEZ MAINTENANT (ex: 'Prenez vos cahiers et en silence')")
        # On écoute jusqu'à ce que vous arrêtiez de parler
        audio = recognizer.listen(source)
        print("🔴 Traitement en cours...")

    # On sauvegarde l'audio temporairement pour que Whisper puisse le lire
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fichier_temp:
        fichier_temp.write(audio.get_wav_data())
        nom_fichier = fichier_temp.name

    try:
        # --- ÉTAPE A : Transcription avec Whisper ---
        resultat = modele_whisper.transcribe(nom_fichier, language="fr")
        texte_transcrit = resultat["text"].strip()
        print(f"\n🗣️ Whisper a entendu : '{texte_transcrit}'")

        # --- ÉTAPE B : Analyse avec spaCy ---
        doc = nlp(texte_transcrit)
        mots_clefs = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        print(f"🧠 spaCy a extrait les lemmes : {mots_clefs}")

        # --- ÉTAPE C : Recherche des pictogrammes ---
        print("\n🖼️ RÉSULTAT A AFFICHER A L'ÉCRAN :")
        pictos_trouves = 0
        for lemme in mots_clefs:
            if lemme in base_pictogrammes:
                print(f"  -> Affichage de : {base_pictogrammes[lemme]}")
                pictos_trouves += 1
        
        if pictos_trouves == 0:
            print("  -> Aucun pictogramme connu trouvé dans cette phrase.")

    finally:
        # On nettoie le fichier audio temporaire
        os.remove(nom_fichier)

# Boucle pour tester plusieurs phrases d'affilée
if __name__ == "__main__":
    while True:
        ecouter_et_analyser()
        choix = input("\nAppuyez sur Entrée pour parler à nouveau, ou tapez 'q' pour quitter : ")
        if choix.lower() == 'q':
            break