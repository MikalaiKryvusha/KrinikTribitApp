#!/usr/bin/env python3
"""Fetch every device picture of Tribit's catalogs - the owner's exception 2 to HOUSE_RULES R2 (2026-10-16 ≈ 20:0x–20:3x
+03:00: «мы сейчас забираем у него картинки из запросов и зашиваем в наш апп» · «наш апп не будет делать запросы на
сервер» · «так анонимно авторизуйся» · «приди так, словно новое устройство» · «и все устройства из их каталога запроси»).
Run by the agent on this machine, never by the app.

The requests, in order (as Tribit's app 5.0.0 sends them - its own request log `diagnostics/2026-10-16_a51_easyhttp_visitor.log`):
  1. POST api-user/thirdApi/tribit-users/visitorLoginOfTribit?... - the anonymous guest login of their app
     (`ViewModelLogin.kt:282`). Every run comes as a NEW device: a random 16-hex guest id, a random real phone model of
     2022+ from our device base (`patches/assets/krinik_devices.txt`, the owner's choice 2026-10-16 11:00–11:07) and a
     random Android 15 or 16; nothing about this PC or the owner's phones. The answer's `loginToken` is the Bearer token.
  2. GET api-equip/thirdApi/equip-anon/produCateByClient?clientId=Tribit - the model catalog (`DeviceDetail.java:31-38`).
  3. GET api-equip/thirdApi/equip-anon/queryAllThridProducts - all supported devices (`GetAllDevices.java:16`).
  4. GET of every picture URL in both answers (`resource.1000shores.com`).

Everything lands in design/photos/tribit_server/ (ignored by git): login.json (the token removed), the two catalogs, one
file per picture named by model and field. [NOT-TESTED]

Usage: python -I tools/fetch_speaker_images.py
"""
import json
import os
import random
import re
import secrets
import sys
import urllib.parse
import urllib.request

GATEWAY = "https://gateway.tribit.com/"
LOGIN = "api-user/thirdApi/tribit-users/visitorLoginOfTribit"
CATALOGS = {
    "produCateByClient": "api-equip/thirdApi/equip-anon/produCateByClient?clientId=Tribit",
    "queryAllThridProducts": "api-equip/thirdApi/equip-anon/queryAllThridProducts",
}
DEVICES = os.path.join("patches", "assets", "krinik_devices.txt")
OUT = os.path.join("design", "photos", "tribit_server")
# Their app's own header, spelling included (`TribitApp.java:225`): the request looks like the app's.
CONTENT_TYPE = "applicatin/json;charset=UTF-8"
TIMEOUT_S = 30
PICTURE = (".png", ".jpg", ".jpeg", ".webp")


def call(method, path, token=None, data=None):
    headers = {"Content-Type": CONTENT_TYPE}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.loads(r.read().decode("utf-8"))


def new_device():
    """A new device every run: random guest id, random real model, random Android 15/16."""
    with open(DEVICES, encoding="ascii") as f:
        models = [line.strip().split("|", 1)[1] for line in f if "|" in line]
    return {
        "appChannel": "Google Play",
        "appVersion": "5.0.0",
        "emailAccount": secrets.token_hex(8),
        "lang": "en",
        "logMobModel": random.choice(models),
        "operSystem": f"Android {random.choice([15, 16])}",
    }


def pictures(o, name=""):
    """(model name, field, url) for every picture URL anywhere in the answer."""
    if isinstance(o, dict):
        name = str(o.get("productName") or o.get("productModel") or name)
        for k, v in o.items():
            if isinstance(v, str) and v.startswith("http") and urllib.parse.urlparse(v).path.lower().endswith(PICTURE):
                yield name, k, v
            else:
                yield from pictures(v, name)
    elif isinstance(o, list):
        for v in o:
            yield from pictures(v, name)


def safe(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_") or "x"


def save(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(OUT, exist_ok=True)
    device = new_device()
    print(f"as a new device: model={device['logMobModel']!r}, {device['operSystem']}, guest={device['emailAccount']}")
    login = call("POST", LOGIN + "?" + urllib.parse.urlencode(device), data=b"")
    token = (login.get("datas") or {}).get("loginToken")
    print(f"login: resp_code={login.get('resp_code')} msg={login.get('resp_msg')} token={'yes' if token else 'NO'}")
    if not token:
        save("login.json", login)
        return 1
    login["datas"]["loginToken"] = "<removed>"
    save("login.json", login)

    seen, n = set(), 0
    for key, path in CATALOGS.items():
        answer = call("GET", path, token)
        save(f"{key}.json", answer)
        items = answer.get("datas")
        print(f"{key}: resp_code={answer.get('resp_code')} items={len(items) if isinstance(items, list) else items!r}")
        for model, field, url in pictures(answer):
            if url in seen:
                continue
            seen.add(url)
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
            file = os.path.join(OUT, f"{safe(model)}__{safe(field)}__{safe(os.path.basename(url))[:12]}{ext}")
            try:
                with urllib.request.urlopen(url, timeout=TIMEOUT_S) as r:
                    img = r.read()
            except Exception as e:  # one broken picture never stops the rest
                print(f"FAIL {model} {field}: {e}")
                continue
            with open(file, "wb") as f:
                f.write(img)
            n += 1
    print(f"pictures: {n} of {len(seen)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
