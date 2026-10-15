"""Compact tree of a layout: tag, id, height, vertical margins. Usage: python -I s4_tree.py <res dir> <layout> [maxdepth]"""
import pathlib, sys
import xml.etree.ElementTree as ET
A = "{http://schemas.android.com/apk/res/android}"
res = pathlib.Path(sys.argv[1]); name = sys.argv[2]; maxd = int(sys.argv[3]) if len(sys.argv) > 3 else 4
def walk(n, d):
    if d > maxd or n.tag in ("data", "variable", "import"): return
    g = lambda k: n.get(A + k)
    extra = " ".join(f"{k}={g(k)}" for k in ("layout_height", "layout_weight", "layout_marginTop", "layout_marginBottom", "visibility", "orientation") if g(k))
    lay = n.get("layout") or ""
    print("  " * d + f"{n.tag.rsplit('.',1)[-1]} {(g('id') or '').split('/')[-1]} {lay} {extra}")
    for c in n: walk(c, d + 1)
walk(ET.parse(res / f"layout/{name}.xml").getroot(), 0)
