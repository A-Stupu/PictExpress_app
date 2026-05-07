"""
OntologyService — semantic core of the Pict'Express pipeline.

Responsibilities:
  - Load maths.owl and parse SWRL DLSafeRule axioms into owlready2 Imp objects.
  - Index rdfs:label@fr annotations for fast O(1) lemma→class lookup.
  - Index #arasaacId annotations for pictogram resolution.
  - Run Pellet (sync_reasoner_pellet) on temporary runtime individuals to infer
    which school materials are needed for a given teacher instruction.

DESIGN: owlready2 0.50 does not parse OWL/XML DLSafeRule elements; it uses the
older swrl: RDF vocabulary internally. We bridge this by reading the DLSafeRule
XML manually and converting each rule to an owlready2 Imp object at load time.
This keeps the OWL file as the single source of truth for rule declarations while
remaining compatible with owlready2's Pellet integration.

DESIGN: owlready2 file:// URI resolution is broken on Windows (leading slash
added to drive letter). Workaround: copy maths.owl to a temp directory with the
name matching the ontologyIRI filename ("math.owl"), then use onto_path to
let owlready2 resolve by IRI filename.

DESIGN: each OntologyService uses its own owlready2 World() to avoid cross-
instance contamination in tests and concurrent requests.

Requires:
  - Python 3.10+
  - owlready2 0.50+ (with jena-arq JAR patched — run scripts/patch_owlready2_jars.py)
  - Java 21 LTS in PATH
"""

import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import owlready2

# ---- Constants ---------------------------------------------------------------

_OWL_NS = "http://www.w3.org/2002/07/owl#"
# The ontologyIRI declared inside the file. owlready2 resolves onto_path files
# by matching the last segment of this IRI to a filename in the search paths.
_ONTO_IRI = "http://www.pictexpress.org/ontologies/math.owl"
_ONTO_FILENAME = "math.owl"  # last segment of _ONTO_IRI


# ---- OntologyService ---------------------------------------------------------

class OntologyService:

    def __init__(self, owl_path: str) -> None:
        self.owl_path = Path(owl_path).resolve()
        self.world: Optional[owlready2.World] = None
        self.onto = None
        self._tmp_dir: Optional[str] = None

        # Indices built at load time
        self._fr_label_to_class: dict[str, owlready2.ThingClass] = {}
        self._arasaac_ids: dict[str, int] = {}   # class name → integer ID

    # ---- Lifecycle ------------------------------------------------------------

    def load(self) -> None:
        """
        Load the ontology, parse SWRL rules, build lookup indices, and run an
        initial Pellet pass to validate consistency.
        """
        # 1. Workaround: copy the OWL file so its filename matches the ontologyIRI
        self._tmp_dir = tempfile.mkdtemp()
        shutil.copy(self.owl_path, os.path.join(self._tmp_dir, _ONTO_FILENAME))

        # 2. Fresh isolated world per instance
        self.world = owlready2.World()

        # 3. Append tmp_dir to onto_path (owlready2 module-level, shared across worlds)
        if self._tmp_dir not in owlready2.onto_path:
            owlready2.onto_path.append(self._tmp_dir)

        # 4. Load structural axioms
        self.onto = self.world.get_ontology(_ONTO_IRI).load()

        # 5. Parse DLSafeRule from OWL/XML → owlready2 Imp objects
        # DESIGN: owlready2 ignores DLSafeRule elements when parsing OWL/XML;
        # we convert them manually so Pellet can execute them.
        rules = self._parse_swrl_rules()
        with self.onto:
            for rule_str in rules:
                owlready2.Imp().set_as_rule(rule_str)

        # 6. Build label and arasaacId lookup indices
        self._build_label_index()
        self._load_arasaac_ids()

        # 7. Validate with initial Pellet pass (catches ontology inconsistencies early)
        owlready2.sync_reasoner_pellet(
            [self.onto],
            infer_property_values=True,
            infer_data_property_values=False,
            debug=0,
        )

    # ---- Public API -----------------------------------------------------------

    def find_class_by_label(self, label_fr: str) -> Optional[owlready2.ThingClass]:
        """Return the OWL class whose rdfs:label@fr matches label_fr (case-insensitive)."""
        return self._fr_label_to_class.get(label_fr.strip().lower())

    def get_arasaac_id(self, cls: owlready2.ThingClass) -> Optional[int]:
        """Return the ARASAAC integer ID for the class, or None if not annotated."""
        return self._arasaac_ids.get(cls.name)

    def infer_pictograms(self, lemmas: list[str]) -> list[dict]:
        """
        Map French lemmas to OWL classes, create temporary runtime individuals,
        run Pellet, and return the inferred pictogram descriptors.

        Returns a list of dicts: {class_name, label_fr, arasaac_id}

        DESIGN: only the classes that have an arasaacId are returned — abstract
        intermediary classes (Actions, MathematicalConcept, …) are excluded.
        """
        # Map lemmas to classes
        mapped: list[tuple[str, owlready2.ThingClass]] = []
        for lemma in lemmas:
            cls = self.find_class_by_label(lemma)
            if cls is not None:
                mapped.append((lemma, cls))

        if not mapped:
            return []

        actions   = [(l, c) for l, c in mapped if self._is_action(c)]
        concepts  = [(l, c) for l, c in mapped if self._is_concept(c)]

        tmp_instances: list = []

        with self.onto:
            # Create concept instances
            concept_insts = []
            for _, cls in concepts:
                inst = cls(f"_runtime_{cls.name}_{id(self)}")
                concept_insts.append(inst)
                tmp_instances.append(inst)

            # Create action instances and wire hasTarget
            action_insts = []
            for _, cls in actions:
                inst = cls(f"_runtime_{cls.name}_{id(self)}")
                if concept_insts:
                    inst.hasTarget = list(concept_insts)
                action_insts.append(inst)
                tmp_instances.append(inst)

        try:
            if tmp_instances:
                owlready2.sync_reasoner_pellet(
                    [self.onto],
                    infer_property_values=True,
                    infer_data_property_values=False,
                    debug=0,
                )

            results: dict[str, dict] = {}

            # Include input classes with arasaacId
            for _, cls in mapped:
                aid = self.get_arasaac_id(cls)
                if aid is not None:
                    results[cls.name] = self._make_entry(cls, aid)

            # Include inferred tools from action.requires
            for action_inst in action_insts:
                for tool_inst in action_inst.requires:
                    for tool_cls in tool_inst.is_a:
                        if not isinstance(tool_cls, owlready2.ThingClass):
                            continue
                        if tool_cls.name == "Thing":
                            continue
                        aid = self.get_arasaac_id(tool_cls)
                        if aid is not None and tool_cls.name not in results:
                            results[tool_cls.name] = self._make_entry(tool_cls, aid)

            return list(results.values())

        finally:
            for inst in tmp_instances:
                owlready2.destroy_entity(inst)

    # ---- Private helpers ------------------------------------------------------

    def _make_entry(self, cls: owlready2.ThingClass, arasaac_id: int) -> dict:
        return {
            "class_name": cls.name,
            "label_fr":   self._get_primary_fr_label(cls),
            "arasaac_id": arasaac_id,
        }

    def _get_primary_fr_label(self, cls: owlready2.ThingClass) -> Optional[str]:
        for lbl in cls.label:
            if getattr(lbl, "lang", None) == "fr":
                return str(lbl)
        return cls.name

    def _is_action(self, cls: owlready2.ThingClass) -> bool:
        Actions = self.onto.search_one(iri="*#Actions")
        return Actions is not None and issubclass(cls, Actions)

    def _is_concept(self, cls: owlready2.ThingClass) -> bool:
        Concept = self.onto.search_one(iri="*#MathematicalConcept")
        return Concept is not None and issubclass(cls, Concept)

    def _build_label_index(self) -> None:
        """Build a lowercase FR label → class dict for O(1) lookups."""
        for cls in self.onto.classes():
            for lbl in cls.label:
                if getattr(lbl, "lang", None) == "fr":
                    self._fr_label_to_class[str(lbl).lower()] = cls

    def _load_arasaac_ids(self) -> None:
        """Parse #arasaacId AnnotationAssertions directly from the OWL/XML file.

        DESIGN: owlready2 may not expose custom AnnotationProperty values via
        attribute access after loading from OWL/XML. Reading from the source XML
        is simpler and guaranteed to be correct.
        """
        ARASAAC_PROP_IRI = "#arasaacId"
        tree = ET.parse(self.owl_path)
        root = tree.getroot()

        for assertion in root.iter(f"{{{_OWL_NS}}}AnnotationAssertion"):
            prop_elem    = assertion.find(f"{{{_OWL_NS}}}AnnotationProperty")
            iri_elem     = assertion.find(f"{{{_OWL_NS}}}IRI")
            literal_elem = assertion.find(f"{{{_OWL_NS}}}Literal")

            if (
                prop_elem is not None
                and prop_elem.attrib.get("IRI") == ARASAAC_PROP_IRI
                and iri_elem is not None
                and literal_elem is not None
            ):
                class_name = (iri_elem.text or "").lstrip("#")
                try:
                    self._arasaac_ids[class_name] = int(literal_elem.text)
                except (ValueError, TypeError):
                    pass

    def _parse_swrl_rules(self) -> list[str]:
        """Convert DLSafeRule OWL/XML elements to owlready2 rule strings.

        Example output: 'Draw(?a), hasTarget(?a, ?s), Circle(?s), Compass(?c) -> requires(?a, ?c)'
        """
        tree = ET.parse(self.owl_path)
        root = tree.getroot()
        rules: list[str] = []

        for rule_elem in root.iter(f"{{{_OWL_NS}}}DLSafeRule"):
            body_atoms: list[str] = []
            head_atoms: list[str] = []

            for section_tag, target in (("Body", body_atoms), ("Head", head_atoms)):
                section = rule_elem.find(f"{{{_OWL_NS}}}{section_tag}")
                if section is None:
                    continue
                for atom in section:
                    atom_str = self._atom_to_str(atom)
                    if atom_str:
                        target.append(atom_str)

            if body_atoms and head_atoms:
                rules.append(", ".join(body_atoms) + " -> " + ", ".join(head_atoms))

        return rules

    def _atom_to_str(self, atom_elem: ET.Element) -> Optional[str]:
        tag = atom_elem.tag

        if tag == f"{{{_OWL_NS}}}ClassAtom":
            cls_el  = atom_elem.find(f"{{{_OWL_NS}}}Class")
            var_el  = atom_elem.find(f"{{{_OWL_NS}}}Variable")
            if cls_el is not None and var_el is not None:
                cls_name = cls_el.attrib.get("IRI", "").lstrip("#")
                var_name = var_el.attrib.get("IRI", "").rsplit("#", 1)[-1]
                return f"{cls_name}(?{var_name})"

        elif tag == f"{{{_OWL_NS}}}ObjectPropertyAtom":
            prop_el = atom_elem.find(f"{{{_OWL_NS}}}ObjectProperty")
            vars_el = atom_elem.findall(f"{{{_OWL_NS}}}Variable")
            if prop_el is not None and len(vars_el) == 2:
                prop_name = prop_el.attrib.get("IRI", "").lstrip("#")
                v1 = vars_el[0].attrib.get("IRI", "").rsplit("#", 1)[-1]
                v2 = vars_el[1].attrib.get("IRI", "").rsplit("#", 1)[-1]
                return f"{prop_name}(?{v1}, ?{v2})"

        return None

    def __del__(self) -> None:
        if self._tmp_dir and os.path.isdir(self._tmp_dir):
            shutil.rmtree(self._tmp_dir, ignore_errors=True)
