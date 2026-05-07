# Pict'Express — Project Report
**Elaboration Phase — Unified Process**

*Collaboration: LBA Marseille · ESIEE Paris*  
*Supervisors: Adrien UGON, Akram REDJDAL*

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Design Choices and Patterns](#3-design-choices-and-patterns)
4. [OWL Ontology](#4-owl-ontology)
5. [Unified Process Phase Status](#5-unified-process-phase-status)
6. [Weekly Timeline](#6-weekly-timeline)
7. [Work Distribution — Actual Team (3 people)](#7-work-distribution--actual-team-3-people)
8. [Work Distribution — Ideal Team (6 people)](#8-work-distribution--ideal-team-6-people)
9. [Known Limitations and Future Roadmap](#9-known-limitations-and-future-roadmap)

---

## 1. Introduction

**Pict'Express** is a mobile application that supports communication between teachers and students with autism spectrum disorder or language/speech difficulties.

The application operates within a restricted scope — **elementary school, mathematics and daily routine domain** — to keep the vocabulary manageable and the ontology verifiable during the Elaboration phase.

### Target Users
| User | Role |
|------|------|
| Teacher (Enseignant) | Speaks instructions; receives pictogram suggestions |
| Student (Élève) | Selects pictograms from a communication board to express needs |
| Assistant (AESH) | Can substitute for Teacher in Flow 1 |

### Two Distinct Flows

**Flow 1 — Teacher → Pictograms (NLP + OWL)**  
The teacher speaks a French instruction ("Tracez un cercle"). The system transcribes it via Whisper, lemmatises it via spaCy, reasons over the OWL ontology with Pellet/SWRL, and returns 2–4 pictograms showing the concept and required tools.

**Flow 2 — Student → Communication (Selection)**  
The student opens a categorised grid of pictograms representing personal needs (hunger, fatigue, confusion…), taps one, and shows the enlarged image to the teacher. No NLP, no server required — images load directly from the ARASAAC CDN.

### Methodology
**Unified Process (UP)**, iterative and architecture-centric. Team of 3, approximately one working day per week for 12 weeks.

---

## 2. System Architecture

The system is organised in four layers. See [Class Diagram](uml/class_diagram.puml) for full detail.

```
┌─────────────────────────────────────────────────────────┐
│  Presentation (Flutter — Dart)                          │
│  HomeScreen → TeacherScreen | ChildScreen               │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / ARASAAC CDN
┌──────────────────────▼──────────────────────────────────┐
│  Application (FastAPI — Python, uvicorn)                 │
│  POST /api/transcrire  ·  GET /needs  ·  /pictogrammes/ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Domain (OntologyService)                               │
│  load · find_class_by_label · infer_pictograms          │
│  get_needs_grouped · ensure_pictograms_cached           │
└──────┬───────────────────────────────────┬──────────────┘
       │                                   │
┌──────▼──────┐                   ┌────────▼───────────────┐
│ Infrastructure│                 │ OWL Ontology (maths.owl)│
│ Whisper · spaCy │               │ 62 classes · 17 SWRL   │
│ Pellet (Java) │                 │ rules · 34 arasaacIds  │
│ ARASAAC CDN  │                  └────────────────────────┘
└─────────────┘
```

### 7-Step Pipeline Status

| Step | Description | Component | Status |
|------|-------------|-----------|--------|
| 1 | Voice input capture | Flutter `record` plugin | ✅ Implemented |
| 2 | Speech-to-Text (French) | Whisper `small` model | ✅ Implemented |
| 3 | Lemmatisation / NER | spaCy `fr_core_news_md` | ✅ Implemented |
| 4 | Lemma → OWL class mapping | `OntologyService.find_class_by_label()` | ✅ Implemented |
| 5 | SWRL reasoning | Pellet via owlready2 | ✅ Implemented |
| 6 | Pictogram resolution | `get_arasaac_id()` + StaticFiles | ✅ Implemented |
| 7 | GUI display | `TeacherScreen` / `ChildScreen` | ✅ Implemented |

Flow 2 uses a shortened pipeline: tap → CDN image → dialog.

---

## 3. Design Choices and Patterns

### Applied Patterns

#### Service Layer (`OntologyService` — `ontology_service.py`)
**Problem:** `serveur_api.py` originally contained a hardcoded `interroger_ontologie()` function (dict of 6 words). Domain logic was mixed with HTTP routing.  
**Solution:** All semantic logic extracted into `OntologyService`, a class with a clear public API. `serveur_api.py` only calls `app.state.ontology.infer_pictograms(lemmas)`.  
**Alternative rejected:** Keeping logic in the endpoint — makes testing impossible without starting a server.

#### Singleton via FastAPI Lifespan (`serveur_api.py`)
**Problem:** Loading Whisper (~244 MB), spaCy, owlready2, and starting Pellet's JVM takes 30–60 seconds. This cannot happen per request.  
**Solution:** FastAPI's `@asynccontextmanager lifespan` pattern loads all models once at startup and attaches them to `app.state`. Subsequent requests access pre-loaded objects.  
**Alternative rejected:** Global module-level variables — obscures dependency injection and makes testing harder.

#### Adapter — Async Wrapper for Synchronous CPU Work (`serveur_api.py`)
**Problem:** `whisper.transcribe()` is a blocking CPU-bound call in an async FastAPI endpoint — it blocks the event loop.  
**Solution:** `await asyncio.to_thread(app.state.whisper.transcribe, tmp_path, language="fr")` wraps the call in a thread pool worker.

#### Strategy (implicit) — SWRL Rule Parser (`OntologyService._parse_swrl_rules()`)
**Problem:** owlready2 0.50 silently ignores `DLSafeRule` elements when loading OWL/XML files. It uses an older `swrl:Imp` RDF vocabulary internally.  
**Solution:** `_parse_swrl_rules()` uses `xml.etree.ElementTree` to read `DLSafeRule` elements from the raw OWL/XML file and converts each atom to owlready2's `Imp().set_as_rule(str)` format at load time. The OWL file remains the canonical source; Python only interprets it.

#### Repository (implicit) — `OntologyService` as Domain Gateway
`OntologyService` is the single entry point for all ontology queries. No other module imports owlready2 directly. This isolates the OWL/reasoner stack from the rest of the system.

#### Static Resource Mount (`serveur_api.py`)
Pictogram PNGs served from `pictogrammes/` via FastAPI `StaticFiles` mount at `/pictogrammes`. Decouples file management from request handling.

#### Navigator Pattern (Flutter — `main.dart`)
`Navigator.push(MaterialPageRoute(...))` for bidirectional navigation between HomeScreen, TeacherScreen, and ChildScreen. No named routes, no go_router — sufficient for the current 3-screen structure.

### GRASP Principles

| Principle | Application |
|-----------|-------------|
| Information Expert | `OntologyService` owns all ontology knowledge and is the only class that queries it |
| Low Coupling | Flutter presentation layer has no knowledge of owlready2; it only speaks HTTP |
| High Cohesion | One service class per functional concern (ontology logic, HTTP routing) |
| Creator | `OntologyService` creates temporary OWL individuals and `Pictogram` structs; it cleans up via `destroy_entity()` |

### GoF Patterns Absent (by choice)

| Pattern | Reason not applied |
|---------|--------------------|
| Observer / Bloc | Prototype scope — `setState()` sufficient for 1-2 screens |
| Factory | Object creation is trivial; no hierarchy of creators needed |
| Strategy (explicit) | Single reasoner backend (Pellet); no need for runtime swap |

---

## 4. OWL Ontology

File: [`maths.owl`](../maths.owl) — OWL 2 XML syntax  
IRI: `http://www.pictexpress.org/ontologies/math.owl`

### Statistics

| Metric | Value |
|--------|-------|
| Total classes | 62 |
| Object properties | 10 |
| French `rdfs:label@fr` annotations | 34 labels on 30 classes |
| `#arasaacId` annotations | 34 integer IDs |
| SWRL `DLSafeRule` axioms | 17 |
| Named individuals (tool singletons) | 7 |

### Top-Level Class Hierarchy

```
owl:Thing
├── Actions          (MathAction, ManualAction + 9 leaf classes)
├── CalculationMethod (Hands, Mind)
├── MathematicalConcept (GeometricShape, MathOperation, Magnitude, Number + 14 leaves)
├── Needs            (PhysicalNeed, MentalNeed, HelpNeed, ValidationNeed + 11 leaves)
├── Person           (Student, Teacher, Assistant)
└── SchoolMaterial   (BasicTool, GeometryTool, CalculationTool + 10 leaves)
```

All six top-level categories are declared mutually disjoint.

### 17 SWRL Rules (DLSafeRules)

| # | Rule | Semantic |
|---|------|----------|
| 1 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Circle(?s) ∧ Compass(?c) → requires(?a,?c)` | Drawing circle needs compass |
| 2 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Circle(?s) ∧ Pencil(?p) → requires(?a,?p)` | Drawing circle needs pencil |
| 3 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Square(?s) ∧ Ruler(?r) → requires(?a,?r)` | Drawing square needs ruler |
| 4 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Square(?s) ∧ Pencil(?p) → requires(?a,?p)` | Drawing square needs pencil |
| 5 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Triangle(?s) ∧ SetSquare(?q) → requires(?a,?q)` | Drawing triangle needs set square |
| 6 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Triangle(?s) ∧ Pencil(?p) → requires(?a,?p)` | Drawing triangle needs pencil |
| 7 | `Measure(?a) ∧ hasTarget(?a,?s) ∧ GeometricShape(?s) ∧ Ruler(?r) → requires(?a,?r)` | Measuring shape needs ruler |
| 8 | `Calculate(?a) ∧ Calculator(?c) → requires(?a,?c)` | Calculating needs calculator |
| 9 | `Write(?a) ∧ Pencil(?p) → requires(?a,?p)` | Writing needs pencil |
| 10 | `Write(?a) ∧ Notebook(?n) → requires(?a,?n)` | Writing needs notebook |
| 11 | `Erase(?a) ∧ Eraser(?e) → requires(?a,?e)` | Erasing needs eraser |
| 12 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Rectangle(?s) ∧ Ruler(?r) → requires(?a,?r)` | Drawing rectangle needs ruler |
| 13 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Rectangle(?s) ∧ Pencil(?p) → requires(?a,?p)` | Drawing rectangle needs pencil |
| 14 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Pentagon(?s) ∧ Ruler(?r) → requires(?a,?r)` | Drawing pentagon needs ruler |
| 15 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Pentagon(?s) ∧ Pencil(?p) → requires(?a,?p)` | Drawing pentagon needs pencil |
| 16 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Hexagon(?s) ∧ Ruler(?r) → requires(?a,?r)` | Drawing hexagon needs ruler |
| 17 | `Draw(?a) ∧ hasTarget(?a,?s) ∧ Hexagon(?s) ∧ Pencil(?p) → requires(?a,?p)` | Drawing hexagon needs pencil |

Rules are DL-Safe: they fire only on named individuals. Tool singletons (`theCompass`, `thePencil`, `theRuler`, `theSetSquare`, `theCalculator`, `theNotebook`, `theEraser`) are declared in the ontology to satisfy the DL-safety requirement.

### Key Modelling Decisions

**SWRL over OWL restrictions:** OWL existential restrictions (`Circle SubClassOf requiresTool some Compass`) would infer tools whenever a Circle is mentioned, even without a Draw verb. SWRL rules add the verb as a necessary condition, making the inference faithful to the use case: "Tracez un cercle" → tools; "le cercle est rond" → no tools.

**`PhysicalNeed` as a new branch:** Hunger, thirst, pain, and toilet needs are bodily states, categorically different from cognitive/sensory `MentalNeed` (fatigue, noise). A separate branch avoids misclassification and makes the UI grouping ("J'ai besoin de…" vs "Je me sens…") directly derivable from the ontology.

**`CalculationMethod` for `Hands` and `Mind`:** These represent means of calculation, not physical school supplies. Placing them under `SchoolMaterial → CalculationTool` (original file) would have made the reasoner infer logical inconsistencies since `SchoolMaterial` is disjoint from `Person`.

**Needs labels as phrases:** Labels like "j'ai faim" are full phrases rather than lemmas. This is intentional: Flow 2 (student communication) uses these labels as display text for the teacher, not for NLP matching.

### Technical Issues Resolved

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Pellet fails on Java 21 | owlready2 0.50 bundles Jena JARs compiled for Java 25 (class version 69); Java 21 supports up to 65 | Replace 3 `LangRDFXML` classes with originals from Jena 2.10.0 (Maven Central) via `scripts/patch_owlready2_jars.py` |
| `DLSafeRule` not parsed by owlready2 | owlready2 uses older `swrl:` RDF vocabulary, not OWL 2 XML `DLSafeRule` elements | `_parse_swrl_rules()` reads rules via `xml.etree.ElementTree` and converts each to `Imp().set_as_rule(str)` |
| Windows `file:///` URI bug | owlready2 produces `/C:/path` (leading slash) from `file:///C:/path` on Windows | Copy OWL to temp dir as `math.owl` (matching ontologyIRI filename), use `onto_path` for resolution |

---

## 5. Unified Process Phase Status

### Inception — Completed

**Goal:** Define project vision, scope, and feasibility.

| Deliverable | Status |
|-------------|--------|
| Project charter (`README.md`) | ✅ |
| Initial Use Case Diagram | ✅ |
| Domain glossary (partial, ~30 concepts) | ✅ |
| Scope constraints (French, school, 50–80 concepts, mobile) | ✅ |
| Technology stack selection (Flutter, Python, OWL) | ✅ |

### Elaboration — Closing (this report)

**Goal:** Stabilise architecture, mitigate technical risks, produce an architecture baseline.

| Deliverable | Status |
|-------------|--------|
| Use Case Diagram (updated, implemented UCs only) | ✅ |
| Class Diagram (4-layer architecture) | ✅ |
| Sequence Diagram — Flow 1 (Teacher) | ✅ |
| Sequence Diagram — Flow 2 (Student) | ✅ |
| Domain Model | ✅ |
| OWL ontology (62 classes, 17 SWRL rules) | ✅ |
| Functioning prototype — both flows end-to-end | ✅ |
| 30/30 automated tests passing | ✅ |
| Architecture documentation (`docs/ONTOLOGY_INTEGRATION.md`) | ✅ |

### Construction — Not yet started

**Goal:** Implement the complete system, reach beta release.

Planned deliverables:
- Extended vocabulary (Fraction, Equation, Trapezoid, additional verbs)
- AI pictogram generation as fallback (no ARASAAC match)
- Flutter state management (Riverpod)
- TeacherScreen UI/logic separation
- Widget and integration tests (Flutter)
- Structured logging

### Transition — Planned

**Goal:** Deployment, user validation, training.

Planned deliverables:
- Android/iOS beta on tablet
- User documentation (teachers, speech therapists)
- Demo video
- User testing sessions with children (LBA supervision)
- Final project report

---

## 6. Weekly Timeline

Approximately 12 working weeks, one day per week per team member, February–April 2026.

| Week | Period | Key Activities | Outputs |
|------|--------|---------------|---------|
| W1 | Early Feb | Project kickoff, requirements analysis with supervisors, CAA domain study | Initial scope, technology choices |
| W2 | | Literature review (ARASAAC, AAC, OWL ontologies), tool selection | Bibliography, PlantUML + Protégé setup |
| W3 | | Repository setup, first Use Case Diagram, initial domain glossary | Git repo, UC diagram, partial glossary |
| W4 | | First OWL T-Box skeleton in Protégé, Flutter project scaffold | `maths_v0.owl`, Flutter `main.dart` skeleton |
| W5 | | Whisper integration, first Python CLI prototype | `prototype_ecole.py` (offline mic + Whisper) |
| W6 | | First FastAPI server, hardcoded pictogram dictionary | `serveur_api.py` v1 (6-word dict) |
| W7 | | Flutter ↔ server HTTP communication, audio recording UI | `main.dart` with mic button + pictogram display |
| W8 | Mid-Mar | Architecture review, identification of OWL passivity gap | Refactoring plan, OWL enrichment requirements |
| W9 | | OWL structural bug fixes, French labels, arasaacId via ARASAAC API | `maths.owl` v2 (23 annotated classes) |
| W10 | | owlready2 + Pellet integration, 11 SWRL rules, `OntologyService` | `feature/owl-integration` (17/17 tests) |
| W11 | Early Apr | Needs cluster (11 classes), `ChildScreen`, dual-flow navigation | `feature/child-communication` (30/30 tests) |
| W12 | Late Apr | UML diagrams updated, `PROJECT_REPORT.md`, Elaboration closure | `docs/project-report` branch, PR |

---

## 7. Work Distribution — Actual Team (3 people)

The team of three operated with approximately one working day per week each, over 12 weeks — **~36 person-days** of total effort.

### Area 1 — Software Engineering and Architecture
Responsibilities: UML design, Unified Process methodology, repository management, cross-module integration, design pattern selection, code review, technical documentation.  
Key outputs: Use Case and Domain Model (Inception), Class and Sequence diagrams (Elaboration), `PROJECT_REPORT.md`, `README.md` architecture section, choice of Service Layer and Lifespan Singleton patterns.

### Area 2 — Backend and Intelligence
Responsibilities: FastAPI server, Whisper/spaCy integration, `OntologyService` implementation, Pellet debugging, ARASAAC CDN integration, pictogram caching, async handling.  
Key outputs: `serveur_api.py`, `ontology_service.py`, `conftest.py`, `requirements.txt`, `scripts/patch_owlready2_jars.py`, `tests/test_pipeline.py`, `tests/test_needs.py`.

### Area 3 — Domain Modelling and Ontology
Responsibilities: OWL ontology design in Protégé, class hierarchy, SWRL rule authoring, ARASAAC ID mapping, `maths.owl` maintenance, ontology integration documentation.  
Key outputs: `maths.owl` (62 classes, 17 rules, 34 arasaacIds), `analysis/arasaac_mapping.md`, `docs/ONTOLOGY_INTEGRATION.md`, `scripts/populate_arasaac_ids.py`.

**Note:** With 36 person-days of capacity, scope decisions were essential. The Elaboration phase deliberately excluded AI pictogram generation, full NLP disambiguation, and Flutter testing — all deferred to Construction.

---

## 8. Work Distribution — Ideal Team (6 people)

A team of 6 at one day/week × 12 weeks = **~72 person-days** — double the actual capacity.

### Role 1 — Project Manager / Scrum Master
**Responsibilities:** Stakeholder communication (LBA + ESIEE), backlog management, sprint facilitation, risk tracking, escalation of technical blockers.  
**Skills required:** Agile/UP, planning tools, soft skills.  
**Contribution:** Roadmap, sprint reviews, charter, retrospectives. Freed the technical team from coordination overhead.

### Role 2 — Software Architect / UML Designer
**Responsibilities:** Architectural decisions, UML diagram suite (UC, Class, Sequence, Domain), pattern governance (GRASP, GoF), code review for architectural consistency.  
**Skills required:** UP methodology, UML, design patterns, separation of concerns.  
**Contribution:** All 5 UML diagrams, layer design, `PROJECT_REPORT.md` sections 2 and 3, pattern selection rationale.

### Role 3 — Ontology Engineer
**Responsibilities:** OWL 2 design in Protégé, SWRL rule authoring, ARASAAC mapping, reasoner validation (HermiT/Pellet), glossary maintenance.  
**Skills required:** OWL 2, SWRL, Protégé, owlready2, knowledge engineering.  
**Contribution:** `maths.owl`, `DLSafeRule` axioms, `scripts/populate_arasaac_ids.py`, `docs/ONTOLOGY_INTEGRATION.md`.

### Role 4 — Backend / NLP Engineer
**Responsibilities:** FastAPI server, Whisper + spaCy integration, `OntologyService` implementation, async handling, REST API design, ARASAAC download logic.  
**Skills required:** Python, FastAPI, asyncio, NLP, REST API.  
**Contribution:** `serveur_api.py`, `ontology_service.py`, `requirements.txt`, `scripts/patch_owlready2_jars.py`.

### Role 5 — Mobile Developer (Flutter)
**Responsibilities:** UI/UX implementation, navigation, state management, microphone permissions, HTTP client, widget and integration tests.  
**Skills required:** Flutter, Dart, Material Design, Riverpod or Bloc, platform channels.  
**Contribution:** `HomeScreen`, `TeacherScreen`, `ChildScreen`, `AndroidManifest.xml`, `Info.plist`, `--dart-define` URL parametrisation, Flutter test suite (planned).

### Role 6 — AI / Generative & QA Engineer
**Responsibilities:** AI pictogram generation fallback (DALL-E or Stable Diffusion API) for concepts not covered by ARASAAC. QA: unit tests, integration tests, CI/CD pipeline, structured logging.  
**Skills required:** Generative AI APIs, prompt engineering, pytest, Flutter test, GitHub Actions.  
**Contribution:** AI generation pipeline, extended `tests/`, CI workflow (`.github/workflows/`), structured logging layer.

### Impact of a 6-Person Team
With 72 person-days:
- AI pictogram generation would reach Elaboration (not deferred to Construction)
- Flutter widget and integration tests would be available from Elaboration
- Vocabulary coverage would be broader (~100 concepts vs ~34 currently)
- UI polish and accessibility (font scaling, contrast) could be addressed
- User validation sessions with real children could start earlier (Elaboration end)

---

## 9. Known Limitations and Future Roadmap

### Current Prototype Limitations

| Limitation | Impact |
|-----------|--------|
| Flutter `setState` only (no state management) | No cross-screen state; each screen independent |
| No Flutter widget / integration tests | UI regressions not automatically caught |
| Teacher flow images served locally | Requires server running; images not available offline |
| AI pictogram generation absent | Concepts not in ARASAAC have no fallback image |
| NLP disambiguation partial | Single lemma–class mapping; polysemy not resolved |
| Vocabulary: ~34 annotated concepts | Far from target of 80; key verbs (lire, écouter) missing |
| Logging: print() only | No structured logs; debugging in production is difficult |
| No upload MIME validation | Any file accepted as audio by `/api/transcrire` |

### Limitations of the Model (discrepancies between spec and implementation)

- **`/needs` endpoint exists but is unused:** `GET /needs` and `OntologyService.get_needs_grouped()` are implemented in the backend, but `ChildScreen` was refactored to load images directly from the ARASAAC CDN with hardcoded data — eliminating the server dependency for Flow 2. The endpoint remains available for future integration.
- **Flow 2 needs data is hardcoded in Dart:** The 11 `NeedItem` constants in `child_screen.dart` must be manually updated when the ontology changes. An automated sync script would be needed at scale.
- **`ApiService` does not exist as a class:** HTTP calls are inline in `TeacherScreen._envoyerAudioAuServeur()`. Extraction into a dedicated service class is a Construction-phase refactoring.

### Construction Phase Roadmap

**Priority High:**
1. AI pictogram generation (DALL-E API) as fallback when ARASAAC returns no result
2. Flutter state management with Riverpod (cross-screen pictogram history)
3. Refactor `TeacherScreen` — extract API call to `ApiService`
4. Flutter widget and integration tests

**Priority Medium:**
5. Vocabulary extension: Read (lire), Listen (écouter), Color (colorier), Fraction, Equation
6. `ChildScreen` fed by live API call instead of hardcoded constants
7. TTS for student communication board (read label aloud)
8. Structured logging (Python `logging` module + Flutter `logger` package)
9. GitHub Actions CI (run pytest on every push)

**Priority Low:**
10. MIME validation for audio upload
11. Offline mode (local SQLite cache for pictograms)
12. Accessibility (font scaling, high-contrast mode)
13. Internationalisation beyond French

### Transition Phase Roadmap

- Android and iOS beta release on tablet hardware
- User documentation for teachers and speech therapists
- Demo video (2–3 minutes)
- User testing with children under LBA supervision
- Final academic report

---

## UML Diagrams

All `.puml` files are in [`docs/uml/`](uml/). Render to PNG with:

```bash
plantuml docs/uml/*.puml
```

| Diagram | File |
|---------|------|
| Use Case Diagram | [use_case_diagram.puml](uml/use_case_diagram.puml) |
| Class Diagram | [class_diagram.puml](uml/class_diagram.puml) |
| Sequence — Teacher Flow | [sequence_teacher_flow.puml](uml/sequence_teacher_flow.puml) |
| Sequence — Child Flow | [sequence_child_flow.puml](uml/sequence_child_flow.puml) |
| Domain Model | [domain_model.puml](uml/domain_model.puml) |
