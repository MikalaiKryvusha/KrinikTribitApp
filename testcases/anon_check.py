"""Acceptance check of patch 8 «Tribit does not learn who the person is» (plans/01 §4б, the criterion under the owner's
principle 2026-10-16 10:50 +03:00): no real value of the phone or the speaker in any request to Tribit's server.

Usage:
    adb -s <serial> logcat -d --pid <pid> > <log>
    python testcases/anon_check.py <log> <real value> [<real value> ...]
Real values: the app's ANDROID_ID (the emailAccount of their original guest login), Build.MODEL, «Android <release>»,
the serial number, the speaker MAC, the account e-mail if any. A MAC is also searched without colons.
Reads every EasyHttp line of the app's own log (URL, parameters, bodies); prints the guest fields it sent, the API paths
it called, and the hits of each real value. Exit 1 when any real value is found, 2 when the log has no guest login.
[NOT-TESTED]
"""
import re
import sys

log_path, real = sys.argv[1], [v for v in sys.argv[2:] if v]
lines = [l for l in open(log_path, encoding="utf-8", errors="replace") if " EasyHttp " in l]
paths = sorted({m.group(1) for l in lines for m in [re.search(r"RequestUrl = https?://[^/]+(/[^?\s]*)", l)] if m})
fields = [re.sub(r"^.*?: ", "", l.strip()) for l in lines
          if re.search(r": (emailAccount|logMobModel|operSystem|packageName) = ", l)]
print("paths called:")
for p in paths:
    print("  " + p)
print("guest/identity fields sent:")
for f in fields:
    print("  " + f)
hits = 0
for v in real:
    variants = {v.lower(), v.replace(":", "").lower()}
    n = sum(1 for l in lines if any(x in l.lower() for x in variants))
    hits += n
    print(f"real value {v!r}: {n} line(s)")
if not any("emailAccount" in f for f in fields):
    print("FAIL: no guest login in this log")
    sys.exit(2)
print("OK: no real value reached a request" if hits == 0 else f"FAIL: {hits} line(s) carry a real value")
sys.exit(1 if hits else 0)
