"""(b)+(c) Hard-coded strings and server-key usage in own code. python -I inv_code.py <jadx-sources> <apktool-dir>"""
import pathlib, re, sys, collections
SRC, ROOT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
OWN = SRC / "com/thousandshores"
CJK = re.compile(r"[　-〿㐀-䶿一-鿿＀-￯]")
LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
SINK = re.compile(r"\b(setText|setHint|setTitle|setSubTitle|setMessage|setContent|setContentText|setLeftTitle|setRightTitle|"
                  r"setLeftText|setRightText|setConfirmText|setCancelText|setPositiveButton|setNegativeButton|setTips|"
                  r"showToast|makeText|ToastUtils\.show|ToastUtils\.showShort|ToastUtils\.showLong|setTitleText|setBtnText|setItemList)\s*\(")
LOG = re.compile(r"\b(Log|LogUtils|BleLogger|Timber|XLog|LogUtil)\.\w+\(|printStackTrace|\.d\(\"|synchPoint")
VISIBLE = re.compile(r"[A-Za-z一-鿿]{2}")  # literal must look like words

sink_tot = sink_cjk = 0; sink_cls = collections.Counter(); sink_cjk_cls = collections.Counter(); sink_uniq = set()
cjk_all = 0; cjk_cls = collections.Counter(); cjk_zh_branch = 0; cjk_uniq = set()
ret_cjk = 0
for f in OWN.rglob("*.java"):
    if f.name in ("R.java", "BuildConfig.java"):
        continue
    cls = str(f.relative_to(SRC)).replace("\\", "/")[:-5].replace("/", ".")
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, ln in enumerate(lines):
        if LOG.search(ln) or ln.lstrip().startswith(("//", "/*", "*", "@")):
            continue
        lits = [l for l in LIT.findall(ln)]
        if not lits:
            continue
        cj = [l for l in lits if CJK.search(l)]
        if cj:
            ctx = "\n".join(lines[max(0, i - 4):i + 1])
            zh = '"zh"' in ctx or "zh_CN" in ctx
            for l in cj:
                cjk_all += 1; cjk_cls[cls] += 1; cjk_uniq.add(l); cjk_zh_branch += zh
            if ln.strip().startswith("return "):
                ret_cjk += len(cj)
        if SINK.search(ln):
            vis = [l for l in lits if VISIBLE.search(l) and not l.startswith(("http", "#", "%"))]
            for l in vis:
                sink_tot += 1; sink_uniq.add(l); sink_cls[cls] += 1
                if CJK.search(l):
                    sink_cjk += 1; sink_cjk_cls[cls] += 1

print(f"(b) literals in visible sinks (setText/Toast/dialog setters) in com.thousandshores: {sink_tot} (unique {len(sink_uniq)}), CJK {sink_cjk}")
print("   top classes:"); [print(f"     {n:3d} (CJK {sink_cjk_cls[c]:3d}) {c}") for c, n in sink_cls.most_common(12)]
print(f"(b') ALL CJK literals in own code outside log lines: {cjk_all} (unique {len(cjk_uniq)}), in a 'zh' branch (<=4 lines after \"zh\"): {cjk_zh_branch}, in return statements: {ret_cjk}")
print("   top classes:"); [print(f"     {n:3d} {c}") for c, n in cjk_cls.most_common(12)]

# (c) server keys = resource entry names fetched through ResourceUtils.getString / direct SP reads
code = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in OWN.rglob("*.java"))
calls = re.findall(r"ResourceUtils\.getString\(R\.string\.(\w+)", code)
other_get = re.findall(r"(?<!ResourceUtils)\.getString\(R\.string\.(\w+)", code)
import xml.etree.ElementTree as ET
sx = ET.parse(ROOT / "res/values/strings.xml").getroot()
names = {e.get("name"): ("".join(e.itertext())) for e in sx if e.tag == "string"}
sp_direct = set(k for k in re.findall(r'SPUtils\.getInstance\(\)\.getString\("(\w+)"', code) if k in names)
lay_refs = set()
for f in (ROOT / "res").glob("layout*/*.xml"):
    lay_refs.update(re.findall(r'"@string/(\w+)"', f.read_text(encoding="utf-8")))
via_ru = set(calls)
print(f"(c) ResourceUtils.getString(R.string.X) call sites: {len(calls)}, distinct keys {len(via_ru)}; other getString(R.string) sites: {len(other_get)}")
print(f"    keys read straight from SPUtils by literal name that are also string names: {sorted(sp_direct)}")
print(f"    strings.xml: {len(names)} strings; used via ResourceUtils {len(via_ru & names.keys())}; only via layouts @string {len((lay_refs - via_ru) & names.keys())}; "
      f"layout @string refs total distinct {len(lay_refs & names.keys())}; neither {len(names.keys() - via_ru - lay_refs)}")
print(f"    keys used in code but missing in strings.xml: {sorted(via_ru - names.keys())[:10]}")
cjk_vals = [k for k, v in names.items() if CJK.search(v)]
print(f"    strings.xml values containing CJK: {len(cjk_vals)} e.g. {cjk_vals[:8]}")
empty = [k for k, v in names.items() if not v.strip()]
print(f"    empty values: {len(empty)}")
fmt = sum(1 for k in via_ru & names.keys() if re.search(r"%(\d\$)?[sdf]", names[k]))
print(f"    used keys with format args: {fmt}")
dyn = len(re.findall(r"ResourceUtils\.getStringFormServer\(", code))
print(f"    ResourceUtils.getStringFormServer(String) dynamic-key call sites: {dyn}")
