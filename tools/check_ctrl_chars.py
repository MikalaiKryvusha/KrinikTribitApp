"""Guard: no stray control characters (BEL, form feed, backspace...) in the text files about to be committed.

A lost escaping level turns `\\a`, `\\f`, `\\b` of a Windows path into a control byte with a green exit code
(EXPERIENCE.md EXP-0007). Run before a commit:
    python tools/check_ctrl_chars.py            # staged + modified tracked text files
    python tools/check_ctrl_chars.py <files...>
Exit 1 and the file:line of every hit; tab, CR and LF are allowed.
[TESTED: 2026-10-16 · red on a file with a form feed written on purpose, green after the fix; see EXP-0007]
"""
import pathlib
import subprocess
import sys

TEXT = {".md", ".py", ".mjs", ".js", ".json", ".sh", ".xml", ".smali", ".java", ".kts", ".txt", ".svg", ".yml"}
ALLOWED = {9, 10, 13}

files = sys.argv[1:] or sorted(set(subprocess.run(
    ["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split()))
bad = 0
for name in files:
    p = pathlib.Path(name)
    if p.suffix not in TEXT or not p.is_file():
        continue
    # split on "\n" only: str.splitlines() treats form feed and other controls as line breaks and hides them
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
        hits = sorted({ord(c) for c in line if ord(c) < 32 and ord(c) not in ALLOWED})
        if hits:
            bad += 1
            print(f"{name}:{n}: control chars {hits}: {line[:80]!r}")
print("ctrl-chars:", "FAIL" if bad else "OK", f"({bad} lines)")
sys.exit(1 if bad else 0)
