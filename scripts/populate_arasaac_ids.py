"""
Populate arasaacId annotations in maths.owl by querying the ARASAAC API.

Usage:
    python scripts/populate_arasaac_ids.py [--dry-run] [--owl PATH]

The script loads the ontology, iterates classes that have a French rdfs:label,
queries the ARASAAC search API for the first result, and writes the numeric ID
as an arasaacId annotation. Ambiguous results are logged for manual review.

Note: arasaacId values are already seeded in maths.owl (retrieved 2026-05-07).
Re-run this script only when adding new classes or updating IDs.
"""

import argparse
import time
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Install requests: pip install requests")

try:
    from owlready2 import get_ontology, INDIRECT_label
except ImportError:
    sys.exit("Install owlready2: pip install owlready2")


ARASAAC_SEARCH = "https://api.arasaac.org/api/pictograms/fr/search/{keyword}"
# DESIGN: rate-limit to avoid hitting the public API aggressively
REQUEST_DELAY_S = 0.5

# Classes whose first API result is ambiguous (manual review required).
# Add IDs here after visual inspection of https://arasaac.org.
MANUAL_OVERRIDES: dict[str, int] = {
    # "Ruler" -> "règle" can mean ruler or rule/law; ID 2815 confirmed as ruler
    "Ruler": 2815,
}


def get_fr_labels(cls) -> list[str]:
    labels = []
    for lbl in cls.label:
        if hasattr(lbl, "lang") and lbl.lang == "fr":
            labels.append(str(lbl))
    return labels


def query_arasaac(keyword: str) -> tuple[int | None, list[dict]]:
    url = ARASAAC_SEARCH.format(keyword=keyword)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None, []
        return results[0].get("_id"), results
    except Exception as exc:
        print(f"  [WARN] API error for '{keyword}': {exc}")
        return None, []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would change without saving")
    parser.add_argument("--owl", default="maths.owl",
                        help="Path to the OWL file (default: maths.owl)")
    args = parser.parse_args()

    owl_path = Path(args.owl).resolve()
    if not owl_path.exists():
        sys.exit(f"OWL file not found: {owl_path}")

    print(f"Loading ontology from {owl_path} ...")
    onto = get_ontology(owl_path.as_uri()).load()

    # Ensure the arasaacId annotation property is accessible
    with onto:
        arasaac_id_prop = onto.search_one(iri="*#arasaacId")
        if arasaac_id_prop is None:
            print("[WARN] #arasaacId annotation property not found in ontology.")
            return

    updated = 0
    skipped = 0
    ambiguous = []

    for cls in onto.classes():
        fr_labels = get_fr_labels(cls)
        if not fr_labels:
            continue

        keyword = fr_labels[0]  # use primary French label for search
        print(f"\n{cls.name} ('{keyword}') ...", end=" ")

        # Use manual override if available
        if cls.name in MANUAL_OVERRIDES:
            pid = MANUAL_OVERRIDES[cls.name]
            print(f"manual override -> {pid}")
        else:
            pid, results = query_arasaac(keyword)
            time.sleep(REQUEST_DELAY_S)

            if pid is None:
                print("no result")
                skipped += 1
                continue

            if len(results) > 5:
                ambiguous.append({
                    "class": cls.name,
                    "keyword": keyword,
                    "first_id": pid,
                    "total_results": len(results),
                })
                print(f"AMBIGUOUS ({len(results)} results) -> {pid}")
            else:
                print(f"-> {pid}")

        # Check existing value
        existing = getattr(cls, "arasaacId", None)
        if existing and existing == pid:
            print(f"  (already set, skipping)")
            skipped += 1
            continue

        if not args.dry_run:
            cls.arasaacId = [pid]
        updated += 1

    if not args.dry_run and updated > 0:
        onto.save(file=str(owl_path), format="rdfxml")
        print(f"\nSaved {owl_path}")

    print(f"\nDone: {updated} updated, {skipped} skipped.")

    if ambiguous:
        print("\nAmbiguous results requiring manual review:")
        for item in ambiguous:
            print(f"  {item['class']} ('{item['keyword']}'): "
                  f"first_id={item['first_id']}, total={item['total_results']}")
        print("Add confirmed IDs to MANUAL_OVERRIDES in this script.")


if __name__ == "__main__":
    main()
