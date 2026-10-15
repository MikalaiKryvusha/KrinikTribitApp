"""Functional run of the patched Tribit app (debug variant) on the Titan through the UI agent.

Usage (PowerShell, from the repo root; platform-tools first in PATH so ui.py's bare `adb` is the SDK one):
    $env:PATH="C:\\Android\\Sdk\\platform-tools;$env:PATH"; $env:PYTHONUTF8="1"
    python testcases/run_fork_titan.py <out-dir> [package]   # default com.kriniks.tribit.debug; com.thousandshores.tribit = the original
Walks: splash (T16) -> login (T17) -> registration (T8) -> landscape on login (T10), a screenshot and the on-screen
labels at every step, the crash buffer at the end. Rotation settings are restored to what they were.
[NOT-TESTED]
"""
import json
import subprocess
import sys
import time

sys.path.append(r"C:\Android\private\ui-agent")
from ui import Agent  # noqa: E402

SERIAL = "192.168.1.3:5555"
OUT = sys.argv[1]
PKG = sys.argv[2] if len(sys.argv) > 2 else "com.kriniks.tribit.debug"


def adb(*args):
    return subprocess.run(["adb", "-s", SERIAL, *args], capture_output=True, text=True, encoding="utf-8").stdout.strip()


def top():
    line = [l for l in adb("shell", "dumpsys", "activity", "activities").splitlines() if "topResumedActivity" in l]
    return line[0].split()[2] if line else "?"


def shot(name):
    png = f"{OUT}/{name}.png"
    with open(png, "wb") as f:
        subprocess.run(["adb", "-s", SERIAL, "exec-out", "screencap", "-p"], stdout=f, check=True)
    subprocess.run(["magick", png, "-resize", "500x", "-quality", "80", f"{OUT}/{name}.webp"], check=True)
    subprocess.run(["cmd", "/c", "del", png.replace("/", "\\")], check=False)


log = {}
rotation = {k: adb("shell", "settings", "get", "system", k) for k in ("accelerometer_rotation", "user_rotation")}
with Agent(serial=SERIAL) as ui:
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    log["01_splash.wait"] = ui.cmd("wait START 15000")
    time.sleep(1)
    log["01_splash.top"] = top()
    log["01_splash.labels"] = ui.labels()
    shot("01_splash")

    if PKG in top():
        log["02_login.tap"] = ui.cmd("tapText START")
    log["02_login.wait"] = ui.cmd("wait Войти 20000")
    time.sleep(1)
    log["02_login.top"] = top()
    log["02_login.labels"] = ui.labels()
    log["02_login.tree"] = ui.ok("tree")
    shot("02_login")

    if PKG in top():
        log["03_register.tap"] = ui.cmd("tapText Зарегистрировать")
    time.sleep(3)
    log["03_register.top"] = top()
    log["03_register.labels"] = ui.labels()
    log["03_register.tree"] = ui.ok("tree")
    shot("03_register")
    log["03_back"] = ui.cmd("back")
    time.sleep(2)

    adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
    adb("shell", "settings", "put", "system", "user_rotation", "1")
    time.sleep(3)
    log["04_land.top"] = top()
    log["04_land.labels"] = ui.labels()
    shot("04_login_landscape")
    for k, v in rotation.items():
        adb("shell", "settings", "put", "system", k, v if v not in ("", "null") else "0")
    time.sleep(2)

log["crash"] = adb("logcat", "-d", "-b", "crash")
log["pid"] = adb("shell", "pidof", PKG)
with open(f"{OUT}/run.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k.endswith(("top", "wait", "tap", "pid")) else (v[:300] if isinstance(v, str) else v[:25]))
                  for k, v in log.items() if not k.endswith("tree")}, ensure_ascii=False, indent=1))
