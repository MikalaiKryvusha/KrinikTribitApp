#!/usr/bin/env python3
"""Fetch the speaker pictures of Tribit's model catalog - the owner's exception 2 to HOUSE_RULES R2 (2026-10-16 ≈ 20:0x
+03:00: «мы сейчас забираем у него картинки из запросов и зашиваем в наш апп» · «наш апп не будет делать запросы на
сервер»). Run by the agent on this machine, never by the app.

The catalog itself is NOT requested: the gateway answers it only to a logged-in guest («Full authentication is required»,
2026-10-16 20:12), and the answer already sits in the request log of their app on the A51
(`diagnostics/2026-10-16_a51_easyhttp_visitor.log`, `DeviceDetail@…` = `produCateByClient?clientId=Tribit`, 09:44). So the
only requests are plain GETs of the picture URLs in that answer (`resource.1000shores.com`, their app loads them with
Glide - `utils/UpdateUtils.java`). Nothing about a user or a phone is sent.

Everything lands in design/photos/tribit_server/ (ignored by git): catalog.json and one file per picture, named by model.
[NOT-TESTED]

Usage: python -I tools/fetch_speaker_images.py [log]
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

LOG = os.path.join("diagnostics", "2026-10-16_a51_easyhttp_visitor.log")
OUT = os.path.join("design", "photos", "tribit_server")
AGENT = "Krinik Tribit design fetch"
TIMEOUT_S = 30
TAG = re.compile(r"I EasyHttp (DeviceDetail@[0-9a-f]+): ?(.*)$")


FIELD = re.compile(r'"(\w+)"\s*:\s*"([^"]*)"')


def catalog_from_log(path):
    """The catalog as [{field: value}] from the lines of the FIRST DeviceDetail request in the log, read field by field:
    a «productName» line opens a new model, every other string field belongs to it (the log prints the JSON pretty,
    one field per line - a whole-JSON parse stopped at the first inner object and gave 1 picture of 23, 20:13)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    first, models = None, []
    for line in lines:
        m = TAG.search(line)
        if not m:
            continue
        first = first or m.group(1)
        if m.group(1) != first:
            continue
        for key, value in FIELD.findall(m.group(2)):
            if key == "productName":
                models.append({})
            if models:
                models[-1][key] = value
    if not models:
        raise SystemExit(f"no DeviceDetail answer in {path}")
    return models


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "model"


def main():
    os.makedirs(OUT, exist_ok=True)
    data = catalog_from_log(sys.argv[1] if len(sys.argv) > 1 else LOG)
    with open(os.path.join(OUT, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    seen = set()
    for item in walk(data):
        name = str(item.get("productName") or item.get("productModel") or "")
        if not name:
            continue
        for key, url in item.items():
            if not isinstance(url, str) or not url.startswith("http"):
                continue
            path = urllib.parse.urlparse(url).path.lower()
            if not path.endswith((".png", ".jpg", ".jpeg", ".webp")) or url in seen:
                continue
            seen.add(url)
            file = os.path.join(OUT, f"{safe(name)}__{safe(key)}{os.path.splitext(path)[1]}")
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=TIMEOUT_S) as r:
                    img = r.read()
            except Exception as e:  # one broken picture never stops the rest
                print(f"FAIL {name} {key}: {e}")
                continue
            with open(file, "wb") as f:
                f.write(img)
            print(f"{file}  {len(img)} bytes")
    print(f"pictures: {len(seen)}")


if __name__ == "__main__":
    sys.exit(main())
