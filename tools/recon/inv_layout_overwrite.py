"""Which layout literals are likely overwritten in code by setText? python -I this.py <apktool-dir> <jadx-sources>"""
import pathlib, re, sys, collections
ROOT, SRC = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
CJK = re.compile(r"[　-〿㐀-䶿一-鿿＀-￯]")
code = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in (SRC / "com/thousandshores").rglob("*.java"))
settext_ids = set(re.findall(r"R\.id\.(\w+)\)*\.setText\(", code))
settext_fields = set(re.findall(r"\.(\w+)\.setText\(", code))
def camel(s): p = s.split("_"); return p[0] + "".join(x[:1].upper() + x[1:] for x in p[1:])
tag = re.compile(r"<[^>]*?android:text=\"([^@?\"][^\"]*)\"[^>]*>")
n = cjk = ow = ow_cjk = noid = 0
for f in (ROOT / "res").glob("layout*/*.xml"):
    for m in tag.finditer(f.read_text(encoding="utf-8")):
        t = m.group(0); v = m.group(1); c = bool(CJK.search(v))
        n += 1; cjk += c
        mid = re.search(r'android:id="@\+?id/(\w+)"', t)
        if not mid: noid += 1; continue
        i = mid.group(1)
        if i in settext_ids or camel(i) in settext_fields:
            ow += 1; ow_cjk += c
print(f"android:text literals {n} (CJK {cjk}); without id (never touched by code) {noid}; "
      f"id is setText()-ed somewhere in own code: {ow} (CJK {ow_cjk}); left as-is: {n-ow} (CJK {cjk-ow_cjk})")
