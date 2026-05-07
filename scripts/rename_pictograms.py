"""
Rename pictogram PNG files from semantic names (cercle.png) to ARASAAC IDs (4603.png).

This script loads the ontology, reads the arasaacId annotations and rdfs:label@fr
values, then renames matching files in the pictogrammes/ directory.

Usage:
    python scripts/rename_pictograms.py [--dir pictogrammes] [--dry-run]

After running, update analysis/pictogram_renaming.md with the mapping.
"""

import os
import sys
import shutil
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

OWL_NS   = "http://www.w3.org/2002/07/owl#"
OWL_FILE = Path(__file__).parent.parent / "maths.owl"


def load_class_metadata(owl_path: Path) -> dict[str, dict]:
    """Return {class_name: {arasaac_id, fr_labels}} from the OWL/XML file."""
    tree = ET.parse(owl_path)
    root = tree.getroot()

    classes: dict[str, dict] = {}

    # Gather arasaacId annotations
    for assertion in root.iter(f"{{{OWL_NS}}}AnnotationAssertion"):
        prop    = assertion.find(f"{{{OWL_NS}}}AnnotationProperty")
        iri_el  = assertion.find(f"{{{OWL_NS}}}IRI")
        literal = assertion.find(f"{{{OWL_NS}}}Literal")

        if prop is None or iri_el is None or literal is None:
            continue

        if prop.attrib.get("IRI") == "#arasaacId":
            cls_name = iri_el.text.lstrip("#")
            try:
                classes.setdefault(cls_name, {"arasaac_id": None, "fr_labels": []})
                classes[cls_name]["arasaac_id"] = int(literal.text)
            except (ValueError, TypeError):
                pass

    # Gather rdfs:label@fr annotations
    for assertion in root.iter(f"{{{OWL_NS}}}AnnotationAssertion"):
        prop    = assertion.find(f"{{{OWL_NS}}}AnnotationProperty")
        iri_el  = assertion.find(f"{{{OWL_NS}}}IRI")
        literal = assertion.find(f"{{{OWL_NS}}}Literal")

        if prop is None or iri_el is None or literal is None:
            continue

        if prop.attrib.get("abbreviatedIRI") == "rdfs:label":
            if literal.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "fr":
                cls_name = iri_el.text.lstrip("#")
                classes.setdefault(cls_name, {"arasaac_id": None, "fr_labels": []})
                classes[cls_name]["fr_labels"].append(literal.text.lower())

    return classes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir",     default="pictogrammes", help="Pictogram directory")
    parser.add_argument("--dry-run", action="store_true",    help="Print without renaming")
    args = parser.parse_args()

    pic_dir = Path(args.dir)
    if not pic_dir.is_dir():
        sys.exit(f"Directory not found: {pic_dir}")

    metadata = load_class_metadata(OWL_FILE)

    # Build semantic-label → arasaacId map
    label_to_id: dict[str, int] = {}
    for cls_name, info in metadata.items():
        if info["arasaac_id"] is None:
            continue
        for lbl in info["fr_labels"]:
            label_to_id[lbl] = info["arasaac_id"]
        # Also try the class name lowercased as a fallback
        label_to_id[cls_name.lower()] = info["arasaac_id"]

    existing_pngs = {f.stem.lower(): f for f in pic_dir.glob("*.png")}
    mapping: list[tuple[Path, Path]] = []
    orphans: list[str] = []

    for stem, png_path in existing_pngs.items():
        if stem.isdigit():
            print(f"  Already renamed: {png_path.name}")
            continue

        if stem in label_to_id:
            new_name = f"{label_to_id[stem]}.png"
            new_path = pic_dir / new_name
            mapping.append((png_path, new_path))
        else:
            orphans.append(str(png_path.name))

    print(f"\nRenaming plan ({len(mapping)} files):")
    for old, new in mapping:
        print(f"  {old.name:30} -> {new.name}")

    if orphans:
        print(f"\nOrphans (no matching ontology class, kept as-is):")
        for o in orphans:
            print(f"  {o}")

    if args.dry_run:
        print("\nDry-run complete. No files changed.")
        return

    for old, new in mapping:
        if new.exists():
            print(f"  [SKIP] {new.name} already exists")
            continue
        shutil.move(str(old), str(new))
        print(f"  Renamed: {old.name} -> {new.name}")

    # Write audit log
    audit_path = Path("analysis/pictogram_renaming.md")
    audit_path.parent.mkdir(exist_ok=True)
    with open(audit_path, "w", encoding="utf-8") as f:
        f.write("# Pictogram Renaming Audit\n\n")
        f.write("| Old name | New name (arasaacId.png) | Class |\n")
        f.write("|----------|--------------------------|-------|\n")
        for old, new in mapping:
            # find class name
            cls_nm = next(
                (cn for cn, info in metadata.items()
                 if info["arasaac_id"] and str(info["arasaac_id"]) == new.stem),
                "?"
            )
            f.write(f"| {old.name} | {new.name} | {cls_nm} |\n")
        if orphans:
            f.write("\n## Orphans (no matching ontology class)\n\n")
            for o in orphans:
                f.write(f"- {o}\n")

    print(f"\nAudit log written to {audit_path}")


if __name__ == "__main__":
    main()
