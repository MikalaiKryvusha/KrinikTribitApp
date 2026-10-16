"""Patch 8a check: does a cold start with clean data ask their server for the language dictionary?

Usage (PowerShell, PYTHONUTF8=1, the UI agent started on the device):
    python testcases/splash_request_check.py <serial> <agent port>
Clears the data of com.kriniks.tribit.debug (our package only), clears nothing else, starts the app, waits for START,
then counts in the logcat since the start the EasyHttp lines of the dictionary request
`api-app/api/lang/getLangInfoBySchemaOrLangKey` (ProductString.smali:92). Old build: > 0. Patch 8a: 0.
The app talks to its own server by itself (HOUSE_RULES R2: not a request of the agent).
[NOT-TESTED]
"""
import subprocess
import sys
import time

sys.path.append(r"C:\Android\private\ui-agent")
from ui import Agent  # noqa: E402

ADB = r"C:\Android\Sdk\platform-tools\adb.exe"
PACKAGE = "com.kriniks.tribit.debug"
MARK = "getLangInfoBySchemaOrLangKey"

serial, port = sys.argv[1], int(sys.argv[2])
adb = lambda *a: subprocess.run([ADB, "-s", serial, *a], capture_output=True, text=True, encoding="utf-8").stdout
adb("shell", "pm", "clear", PACKAGE)
since = adb("shell", "date '+%m-%d %H:%M:%S.000'").strip()  # one string: adb shell joins args with spaces
adb("shell", "monkey", "-p", PACKAGE, "-c", "android.intent.category.LAUNCHER", "1")
with Agent(serial=serial, port=port) as ui:
    print("START:", ui.cmd("wait START 30000"))
time.sleep(5)  # let the request (if any) go out and log
log = adb("logcat", "-d", "-T", since)
hits = [line for line in log.splitlines() if MARK in line]
print(f"dictionary request lines since {since}: {len(hits)}")
for line in hits[:3]:
    print("  ", line[:160])
