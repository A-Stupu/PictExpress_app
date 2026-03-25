# UML Artifacts — Pictograme App (School Context)

Foundational UML artifacts produced during the **Inception phase** of the Unified Process (UP).

---

## 1. Use Case Diagram

**File:** `use_case_diagram.puml`

### Scope
School context only. The app converts spoken language into a sequence of pictograms in real time — no manual board assembly.

### Actors

- **Teacher** — converts speech to pictograms, saves results and shares them with students.
- **Support Teacher** — inherits all Teacher capabilities via generalisation (`ST --|> T`); can additionally add custom pictograms to the library.
- **Student** — converts speech to pictograms; views sequences shared by teachers.
- **System Admin** — manages user accounts and the pictogram library.
- **Speech-to-Text Service** *(external)* — transcribes recorded audio to text.
- **Pictogram DB / ARASAAC** *(external)* — queried to match transcribed words to pictograms.

### Use Cases

**Core: Speech to Pictogram** — the primary flow shared by all users:
- Convert Speech to Pictogram(s)
- Record Voice Input
- Transcribe Speech to Text
- Match Text to Pictogram(s)
- Display Pictogram Sequence
- Edit Generated Sequence

**Saved Sequences** — actions available after a conversion:
- Save Sequence
- View Saved Sequence
- Share Sequence with Student
- Export / Print Sequence

**Customisation** *(Support Teacher only)*:
- Add Custom Pictogram

**Administration** *(System Admin only)*:
- Manage User Accounts
- Manage Pictogram Library

### Core Flow

```
User speaks
  → [include] Record Voice Input
  → [include] Transcribe Speech to Text  ──► Speech-to-Text Service
  → [include] Match Text to Pictogram(s) ──► ARASAAC
  → [include] Display Pictogram Sequence
  → [extend]  Edit Generated Sequence    (optional)
  → [extend]  Save Sequence              (optional)
```

---

## 2. Domain Model

**File:** `domain_model.puml`

Identifies the conceptual classes, their attributes, and relationships. Not a design diagram — captures the vocabulary of the problem domain.

### Classes

- **User** — base concept for all authenticated users; specialised into `Teacher`, `SupportTeacher`, `Student`, and `Administrator`.
- **SpeechConversion** — one voice-to-pictogram conversion event; stores the audio reference, the transcribed text, date, and language.
- **SequenceEntry** — one element of the conversion output; binds an order index and a word/phrase to the resolved pictogram.
- **SavedSequence** — optional named snapshot of a conversion result that can be retrieved and shared with students.
- **Pictogram** — a visual symbol with label, image URL, and tags; sourced from ARASAAC or uploaded as a custom image.
- **CustomPictogram** — extends `Pictogram` with a user-supplied image path; created by Teacher or Support Teacher.
- **PictogramCategory** — thematic grouping (e.g., Actions, Emotions) for organising the library.
- **PictogramLibrary** — system-wide catalogue of standard pictograms, managed by Administrator.

### Core Flow

```
User
  initiates ──► SpeechConversion
                  produces ──► SequenceEntry (ordered)
                                 resolved to ──► Pictogram
                  saved as ──► SavedSequence
                                 shared with ──► Student
```

---

## Rendering the Diagrams

- **VS Code**: [PlantUML extension](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)
- **Online**: paste content into [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/)
- **CLI**: `plantuml <filename>.puml`

---

## Next Artifacts (Elaboration Phase)

- **System Sequence Diagrams (SSD)** — one per main scenario (e.g., Convert Speech to Pictogram)
- **Contracts** — pre/post-conditions for system operations
- **Logical Architecture** — layer diagram (UI, Application, Domain, Infrastructure)
- **Design Class Diagram (DCD)** — refined from the domain model with GRASP/GoF patterns
