"""Patch 8a check: seconds from a cold start with clean app data to the START button on the splash.

Usage (PowerShell, SDK first in PATH for ui.py, PYTHONUTF8=1, the UI agent already started on the device):
    python testcases/splash_timing.py <serial> <agent port> <runs>
Clears the data of com.kriniks.tribit.debug (our package only, HOUSE_RULES R1/R7), starts it, waits for "START"
through the UI agent and prints one line per run plus the median. Run it on the old build (control) and on the new one.
[NOT-TESTED]
"""
import statistics
import subprocess
import sys
import time

sys.path.append(r"C:\Android\private\ui-agent")
from ui import Agent  # noqa: E402

ADB = r"C:\Android\Sdk\platform-tools\adb.exe"
PACKAGE = "com.kriniks.tribit.debug"
WAIT_MS = 90000  # their dictionary wait can reach ~80 s (researches/06 Z1)

serial, port, runs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
times = []
for i in range(runs):
    subprocess.run([ADB, "-s", serial, "shell", "pm", "clear", PACKAGE], capture_output=True, check=True)
    t0 = time.monotonic()
    subprocess.run([ADB, "-s", serial, "shell", "monkey", "-p", PACKAGE, "-c", "android.intent.category.LAUNCHER", "1"],
                   capture_output=True, check=True)
    with Agent(serial=serial, port=port) as ui:
        reply = ui.cmd(f"wait START {WAIT_MS}")
    dt = time.monotonic() - t0
    times.append(dt)
    print(f"run {i + 1}: {reply} after {dt:.1f} s")
print(f"median {statistics.median(times):.1f} s over {runs} runs")
