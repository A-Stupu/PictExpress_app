from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from owlready2 import *
import whisper
import spacy
import tempfile
import os
import requests
import json

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ready", "server": "PictExpress AI"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Configuration des dossiers
DOSSIER_PICTOS = "pictogrammes"
FICHIER_MAPPING = "mapping_mots.json"
os.makedirs(DOSSIER_PICTOS, exist_ok=True)

#Chargement du cache
if os.path.exists(FICHIER_MAPPING):
    with open(FICHIER_MAPPING, "r", encoding="utf-8") as f:
        cache_mots = json.load(f)
else:
    cache_mots = {}

#Chargement IA
print("⏳ Chargement des modèles...")
modele_whisper = whisper.load_model("small")
nlp = spacy.load("fr_core_news_md")
onto = get_ontology("maths_upgrade.owl").load()

def sauvegarder_cache():
    """Enregistre les nouvelles connaissances sur le disque."""
    with open(FICHIER_MAPPING, "w", encoding="utf-8") as f:
        json.dump(cache_mots, f, ensure_ascii=False, indent=4)

def rechercher_id_arasaac_scolaire(mot):
    """Cherche sur l'API et met en cache le résultat."""
    if mot in cache_mots:
        print(f"🧠 Mémoire : '{mot}' est déjà associé à l'ID {cache_mots[mot]}")
        return cache_mots[mot]

    print(f"🌐 Recherche API ARASAAC pour : {mot}")
    try:
        url_search = f"https://api.arasaac.org/api/pictograms/fr/search/{mot}"
        res = requests.get(url_search, timeout=5).json()
        if not res or "error" in res: return None

        meilleur_id = None
        score_max = -1
        for candidat in res[:5]:
            picto_id = str(candidat['_id'])
            url_details = f"https://api.arasaac.org/api/pictograms/fr/{picto_id}"
            details = requests.get(url_details, timeout=3).json()
            score = 0
            cats = [c.upper() for c in details.get('categories', [])]
            if "EDUCATION" in cats or "EDUCATIONAL TASK" in cats: score += 5
            
            keywords = str(details.get('keywords', [])).lower()
            if any(x in keywords for x in ["école", "élève", "classe", "scolaire"]): score += 10

            if score > score_max:
                score_max = score
                meilleur_id = picto_id

        if meilleur_id:
            cache_mots[mot] = meilleur_id
            sauvegarder_cache()
            return meilleur_id
    except:
        return None

def interroger_ontologie(mots_clefs):
    pictos_ordonnes = []
    classes_trouvees = []

    print(f"🔎 Analyse ordonnée : {mots_clefs}")

    for mot in mots_clefs:
        id_trouve = None
        mot_norm = mot.lower().strip()
        
        for classe in onto.classes():
            labels = [str(l).lower().strip() for l in (classe.label if hasattr(classe, "label") else [])]
            if mot_norm in labels:
                if hasattr(classe, "arasaacId") and classe.arasaacId:
                    id_trouve = str(classe.arasaacId[0])
                    classes_trouvees.append(classe)
                    print(f"🎯 Onto Match : {mot_norm} -> {id_trouve}")
                    break

        if not id_trouve:
            id_trouve = rechercher_id_arasaac_scolaire(mot_norm)
            if id_trouve: 
                print(f"🌐 API Match : {mot_norm} -> {id_trouve}")

        if id_trouve:
            nom_fichier = f"{id_trouve}.png"
            pictos_ordonnes.append(nom_fichier)

    return pictos_ordonnes

@app.get("/pictogrammes/{nom_fichier}")
async def get_picto(nom_fichier: str):
    chemin = os.path.join(DOSSIER_PICTOS, nom_fichier)
    if not os.path.exists(chemin):
        id_p = nom_fichier.split(".")[0]
        url = f"https://static.arasaac.org/pictograms/{id_p}/{id_p}_300.png"
        r = requests.get(url)
        if r.status_code == 200:
            with open(chemin, "wb") as f: f.write(r.content)
    return FileResponse(chemin)

@app.post("/api/transcrire")
async def process_audio(file: UploadFile = File(...)):
    """
    Pipeline complet : 
    1. Audio -> Texte (Whisper)
    2. Correction des fautes de transcription
    3. Extraction des mots-clés (spaCy : Noms, Verbes, Adj, Nombres)
    4. Correspondance Pictogrammes (Ontologie + Cache/API)
    """
    print(f"📥 Réception d'un nouvel enregistrement : {file.filename}")
    
    #Création du fichier temporaire pour l'audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        #Transcription Whisper
        print("🤖 Whisper transcrit...")
        res = modele_whisper.transcribe(tmp_path, language="fr")
        texte_brut = res["text"].strip()
        print(f"🗣️ Texte brut : {texte_brut}")

        #Correction des fautes de transcription
        corrections = {
            "décine": "dessine",
            "Décine": "Dessine",
            "côte": "côté",
            "fercle": "cercle",
            "réquerre": "équerre",
            "cm": "centimètre",
            "mm": "millimètre",
            "tracé": "trace",
            "combat": "compas"
        }
        
        texte_propre = texte_brut
        for faute, correction in corrections.items():
            texte_propre = texte_propre.replace(faute, correction)
        
        if texte_propre != texte_brut:
            print(f"🔧 Texte corrigé : {texte_propre}")

        #Analyse NLP
        doc = nlp(texte_propre)

        mots_utiles = [
            t.lemma_.lower() 
            for t in doc 
            if t.pos_ in ["NOUN", "VERB", "ADJ", "NUM", "SYM"]
        ]
        
        print(f"📝 Mots retenus pour l'affichage : {mots_utiles}")

        #Recherche des Pictogrammes
        pictos = interroger_ontologie(mots_utiles)
        print(f"🖼️ Liste des images à afficher : {pictos}")

        return {
            "texte_compris": texte_propre,
            "pictogrammes": pictos
        }

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        return {"error": str(e)}

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)