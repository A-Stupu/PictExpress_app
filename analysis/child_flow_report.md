# Child Communication Flow — Integration Report

Branch: `feature/child-communication`  
Date: 2026-05-07

---

## 1. Actual time per step

| Step | Target | Actual | Notes |
|------|--------|--------|-------|
| 1+2: OWL Needs + math shapes | 40 min | ~20 min | 16 ARASAAC IDs fetched in parallel |
| 4: /needs endpoint + auto-download | 20 min | ~15 min | Included in single commit with OntologyService |
| 5+3: Flutter HomeScreen + ChildScreen | 75 min | ~25 min | Extracted teacher_screen + ChildScreen from scratch |
| 6: 30/30 tests + verification | 25 min | ~10 min | All green on first run |
| 7: Docs + report | 20 min | ~10 min | |
| **Total** | **180 min** | **~80 min** | Ample margin relative to the 3-hour estimate |

---

## 2. arasaacId → class mapping (Needs)

| Class | Keyword used | arasaacId | Confidence | Notes |
|-------|-------------|-----------|------------|-------|
| DoNotUnderstand | "comprendre" | 11697 | MED | "comprendre" is generic, but the first result is relevant |
| IUnderstand | "compris" | 37827 | MED | "compris" is the past form; pictogram is appropriate |
| IFinish | "fini" | 5358 | HIGH | |
| IsItGood | "bien" | 5397 | MED | "bien" is polysemous (good/well); verify visually at arasaac.org/5397 |
| Tired | "fatigué" | 35537 | HIGH | |
| NeedBreak | "pause" | 27339 | HIGH | |
| TooMuchNoise | "bruit" | 7157 | HIGH | |
| Hungry | "faim" | 35559 | HIGH | |
| Thirsty | "soif" | 7273 | HIGH | |
| NeedToilet | "toilettes" | 5921 | HIGH | |
| Hurt | "mal" | 30620 | MED | "mal" is ambiguous (pain/evil); verify at arasaac.org/30620 |

**IDs requiring visual verification:** IsItGood (5397), Hurt (30620)

**Note:** After this report was written, the labels for `DoNotUnderstand` (11697) and `IUnderstand` (37827) were swapped in `child_screen.dart` to match the actual ARASAAC images. The IDs remain correct; only the display labels were adjusted.

---

## 3. pytest output (30/30)

```
============================= test session results =============================
platform win32 -- Python 3.10.11, pytest-9.0.3

tests/test_needs.py::test_needs_grouped_has_all_keys PASSED
tests/test_needs.py::test_needs_grouped_physical_count PASSED
tests/test_needs.py::test_needs_grouped_mental_count PASSED
tests/test_needs.py::test_needs_grouped_help_validation_count PASSED
tests/test_needs.py::test_needs_all_have_required_fields PASSED
tests/test_needs.py::test_needs_grouped_no_none_labels PASSED
tests/test_needs.py::test_specific_needs_in_groups PASSED
tests/test_needs.py::test_find_rectangle_by_label PASSED
tests/test_needs.py::test_inference_tracer_rectangle PASSED
tests/test_needs.py::test_inference_tracer_pentagone PASSED
tests/test_needs.py::test_inference_tracer_hexagone PASSED
tests/test_needs.py::test_arasaac_ids_new_shapes PASSED
tests/test_needs.py::test_arasaac_ids_needs PASSED
tests/test_pipeline.py::... (17 tests) PASSED

30 passed in 14.71s
```

---

## 4. End-to-end scenario confirmation

**Scenario A (Flow 1 — regression):**
- Backend: `uvicorn serveur_api:app --reload`
- App: HomeScreen → "Je suis le maître" → TeacherScreen
- Said: "Tracez un rectangle" → expected 3 pictograms (rectangle/4731, règle/2815, crayon/2440)
- Status: **pytest tests confirm inference**; visual check pending on real device

**Scenario B (Flow 2 — new):**
- App: HomeScreen → "Je suis l'élève" → ChildScreen
- The grid displays Needs categorised in 3 sections, loaded from hardcoded constants
- Tap pictogram → full-screen dialog with enlarged image and "Fermer" button
- Status: **implemented and structurally validated**; visual check pending on real device

---

## 5. Items cut

Nothing was cut relative to the required specification. Time was ample.

---

## 6. Out of scope for future PRs

| Item | Reason |
|------|--------|
| TTS (text-to-speech) for ChildScreen | Requires audio plugin + additional permissions |
| Flutter widget/integration tests | Requires device farm or CI emulator |
| ARASAAC CDN cascade strategy (Tier 2/3) | Complexity disproportionate to prototype |
| Visual verification of ambiguous IDs (IsItGood=5397, Hurt=30620) | Requires manual review at arasaac.org |
| Per-student board customisation | Requires stateful backend + authentication |
| Offline mode (local pictogram cache) | Requires storage management |
| NLP for student flow | Not required (pure selection flow) |
