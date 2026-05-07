from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import whisper
import spacy
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("pictogrammes", exist_ok=True) 
app.mount("/pictogrammes", StaticFiles(directory="pictogrammes"), name="pictogrammes")

print("⏳ Chargement des modèles IA...")
modele_whisper = whisper.load_model("small")
nlp = spacy.load("fr_core_news_md")

def interroger_ontologie(mots_clefs):
    base_pictogrammes = {
        "cahier": "cahier.png", 
        "manger": "manger.png", 
        "silence": "silence.png", 
        "feuille": "feuille.png",
        "prendre": "prenez.png",
        "aller": "aller.png"
    }
    
    pictos_trouves = []
    for mot in mots_clefs:
        if mot in base_pictogrammes:
            pictos_trouves.append(base_pictogrammes[mot])
            
    return pictos_trouves

@app.post("/api/transcrire")
async def transcrire_audio(file: UploadFile = File(...)):
    print(f"📥 Fichier audio reçu : {file.filename}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await file.read())
        temp_path = temp_audio.name

    try:
        # 1. Écoute (Whisper)
        # DESIGN: transcribe is CPU-bound; run in a thread pool so the event loop
        # is not blocked and other requests can be handled concurrently.
        print("🤖 Whisper écoute...")
        resultat = await asyncio.to_thread(modele_whisper.transcribe, temp_path, language="fr")
        texte_entendu = resultat["text"].strip()
        print(f"🗣️ Phrase entendue : '{texte_entendu}'")

        # 2. Nettoyage et Grammaire (spaCy)
        doc = nlp(texte_entendu)
        mots_clefs = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]

        # 3. Réflexion : On confie les mots au module indépendant
        # Si le module change plus tard, cette ligne, elle, ne changera jamais !
        pictos_a_afficher = interroger_ontologie(mots_clefs)

        # 4. Réponse envoyée à Flutter
        return {
            "texte_compris": texte_entendu,
            "pictogrammes": pictos_a_afficher
        }
    finally:
        os.remove(temp_path)