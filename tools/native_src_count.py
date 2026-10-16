"""Counter of the epic plans/03 (acceptance criterion 3): how many of Tribit's top-level classes (com/thousandshores)
live as Java/Kotlin source in native/src/ and how many are still smali. Inner classes ($) are counted with their owner.

Usage:  python -I tools/native_src_count.py <native-dir>      prints «source N of M (P %)»
[TESTED: 2026-10-16 · «source 1 of 1259 (0.08 %)» after AboutActivity moved to native/src]
"""
import pathlib
import sys

native = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("native")
src = sorted(p for ext in ("*.java", "*.kt") for p in (native / "src" / "com" / "thousandshores").rglob(ext))
smali = sorted(p for d in native.glob("smali*") for p in (d / "com" / "thousandshores").rglob("*.smali") if "$" not in p.name)
total = len(src) + len(smali)
print(f"source {len(src)} of {total} ({100 * len(src) / total:.2f} %) Tribit top-level classes; smali {len(smali)}")
