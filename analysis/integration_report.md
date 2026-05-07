# OWL Integration Report

Branch: `feature/owl-integration`  
Date: 2026-05-07  
Author: Claude Sonnet 4.6 (pair-programming session with Andrei Stupu)

---

## 1. What was done in each step

| Step | Commit | Summary |
|------|--------|---------|
| Step 0 | `2438dba` | Baseline analysis (`analysis/owl_baseline.md`): 51 classes, 8 object properties, 7 structural bugs documented |
| Steps 1–3 | `c42d85f` | OWL structural fixes + French labels + arasaacId |
| Step 3 (support) | `d6fc678` | `scripts/populate_arasaac_ids.py` + `analysis/arasaac_mapping.md` |
| Step 9 | `694dc1a` | Non-OWL critical fixes (mic permissions, URL param, Whisper async, requirements.txt) |
| Pre-condition | `bdd8c11` | Pellet smoke test + JAR patch (`scripts/patch_owlready2_jars.py`) |
| Steps 5–8 | `7cdaa61` | SWRL rules in OWL + OntologyService + pictogram rename + 17/17 tests |

---

## 2. OWL changes (conceptual diff)

### Bug fixes

| Bug | Before | After |
|-----|--------|-------|
| Plural class name | `MathematicalConcepts` | `MathematicalConcept` |
| French misspelling | `Soustraction` | `Subtraction` |
| French misspelling | `Mesure` | `Measure` |
| Wrong hierarchy | `Hands, Mind` under `CalculationTool → SchoolMaterial` | `Hands, Mind` under new `CalculationMethod` (top-level) |
| Empty domain bug | Two `ObjectPropertyDomain` for `isPerformedBy` → interpreted as `Actions ∩ Needs = ∅` | Single `ObjectPropertyDomain` with `ObjectUnionOf(Actions, Needs)` |
| Same bug | Two domains for `isRequestedBy` → `Assistant ∩ Teacher = ∅` | `ObjectUnionOf(Assistant, Teacher)` |
| Same bug (range) | Two `ObjectPropertyRange` for `performsAction` → `Actions ∩ Needs = ∅` | `ObjectUnionOf(Actions, Needs)` |
| Same bug (range) | Two ranges for `requestHelpFrom` → `Assistant ∩ Teacher = ∅` | `ObjectUnionOf(Assistant, Teacher)` |
| Functional wrong | `FunctionalObjectProperty(isPerformedBy)` | Removed |
| InvFunctional wrong | `InverseFunctionalObjectProperty(performsAction)` | Removed |
| Redundant | 6 `IrreflexiveObjectProperty` (implied by Asymmetric in OWL 2) | Removed |

### Additions

| What | Count/Detail |
|------|-------------|
| New top-level class | `CalculationMethod` |
| French `rdfs:label@fr` | 27 annotations on 23 classes (some have synonyms) |
| `#arasaacId` AnnotationProperty | Declared + 23 integer values |
| `#hasTarget` ObjectProperty | domain: Actions, range: MathematicalConcept |
| `#requires` ObjectProperty | domain: Actions, range: SchoolMaterial |
| Tool singleton individuals | 7: theCompass, thePencil, theRuler, theSetSquare, theCalculator, theNotebook, theEraser |
| `DLSafeRule` SWRL rules | 11 rules (Draw+Circle→Compass+Pencil, Draw+Square→Ruler+Pencil, etc.) |

### Final stats

| Metric | Before | After |
|--------|--------|-------|
| Classes | 51 | 52 (+CalculationMethod, -Mesure/Soustraction/MathematicalConcepts as renames) |
| Object properties | 8 | 10 (+hasTarget, +requires) |
| French labels | 0 | 27 |
| arasaacId annotations | 0 | 23 |
| DLSafeRules | 0 | 11 |
| Named individuals | 0 | 7 |

---

## 3. New backend files

| File | Purpose |
|------|---------|
| `ontology_service.py` | `OntologyService` class: load, label index, arasaacId index, Pellet inference |
| `serveur_api.py` (modified) | Replaces `interroger_ontologie()` with `OntologyService`; adds lifespan startup; Whisper async |
| `requirements.txt` | All backend dependencies |
| `scripts/patch_owlready2_jars.py` | Fix owlready2 0.50 JAR incompatibility with Java < 25 |
| `scripts/test_pellet.py` | Smoke test: verifies SWRL rule fires |
| `scripts/populate_arasaac_ids.py` | Queries ARASAAC API and updates arasaacId annotations |
| `scripts/rename_pictograms.py` | Renames PNG files from semantic names to `{arasaacId}.png` |
| `tests/test_pipeline.py` | 17 pytest tests |

---

## 4. Test results

```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.0.3
collected 17 items

tests/test_pipeline.py::test_find_class_by_label_circle PASSED
tests/test_pipeline.py::test_find_class_by_label_case_insensitive PASSED
tests/test_pipeline.py::test_find_class_by_label_unknown_returns_none PASSED
tests/test_pipeline.py::test_find_class_by_label_draw_tracer PASSED
tests/test_pipeline.py::test_find_class_by_label_draw_dessiner PASSED
tests/test_pipeline.py::test_arasaac_id_circle PASSED
tests/test_pipeline.py::test_arasaac_id_compass PASSED
tests/test_pipeline.py::test_arasaac_id_pencil PASSED
tests/test_pipeline.py::test_inference_tracer_cercle PASSED
tests/test_pipeline.py::test_inference_tracer_cercle_arasaac_ids PASSED
tests/test_pipeline.py::test_inference_tracer_carre PASSED
tests/test_pipeline.py::test_inference_tracer_triangle PASSED
tests/test_pipeline.py::test_no_inference_without_verb PASSED
tests/test_pipeline.py::test_inference_ecrire PASSED
tests/test_pipeline.py::test_inference_effacer PASSED
tests/test_pipeline.py::test_inference_calculer PASSED
tests/test_pipeline.py::test_inference_unknown_lemma_returns_empty PASSED

============================= 17 passed in 8.20s ==============================
```

All 17 tests pass. The critical discriminator test (`test_no_inference_without_verb`) confirms that SWRL (Opzione B) fires only when both the action verb AND the concept are present — unlike OWL existential restrictions which would fire on the concept alone.

---

## 5. Problems encountered and how they were resolved

### Problem 1: Pellet JAR incompatibility with Java 21

**Symptom:** `UnsupportedClassVersionError: class version 69.0 … recognizes up to 65.0`

**Root cause:** owlready2 0.50 ships `jena-arq-fixed2.10.0.jar` with three `LangRDFXML` classes compiled for Java 25 (class version 69). Java 21 supports only up to class version 65.

**Fix:** Download the original `jena-arq-2.10.0.jar` from Maven Central, extract the three affected classes (compiled for Java 6), and replace them in the owlready2 JAR. Automated via `scripts/patch_owlready2_jars.py`. Backup of original JAR at `jena-arq-fixed2.10.0.jar.bak_java25`.

### Problem 2: owlready2 does not parse DLSafeRule from OWL/XML

**Symptom:** After loading `maths.owl`, `list(onto.rules())` returned `[]` despite 11 `DLSafeRule` elements being present.

**Root cause:** owlready2 uses the older SWRL RDF vocabulary (`swrl:Imp`, `swrl:body`, etc.) internally; it does not parse the OWL 2 XML `DLSafeRule` element when loading OWL/XML files.

**Fix:** `OntologyService._parse_swrl_rules()` uses `xml.etree.ElementTree` to read `DLSafeRule` elements from the raw OWL/XML file and converts each one to an owlready2 `Imp().set_as_rule(str)` call at load time. This keeps `maths.owl` as the source of truth (Protégé-readable DLSafeRule) while making owlready2+Pellet execute the rules at runtime.

### Problem 3: Windows file URI resolution bug in owlready2

**Symptom:** `get_ontology("file:///C:/path/maths.owl").load()` → `OSError: [Errno 22] Invalid argument: '/C:/path/maths.owl'` (leading slash added to Windows drive letter).

**Fix:** Copy the OWL file to a temp directory using the filename matching the ontologyIRI (`math.owl`), then append that directory to `owlready2.onto_path` and load by HTTP IRI. owlready2 resolves the IRI to the local file via `onto_path`.

---

## 6. Out of scope (remaining work)

| Item | Why deferred |
|------|-------------|
| ARASAAC API live client | Requires handling rate limits, caching, license headers |
| Auto-download CDN pictograms | Depends on ARASAAC API client |
| Full NLP disambiguation (polysemy) | Requires larger training corpus and NER fine-tuning |
| Flutter state management | Mobile team's responsibility (Member 3) |
| Full Flutter UI test coverage | Requires device farm or emulator CI |
| Protégé SWRL verification | Protégé uses HermiT by default; Pellet plugin is optional. SWRL fires via Pellet in tests but was not separately verified in Protégé GUI. |
| Step 10: production PR | Documentation committed; PR to be opened after team review |
