"""One step of a manual walk on the Titan through the UI agent: optional action, then a WebP screenshot and labels.

Usage (PowerShell, platform-tools first in PATH, PYTHONUTF8=1):
    python testcases/snap.py <out-dir> <name> [<agent command> ...]      e.g.  ... 03_device "tapText StormBox" "wait EQ 15000"
Prints the foreground activity and the on-screen labels; the screenshot lands in <out-dir>/<name>.webp.
[NOT-TESTED]
"""
import subprocess
import sys
import time

sys.path.append(r"C:\Android\private\ui-agent")
from ui import Agent  # noqa: E402

SERIAL = "192.168.1.3:5555"
out, name, actions = sys.argv[1], sys.argv[2], sys.argv[3:]
with Agent(serial=SERIAL) as ui:
    for a in actions:
        if a.startswith("sleep "):
            time.sleep(float(a.split()[1]))
        else:
            print(a, "->", ui.cmd(a))
    time.sleep(1)
    top = [l for l in subprocess.run(["adb", "-s", SERIAL, "shell", "dumpsys", "activity", "activities"], capture_output=True,
                                      text=True, encoding="utf-8").stdout.splitlines() if "topResumedActivity" in l]
    print("top:", top[0].split()[2] if top else "?")
    print("labels:", " | ".join(l for l in ui.labels() if not l.startswith(("Уведомление", "Модуль", "Ночной", "Wi-Fi", "MTS", "Заряд"))))
png = f"{out}/{name}.png"
with open(png, "wb") as f:
    subprocess.run(["adb", "-s", SERIAL, "exec-out", "screencap", "-p"], stdout=f, check=True)
subprocess.run(["magick", png, "-resize", "500x", "-quality", "80", f"{out}/{name}.webp"], check=True)
subprocess.run(["cmd", "/c", "del", png.replace("/", "\\")], check=False)
