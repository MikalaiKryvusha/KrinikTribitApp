"""Reconnect-retry defect: retry branch re-enters checkedToConnect while isConnecting is still true.
Usage: python -I s2_reconnect.py <jadx sources dir>"""
import pathlib, re, sys
S = pathlib.Path(sys.argv[1]) / "com/thousandshores/tribit"
for f in sorted(S.rglob("*.java")):
    t = f.read_text(encoding="utf-8", errors="replace")
    if "普通连接。。 中" not in t:
        continue
    lines = t.splitlines()
    guard = [i + 1 for i, l in enumerate(lines) if "普通连接。。 中" in l]
    # retry branch: a "reconnect = i - 1" style decrement
    dec = [i + 1 for i, l in enumerate(lines) if re.search(r"\.reconnect = \w+ - 1;", l)]
    bad = []
    for d in dec:
        window = lines[d - 1:d + 6]
        if not any("isConnecting = false" in w for w in window):
            bad.append(d)
    print(f"{f.name}: guard@{guard} retry-decrement@{dec} retry-without-reset@{bad}")
