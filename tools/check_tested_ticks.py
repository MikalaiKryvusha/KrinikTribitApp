"""Guard: a «tested» tick in plans/02 names the run report that observed it, and that report exists.

    python tools/check_tested_ticks.py [plans/02_play_complaints_checklist.md]

Every table row whose LAST cell (the «Проверено» column) starts with ☑ must carry a backticked report name
`YYYY-MM-DD_<name>.md` that exists in testcases/reports/. Exit 1 with the row otherwise.
The class it guards: claim-before-evidence (EXPERIENCE.md EXP-0003, EXP-0008) - a tick wider than its observation.
[TESTED: 2026-10-16 · red on a ☑ row without a report and on a row naming a missing report, green on plans/02]
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # the Windows console is cp1251 and cannot print ☑
REPORT = re.compile(r"`(\d{4}-\d{2}-\d{2}_[\w.-]+\.md)`")
path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "plans/02_play_complaints_checklist.md")
reports = pathlib.Path("testcases/reports")
bad = 0
for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells or not cells[-1].startswith("☑"):
        continue
    names = REPORT.findall(cells[-1])
    missing = [x for x in names if not (reports / x).is_file()]
    if not names or missing:
        bad += 1
        why = "no report named" if not names else f"report not found: {missing}"
        print(f"{path}:{n}: ☑ tested without evidence - {why}: {cells[0]} {cells[1][:50]}")
print("tested-ticks:", "FAIL" if bad else "OK", f"({bad} rows)")
sys.exit(1 if bad else 0)
