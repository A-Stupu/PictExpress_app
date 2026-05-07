"""
Tests for the child communication flow (Step 1+2, feature/child-communication).
"""

import pytest
from ontology_service import OntologyService

OWL_PATH = "./maths.owl"


@pytest.fixture(scope="module")
def svc():
    s = OntologyService(OWL_PATH)
    s.load()
    return s


# ---- Needs grouped structure ------------------------------------------------

def test_needs_grouped_has_all_keys(svc):
    needs = svc.get_needs_grouped()
    assert "physical" in needs
    assert "mental" in needs
    assert "help_validation" in needs


def test_needs_grouped_physical_count(svc):
    needs = svc.get_needs_grouped()
    # PhysicalNeed (Hungry, Thirsty, NeedToilet, Hurt) + NeedBreak = 5
    assert len(needs["physical"]) >= 5, f"Expected >=5, got {len(needs['physical'])}: {needs['physical']}"


def test_needs_grouped_mental_count(svc):
    needs = svc.get_needs_grouped()
    # MentalNeed minus NeedBreak = Tired + TooMuchNoise = 2
    assert len(needs["mental"]) >= 2, f"Expected >=2, got {len(needs['mental'])}"


def test_needs_grouped_help_validation_count(svc):
    needs = svc.get_needs_grouped()
    # HelpNeed (DoNotUnderstand) + ValidationNeed (IFinish, IUnderstand, IsItGood) = 4
    assert len(needs["help_validation"]) >= 4, f"Expected >=4, got {needs['help_validation']}"


def test_needs_all_have_required_fields(svc):
    needs = svc.get_needs_grouped()
    for group_items in needs.values():
        for item in group_items:
            assert "arasaac_id" in item, f"Missing arasaac_id in {item}"
            assert "label_fr" in item, f"Missing label_fr in {item}"
            assert "class_name" in item, f"Missing class_name in {item}"
            assert isinstance(item["arasaac_id"], int), f"arasaac_id not int: {item}"


def test_needs_grouped_no_none_labels(svc):
    needs = svc.get_needs_grouped()
    for group_items in needs.values():
        for item in group_items:
            assert item["label_fr"] is not None
            assert item["label_fr"] != item["class_name"], \
                f"{item['class_name']} has no real FR label (uses class name as fallback)"


def test_specific_needs_in_groups(svc):
    needs = svc.get_needs_grouped()
    physical_classes = {i["class_name"] for i in needs["physical"]}
    mental_classes   = {i["class_name"] for i in needs["mental"]}
    hv_classes       = {i["class_name"] for i in needs["help_validation"]}

    assert "Hungry"        in physical_classes, f"Hungry missing from physical: {physical_classes}"
    assert "Thirsty"       in physical_classes
    assert "NeedToilet"    in physical_classes
    assert "Hurt"          in physical_classes
    assert "NeedBreak"     in physical_classes

    assert "Tired"         in mental_classes,   f"Tired missing from mental: {mental_classes}"
    assert "TooMuchNoise"  in mental_classes
    assert "NeedBreak"     not in mental_classes, "NeedBreak should be in physical, not mental"

    assert "DoNotUnderstand" in hv_classes,     f"DoNotUnderstand missing: {hv_classes}"
    assert "IFinish"         in hv_classes
    assert "IUnderstand"     in hv_classes
    assert "IsItGood"        in hv_classes


# ---- New math shapes and SWRL inference ------------------------------------

def test_find_rectangle_by_label(svc):
    cls = svc.find_class_by_label("rectangle")
    assert cls is not None
    assert cls.name == "Rectangle"


def test_inference_tracer_rectangle(svc):
    result = svc.infer_pictograms(["tracer", "rectangle"])
    names = {p["class_name"] for p in result}
    assert "Rectangle" in names, f"Rectangle missing: {names}"
    assert "Ruler"     in names, f"Ruler missing: {names}"
    assert "Pencil"    in names, f"Pencil missing: {names}"


def test_inference_tracer_pentagone(svc):
    result = svc.infer_pictograms(["tracer", "pentagone"])
    names = {p["class_name"] for p in result}
    assert "Pentagon" in names, f"Pentagon missing: {names}"
    assert "Ruler"    in names
    assert "Pencil"   in names


def test_inference_tracer_hexagone(svc):
    result = svc.infer_pictograms(["tracer", "hexagone"])
    names = {p["class_name"] for p in result}
    assert "Hexagon" in names, f"Hexagon missing: {names}"
    assert "Ruler"   in names
    assert "Pencil"  in names


def test_arasaac_ids_new_shapes(svc):
    assert svc.get_arasaac_id(svc.find_class_by_label("rectangle"))    == 4731
    assert svc.get_arasaac_id(svc.find_class_by_label("pentagone"))    == 4715
    assert svc.get_arasaac_id(svc.find_class_by_label("hexagone"))     == 4663
    assert svc.get_arasaac_id(svc.find_class_by_label("multiplication")) == 5798
    assert svc.get_arasaac_id(svc.find_class_by_label("division"))     == 5707


def test_arasaac_ids_needs(svc):
    assert svc.get_arasaac_id(svc.find_class_by_label("je ne comprends pas")) == 11697
    assert svc.get_arasaac_id(svc.find_class_by_label("j'ai faim"))           == 35559
    assert svc.get_arasaac_id(svc.find_class_by_label("toilettes"))           == 5921
    assert svc.get_arasaac_id(svc.find_class_by_label("pause"))               == 27339
