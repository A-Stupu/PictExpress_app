from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import whisper
import spacy
import tempfile
import os

from ontology_service import OntologyService

# Whisper transcription corrections — common French mis-transcriptions
# from the team's empirical testing on the target vocabulary.
_CORRECTIONS: dict[str, str] = {
    "décine":   "dessine",
    "Décine":   "Dessine",
    "fercle":   "cercle",
    "réquerre": "équerre",
    "tracé":    "trace",
    "combat":   "compas",
    "côte":     "côté",
}


# ---- Lifespan: load heavy models once at startup ----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Chargement des modèles IA...")
    app.state.whisper = whisper.load_model("small")
    app.state.nlp     = spacy.load("fr_core_news_md")

    print("⏳ Chargement de l'ontologie + Pellet...")
    svc = OntologyService("./maths.owl")
    svc.load()
    app.state.ontology = svc
    print("✅ Tous les modèles sont prêts.")
    yield


# ---- App setup ---------------------------------------------------------------

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("pictogrammes", exist_ok=True)
app.mount("/pictogrammes", StaticFiles(directory="pictogrammes"), name="pictogrammes")


# ---- API endpoints -----------------------------------------------------------

@app.get("/")
async def health_check():
    return {"status": "ready", "server": "PictExpress AI"}


@app.post("/api/transcrire")
async def transcrire_audio(file: UploadFile = File(...)):
    print(f"📥 Fichier audio reçu : {file.filename}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 1. Transcription (CPU-bound — thread pool to avoid blocking event loop)
        print("🤖 Whisper écoute...")
        resultat = await asyncio.to_thread(
            app.state.whisper.transcribe, tmp_path, language="fr"
        )
        texte_brut = resultat["text"].strip()
        print(f"🗣️  Texte brut : '{texte_brut}'")

        # 2. Correction of common mis-transcriptions
        texte_propre = texte_brut
        for faute, correction in _CORRECTIONS.items():
            texte_propre = texte_propre.replace(faute, correction)
        if texte_propre != texte_brut:
            print(f"🔧 Texte corrigé : '{texte_propre}'")

        # 3. Lemmatisation (spaCy)
        doc = app.state.nlp(texte_propre)
        lemmes = [
            token.lemma_ for token in doc if not token.is_stop and not token.is_punct
        ]
        print(f"🧠 Lemmes : {lemmes}")

        # 4. Inférence sémantique (Pellet via OntologyService)
        pictos = app.state.ontology.infer_pictograms(lemmes)
        print(f"🖼️  Pictogrammes inférés : {pictos}")

        pictogrammes_files = [f"{p['arasaac_id']}.png" for p in pictos]

        return {
            "texte_compris": texte_propre,
            "pictogrammes":  pictogrammes_files,
            "details":       pictos,
        }

    finally:
        os.remove(tmp_path)


@app.get("/needs")
async def get_needs():
    """Return Needs grouped by UI category for the child communication board."""
    return app.state.ontology.get_needs_grouped()
