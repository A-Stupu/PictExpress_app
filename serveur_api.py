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


# ---- Lifespan: load heavy models once at startup ----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # DESIGN: OntologyService.load() starts the JVM via Pellet; doing it once
    # at startup avoids per-request JVM cold-start overhead (~2-4 s).
    print("⏳ Chargement des modèles IA...")
    app.state.whisper = whisper.load_model("small")
    app.state.nlp     = spacy.load("fr_core_news_md")

    print("⏳ Chargement de l'ontologie + Pellet...")
    svc = OntologyService("./maths.owl")
    svc.load()
    app.state.ontology = svc
    print("✅ Tous les modèles sont prêts.")
    yield
    # cleanup (Pellet JVM is managed by owlready2 internally)


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


# ---- API endpoint ------------------------------------------------------------

@app.post("/api/transcrire")
async def transcrire_audio(file: UploadFile = File(...)):
    print(f"📥 Fichier audio reçu : {file.filename}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 1. Transcription (CPU-bound — run in thread pool to avoid blocking event loop)
        print("🤖 Whisper écoute...")
        resultat = await asyncio.to_thread(
            app.state.whisper.transcribe, tmp_path, language="fr"
        )
        texte_entendu = resultat["text"].strip()
        print(f"🗣️  Phrase entendue : '{texte_entendu}'")

        # 2. Lemmatisation (spaCy)
        doc = app.state.nlp(texte_entendu)
        lemmes = [
            token.lemma_ for token in doc if not token.is_stop and not token.is_punct
        ]
        print(f"🧠 Lemmes : {lemmes}")

        # 3. Inférence sémantique (Pellet via OntologyService)
        pictos = app.state.ontology.infer_pictograms(lemmes)
        print(f"🖼️  Pictogrammes inférés : {pictos}")

        # 4. Build response: filenames use arasaac_id to match the renamed PNGs
        pictogrammes_files = [f"{p['arasaac_id']}.png" for p in pictos]

        return {
            "texte_compris": texte_entendu,
            "pictogrammes":  pictogrammes_files,
            "details":       pictos,          # includes class_name, label_fr, arasaac_id
        }

    finally:
        os.remove(tmp_path)


@app.get("/needs")
async def get_needs():
    """
    Return Needs grouped by UI category for the child communication board.
    Response: {physical: [...], mental: [...], help_validation: [...]}
    Each item: {class_name, label_fr, arasaac_id}
    """
    return app.state.ontology.get_needs_grouped()
