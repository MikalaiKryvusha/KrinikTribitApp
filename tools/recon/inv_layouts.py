"""(a) Layout literals. Usage: python -I inv_layouts.py <apktool-dir>. Read-only."""
import pathlib, re, sys, collections
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(sys.argv[1])
RES = ROOT / "res"
A = "{http://schemas.android.com/apk/res/android}"
CJK = re.compile(r"[　-〿㐀-䶿一-鿿＀-￯]")

# layout name -> id from public.xml
pub = ET.parse(RES / "values/public.xml").getroot()
lay_id = {e.get("name"): int(e.get("id"), 16) for e in pub if e.get("type") == "layout"}

# own layouts: id referenced from smali of com/thousandshores (const 0x7f...)
own_ids = set()
idre = re.compile(r"0x7f[0-9a-f]{6}")
for d in ROOT.glob("smali*/com/thousandshores"):
    for f in d.rglob("*.smali"):
        if re.match(r"R(\$|\.smali)", f.name) or f.name.startswith("BR"): continue
        for m in idre.findall(f.read_text(encoding="utf-8", errors="replace")):
            own_ids.add(int(m, 16))
own = {n for n, i in lay_id.items() if i in own_ids}
# plus layouts included (<include layout=@layout/x>) from own layouts, transitively
inc = {}
for f in RES.glob("layout*/*.xml"):
    inc.setdefault(f.stem, set()).update(re.findall(r'layout="@layout/(\w+)"', f.read_text(encoding="utf-8")))
stack = list(own)
while stack:
    for c in inc.get(stack.pop(), ()):
        if c not in own:
            own.add(c); stack.append(c)

attrs = collections.Counter(); per_file = collections.Counter(); cjk_file = collections.Counter()
tot = cjk = tot_own = cjk_own = 0
other_ns = collections.Counter()
uniq = set(); uniq_own = set()
for f in sorted(RES.glob("layout*/*.xml")):
    root = ET.parse(f).getroot()
    for el in root.iter():
        for k, v in el.attrib.items():
            if not v or v.startswith(("@", "?")):
                continue
            if k in (A + "text", A + "hint", A + "contentDescription"):
                is_own = f.stem in own
                c = bool(CJK.search(v))
                tot += 1; cjk += c; attrs[k.replace(A, "android:")] += 1
                uniq.add(v)
                if is_own:
                    tot_own += 1; cjk_own += c; uniq_own.add(v)
                    per_file[f"{f.parent.name}/{f.name}"] += 1
                    if c: cjk_file[f"{f.parent.name}/{f.name}"] += 1
            elif k.startswith("{http://schemas.android.com/apk/res-auto}") and re.search(r"[A-Za-z一-鿿]{2}", v) \
                    and re.search(r"(?i)text|title|hint|desc", k) and f.stem in own:
                other_ns[k.split("}")[1]] += 1

print(f"layouts total {len(list(RES.glob('layout*/*.xml')))}, own (referenced from com/thousandshores smali + includes) {len(own)}")
print(f"literal text/hint/contentDescription: all={tot} (CJK {cjk}); own={tot_own} (CJK {cjk_own}); unique own values={len(uniq_own)}")
print("by attr (all):", dict(attrs))
print("own files with literals:", len(per_file), " files with CJK:", len(cjk_file))
print("top own files:"); [print(f"  {n:4d} {k}  (CJK {cjk_file[k]})") for k, n in per_file.most_common(15)]
print("top CJK files:"); [print(f"  {n:4d} {k}") for k, n in cjk_file.most_common(10)]
print("app: namespace text-like literal attrs in own layouts:", dict(other_ns.most_common(10)))
