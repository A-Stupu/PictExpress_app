"""
Patch owlready2's bundled Pellet JARs for compatibility with Java 21 LTS.

owlready2 0.50 ships jena-arq-fixed2.10.0.jar with three LangRDFXML
classes compiled for Java 25 (class file version 69). Java 21 only
supports up to class file version 65, so Pellet crashes on startup.

This script replaces those three classes with the originals from the
official Apache Jena 2.10.0 release (compiled for Java 6, class version 50).

Usage (run once per machine after installing owlready2):
    python scripts/patch_owlready2_jars.py

A backup of the original JAR is written alongside it as .bak_java25.
"""

import sys
import struct
import zipfile
import shutil
import tempfile
import os
from pathlib import Path

MAVEN_URL = (
    "https://repo1.maven.org/maven2/org/apache/jena/jena-arq/2.10.0/"
    "jena-arq-2.10.0.jar"
)
TARGET_CLASSES = {
    "org/apache/jena/riot/lang/LangRDFXML.class",
    "org/apache/jena/riot/lang/LangRDFXML$HandlerSink.class",
    "org/apache/jena/riot/lang/LangRDFXML$ErrorHandlerBridge.class",
}
JAVA25_CLASS_VERSION = 69  # requires Java 25
MAX_SUPPORTED_VERSION = 65  # Java 21


def get_class_version(data: bytes) -> int:
    _, minor, major = struct.unpack(">IHH", data[:8])
    return major


def needs_patch(jar_path: Path) -> bool:
    with zipfile.ZipFile(jar_path) as zf:
        for name in zf.namelist():
            if name in TARGET_CLASSES:
                data = zf.read(name)
                if get_class_version(data) > MAX_SUPPORTED_VERSION:
                    return True
    return False


def download_jar(url: str) -> bytes:
    try:
        import urllib.request
        print(f"Downloading {url} ...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        print(f"  Downloaded {len(data):,} bytes.")
        return data
    except Exception as exc:
        sys.exit(f"Failed to download original Jena JAR: {exc}")


def extract_replacements(jar_data: bytes) -> dict[str, bytes]:
    replacements = {}
    with zipfile.ZipFile(tempfile.SpooledTemporaryFile()) as tmp:
        pass  # just test import
    import io
    with zipfile.ZipFile(io.BytesIO(jar_data)) as zf:
        for name in zf.namelist():
            if name in TARGET_CLASSES:
                data = zf.read(name)
                ver = get_class_version(data)
                replacements[name] = data
                print(f"  Replacement: {name}  class_version={ver} (Java {ver - 44}+)")
    return replacements


def patch_jar(jar_path: Path, replacements: dict[str, bytes]) -> None:
    backup = jar_path.with_suffix(".jar.bak_java25")
    if not backup.exists():
        shutil.copy2(jar_path, backup)
        print(f"Backup: {backup}")
    else:
        print(f"Backup already exists: {backup}")

    tmp_path = jar_path.with_suffix(".jar.patching")
    with zipfile.ZipFile(jar_path) as zin, \
         zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in replacements:
                print(f"  Replacing {item.filename}")
                zout.writestr(item, replacements[item.filename])
            else:
                zout.writestr(item, zin.read(item.filename))

    os.replace(tmp_path, jar_path)
    print(f"Patched: {jar_path}")


def main() -> None:
    try:
        import owlready2
    except ImportError:
        sys.exit("owlready2 not installed. Run: pip install owlready2")

    pellet_dir = Path(owlready2.__file__).parent / "pellet"
    fixed_jar = pellet_dir / "jena-arq-fixed2.10.0.jar"

    if not fixed_jar.exists():
        sys.exit(f"JAR not found: {fixed_jar}")

    if not needs_patch(fixed_jar):
        print("No patch needed — all LangRDFXML classes are already Java 21 compatible.")
        return

    print(f"Patch needed in: {fixed_jar}")
    orig_data = download_jar(MAVEN_URL)
    replacements = extract_replacements(orig_data)

    if len(replacements) != 3:
        sys.exit(
            f"Expected 3 replacement classes, got {len(replacements)}. "
            "The original Jena 2.10.0 JAR may have changed. Aborting."
        )

    patch_jar(fixed_jar, replacements)
    print("\nPatch applied successfully.")
    print("Run 'python scripts/test_pellet.py' to verify.")


if __name__ == "__main__":
    main()
