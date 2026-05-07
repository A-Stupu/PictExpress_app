"""
Pellet smoke test — verifies that owlready2 + Pellet can execute a trivial
SWRL rule before any real integration work is done.

Rule under test: A(?x) -> B(?x)
Expected:        individual_a (type A) should also be classified as type B.

Run:
    python scripts/test_pellet.py
"""

import sys
import subprocess

# --- Java availability check ---
try:
    result = subprocess.run(
        ["java", "-version"],
        capture_output=True, text=True, timeout=10
    )
    java_version_output = result.stderr or result.stdout
    print(f"Java detected:\n  {java_version_output.strip()}")
except FileNotFoundError:
    print("ERROR: Java not found in PATH. Pellet requires Java 8+.")
    print("Install Java and ensure 'java' is on your PATH.")
    sys.exit(1)
except Exception as exc:
    print(f"ERROR checking Java: {exc}")
    sys.exit(1)

try:
    from owlready2 import (
        get_ontology, Thing, sync_reasoner_pellet,
        ObjectProperty, Imp
    )
except ImportError:
    print("ERROR: owlready2 not installed. Run: pip install owlready2")
    sys.exit(1)

print("\nBuilding minimal test ontology...")
onto = get_ontology("http://test.org/pellet_smoke_test.owl")

with onto:
    class A(Thing):
        pass

    class B(Thing):
        pass

    # SWRL rule: A(?x) -> B(?x)
    rule = Imp()
    rule.set_as_rule("A(?x) -> B(?x)")

    individual_a = A("individual_a")

print(f"Individual type before reasoning: {individual_a.is_a}")

print("\nRunning sync_reasoner_pellet ...")
try:
    sync_reasoner_pellet(
        [onto],
        infer_property_values=True,
        infer_data_property_values=True,
        debug=0
    )
except Exception as exc:
    print(f"\nERROR: Pellet failed: {exc}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    sys.exit(2)

types_after = individual_a.is_a
print(f"Individual type after reasoning: {types_after}")

if B in types_after:
    print("\nSMOKE TEST PASSED: SWRL rule fired correctly.")
    print("  individual_a is classified as B after reasoning.")
    sys.exit(0)
else:
    print("\nSMOKE TEST FAILED: individual_a is not classified as B.")
    print("  The SWRL rule did not fire as expected.")
    sys.exit(3)
