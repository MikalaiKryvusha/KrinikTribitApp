"""Guard of the hybrid build (plans/03_epic03_phase1, step 3): a class written as source in native/src/ must not keep its
smali in native/smali*/ - Android resolves a class to its FIRST copy (android.googlesource.com/platform/art/+/de7b436),
so a forgotten smali would silently win over the source. Inner classes count too: X.java owns X$*.smali.

Usage:  python -I tools/native_src_guard.py <native-dir>      exit 1 names every class that has both.

@guard native-src-duplicate-class
THREAT:         a Tribit class rewritten in Java while its old smali still ships - the app runs the old code
PROVED-AGAINST: native/smali_classes5/.../AboutActivity.smali kept beside native/src/.../AboutActivity.java (red, exit 1)
GAP:            classes declared inside a .java under another name (one top-level class per file is the rule here)
ON-REAL-PATH:   bash build.sh runs it before compiling native/src: green build 2026-10-16 14:59
[TESTED: 2026-10-16 · red with AboutActivity.smali kept (exit 1, the file named), green after git rm]
"""
import pathlib
import sys

native = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if native is None or not (native / "apktool.yml").exists():
    sys.exit("usage: python -I tools/native_src_guard.py <native-dir>")
src = native / "src"
both = []
for f in sorted(src.rglob("*.java")) + sorted(src.rglob("*.kt")):
    rel = f.relative_to(src).with_suffix("")          # com/thousandshores/.../AboutActivity
    for d in native.glob("smali*"):
        hits = [d / f"{rel}.smali"] + sorted((d / rel.parent).glob(f"{rel.name}$*.smali"))
        both += [h for h in hits if h.exists()]
for h in both:
    print(f"FAIL: {h.relative_to(native)} still ships beside its source in native/src")
if both:
    sys.exit(1)
print(f"ok  native/src: {sum(1 for _ in src.rglob('*.java')) + sum(1 for _ in src.rglob('*.kt'))} source class(es), no smali twin")
