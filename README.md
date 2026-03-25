# Pict'Express — School Pictogram Translation System

A research application that automatically translates French sentences into pictogram sequences to support communication with autistic children and students with speech/language difficulties.

**Supervisors**: Adrien UGON, Akram REDJDAL  
**Institutions**: Laboratoire de Biomécanique Appliquée (LBA, Marseille), ESIEE Paris

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
PictExpress_app/
├── README.md                                    <- This file
├── docs/
│   ├── ONTOLOGY_DEVELOPMENT_GUIDE.md           <- Step-by-step guide (this phase)
│   ├── uml/
│   │   ├── README.md                            <- UML artifacts guide
│   │   ├── use_case_diagram.puml                - COMPLETED
│   │   └── domain_model.puml                    - COMPLETED
│   ├── domain/
│   │   ├── README.md
│   │   └── domain_glossary.md                   <- 50–80 concepts (in progress)
│   ├── ontology/
│   │   ├── README.md
│   │   ├── ARCHITECTURE.md                      <- OWL design decisions (in progress)
│   │   ├── pict-express-v0.1.owl                <- Schema (skeleton)
│   │   ├── pict-express-v0.6.owl                <- Final ontology (target)
│   │   └── examples/
│   │       └── sample_instances.owl             <- Usage examples
│   └── ontology-setup/
│       ├── OWL_PRIMER.md                        <- OWL cheat sheet (in progress)
│       └── PROTEGE_SETUP.md                     <- Protégé setup guide
```

---

## Methodology

The project follows the **Unified Process (UP)** with team co-ownership across four phases:

### Inception — COMPLETED
**Deliverables**:
- Use Case Diagram (school context scope, 6 actors, core use case flows)
- Domain Model (8 conceptual classes and relationships)
- Project charter and scope definition

### Initiation: Ontology — IN PROGRESS
**Deliverables**:
- Domain glossary (50–80 concepts with French synonyms and OWL class names)
- OWL ontology structure (Phase 1–5: setup, core concepts, properties, rules, validation)
- SWRL reasoning rules for semantic disambiguation
- Integration guide for downstream teams

### Elaboration — PENDING
**Deliverables**:
- System Sequence Diagrams (SSD) for key use cases
- Design Contracts (preconditions, postconditions, invariants)
- Logical Architecture (detailed layer interactions)
- NLP ↔ Ontology mapping specifications

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

## Completed Deliverables (Inception Phase)

###  UML Artifacts
- **Use Case Diagram** ([docs/uml/use_case_diagram.puml](docs/uml/use_case_diagram.puml))
  - School context scope
  - 6 actors: Teacher, Support Teacher, Student, System Admin, Speech-to-Text Service, ARASAAC DB
  - Core use case: "Convert Speech to Pictogram" with supporting flows

- **Domain Model** ([docs/uml/domain_model.puml](docs/uml/domain_model.puml))
  - 8 conceptual classes: User, SpeechConversion, SequenceEntry, SavedSequence, Pictogram, CustomPictogram, PictogramCategory, PictogramLibrary
  - Relationships: initiates, produces, resolved to, saved as, shared with

### Documentation
- **Artifact Guide** ([docs/uml/README.md](docs/uml/README.md)) — Rendering instructions & artifact descriptions

---

## In-Progress: Ontology Development (Current Phase)

### Target Deliverable
A complete **OWL ontology** encoding the school domain with:
- ~50–80 core concepts organized hierarchically
- Object properties for semantic relationships (performedBy, usesObject, locatedIn, etc.)
- SWRL reasoning rules for disambiguation (e.g., resolve "maître" → Teacher in school context)
- Full validation (zero inconsistencies, reasoner tests passed)

### Key Foundation
- **domain_glossary.md** — vocabulary bridge for all team members
  - Concept | Category | French Synonyms | OWL Class Name
  - Enables parallel work: Member 2 builds ontology, Member 3 maps pictograms
  - Versioned together with ontology

### Development Steps (See [ONTOLOGY_DEVELOPMENT_GUIDE.md](docs/ONTOLOGY_DEVELOPMENT_GUIDE.md))

**Phase 1: Setup & Training**
1. Install Protégé
2. OWL fundamentals training
3. Define ontology architecture (top-level classes, properties)

**Phase 2: Iteration 1 — Core Concepts**
4. Collect 50 domain concepts → draft domain_glossary.md
5. Create OWL schema in Protégé (classes, properties)
6. Populate with 50 individuals + validation
7. Review checkpoint (feedback cycle)

**Phase 3: Iteration 2 — Properties & Rules**
8. Add relational properties (performedBy, locatedIn, usesObject, etc.)
9. Add disjointness axioms and cardinality constraints
10. Write 5–10 SWRL rules for semantic disambiguation
11. Test with reasoner (HermiT) — ensure consistency

**Phase 4: Documentation & Handoff**
12. Export final ontology
13. Create README + examples + SPARQL queries
14. Brief Member 1 (arch implications) and Member 3 (pictogram mapping)

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
