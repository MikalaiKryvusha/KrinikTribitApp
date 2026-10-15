"""Add our compiled classes.dex to a built APK as the next classesN.dex (Android loads every classesN.dex in order).

Usage:  python -I patches/add_dex.py <apk> <our classes.dex>
Fails if the APK's dex files are not numbered contiguously (classes.dex, classes2.dex, ...) - a gap would hide ours.
[NOT-TESTED]
"""
import re
import sys
import zipfile

apk, dex = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(apk) as z:
    names = [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", n)]
numbers = sorted(1 if n == "classes.dex" else int(n[7:-4]) for n in names)
if numbers != list(range(1, len(numbers) + 1)):
    sys.exit(f"FAIL: dex numbering has gaps: {sorted(names)}")
target = f"classes{len(numbers) + 1}.dex"
with zipfile.ZipFile(apk, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(dex, target)
print(f"ok  our code added as {target}")
