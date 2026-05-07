# Pellet Smoke Test Report

Date: 2026-05-07  
Branch: feature/owl-integration

## Final Status: PASSED (after JAR patch)

## Environment

| Component | Value |
|-----------|-------|
| Java (after upgrade) | OpenJDK 21.0.11 Temurin LTS |
| owlready2 version | 0.50 (patched) |
| Python version | 3.10.11 |

## Root Cause

owlready2 0.50 bundles `jena-arq-fixed2.10.0.jar`, which contains three
`LangRDFXML` classes compiled with Java 25 (class file version 69).
Java 21 supports only up to class file version 65.

The rest of the JAR (≈ 500 other classes) is compiled for Java 6 — only
three classes are the problem:

- `org/apache/jena/riot/lang/LangRDFXML.class` (was: 69, now: 50)
- `org/apache/jena/riot/lang/LangRDFXML$HandlerSink.class` (was: 69, now: 50)
- `org/apache/jena/riot/lang/LangRDFXML$ErrorHandlerBridge.class` (was: 69, now: 50)

## Fix Applied

Replaced the three Java-25 classes with their originals from the official
Apache Jena 2.10.0 release (`jena-arq-2.10.0.jar` from Maven Central).
The originals are compiled for Java 6 (class version 50) — fully compatible
with Java 21 (which supports up to class version 65).

Backup of the original owlready2 JAR is at:
`jena-arq-fixed2.10.0.jar.bak_java25` in the owlready2 pellet directory.

Apply the fix on a new machine:
```
python scripts/patch_owlready2_jars.py
```

## Smoke Test Output

```
Java detected: openjdk version "21.0.11" 2026-04-21 LTS
Individual type before reasoning: [A]
Running sync_reasoner_pellet ...
Individual type after reasoning: [A, B]
SMOKE TEST PASSED: SWRL rule fired correctly.
```

## Notes for Teammates

1. Install Java 21 LTS from https://adoptium.net/temurin/releases/?version=21
2. Ensure `java -version` shows 21.x
3. Run `python scripts/patch_owlready2_jars.py` once per machine
4. Run `python scripts/test_pellet.py` to confirm
