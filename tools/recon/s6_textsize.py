"""textSize units in own layouts. Usage: python -I s6_textsize.py <res dir> <layouts.tsv>"""
import pathlib, re, sys, collections
res = pathlib.Path(sys.argv[1]); own = [l.split("\t")[0] for l in pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()]
dim = dict(re.findall(r'<dimen name="(\w+)">([^<]+)<', (res / "values/dimens.xml").read_text(encoding="utf-8")))
c = collections.Counter()
for n in own:
    for v in re.findall(r'android:textSize="([^"]+)"', (res / f"layout/{n}.xml").read_text(encoding="utf-8")):
        v = dim.get(v[7:], v) if v.startswith("@dimen/") else v
        c["sp" if v.endswith("sp") else "dp" if v.endswith(("dip", "dp")) else "other"] += 1
print("textSize units in own layouts:", dict(c))
