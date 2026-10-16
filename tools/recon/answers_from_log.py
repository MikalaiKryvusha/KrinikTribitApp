"""Pull the JSON answers out of the app's own EasyHttp log - raw material for the local catalog of patch 8 (research 07).

Usage:
    python tools/recon/answers_from_log.py diagnostics/2026-10-16_a51_easyhttp_visitor.log <out-dir>
Writes one file per request kind and URL path into <out-dir> (keep it under diagnostics/ or work/ - ignored by git:
the answers are their server's data and the log holds a guest token), e.g. `DeviceDetail__produCateByClient.json`,
and prints the list. The log is what the app itself received (HOUSE_RULES R2: no request of ours).
[TESTED: 2026-10-16 · ran on the A51 guest log: 7 answers written and parsed, catalog 27 products with Blast 2 · research 07]
"""
import json
import pathlib
import re
import sys

LINE = re.compile(r"EasyHttp (\w+)@([0-9a-f]+): ?(.*)$")

log, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
calls = {}  # "Kind@id" -> {"kind", "url", "body": [lines]}
for raw in log.read_text(encoding="utf-8", errors="replace").split("\n"):
    m = LINE.search(raw)
    if not m:
        continue
    kind, ident, text = m.groups()
    call = calls.setdefault(f"{kind}@{ident}", {"kind": kind, "url": "", "body": [], "open": False})
    if text.startswith("RequestUrl = "):
        call["url"] = text[len("RequestUrl = "):].split("?")[0]
    elif text.strip() == "{" and not call["body"]:
        call["open"] = True
    if call["open"]:
        call["body"].append(text)
        if text == "}":
            call["open"] = False
written = {}
for call in calls.values():
    if not call["body"] or not call["url"]:
        continue
    try:
        data = json.loads("\n".join(call["body"]))
    except json.JSONDecodeError:
        # logcat cuts a long line into several entries; between JSON tokens no separator is needed, inside a string
        # the cut must vanish - so join without one
        try:
            data = json.loads("".join(call["body"]))
        except json.JSONDecodeError:
            print(f'skip {call["kind"]} {call["url"]}: answer not parseable')
            continue
    name = f'{call["kind"]}__{call["url"].rsplit("/", 1)[-1]}.json'
    if name not in written:  # first answer of each kind wins; later ones are the same call repeated
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        written[name] = len(data.get("datas") or []) if isinstance(data.get("datas"), list) else type(data.get("datas")).__name__
for name, size in sorted(written.items()):
    print(f"{name}: datas {size}")
