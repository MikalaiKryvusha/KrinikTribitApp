"""Manifest + activity code survey. Usage: python -I s1_manifest.py <repo>"""
import pathlib, re, sys, collections
R = pathlib.Path(sys.argv[1])
man = (R / "work/base/AndroidManifest.xml").read_text(encoding="utf-8")
SRC = R / "decompiled/jadx-base/sources"
acts = re.findall(r"<activity(?:-alias)? ([^>]*)>", man)
print("activity tags:", len(acts))
own = []
ori = collections.Counter(); cc = collections.Counter()
for a in acts:
    name = re.search(r'android:name="([^"]+)"', a).group(1)
    o = re.search(r'screenOrientation="([^"]+)"', a)
    c = re.search(r'configChanges="([^"]+)"', a)
    mine = name.startswith("com.thousandshores")
    if mine: own.append(name)
    ori[(mine, o.group(1) if o else "-")] += 1
    if c: cc[(mine, c.group(1))] += 1
    if o: print("  orientation", o.group(1), name)
print("own activities:", len(own))
print("orientation (own?, value):", dict(ori))
print("configChanges (own?, value):", dict(cc))
for m in re.finditer(r'resizeableActivity="([^"]+)"|android:theme="(@style/[^"]+)"', man[:man.find("<activity")]):
    print("  app attr", m.group(0))
# code
rso, save, restore, cfg, nolayout = 0, [], [], [], []
lay = {}
for name in own:
    f = SRC / (name.replace(".", "/") + ".java")
    if not f.exists():
        nolayout.append(name); continue
    t = f.read_text(encoding="utf-8", errors="replace")
    if "onSaveInstanceState" in t: save.append(name.rsplit(".", 1)[1])
    if "onRestoreInstanceState" in t or re.search(r"bundle\.get|savedInstanceState\.get", t): restore.append(name.rsplit(".", 1)[1])
    if "onConfigurationChanged" in t: cfg.append(name.rsplit(".", 1)[1])
    m = re.findall(r"R\.layout\.(\w+)", t)
    lay[name] = m
print("own activities overriding onSaveInstanceState:", len(save), save)
print("own activities reading a saved bundle:", len(restore), restore)
print("own activities with onConfigurationChanged:", len(cfg), cfg)
print("own activities w/o jadx file:", nolayout)
n = 0
for f in (SRC / "com/thousandshores").rglob("*.java"):
    t = f.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(t.splitlines(), 1):
        if "setRequestedOrientation" in line:
            n += 1; print("  setRequestedOrientation", f.relative_to(SRC), i)
print("setRequestedOrientation in own code:", n)
pathlib.Path("act_layouts.txt").write_text("\n".join(f"{k}\t{','.join(v)}" for k, v in lay.items()), encoding="utf-8")
