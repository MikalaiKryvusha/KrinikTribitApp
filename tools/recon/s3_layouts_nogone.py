"""Layout survey: own layouts, scroll presence, rough min content height (dp), hard-coded vs @dimen.
Usage: python -I s3_layouts.py <repo>   -> prints summary, writes layouts.tsv next to the script (cwd)."""
import pathlib, re, sys, collections
import xml.etree.ElementTree as ET
R = pathlib.Path(sys.argv[1])
RES = R / "work/base/res"
SRC = R / "decompiled/jadx-base/sources/com/thousandshores"
A = "{http://schemas.android.com/apk/res/android}"
APP = "{http://schemas.android.com/apk/res-auto}"

dimens = {}
for e in ET.parse(RES / "values/dimens.xml").getroot():
    if e.tag == "dimen":
        dimens[e.get("name")] = (e.text or "").strip()

def dp(v, depth=0):
    """dp value of a dimension string; None for match_parent/wrap/unknown."""
    if v is None or depth > 5: return None
    if v.startswith("@dimen/"): return dp(dimens.get(v[7:]), depth + 1)
    m = re.fullmatch(r"(-?[\d.]+)(dip|dp|sp|px|pt|mm|in)", v)
    return float(m.group(1)) if m else None

all_layouts = {p.stem: p for p in (RES / "layout").glob("*.xml")}
# own layouts: referenced from com.thousandshores code, plus their <include>s
refs = set()
for f in SRC.rglob("*.java"):
    if "/databinding/" in f.as_posix() or f.name.startswith("R"): continue
    refs.update(re.findall(r"R\.layout\.(\w+)", f.read_text(encoding="utf-8", errors="replace")))
own = set(l for l in refs if l in all_layouts)
queue = list(own)
while queue:
    t = all_layouts[queue.pop()].read_text(encoding="utf-8")
    for inc in re.findall(r'layout="@layout/(\w+)"', t):
        if inc in all_layouts and inc not in own:
            own.add(inc); queue.append(inc)

SCROLL = ("ScrollView", "NestedScrollView", "RecyclerView", "ListView", "GridView", "ViewPager",
          "ViewPager2", "WebView", "SmartRefreshLayout", "ExpandableListView")
def short(tag): return tag.rsplit(".", 1)[-1]
def is_scroll(tag): return any(short(tag).endswith(s) for s in SCROLL)

def vmargins(n):
    m = dp(n.get(A + "layout_margin")) or 0
    t = dp(n.get(A + "layout_marginTop")) or dp(n.get(A + "layout_marginVertical")) or m
    b = dp(n.get(A + "layout_marginBottom")) or dp(n.get(A + "layout_marginVertical")) or m
    return t or 0, b or 0

def vpad(n):
    p = dp(n.get(A + "padding")) or 0
    t = dp(n.get(A + "paddingTop")) or dp(n.get(A + "paddingVertical")) or p
    b = dp(n.get(A + "paddingBottom")) or dp(n.get(A + "paddingVertical")) or p
    return (t or 0) + (b or 0)

def children(n):
    return [c for c in n if c.tag not in ("data", "requestFocus", "tag") and not c.tag.startswith("{")]

def root_of(path):
    r = ET.parse(path).getroot()
    if r.tag == "layout":
        ch = children(r)
        return ch[0] if ch else None
    return r

def est(n, seen):
    """min height in dp of node n (0 for flexible parts)."""
    if n.get(A + "visibility") == "gone" and (n.get("layout") or "").find("no_") >= 0: return 0.0
    tag = n.tag
    if tag == "include":
        name = (n.get("layout") or "")[8:]
        h = dp(n.get(A + "layout_height"))
        if h is not None: return h
        if name in all_layouts and name not in seen:
            r = root_of(all_layouts[name])
            return est(r, seen | {name}) if r is not None else 0.0
        return 0.0
    if tag == "merge":
        return sum(full(c, seen) for c in children(n))
    h = n.get(A + "layout_height")
    hv = dp(h)
    if hv is not None and hv > 0: return hv
    if is_scroll(tag): return 0.0
    ch = children(n)
    if not ch and (h in ("match_parent", "fill_parent") or hv == 0): return 0.0
    if not ch:
        s = short(tag)
        if "Text" in s or "Button" in s or "EditText" in s:
            ts = dp(n.get(A + "textSize")) or 14
            return ts * 1.35 + vpad(n)
        return vpad(n)
    s = short(tag)
    if s == "LinearLayout" and n.get(A + "orientation") == "vertical":
        return sum(full(c, seen) for c in ch) + vpad(n)
    if s == "ConstraintLayout": return constraint(ch, seen) + vpad(n)
    if s == "RelativeLayout": return relative(ch, seen) + vpad(n)
    return max(full(c, seen) for c in ch) + vpad(n)

def full(c, seen):
    t, b = vmargins(c)
    return est(c, seen) + t + b

def cid(c):
    i = c.get(A + "id") or ""
    return i.split("/")[-1]

def constraint(ch, seen):
    byid = {cid(c): c for c in ch}
    top, bot = {}, {}
    def tpos(c, d=0):
        k = id(c)
        if k in top: return top[k]
        if d > 50: return 0
        t, b = vmargins(c)
        ref = c.get(APP + "layout_constraintTop_toBottomOf")
        base = 0.0
        if ref and ref != "parent" and ref.split("/")[-1] in byid:
            base = tpos(byid[ref.split("/")[-1]], d + 1)
        else:
            ref2 = c.get(APP + "layout_constraintTop_toTopOf")
            if ref2 and ref2 != "parent" and ref2.split("/")[-1] in byid:
                o = byid[ref2.split("/")[-1]]
                base = tpos(o, d + 1) - est(o, seen) - vmargins(o)[1]
        top[k] = base + t + est(c, seen) + b
        return top[k]
    def bpos(c, d=0):
        k = id(c)
        if k in bot: return bot[k]
        if d > 50: return 0
        t, b = vmargins(c)
        ref = c.get(APP + "layout_constraintBottom_toTopOf")
        base = 0.0
        if ref and ref != "parent" and ref.split("/")[-1] in byid:
            base = bpos(byid[ref.split("/")[-1]], d + 1)
        bot[k] = base + t + est(c, seen) + b
        return bot[k]
    tops = [tpos(c) for c in ch if c.get(APP + "layout_constraintTop_toBottomOf") or c.get(APP + "layout_constraintTop_toTopOf") or not c.get(APP + "layout_constraintBottom_toBottomOf")]
    bots = [bpos(c) for c in ch if (c.get(APP + "layout_constraintBottom_toBottomOf") == "parent" or c.get(APP + "layout_constraintBottom_toTopOf")) and not c.get(APP + "layout_constraintTop_toBottomOf")]
    return max(tops or [0]) + max(bots or [0])

def relative(ch, seen):
    byid = {cid(c): c for c in ch}
    memo = {}
    def pos(c, d=0):
        k = id(c)
        if k in memo: return memo[k]
        t, b = vmargins(c)
        ref = (c.get(A + "layout_below") or "").split("/")[-1]
        base = pos(byid[ref], d + 1) if ref in byid and d < 50 else 0.0
        memo[k] = base + t + est(c, seen) + b
        return memo[k]
    tops = [pos(c) for c in ch if c.get(A + "layout_alignParentBottom") != "true"]
    bots = [full(c, seen) for c in ch if c.get(A + "layout_alignParentBottom") == "true"]
    return max(tops or [0]) + max(bots or [0])

rows = []
dimcnt = collections.Counter()
for name in sorted(own):
    p = all_layouts[name]
    txt = p.read_text(encoding="utf-8")
    for m in re.finditer(r'android:(layout_(?:width|height|margin\w*)|padding\w*|textSize)="([^"]+)"', txt):
        v = m.group(2)
        if v.startswith("@dimen/"): dimcnt["@dimen"] += 1
        elif re.fullmatch(r"-?[\d.]+(dip|dp|sp|px)", v) and float(re.match(r"-?[\d.]+", v).group()) != 0: dimcnt["hard"] += 1
    try:
        r = root_of(p)
    except ET.ParseError:
        continue
    if r is None: continue
    all_tags = [e.tag for e in r.iter()]
    any_scroll = any(is_scroll(t) for t in all_tags)
    root_scroll = is_scroll(r.tag) or (len(children(r)) == 1 and is_scroll(children(r)[0].tag))
    h = round(est_root := (est(r, {name}) if r.get(A + "layout_height") not in ("match_parent", "fill_parent") else (
        sum(full(c, {name}) for c in children(r)) if short(r.tag) == "LinearLayout" and r.get(A + "orientation") == "vertical"
        else constraint(children(r), {name}) if short(r.tag) == "ConstraintLayout"
        else relative(children(r), {name}) if short(r.tag) == "RelativeLayout"
        else max([full(c, {name}) for c in children(r)] or [0])) + vpad(r)))
    rows.append((name, short(r.tag), "root" if root_scroll else ("inner" if any_scroll else "none"), h))

kind = lambda n: n.split("_")[0]
print("layouts total in res/layout:", len(all_layouts), "| own (Tribit code + includes):", len(own))
c = collections.Counter(k for _, _, k, _ in rows)
print("scroll: root", c["root"], "| inner", c["inner"], "| none", c["none"])
print("own by prefix:", collections.Counter(kind(n) for n, *_ in rows).most_common(8))
screens = [r for r in rows if r[0].startswith("activity_") or r[0].startswith("fragment_")]
print("screens (activity_/fragment_):", len(screens), "| root-scroll", sum(r[2] == "root" for r in screens),
      "| inner-scroll", sum(r[2] == "inner" for r in screens), "| no scroll", sum(r[2] == "none" for r in screens))
for lo, hi in ((0, 230), (230, 560), (560, 667), (667, 800), (800, 99999)):
    print(f"  no-scroll screens with est. content {lo}-{hi} dp:", sum(r[2] == "none" and lo <= r[3] < hi for r in screens))
print("dimension attrs in own layouts:", dict(dimcnt))
pathlib.Path("layouts.tsv").write_text("\n".join("\t".join(map(str, r)) for r in rows), encoding="utf-8")
