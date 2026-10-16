"""Default values of Kotlin functions, read from the bytecode of the APK itself (plans/03_epic03_phase2, step 1).

A Kotlin function with default parameters compiles to `foo` plus a synthetic static `foo$default(args…, int mask, Object)`
whose body fills every defaulted argument before calling `foo`. The shape is fixed:
    iload <mask> · iconst_<bit>|bipush|sipush|ldc <bit> · iand · ifeq <L> · <ONE instruction pushing a constant> · <x>store <slot>
This module runs `javap -c` on one class of the app's jar and turns each such block into (bit, argument index, Java
expression). A default that is not one constant instruction (a call, a field of an argument) is reported as None - the
cleaner never guesses it.

Usage (library): defaults_of(jar, "kotlin.text.StringsKt__StringsJVMKt") -> {("replace", (param types…)): [(bit, idx, expr|None)…]}
and the key ("replace", (param types…), "static") -> True when the target foo(...) is static (a top-level or extension
function), False when it is a member - then the $default's first argument is the instance: obj.foo(...).
CLI:  python -I tools/kotlin_defaults.py <jar> <class>      prints the table
[TESTED: 2026-10-16 · asLiveData EmptyCoroutineContext + 5000L, launch EmptyCoroutineContext + CoroutineStart.DEFAULT,
split false + 0 - equal to javap -c and kotlinlang.org; lastIndexOf startIndex -> None (not a constant)]
"""
import re
import subprocess
import sys

JAVAP = r"C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot\bin\javap.exe"
HEADER = re.compile(r"^\s*(?:public |private |protected )?static [\w.$<>\[\], ]*?\b(\w+)\$default\(([^)]*)\);$")
INSTR = re.compile(r"^\s*\d+: (\w+)\s*(.*)$")
WIDE = {"long", "double"}


def _slots(params):
    """Argument index of every local slot of a static method with these parameter types."""
    slot_to_arg, slot = {}, 0
    for i, p in enumerate(params):
        slot_to_arg[slot] = i
        slot += 2 if p in WIDE else 1
    return slot_to_arg


def _int_operand(op, arg):
    if op.startswith("iconst_"):
        return -1 if op.endswith("m1") else int(op[-1])
    if op in ("bipush", "sipush"):
        return int(arg)
    if op == "ldc" and re.fullmatch(r"#\d+\s+// int (-?\d+)", arg.strip()):
        return int(arg.split("int")[1])
    return None


def _constant(op, arg, ptype):
    """Java source text of the constant one instruction pushes, typed by the parameter it fills; None if not a constant."""
    comment = arg.split("//", 1)[1].strip() if "//" in arg else ""
    if op == "getstatic" and comment.startswith("Field "):
        owner, field = comment[6:].split(":")[0].rsplit(".", 1)
        return f"{owner.replace('/', '.').replace('$', '.')}.{field}"
    if op == "aconst_null":
        return "null"
    n = _int_operand(op, arg)
    if n is not None:
        return ("true" if n else "false") if ptype == "boolean" else (f"(char) {n}" if ptype == "char" else str(n))
    if op in ("lconst_0", "lconst_1"):
        return f"{op[-1]}L"
    if op in ("fconst_0", "fconst_1", "fconst_2"):
        return f"{op[-1]}.0f"
    if op in ("dconst_0", "dconst_1"):
        return f"{op[-1]}.0"
    m = re.fullmatch(r"(long|float|double|int) (.+)", comment)
    if op in ("ldc", "ldc_w", "ldc2_w") and m:
        kind, val = m.groups()
        suffix = {"long": "L", "float": "f", "double": ""}.get(kind, "")
        return val.rstrip("lLfFdD") + suffix
    # String constants are NOT read: javap drops trailing whitespace in its comment and escapes on its own (the judge
    # pass 2026-10-16 caught joinToString's ", " read as ","). A String default stays None - the call is reported, never
    # guessed. Reading the class file's constant pool would close this; not needed while the cleaner only serves reading.
    return None


def defaults_of(jar, cls):
    out = subprocess.run([JAVAP, "-c", "-p", "-cp", jar, cls], capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout.splitlines()
    table, i = {}, 0
    while i < len(out):
        h = HEADER.match(out[i])
        if not h:
            i += 1
            continue
        name, params = h.group(1), [p.strip() for p in h.group(2).split(",") if p.strip()]
        slot_to_arg, mask_slot = _slots(params), None
        body = []
        i += 1
        while i < len(out) and not HEADER.match(out[i]) and not out[i].strip().startswith(("public ", "private ", "protected ", "static ")):
            m = INSTR.match(out[i])
            if m:
                body.append(m.groups())
            i += 1
        mask_slot = sum(2 if p in WIDE else 1 for p in params[:-2])   # the int mask follows the real arguments
        entries, k = [], 0
        while k + 5 < len(body):
            (o0, a0), (o1, a1), (o2, _), (o3, _) = body[k:k + 4]
            if o0.startswith("iload") and (int(o0.split("_")[1]) if "_" in o0 else int(a0)) == mask_slot \
                    and _int_operand(o1, a1) is not None and o2 == "iand" and o3 == "ifeq":
                bit = _int_operand(o1, a1)
                (ov, av), (os_, as_) = body[k + 4], body[k + 5]
                store = re.fullmatch(r"[ailfd]store(?:_(\d))?", os_)
                if store:
                    slot = int(store.group(1)) if store.group(1) else int(as_.split()[0])
                    idx = slot_to_arg.get(slot)
                    expr = _constant(ov, av, params[idx]) if idx is not None else None
                    entries.append((bit, idx, expr))
                    k += 6
                    continue
                entries.append((bit, None, None))   # more than one instruction: not a constant - never guessed
            k += 1
        table[(name, tuple(params))] = entries
        # Static or member target: the instruction that calls `name` at the end of the $default body says it -
        # invokestatic for a top-level/extension function, invokevirtual/invokeinterface for a member. Unknown -> None.
        calls = [op for op, arg in body if op.startswith("invoke") and re.search(rf"[ ./]{re.escape(name)}:", arg)]
        table[(name, tuple(params), "static")] = (calls[-1] == "invokestatic") if calls else None
    return table


if __name__ == "__main__":
    for key, entries in sorted((k, v) for k, v in defaults_of(sys.argv[1], sys.argv[2]).items() if len(k) == 2):
        name, params = key
        print(f"{name}$default({', '.join(params)}): " + "; ".join(f"bit {b} -> arg {i} = {e}" for b, i, e in entries))
