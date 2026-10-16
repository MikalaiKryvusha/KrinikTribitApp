"""Cleaner of jadx's Java for Tribit classes moving to native/src (plans/03_epic03_phase2, step 2).

javac cannot see Kotlin's synthetic `foo$default(args…, mask, marker)`, and jadx writes such calls everywhere (2 410 in
Tribit's code, 2026-10-16). Each call becomes `foo(args…)`, with every argument whose bit is set in the mask replaced by
the default value read from the APK's own bytecode (tools/kotlin_defaults.py) - jadx puts a dummy (null, 0, false) there,
and a dummy is not always the default (`launch`: null stands where EmptyCoroutineContext belongs).
A call is left as it is, and listed in the report, when: the mask is not a literal, the owner class is not found, the
overload is ambiguous, or a defaulted argument has no constant default. Nothing is guessed.

Usage:  python -I tools/decompile_clean.py <app.jar> <file.java>… | @list.txt   rewrites the files in place, prints the report
[TESTED: 2026-10-16 · tools/test_decompile_clean.py 10 of 10; on Tribit's 2 006 files: javac errors 4 661 -> 3 136
(plans/03_epic03_phase2_kotlin_defaults.md)]
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kotlin_defaults import defaults_of  # noqa: E402

# the owner as jadx wrote it: a simple name (resolved by the file's imports) or a qualified one (kotlin.text.StringsKt__…)
CALL = re.compile(r"\b((?:[a-z]\w*\.)*[A-Z][\w$]*)\.(\w+)\$default\(")
IMPORT = re.compile(r"^import ([\w.]+);$", re.M)
PACKAGE = re.compile(r"^package ([\w.]+);$", re.M)
_cache = {}


def split_args(text, start):
    """Arguments of the call whose '(' is at text[start]; returns (args, index after ')'). Strings, chars, nesting aware."""
    args, depth, cur, i, quote = [], 0, [], start + 1, None
    while i < len(text):
        c = text[i]
        if quote:
            cur.append(c)
            if c == "\\":
                cur.append(text[i + 1])
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            cur.append(c)
        elif c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            if depth == 0:
                args.append("".join(cur).strip())
                return [a for a in args if a != ""] if args != [""] else [], i + 1
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    raise ValueError("unbalanced call")


def _owner(simple, text):
    """Fully qualified owner of a simple class name in this file: an import, or the file's own package."""
    for imp in IMPORT.findall(text):
        if imp.rsplit(".", 1)[-1] == simple:
            return imp
    pkg = PACKAGE.search(text)
    return f"{pkg.group(1)}.{simple}" if pkg else None


def _fits(arg, ptype):
    """Does a call-site argument fit a parameter type? Only casts and literals are evidence; anything else is neutral."""
    cast = re.match(r"\(\s*([\w.$\[\]]+)\s*\)", arg)
    if cast:
        return cast.group(1).rsplit(".", 1)[-1] == ptype.rsplit(".", 1)[-1]
    if re.fullmatch(r"-?\d+L", arg):
        return ptype == "long"
    if re.fullmatch(r'"(?:[^"\\]|\\.)*"', arg):
        return ptype in ("java.lang.String", "java.lang.CharSequence", "java.lang.Object")
    if re.fullmatch(r"'(?:[^'\\]|\\.+)'", arg):
        return ptype == "char"
    arr = re.match(r"new ([\w.$]+)\[\]", arg)
    if arr:
        return ptype.rstrip("[]").rsplit(".", 1)[-1] == arr.group(1).rsplit(".", 1)[-1] and ptype.endswith("[]")
    return True


def _substitutions(entries, mask):
    """What a mask does with these defaults: {argument index: expression}, or None when a default is not a constant."""
    subs = {}
    for bit, idx, expr in entries:
        if mask & bit:
            if idx is None or expr is None:
                return None
            subs[idx] = expr
    return subs


def clean_text(text, jar, report, where, ctx=None):
    """ctx: the whole file - its imports name the owners of calls nested inside arguments."""
    ctx = ctx or text
    out, pos = [], 0
    for m in CALL.finditer(text):
        if m.start() < pos:
            continue   # nested inside a call already rewritten
        simple, name = m.group(1), m.group(2)
        try:
            args, end = split_args(text, m.end() - 1)
        except ValueError:
            continue
        mask = args[-2] if len(args) >= 2 else ""
        if not re.fullmatch(r"\d+", mask):
            report.append(f"{where}: {simple}.{name}$default - mask is not a literal: {mask!r}")
            continue
        owner = simple if "." in simple else _owner(simple, ctx)
        if owner not in _cache:
            _cache[owner] = defaults_of(jar, owner) if owner else {}
        table = _cache[owner]
        overloads = [(k[1], e) for k, e in table.items() if len(k) == 2 and k[0] == name and len(k[1]) == len(args)]
        overloads = [(p, e) for p, e in overloads if all(_fits(a, t) for a, t in zip(args, p))]
        if not overloads:
            report.append(f"{where}: {simple}.{name}$default - no matching overload in {owner}")
            continue
        # Several overloads may still fit (replace(String,char,char) / replace(String,String,String)); if the mask means
        # the same substitutions in all of them, the choice does not matter - javac resolves foo(...) by the real types.
        subs = [_substitutions(e, int(mask)) for _, e in overloads]
        if any(s is None for s in subs):
            report.append(f"{where}: {simple}.{name}$default - a defaulted argument has no constant default")
            continue
        if any(s != subs[0] for s in subs):
            report.append(f"{where}: {simple}.{name}$default - {len(overloads)} overloads with different defaults in {owner}")
            continue
        real = args[:-2]
        for idx, expr in subs[0].items():
            real[idx] = expr
        # recurse into the arguments: nested $default calls inside them get cleaned as well
        real = [clean_text(a, jar, report, where, ctx) for a in real]
        statics = {table.get((name, p, "static")) for p, _ in overloads}
        if statics == {False}:   # a member function: the $default's first argument is the instance
            call = f"{real[0]}.{name}({', '.join(real[1:])})"
        elif statics == {True}:
            call = f"{simple}.{name}({', '.join(real)})"
        else:
            report.append(f"{where}: {simple}.{name}$default - static and member overloads mixed in {owner}")
            continue
        out.append(text[pos:m.start()])
        out.append(call)
        pos = end
    out.append(text[pos:])
    return "".join(out)


if __name__ == "__main__":
    jar, files = sys.argv[1], []
    for a in sys.argv[2:]:   # @list.txt - one path per line (thousands of files do not fit a Windows command line)
        files += pathlib.Path(a[1:]).read_text(encoding="utf-8").split() if a.startswith("@") else [a]
    report, changed = [], 0
    for f in files:
        p = pathlib.Path(f)
        t = p.read_text(encoding="utf-8")
        t2 = clean_text(t, jar, report, p.name)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")
            changed += 1
    for line in report:
        print("left:", line)
    print(f"ok  {changed} file(s) cleaned, {len(report)} call(s) left as they are")
