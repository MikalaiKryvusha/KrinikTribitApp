"""Crash-class scan over Tribit's own code (jadx). Usage: python -I s5_defects.py <jadx sources dir> [show]"""
import pathlib, re, sys, collections
S = pathlib.Path(sys.argv[1]) / "com/thousandshores"
show = len(sys.argv) > 2
pats = {
    # split(...) then get(k>=1) / [k>=1] on the same line, no size() on that line
    "split_index": re.compile(r"split(?:\$default)?\([^;]*\)\s*(?:\.get\(([1-9])\)|\[([1-9])\])"),
    "parse_num": re.compile(r"\b(?:Integer\.parseInt|Long\.parseLong|Float\.parseFloat|Double\.parseDouble)\("),
    "checkNotNull_bang": re.compile(r"Intrinsics\.checkNotNull\(\w+\);"),
    "thread_sleep": re.compile(r"\b(?:Thread\.sleep|SystemClock\.sleep)\("),
    "run_blocking": re.compile(r"\brunBlocking\b"),
    "main_queries": re.compile(r"allowMainThreadQueries\(\)"),
    "static_dialog_field": re.compile(r"public static \w*(?:Dialog|PopupView)\w* \w+;"),
    "dismissAllDialog": re.compile(r"DialogManager\.dismissAllDialog\(\)"),
}
cnt = collections.Counter(); files = collections.defaultdict(set); hits = collections.defaultdict(list)
for f in S.rglob("*.java"):
    rel = f.relative_to(S).as_posix()
    if rel.startswith(("tribit/databinding/",)) or "/R$" in rel or rel.endswith("/R.java"):
        continue
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, l in enumerate(lines, 1):
        if l.lstrip().startswith("@Metadata"): continue
        for k, p in pats.items():
            if p.search(l):
                if k == "split_index" and "size()" in l: continue
                if k == "parse_num":
                    # inside a try? look back 15 lines for 'try {'
                    if any("try {" in x for x in lines[max(0, i - 15):i]): k = "parse_num_in_try"
                cnt[k] += 1; files[k].add(rel); hits[k].append(f"{rel}:{i}")
for k in sorted(cnt):
    print(f"{k}: {cnt[k]} hits in {len(files[k])} files")
if show:
    for k in ("split_index", "thread_sleep", "run_blocking", "static_dialog_field", "main_queries"):
        print(f"--- {k}"); [print("  ", h) for h in hits[k][:40]]
