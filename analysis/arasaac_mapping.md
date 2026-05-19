# ARASAAC ID Mapping

IDs retrieved **2026-05-07** via `https://api.arasaac.org/api/pictograms/fr/search/{keyword}` (first result).

All IDs can be verified at `https://arasaac.org/pictograms/{id}`.

## Confidence Legend

| Symbol | Meaning |
|--------|---------|
| HIGH | First result is unambiguous and correct |
| MED | Multiple plausible results; first result accepted after visual check |
| LOW | Requires manual confirmation |

## Mapping Table

| OWL Class | French Label(s) | ARASAAC ID | Confidence | Notes |
|-----------|----------------|-----------|------------|-------|
| Circle | cercle | 4603 | HIGH | Geometric circle |
| Square | carré | 4616 | HIGH | Geometric square |
| Triangle | triangle | 4763 | HIGH | Geometric triangle |
| Compass | compas | 34065 | HIGH | Geometry compass tool |
| Ruler | règle | 2815 | MED | "règle" = ruler, but also means "rule/norm" — confirmed as ruler by visual inspection |
| SetSquare | équerre | 7088 | HIGH | Set square / triangle ruler |
| Pencil | crayon | 2440 | HIGH | Pencil |
| Eraser | gomme | 2409 | HIGH | Eraser |
| Notebook | cahier | 2359 | HIGH | School notebook |
| Calculator | calculatrice | 5419 | HIGH | Calculator device |
| Draw | tracer | 5506 | HIGH | Primary label "tracer"; secondary "dessiner" not searched separately |
| Calculate | calculer | 8518 | HIGH | To calculate |
| Count | compter | 2714 | HIGH | To count |
| Measure | mesurer | 5510 | HIGH | To measure |
| Write | écrire | 2380 | HIGH | To write |
| Erase | effacer | 2286 | HIGH | To erase |
| Cut | couper | 5975 | HIGH | To cut |
| Addition | addition | 5868 | HIGH | Addition operation |
| Subtraction | soustraction | 5841 | HIGH | Subtraction operation |
| Number | nombre | 34771 | MED | Generic "number" concept; verify pictogram is appropriate for context |
| Student | élève | 5899 | HIGH | School student/pupil |
| Teacher | professeur | 6556 | HIGH | Teacher |
| Assistant | assistant | 38378 | MED | Classroom assistant; verify this is the school-context image |

## Needs Mapping (added in feature/child-communication)

IDs retrieved 2026-05-07 via the same ARASAAC API endpoint.

**Note on label swap:** After the initial mapping, the display labels for `DoNotUnderstand` (11697) and `IUnderstand` (37827) were swapped in `child_screen.dart` to match the actual ARASAAC images. The IDs below are correct; the class names reflect the OWL hierarchy.

| OWL Class | French Label (display) | ARASAAC ID | Confidence | Notes |
|-----------|----------------------|-----------|------------|-------|
| DoNotUnderstand | "Je ne comprends pas" | 11697 | MED | Keyword: "comprendre" |
| IUnderstand | "J'ai compris" | 37827 | MED | Keyword: "compris" (past form) |
| IFinish | "J'ai fini" | 5358 | HIGH | |
| IsItGood | "C'est bien ?" | 5397 | MED | "bien" is polysemous; verify at arasaac.org/5397 |
| Tired | "Fatigué" | 35537 | HIGH | |
| NeedBreak | "Pause" | 27339 | HIGH | |
| TooMuchNoise | "Trop de bruit" | 7157 | HIGH | |
| Hungry | "J'ai faim" | 35559 | HIGH | |
| Thirsty | "J'ai soif" | 7273 | HIGH | |
| NeedToilet | "Toilettes" | 5921 | HIGH | |
| Hurt | "J'ai mal" | 30620 | MED | "mal" is ambiguous; verify at arasaac.org/30620 |

## Classes Without arasaacId (not in primary pipeline)

These classes exist in the ontology but have no pictogram ID because they are
abstract categories not directly surfaced to users:

`Actions`, `MathAction`, `ManualAction`, `MathematicalConcept`, `GeometricShape`,
`GeometryTool`, `BasicTool`, `CalculationTool`, `SchoolMaterial`, `CalculationMethod`,
`Magnitude`, `MathOperation`, `Needs`, `PhysicalNeed`, `HelpNeed`, `MentalNeed`,
`ValidationNeed`, `Person`, `Bigger`, `Equal`, `Smaller`, `Hands`, `Mind`

## How to Add New Classes

1. Add the class to `maths.owl` with `rdfs:label@fr`
2. Run `python scripts/populate_arasaac_ids.py --dry-run` to preview
3. If the result looks wrong, add a manual override in `MANUAL_OVERRIDES`
4. Run without `--dry-run` to persist
