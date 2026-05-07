# OWL Baseline — maths.owl (before feature/owl-integration)

Captured at branch creation, commit `eb4d35a`.

## Summary

| Metric | Value |
|--------|-------|
| Total classes | 51 |
| Object properties | 8 |
| French labels (`rdfs:label@fr`) | 0 |
| `arasaacId` annotation property | absent |
| SWRL rules | absent |
| OWL restrictions (`SubClassOf … some`) | absent |

## Classes (51)

Top-level categories: `Actions`, `MathematicalConcepts`, `Needs`, `Person`, `SchoolMaterial`

| Class | Parent | Notes |
|-------|--------|-------|
| Actions | — | top-level |
| MathematicalConcepts | — | **BUG**: plural, inconsistent with Action/Need |
| Needs | — | top-level |
| Person | — | top-level |
| SchoolMaterial | — | top-level |
| Assistant | Person | |
| Student | Person | |
| Teacher | Person | |
| ManualAction | Actions | |
| MathAction | Actions | |
| Calculate | MathAction | |
| Count | MathAction | |
| Draw | MathAction | represents "tracer"/"dessiner" |
| Mesure | MathAction | **BUG**: French spelling, should be `Measure` |
| Cut | ManualAction | |
| Erase | ManualAction | |
| Write | ManualAction | |
| BasicTool | SchoolMaterial | |
| CalculationTool | SchoolMaterial | |
| GeometryTool | SchoolMaterial | |
| Eraser | BasicTool | |
| Notebook | BasicTool | |
| Pencil | BasicTool | |
| Calculator | CalculationTool | |
| Hands | CalculationTool | **BUG**: not a physical tool |
| Mind | CalculationTool | **BUG**: not a physical tool |
| Compass | GeometryTool | |
| Ruler | GeometryTool | |
| SetSquare | GeometryTool | |
| GeometricShape | MathematicalConcepts | |
| Magnitude | MathematicalConcepts | |
| MathOperation | MathematicalConcepts | |
| Number | MathematicalConcepts | |
| Circle | GeometricShape | |
| Square | GeometricShape | |
| Triangle | GeometricShape | |
| Bigger | Magnitude | |
| Equal | Magnitude | |
| Smaller | Magnitude | |
| Addition | MathOperation | |
| Soustraction | MathOperation | **BUG**: French spelling, should be `Subtraction` |
| HelpNeed | Needs | |
| MentalNeed | Needs | |
| ValidationNeed | Needs | |
| DoNotUnderstand | HelpNeed | |
| NeedBreak | MentalNeed | |
| Tired | MentalNeed | |
| TooMuchNoise | MentalNeed | |
| IFinish | ValidationNeed | |
| IUnderstand | ValidationNeed | |
| IsItGood | ValidationNeed | |

## Object Properties (8)

| Property | Domain | Range | Characteristics | Bugs |
|----------|--------|-------|-----------------|------|
| appliesToConcept | Actions | MathematicalConcepts | Asymmetric, Irreflexive | Irreflexive redundant |
| isAppliedIn | MathematicalConcepts | Actions | Asymmetric, Irreflexive | Irreflexive redundant |
| isPerformedBy | **Actions ∩ Needs** (empty!) | Person | **Functional** | Domain = intersection bug; Functional wrong |
| isRequestedBy | **Assistant ∩ Teacher** (empty!) | Student | Asymmetric, Irreflexive | Domain = intersection bug |
| isUsedIn | SchoolMaterial | Actions | Asymmetric, Irreflexive | Irreflexive redundant |
| performsAction | Person | **Actions ∩ Needs** (empty!) | **InverseFunctional** | Range = intersection bug; InvFunctional wrong |
| requestHelpFrom | Student | **Assistant ∩ Teacher** (empty!) | Asymmetric, Irreflexive | Range = intersection bug |
| usesSupply | Actions | SchoolMaterial | Asymmetric, Irreflexive | Irreflexive redundant |

## Known Bugs (to fix in Step 1)

1. **Multiple domains/ranges interpreted as intersection**: `isPerformedBy`, `isRequestedBy`, `performsAction`, `requestHelpFrom` — domain/range resolves to empty class intersection, causing reasoner inconsistency.
2. **French spelling errors**: `Soustraction` (→ `Subtraction`), `Mesure` (→ `Measure`).
3. **Plural inconsistency**: `MathematicalConcepts` (→ `MathematicalConcept`).
4. **Wrong hierarchy**: `Hands` and `Mind` under `CalculationTool → SchoolMaterial` (they are not physical school supplies).
5. **`FunctionalObjectProperty isPerformedBy`**: implies each Action has at most one performer — wrong at class level.
6. **`InverseFunctionalObjectProperty performsAction`**: implies each Action is performed by at most one Person type — wrong.
7. **Redundant `IrreflexiveObjectProperty`**: Asymmetry in OWL 2 implies irreflexivity; 6 redundant declarations.
