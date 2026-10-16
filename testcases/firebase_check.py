"""Patch 21 check: what Firebase does from a clean start to the main screen.

Usage (PowerShell, PYTHONUTF8=1, the UI agent started on the device):
    python testcases/firebase_check.py <serial> <agent port>
Clears our package's data, starts it, taps START, allows «nearby devices», waits 15 s on the main screen, then counts the
logcat lines (whole device, since the start) of Firebase tags and prints the permissions the package holds that are
about ads and pushes. Run on the build without patch 21 (control) and with it.
[NOT-TESTED]
"""
import collections
import subprocess
import sys
import time

sys.path.append(r"C:\Android\private\ui-agent")
from ui import Agent  # noqa: E402

ADB = r"C:\Android\Sdk\platform-tools\adb.exe"
PACKAGE = "com.kriniks.tribit.old"
TAGS = ("FA", "FA-SVC", "FirebaseCrashlytics", "FirebaseMessaging", "FirebaseSessions", "FirebaseInstallations",
        "FirebaseApp", "FirebaseInAppMessaging")
AD_PERMS = ("AD_ID", "ACCESS_ADSERVICES", "c2dm.permission.RECEIVE")

serial, port = sys.argv[1], int(sys.argv[2])
adb = lambda *a: subprocess.run([ADB, "-s", serial, *a], capture_output=True, text=True, encoding="utf-8").stdout
adb("shell", "pm", "clear", PACKAGE)
since = adb("shell", "date '+%m-%d %H:%M:%S.000'").strip()
adb("shell", "monkey", "-p", PACKAGE, "-c", "android.intent.category.LAUNCHER", "1")
with Agent(serial=serial, port=port) as ui:
    print("START:", ui.cmd("wait START 30000"), ui.cmd("tapText START"))
    print("allow:", ui.cmd("wait Разрешить 15000"), ui.cmd("tapText Разрешить"))
time.sleep(15)
top = [l for l in adb("shell", "dumpsys", "activity", "activities").splitlines() if "topResumedActivity" in l]
print("top:", top[0].split()[2] if top else "?")
counts = collections.Counter()
for line in adb("logcat", "-d", "-T", since).splitlines():
    parts = line.split()
    if len(parts) > 5 and parts[5].rstrip(":") in TAGS:
        counts[parts[5].rstrip(":")] += 1
print("firebase log lines:", dict(sorted(counts.items())) or "none")
perms = [l.strip() for l in adb("shell", "dumpsys", "package", PACKAGE).splitlines()
         if "permission" in l and any(p in l for p in AD_PERMS)]
print("ad/push permissions:", perms or "none")
print("crash buffer:", [l for l in adb("logcat", "-d", "-b", "crash", "-T", since).splitlines() if PACKAGE in l][:3] or "empty")
