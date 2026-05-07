# Pellet Smoke Test Report

Date: 2026-05-07  
Branch: feature/owl-integration

## Environment

| Component | Value |
|-----------|-------|
| Java installed | 1.8.0_461 (Java 8, 32-bit) |
| Java path | `C:\Program Files (x86)\Common Files\Oracle\Java\java8path\java.exe` |
| owlready2 version | 0.50 |
| Python version | 3.13 |

## Test

Script: `scripts/test_pellet.py`  
Ontology: minimal in-memory ontology with 2 classes and SWRL rule `A(?x) -> B(?x)`

## Result: FAILED

### Error

```
java.lang.UnsupportedClassVersionError: org/apache/jena/riot/lang/LangRDFXML
has been compiled by a more recent version of the Java Runtime
(class file version 69.0), this version of the Java Runtime only
recognizes class file versions up to 52.0
```

### Root cause

owlready2 v0.50 bundles "fixed" Jena JARs (`jena-arq-fixed2.10.0.jar`,
`jena-core-fixed2.10.0.jar`) that were recompiled by the owlready2 maintainers
with a modern Java compiler (producing class file version 69 = Java 25).

Java 8 (class file version 52) cannot load class files compiled for Java 25.
The incompatibility is in the Jena loader, which Pellet uses to parse the
N-Triples input file.

## HermiT status: WORKING

`sync_reasoner_hermit()` uses a different JAR set that is Java 8 compatible.
HermiT confirmed functional with the same Java installation.

**Limitation:** HermiT does not execute SWRL rules. If we use HermiT,
SWRL `DLSafeRule` axioms in the OWL file are silently ignored.

## Fix options

| Option | What | Impact |
|--------|------|--------|
| **A — Upgrade Java (recommended)** | Install Java 21 LTS (OpenJDK) or Java 25, update JAVA_HOME + PATH | Pellet works → SWRL (Opzione B) confirmed |
| B — Downgrade owlready2 | `pip install owlready2==0.45` or earlier; older versions shipped Jena 8-compatible JARs | Risk: API changes in owlready2 |
| C — Switch to Opzione A | Use HermiT + OWL `SubClassOf (requiresTool some …)` restrictions | Gives up SWRL verb+object semantics |
| D — Python-native SWRL | Match lemmas manually in Python without a reasoner | Requires explicit user approval |

## Recommendation

**Install Java 21 LTS** (OpenJDK — free, cross-platform).  
Download: `https://adoptium.net/` (Adoptium/Eclipse Temurin builds)

After install:
```
java -version  # should report 21.x
```

Then re-run:
```
python scripts/test_pellet.py
```

Expected output: `SMOKE TEST PASSED`.
