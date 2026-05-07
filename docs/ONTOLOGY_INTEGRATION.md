# Ontology Integration Guide

This document explains how `maths.owl` is structured, how to extend it, and how the runtime inference pipeline works.

---

## 1. File structure

`maths.owl` is in **OWL 2 XML syntax** (`ontologyIRI = http://www.pictexpress.org/ontologies/math.owl`).

### Top-level class hierarchy

```
owl:Thing
├── Actions                  (MathAction, ManualAction)
├── CalculationMethod        (Hands, Mind)
├── MathematicalConcept      (GeometricShape, MathOperation, Magnitude, Number)
├── Needs                    (HelpNeed, MentalNeed, ValidationNeed)
├── Person                   (Student, Teacher, Assistant)
└── SchoolMaterial           (BasicTool, CalculationTool, GeometryTool)
```

All six top-level categories are declared mutually disjoint.

### Object properties

| Property | Domain | Range | Notes |
|----------|--------|-------|-------|
| `hasTarget` | Actions | MathematicalConcept | Links action instance to its concept target at runtime |
| `requires` | Actions | SchoolMaterial | **Populated by Pellet via SWRL** |
| `appliesToConcept` | Actions | MathematicalConcept | Asymmetric |
| `isAppliedIn` | MathematicalConcept | Actions | Inverse of appliesToConcept |
| `isPerformedBy` | Actions ∪ Needs | Person | Domain: ObjectUnionOf |
| `performsAction` | Person | Actions ∪ Needs | Inverse of isPerformedBy |
| `isRequestedBy` | Assistant ∪ Teacher | Student | Domain: ObjectUnionOf |
| `requestHelpFrom` | Student | Assistant ∪ Teacher | Inverse, range: ObjectUnionOf |
| `isUsedIn` | SchoolMaterial | Actions | Asymmetric |
| `usesSupply` | Actions | SchoolMaterial | Inverse of isUsedIn |

### Annotation properties

| Property | Type | Purpose |
|----------|------|---------|
| `rdfs:label@fr` | localized string | French labels for spaCy lemma matching |
| `#arasaacId` | `xsd:integer` | ARASAAC pictogram database ID |

---

## 2. SWRL rules

Eleven `DLSafeRule` axioms are declared in `maths.owl`. They are **read by `OntologyService`** at load time and converted to `owlready2 Imp` objects (owlready2 does not parse `DLSafeRule` from OWL/XML directly — see the `_parse_swrl_rules()` method).

| Rule label | Body | Head |
|------------|------|------|
| draw-circle-needs-compass | Draw(?a), hasTarget(?a,?s), Circle(?s), Compass(?c) | requires(?a,?c) |
| draw-circle-needs-pencil | Draw(?a), hasTarget(?a,?s), Circle(?s), Pencil(?p) | requires(?a,?p) |
| draw-square-needs-ruler | Draw(?a), hasTarget(?a,?s), Square(?s), Ruler(?r) | requires(?a,?r) |
| draw-square-needs-pencil | Draw(?a), hasTarget(?a,?s), Square(?s), Pencil(?p) | requires(?a,?p) |
| draw-triangle-needs-setsquare | Draw(?a), hasTarget(?a,?s), Triangle(?s), SetSquare(?q) | requires(?a,?q) |
| draw-triangle-needs-pencil | Draw(?a), hasTarget(?a,?s), Triangle(?s), Pencil(?p) | requires(?a,?p) |
| measure-shape-needs-ruler | Measure(?a), hasTarget(?a,?s), GeometricShape(?s), Ruler(?r) | requires(?a,?r) |
| calculate-needs-calculator | Calculate(?a), Calculator(?c) | requires(?a,?c) |
| write-needs-pencil | Write(?a), Pencil(?p) | requires(?a,?p) |
| write-needs-notebook | Write(?a), Notebook(?n) | requires(?a,?n) |
| erase-needs-eraser | Erase(?a), Eraser(?e) | requires(?a,?e) |

**Why DL-Safe rules?** SWRL DL-Safe rules only fire on *named* individuals, not inferred ones. This is intentional: the rules work on the temporary runtime individuals created for each request.

**Why tool class in body?** Each rule includes `Compass(?c)` (or similar) in the body. This means the rule fires only when at least one Compass individual exists. The seven pre-declared **tool singletons** (`#theCompass`, `#thePencil`, etc.) serve this purpose.

---

## 3. How to add a new class

### 3.1 Add the class declaration and hierarchy

In `maths.owl`, add inside the class declarations section:

```xml
<Declaration><Class IRI="#Protractor"/></Declaration>
```

Add the subclass axiom:

```xml
<SubClassOf><Class IRI="#Protractor"/><Class IRI="#GeometryTool"/></SubClassOf>
```

Add to the `Compass, Ruler, SetSquare` disjoint group (or create a new one):

```xml
<DisjointClasses>
    <Class IRI="#Compass"/>
    <Class IRI="#Protractor"/>
    <Class IRI="#Ruler"/>
    <Class IRI="#SetSquare"/>
</DisjointClasses>
```

### 3.2 Add French label

```xml
<AnnotationAssertion>
    <AnnotationProperty abbreviatedIRI="rdfs:label"/>
    <IRI>#Protractor</IRI>
    <Literal xml:lang="fr">rapporteur</Literal>
</AnnotationAssertion>
```

### 3.3 Add arasaacId

Query the ARASAAC API:
```
GET https://api.arasaac.org/api/pictograms/fr/search/rapporteur
```
Take the `_id` from the first result. Add:

```xml
<AnnotationAssertion>
    <AnnotationProperty IRI="#arasaacId"/>
    <IRI>#Protractor</IRI>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#integer">XXXXXX</Literal>
</AnnotationAssertion>
```

Or use the automated script:
```bash
python scripts/populate_arasaac_ids.py
```

### 3.4 Add tool singleton individual

```xml
<Declaration><NamedIndividual IRI="#theProtractor"/></Declaration>
<ClassAssertion><Class IRI="#Protractor"/><NamedIndividual IRI="#theProtractor"/></ClassAssertion>
```

### 3.5 Add SWRL rules (if needed)

Example — "Tracer + Triangle also needs a Protractor":

```xml
<DLSafeRule>
    <Annotation><AnnotationProperty abbreviatedIRI="rdfs:label"/>
        <Literal>draw-triangle-needs-protractor</Literal></Annotation>
    <Body>
        <ClassAtom><Class IRI="#Draw"/><Variable IRI="urn:swrl:var#a"/></ClassAtom>
        <ObjectPropertyAtom><ObjectProperty IRI="#hasTarget"/>
            <Variable IRI="urn:swrl:var#a"/><Variable IRI="urn:swrl:var#s"/>
        </ObjectPropertyAtom>
        <ClassAtom><Class IRI="#Triangle"/><Variable IRI="urn:swrl:var#s"/></ClassAtom>
        <ClassAtom><Class IRI="#Protractor"/><Variable IRI="urn:swrl:var#q"/></ClassAtom>
    </Body>
    <Head>
        <ObjectPropertyAtom><ObjectProperty IRI="#requires"/>
            <Variable IRI="urn:swrl:var#a"/><Variable IRI="urn:swrl:var#q"/>
        </ObjectPropertyAtom>
    </Head>
</DLSafeRule>
```

### 3.6 Test

```bash
pytest tests/ -v
```

Add a test in `tests/test_pipeline.py`:
```python
def test_inference_tracer_triangle_protractor(svc):
    result = svc.infer_pictograms(["tracer", "triangle"])
    names = {p["class_name"] for p in result}
    assert "Protractor" in names
```

---

## 4. Runtime inference flow (`OntologyService.infer_pictograms`)

```
lemmas: ["tracer", "cercle"]
        │
        ▼
find_class_by_label("tracer")  → Draw   (Action)
find_class_by_label("cercle")  → Circle (MathematicalConcept)
        │
        ▼
With onto:
  drawInst   = Draw("_runtime_Draw_...")
  circleInst = Circle("_runtime_Circle_...")
  drawInst.hasTarget = [circleInst]
        │
        ▼
sync_reasoner_pellet([onto], infer_property_values=True)
  fires: draw-circle-needs-compass → drawInst requires theCompass
  fires: draw-circle-needs-pencil  → drawInst requires thePencil
        │
        ▼
Collect results:
  Circle  (from input) → arasaacId = 4603
  Compass (from drawInst.requires → theCompass → Compass class) → 34065
  Pencil  (from drawInst.requires → thePencil  → Pencil class)  → 2440
        │
        ▼
destroy_entity(drawInst, circleInst)   ← cleanup
        │
        ▼
Return: [
  {"class_name": "Circle",  "label_fr": "cercle", "arasaac_id": 4603},
  {"class_name": "Compass", "label_fr": "compas", "arasaac_id": 34065},
  {"class_name": "Pencil",  "label_fr": "crayon", "arasaac_id": 2440}
]
```

---

## 5. Updating arasaacIds

If ARASAAC changes IDs or you add new classes, re-run:
```bash
python scripts/populate_arasaac_ids.py --dry-run   # preview
python scripts/populate_arasaac_ids.py             # apply
```

For ambiguous results (e.g., "règle" = ruler/rule), add the correct ID to `MANUAL_OVERRIDES` in the script.

---

## 6. Troubleshooting Pellet

| Error | Cause | Fix |
|-------|-------|-----|
| `UnsupportedClassVersionError: … class version 69` | owlready2 0.50 ships Jena JARs compiled for Java 25 | Run `python scripts/patch_owlready2_jars.py` |
| `Java not found in PATH` | Java not installed | Install Java 21 LTS from adoptium.net |
| `OwlReadyJavaError: OutOfMemoryError` | Pellet ran out of heap | Set `JAVA_OPTS=-Xmx4g` before starting the server |
| `OwlReadyInconsistentOntologyError` | Ontology is logically inconsistent | Run Protégé → Reasoner → HermiT/Pellet and check the explanation |
| Rules not firing | DLSafeRule not parsed from OWL/XML | Expected: `OntologyService._parse_swrl_rules()` converts them manually. Check rule count: `len(list(onto.rules()))` should be > 0 after load. |
