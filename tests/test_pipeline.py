"""
End-to-end pipeline tests for the OWL + Pellet integration.

Run: pytest tests/ -v
Requires: owlready2 patched (scripts/patch_owlready2_jars.py), Java 21+.
"""

import pytest
from ontology_service import OntologyService


OWL_PATH = "./maths.owl"


# ---- Fixtures ----------------------------------------------------------------

@pytest.fixture(scope="module")
def svc():
    """Single OntologyService instance shared across this module's tests."""
    s = OntologyService(OWL_PATH)
    s.load()
    return s


# ---- Test 1: label lookup ----------------------------------------------------

def test_find_class_by_label_circle(svc):
    cls = svc.find_class_by_label("cercle")
    assert cls is not None, "find_class_by_label('cercle') returned None"
    assert cls.name == "Circle"


def test_find_class_by_label_case_insensitive(svc):
    cls = svc.find_class_by_label("Cercle")
    assert cls is not None
    assert cls.name == "Circle"


def test_find_class_by_label_unknown_returns_none(svc):
    cls = svc.find_class_by_label("chien")
    assert cls is None


def test_find_class_by_label_draw_tracer(svc):
    cls = svc.find_class_by_label("tracer")
    assert cls is not None
    assert cls.name == "Draw"


def test_find_class_by_label_draw_dessiner(svc):
    """Draw has two FR labels: tracer and dessiner."""
    cls = svc.find_class_by_label("dessiner")
    assert cls is not None
    assert cls.name == "Draw"


# ---- Test 2: arasaacId lookup ------------------------------------------------

def test_arasaac_id_circle(svc):
    cls = svc.find_class_by_label("cercle")
    assert svc.get_arasaac_id(cls) == 4603


def test_arasaac_id_compass(svc):
    cls = svc.find_class_by_label("compas")
    assert svc.get_arasaac_id(cls) == 34065


def test_arasaac_id_pencil(svc):
    cls = svc.find_class_by_label("crayon")
    assert svc.get_arasaac_id(cls) == 2440


# ---- Test 3: SWRL inference — tracer + cercle --------------------------------

def test_inference_tracer_cercle(svc):
    """Core test: 'Tracez un cercle' should yield Circle + Compass + Pencil."""
    result = svc.infer_pictograms(["tracer", "cercle"])
    names = {p["class_name"] for p in result}

    assert "Circle"  in names, f"Circle missing from {names}"
    assert "Compass" in names, f"Compass missing from {names}"
    assert "Pencil"  in names, f"Pencil missing from {names}"


def test_inference_tracer_cercle_arasaac_ids(svc):
    """The returned arasaac_ids must be the correct integers."""
    result = svc.infer_pictograms(["tracer", "cercle"])
    by_cls = {p["class_name"]: p for p in result}

    assert by_cls["Circle"]["arasaac_id"]  == 4603
    assert by_cls["Compass"]["arasaac_id"] == 34065
    assert by_cls["Pencil"]["arasaac_id"]  == 2440


def test_inference_tracer_carre(svc):
    """Tracer + carré should yield Square + Ruler + Pencil."""
    result = svc.infer_pictograms(["tracer", "carré"])
    names = {p["class_name"] for p in result}

    assert "Square"  in names, f"Square missing: {names}"
    assert "Ruler"   in names, f"Ruler missing: {names}"
    assert "Pencil"  in names, f"Pencil missing: {names}"


def test_inference_tracer_triangle(svc):
    """Tracer + triangle should yield Triangle + SetSquare + Pencil."""
    result = svc.infer_pictograms(["tracer", "triangle"])
    names = {p["class_name"] for p in result}

    assert "Triangle"  in names, f"Triangle missing: {names}"
    assert "SetSquare" in names, f"SetSquare missing: {names}"
    assert "Pencil"    in names, f"Pencil missing: {names}"


# ---- Test 4: SWRL must NOT fire without the action verb ----------------------

def test_no_inference_without_verb(svc):
    """
    'Le cercle est rond' → only cercle lemma, no Draw verb.
    SWRL rule must NOT fire: Compass and Pencil should be absent.
    This is the key advantage of SWRL over OWL restrictions.
    """
    result = svc.infer_pictograms(["cercle"])
    names = {p["class_name"] for p in result}

    assert "Circle"  in names,    f"Circle itself should appear: {names}"
    assert "Compass" not in names, f"Compass must NOT appear without Draw: {names}"
    assert "Pencil"  not in names, f"Pencil must NOT appear without Draw: {names}"


# ---- Test 5: other rules -----------------------------------------------------

def test_inference_ecrire(svc):
    """Écrire → Pencil + Notebook."""
    result = svc.infer_pictograms(["écrire"])
    names = {p["class_name"] for p in result}

    assert "Pencil"   in names, f"Pencil missing: {names}"
    assert "Notebook" in names, f"Notebook missing: {names}"


def test_inference_effacer(svc):
    """Effacer → Eraser."""
    result = svc.infer_pictograms(["effacer"])
    names = {p["class_name"] for p in result}

    assert "Eraser" in names, f"Eraser missing: {names}"


def test_inference_calculer(svc):
    """Calculer → Calculator."""
    result = svc.infer_pictograms(["calculer"])
    names = {p["class_name"] for p in result}

    assert "Calculator" in names, f"Calculator missing: {names}"


def test_inference_unknown_lemma_returns_empty(svc):
    """Unknown lemmas should return an empty list, not raise."""
    result = svc.infer_pictograms(["xyzzy", "frobnicator"])
    assert result == []
