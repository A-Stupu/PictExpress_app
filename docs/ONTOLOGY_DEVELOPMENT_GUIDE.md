# OWL Ontology Development Guide for Pict'Express

## Overview

This guide provides a step-by-step process to develop the OWL ontology for the Pict'Express system. The ontology is the semantic backbone of the Domain Layer and encodes the school domain (50–80 concepts) to support Named Entity Recognition (NER) and reasoning-based disambiguation.

---

## Phase 1: Setup and Training

### Step 1.1: Technical Setup

**Objective**: Install and configure all required tools.

1. **Install Protégé**
   - Download Protégé 5.x from [protege.stanford.edu](https://protege.stanford.edu)
   - Install following official instructions
   - Verify installation by launching Protégé

3. **Repository Setup**
   - Clone the Pict'Express repository
   - Create a new branch: `git checkout -b ontology/development` or use github desktop to create a new branch
   - Create directory structure:
     ```bash
     mkdir -p docs/domain docs/ontology docs/ontology-setup
     ```

### Step 1.2: OWL Fundamentals Training

**Key Topics to Cover**
   - Classes and hierarchies (subclass, disjointness)
   - Object properties (domain, range, cardinality, inverse)
   - Data properties (functional, inverse functional)
   - Individuals (instances) and their properties
   - Logical constraints (allValuesFrom, someValuesFrom, hasValue)
   - SWRL rules (basics for reasoning)
   - How reasoners work (HermiT, Pellet)

**Deliverable: OWL_PRIMER.md**
   - Create `docs/ontology-setup/OWL_PRIMER.md`
   - Summarize key concepts with mini-examples
   - Include Pict'Express-specific patterns (e.g., how to model an Action with performedBy property)
   - This becomes a quick reference during ontology building


### Step 1.3: Define Ontology Architecture

**Objective**: Agree on the structure before building.

1. **Macro-Categories**
   - Decide top-level class hierarchy:
     - `DomainConcept` (root)
     - `Action` (e.g., eating, reading, sitting)
     - `Object` (e.g., book, pencil, backpack)
     - `Person` (e.g., teacher, student, janitor)
     - `Location` (e.g., classroom, hallway, gym)
     - `TimeMarker` (e.g., now, morning, after)

2. **Granularity Decisions**
   - **Question**: Should `eating` be a single class `EatingAction`, or a generic `Action` with a `type` property?
   - **Decision**: Use specific subclasses (`EatingAction`, `ReadingAction`) for clarity and to enable precise reasoner rules.

3. **Shared Properties**
   - **Object Properties**:
     - `performedBy` (range: Person)
     - `usesObject` (range: Object)
     - `locatedIn` (range: Location)
     - `temporalMarker` (range: TimeMarker)
     - `partOf` (for composition)
   - **Data Properties**:
     - `label_FR` (xsd:string) — French label
     - `label_EN` (xsd:string) — English label for ARASAAC mapping
     - `definition` (xsd:string) — description
   - **Functional Properties**:
     - `label_FR` is functional (one French label per concept)

4. **Deliverable: ARCHITECTURE.md**
   - Create `docs/ontology/ARCHITECTURE.md`
   - Document the decisions above
   - Include a small diagram (e.g., ASCII tree of DomainConcept hierarchy)
   - Explain why each property exists (link to use case in NLP/reasoning)

---

## Phase 2: Building the Ontology — Iteration 1 (Core Concepts)

### Step 2.1: Collect Domain Vocabulary

1. **Brainstorm by Category**
   - **Actions** (~12 concepts):
     - eat, drink, read, write, sit, stand, go out, sleep, play, run, listen, raise hand
   - **Objects** (~12 concepts):
     - book, pen, pencil, notebook, backpack, table, chair, door, window, blackboard, desk, eraser
   - **Persons** (~6 concepts):
     - teacher, student, janitor, parent, friend, classmate
   - **Locations** (~6 concepts):
     - classroom, hallway, bathroom, gym, cafeteria, playground
   - **Time Markers** (~4 concepts):
     - now, morning, today, after

2. **French Synonyms**
   - For each concept, collect 2–3 French synonyms:
     - `eat` → manger, déjeuner, dîner
     - `teacher` → enseignant, maître, prof
     - `classroom` → classe, salle, salle de classe

3. **Deliverable: domain_glossary.md**
   - Create `docs/domain/domain_glossary.md`
   - Structure as a table:

   ```markdown
   | Concept      | Category   | Synonyms FR            | OWL Class Name    | Notes |
   |--------------|-----------|------------------------|-------------------|-------|
   | eat          | Action    | manger, déjeuner, dîner | EatingAction      | Core  |
   | book         | Object    | livre, manuel          | Book              | Core  |
   | teacher      | Person    | enseignant, maître     | Teacher           | Core  |
   | classroom    | Location  | classe, salle          | Classroom         | Core  |
   | now          | TimeMarker| maintenant, tout suite | Now               | Temp. |