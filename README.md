# Pict'Express — School Pictogram Translation System

A research application that automatically translates French sentences into pictogram sequences to support communication with autistic children and students with speech/language difficulties.

**Supervisors**: Adrien UGON, Akram REDJDAL  
**Institutions**: Laboratoire de Biomécanique Appliquée (LBA, Marseille), ESIEE Paris

---

## Current Status

The prototype is **functionally connected end-to-end** for both flows. Elaboration phase is closing.

| Component | Status |
|-----------|--------|
| `maths.owl` OWL ontology | 62 classes, 34 French labels, 34 arasaacIds, 17 SWRL rules |
| Pellet reasoner (Java 21) | Working — SWRL rules fire correctly |
| `ontology_service.py` | OntologyService: label lookup, SWRL inference via Pellet, needs grouping |
| `serveur_api.py` | FastAPI backend: Whisper (async) + spaCy + OntologyService |
| Flutter app | Two flows: Teacher (speech → pictograms) + Student (communication board) |
| Tests | 30/30 pytest passing |

**Flow 1 (Teacher):** Whisper transcribes French speech → spaCy lemmatises → OntologyService maps lemmas to OWL classes → Pellet infers required tools via SWRL → pictograms served as static files.

**Flow 2 (Student):** Communication board with categorised need pictograms loaded directly from the ARASAAC CDN — no backend required.

**Not yet implemented:** live CDN download for the teacher flow (pictogram PNG files are pre-loaded locally); NLP disambiguation for polysemy; Flutter state management beyond `setState`; Flutter widget and integration tests.

---

## Setup

### Prerequisites

- Python 3.10+
- **Java 21 LTS** (e.g., [Eclipse Temurin](https://adoptium.net/temurin/releases/?version=21)) — required for Pellet
- Flutter SDK (for the mobile app)

### Backend

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download the French spaCy model
python -m spacy download fr_core_news_md

# 3. Patch owlready2 JARs for Java 21 compatibility (run once per machine)
python scripts/patch_owlready2_jars.py

# 4. Verify Pellet works
python scripts/test_pellet.py

# 5. Start the FastAPI server (default: port 8000)
uvicorn serveur_api:app --reload
```

### Running tests

```bash
pytest tests/ -v
```

### Mobile app (Flutter)

```bash
cd pictexpress_app

# Dev (localhost): default SERVER_URL = http://127.0.0.1:8000
flutter run

# Physical device (LAN): set SERVER_URL to your machine's IP
flutter run --dart-define=SERVER_URL=http://192.168.1.X:8000
```

---

## Architecture

```
[Flutter UI]
     │  HTTP multipart/form-data (WAV file)
     ▼
[FastAPI Controller — serveur_api.py]
     │  await asyncio.to_thread(whisper.transcribe)
     ├─ [WhisperService — openai-whisper]    FR speech → text
     │  spaCy lemmatization
     ├─ [NLP — fr_core_news_md]              text → lemmas
     │  OntologyService.infer_pictograms()
     └─ [OntologyService — ontology_service.py]
            │  load: OWL/XML parse + Pellet JVM startup
            │  infer: temporary OWL individuals → sync_reasoner_pellet
            ├─ [maths.owl]                   62 classes, 17 SWRL rules, 34 arasaacIds
            └─ [Pellet via owlready2]        SWRL DL-Safe rule execution
                     │
                     ▼
           arasaac_id list → {class_name, label_fr, arasaac_id}
                     │
                     ▼
     [pictogrammes/ static files]            {arasaac_id}.png served by FastAPI
```

---

## Project Scope

The application operates within a **restricted domain**: elementary school daily routine with ~50–80 core concepts:
- **Actions**: eat, drink, read, write, sit, stand, go out, play, sleep, listen, raise hand, run
- **Objects**: book, pen, pencil, notebook, backpack, table, chair, blackboard, desk, eraser
- **Persons**: teacher, student, janitor, parent, classmate, friend
- **Locations**: classroom, hallway, bathroom, gym, cafeteria, playground
- **Time Markers**: now, morning, today, after, before

**Target Users**: Parents, teachers, speech therapists (orthophonistes)

---

## System Pipeline

1. **Voice → App** — microphone input captures spoken French
2. **Sound → Text** — Speech-to-Text engine transcribes audio
3. **Select meaningful words** — Named Entity Recognition (NER) filters relevant tokens
4. **Meaningful word → Concept** — token mapped to semantic concept via OWL ontology reasoning
5. **Concept → Pictogram** — concept matched to pictogram from ARASAAC database or Gen AI fallback
6. **Organize pictograms** — sequence ordered using graph semantic representation
7. **Show result on screen** — GUI displays pictogram sequence to user

---

## Project Structure

```
Pictograme_app/
├── README.md                                    <- This file
├── maths.owl                                    <- OWL 2 ontology (62 classes, 17 SWRL rules)
├── ontology_service.py                          <- OntologyService: label index, Pellet inference
├── serveur_api.py                               <- FastAPI server: Whisper, spaCy, OntologyService
├── requirements.txt
├── pictogrammes/                                <- Static pictogram PNG files (arasaacId.png)
├── docs/
│   ├── PROJECT_REPORT.md                        <- Elaboration phase report
│   ├── ONTOLOGY_DEVELOPMENT_GUIDE.md            <- Original ontology planning guide
│   ├── ONTOLOGY_INTEGRATION.md                  <- OWL structure, SWRL rules, extension guide
│   └── uml/
│       ├── README.md                            <- UML artifacts guide
│       ├── use_case_diagram.puml
│       ├── domain_model.puml
│       ├── class_diagram.puml
│       ├── sequence_teacher_flow.puml
│       └── sequence_child_flow.puml
├── analysis/                                    <- Phase working documents
│   ├── arasaac_mapping.md
│   ├── integration_report.md
│   ├── child_flow_report.md
│   ├── owl_baseline.md
│   ├── pellet_smoke_test.md
│   └── pictogram_renaming.md
├── scripts/
│   ├── patch_owlready2_jars.py                  <- Fix owlready2 JAR for Java 21
│   ├── populate_arasaac_ids.py                  <- Fetch ARASAAC IDs into maths.owl
│   └── test_pellet.py                           <- Pellet smoke test
├── tests/
│   ├── test_pipeline.py                         <- 17 inference tests
│   └── test_needs.py                            <- 13 needs tests
└── pictexpress_app/                             <- Flutter mobile application
```

---

## Methodology

The project follows the **Unified Process (UP)** with team co-ownership across four phases:

### Inception — COMPLETED
**Deliverables**:
- Use Case Diagram (school context scope, 6 actors, core use case flows)
- Domain Model (8 conceptual classes and relationships)
- Project charter and scope definition

### Elaboration — CLOSING
**Deliverables produced**:
- OWL ontology (`maths.owl`): 62 classes, 34 French labels, 17 SWRL rules, full Pellet integration
- Use Case Diagram (updated to implemented scope)
- Class Diagram (four-layer architecture)
- Sequence Diagrams for Flow 1 (teacher) and Flow 2 (student)
- Domain Model
- Functional prototype: both flows end-to-end
- 30 automated tests, all passing

### Construction — PENDING
**Deliverables**:
- Design Class Diagram (DCD) based on domain layer contracts
- Full implementation (Flutter/React Native, backend, ontology reasoner)
- Comprehensive testing strategy and test suites

---

## Team Roles & Responsibilities

### Member 1 — Software Architecture & Engineering
- Unified Process oversight (Inception complete, guiding Elaboration and Construction)
- UML artifacts: Use Case Diagram (completed), Domain Model (completed), future SSD and DCD
- Architecture design: layered architecture, design patterns (Strategy, Adapter, Factory)
- Ontology coordination: reviews and integrates Member 2's ontology with overall design
- Contracts and logical design specifications

### Member 2 — Ontology / NLP
- OWL ontology construction in Protégé (following ONTOLOGY_DEVELOPMENT_GUIDE.md)
- Named Entity Recognition (NER) pipeline implementation
- Sentic token→concept mapping using domain glossary
- SWRL rule authoring for context-aware disambiguation
- Reasoner integration (HermiT/Pellet) and consistency validation
- Deliverable: final pict-express-v0.6.owl with 50–80 concepts

### Member 3 — UI / Mobile Development
- Mobile app development (Flutter or React Native, Android/iOS)
- French-language user interface design and implementation
- User experience design adapted for target users (teachers, parents, therapists)
- ARASAAC API integration and pictogram database setup
- Pictogram concept→image matching and caching
- Post-launch: user feedback collection and iterative improvements

---

## Completed Deliverables

### Inception Phase
- **Use Case Diagram** ([docs/uml/use_case_diagram.puml](docs/uml/use_case_diagram.puml)) — school context scope, 4 actors
- **Domain Model** ([docs/uml/domain_model.puml](docs/uml/domain_model.puml)) — conceptual classes and relationships

### Elaboration Phase
- **Class Diagram** ([docs/uml/class_diagram.puml](docs/uml/class_diagram.puml)) — four-layer architecture
- **Sequence Diagram — Teacher Flow** ([docs/uml/sequence_teacher_flow.puml](docs/uml/sequence_teacher_flow.puml))
- **Sequence Diagram — Student Flow** ([docs/uml/sequence_child_flow.puml](docs/uml/sequence_child_flow.puml))
- **OWL Ontology** (`maths.owl`) — 62 classes, 17 SWRL rules, full Pellet integration
- **Functional prototype** — both flows end-to-end, 30/30 tests passing
- **Project Report** ([docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md))

---

## Architecture Overview

The system is organized in four semantic layers that work together to translate spoken French into pictogram sequences:

### **[1] UI Layer** — User Interaction
- **Flutter or React Native** application for mobile (Android/iOS)
- **French-only interface** for end users (teachers, parents, speech therapists)
- Real-time voice input capture via microphone
- Visual display of generated pictogram sequences
- Optional features: sequence saving, sharing, export to PDF/printed format

### **[2] Application Layer** — Orchestration & Control
- Use case controllers that coordinate the 7-step pipeline
- Request handling and response formatting
- Error management and user feedback
- Session management for teachers and students
- Business logic isolation from UI and infrastructure

### **[3] Domain Layer** — Semantic Core & NLP Engine
The heart of the system: transforms tokens into semantic concepts via ontology reasoning.

**OWL Ontology**:
- Class hierarchy encoding the school domain (~50–80 concepts)
- Object properties (performedBy, usesObject, locatedIn, temporalContext)
- Data properties (French labels, English labels, definitions)
- Disjointness axioms and cardinality constraints to ensure consistency

**Named Entity Recognition (NER) Pipeline**:
- Tokenizes transcribed French text
- Filters out stop words (articles, prepositions)
- Maps remaining tokens to OWL individuals via domain_glossary.md

**Semantic Reasoning via OWL Reasoner** (HermiT or Pellet):
- Applies SWRL rules to disambiguate tokens based on context
- Example: "maître" → Teacher (not chess piece) when locatedIn Classroom and performedBy TeacherRole
- Infers implicit relationships (e.g., if action is performedBy Teacher → it's a SchoolContextAction)
- Validates consistency and flags contradictions

### **[4] Infrastructure Layer** — External Services & Data
- **Speech-to-Text Service**: Converts audio to French text (e.g., Google Cloud Speech-to-Text, Azure, or local model)
- **ARASAAC Pictogram Database**: Standard pictogram library for school domain concepts
  - REST API queries: concept name → pictogram image URL(s)
  - Cached locally for performance
- **Pictogram Matching Engine**: Maps OWL concepts to ARASAAC IDs or custom pictogram paths
- **Gen AI Fallback**: If a concept has no ARASAAC match, generate a custom pictogram via image generation API
- **Persistent Storage**: Saved sequences, user profiles, library metadata

---

## Key Design Decisions

1. **OWL Ontology as source of truth** for semantic domain model
2. **SWRL rules for disambiguation** (context-aware token → concept mapping)
3. **domain_glossary.md as team glossary** (bridges ontology & non-ontology work)
4. **Iterative development**: 50 core concepts first, then extend
5. **Design Patterns**: Strategy (pictogram selection), Adapter (API wrapping), Factory (object creation)

---

## Expected Final Deliverables (by Project End)

- Functional mobile app (beta, Android/iOS) with French UI
- Complete OWL ontology (school domain, ~80 concepts)
- Structured pictogram database (ARASAAC + Gen AI generated)
- Technical report (architecture, NLP algorithms, test results)
- User guide (for parents, teachers, speech therapists)
- Demo video

---

## References

- **Project Brief**: Trame description projet E4 ESIEE Recherche (Adrien UGON)
- **OWL Resources**: [W3C OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)
- **Protégé**: [protege.stanford.edu](https://protege.stanford.edu)
- **UML Rendering**: [plantuml.com](https://plantuml.com) |
