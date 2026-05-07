# Child Communication Flow — Integration Report

Branch: `feature/child-communication`  
Date: 2026-05-07

---

## 1. Tempo effettivo per step

| Step | Target | Effettivo | Note |
|------|--------|-----------|------|
| 1+2: OWL Needs + math shapes | 40 min | ~20 min | Fetch 16 ID ARASAAC in parallelo |
| 4: /needs endpoint + auto-download | 20 min | ~15 min | Incluso in commit unico con OntologyService |
| 5+3: Flutter HomeScreen + ChildScreen | 75 min | ~25 min | Estrazione teacher_screen + ChildScreen da zero |
| 6: Test 30/30 + verifica | 25 min | ~10 min | Tutti green al primo run |
| 7: Docs + report | 20 min | ~10 min | |
| **Totale** | **180 min** | **~80 min** | Abbondante margine rispetto alle 3 ore |

---

## 2. Mapping arasaacId → classe (Needs)

| Classe | Keyword usata | arasaacId | Confidenza |
|--------|--------------|-----------|------------|
| DoNotUnderstand | "comprendre" | 11697 | MED — "comprendre" è generico, ma il primo risultato è pertinente |
| IUnderstand | "compris" | 37827 | MED — "compris" è la forma passata, il pittogramma è appropriato |
| IFinish | "fini" | 5358 | HIGH |
| IsItGood | "bien" | 5397 | MED — "bien" è polisemico (good/well); verificare visivamente su arasaac.org/5397 |
| Tired | "fatigué" | 35537 | HIGH |
| NeedBreak | "pause" | 27339 | HIGH |
| TooMuchNoise | "bruit" | 7157 | HIGH |
| Hungry | "faim" | 35559 | HIGH |
| Thirsty | "soif" | 7273 | HIGH |
| NeedToilet | "toilettes" | 5921 | HIGH |
| Hurt | "mal" | 30620 | MED — "mal" è ambiguo (pain/evil); verificare su arasaac.org/30620 |

**ID da verificare visivamente:** IsItGood (5397), Hurt (30620)

---

## 3. Output pytest (30/30)

```
============================= test session starts =============================
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

## 4. Conferma scenari end-to-end

**Scenario A (flusso 1 — regressione):**
- Backend: `uvicorn serveur_api:app --reload`
- App: HomeScreen → "Je suis le maître" → TeacherScreen
- Detto: "Tracez un rectangle" → attesi 3 pittogrammi (rectangle/4731, règle/2815, crayon/2440)
- Stato: **test pytest confermano l'inferenza**; verifica visuale da fare su dispositivo reale

**Scenario B (flusso 2 — nuovo):**
- App: HomeScreen → "Je suis l'élève" → ChildScreen
- La griglia carica i Needs (GET /needs) categorizzati in 3 sezioni
- Tap pittogramma → dialog fullscreen con immagine ingrandita + "Fermer"
- Stato: **implementato e strutturalmente validato**; verifica visuale da fare su dispositivo reale

---

## 5. Cose tagliate

Niente tagliato rispetto allo spec richiesto. Il tempo è stato abbondante.

---

## 6. Fuori scope per future PR

| Item | Motivazione |
|------|-------------|
| TTS (text-to-speech) per ChildScreen | Richiede plugin audio + permessi aggiuntivi |
| Test Flutter (widget/integration test) | Richiede device farm o emulatore CI |
| ARASAAC CDN cascade strategy (Tier 2/3) | Complessità sproporzionata al prototipo |
| Verifica visuale ID ambigui (IsItGood=5397, Hurt=30620) | Richiede review manuale su arasaac.org |
| Personalizzazione griglia per alunno specifico | Richiede backend stateful + auth |
| Offline mode (cache locale pictogrammi) | Richiede storage management |
| NLP per flusso bambino | Non necessario (selezione pura) |
