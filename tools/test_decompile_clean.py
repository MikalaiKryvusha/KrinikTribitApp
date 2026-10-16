"""Tests of tools/decompile_clean.py on calls copied from jadx's Java of Tribit (plans/03_epic03_phase2, step 3).
Needs the app's jar (dex2jar of the APK): python -I tools/test_decompile_clean.py [work/spike/tribit-all.jar]

@guard kotlin-default-substitution
THREAT:         a `foo$default` call rewritten by cutting the mask off - jadx's dummy (null) goes where the default belongs
PROVED-AGAINST: the cleaner with the substitution disabled (dummies kept, mask cut off): both launch cases and asLiveData
                go red (2026-10-16); replace/split/contains stay green there - their dummies equal the defaults
GAP:            Tribit's own `$default` functions are covered only through the same bytecode reader, no case of their own
ON-REAL-PATH:   NOT YET - no cleaned class is in an APK yet; the first migrated class that went through the cleaner closes it
[TESTED: 2026-10-16 · 10 of 10 green; red on the broken copy (launch x2, asLiveData)]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from decompile_clean import clean_text  # noqa: E402

JAR = sys.argv[1] if len(sys.argv) > 1 else "work/spike/tribit-all.jar"
HEAD = ("package com.thousandshores.tribit.x;\nimport kotlin.text.StringsKt__StringsJVMKt;\nimport kotlin.text.StringsKt__StringsKt;\n"
        "import kotlinx.coroutines.BuildersKt__Builders_commonKt;\nimport androidx.lifecycle.FlowLiveDataConversions;\n"
        "import com.thousandshores.tribit.moduledevice.viewmodel.ViewModelDeviceBts;\n")
EC, DEF = "kotlin.coroutines.EmptyCoroutineContext.INSTANCE", "kotlinx.coroutines.CoroutineStart.DEFAULT"
CASES = [
    ("replace, mask 4 (ignoreCase)",
     'String s = StringsKt__StringsJVMKt.replace$default(sb2, "ffffff", "", false, 4, (Object) null);',
     'String s = StringsKt__StringsJVMKt.replace(sb2, "ffffff", "", false);', 0),
    ("launch, mask 3: both dummies are null, the defaults are not",
     "BuildersKt__Builders_commonKt.launch$default(CoroutineScopeKt.MainScope(), null, null, new Job1(btClient, null), 3, null);",
     f"BuildersKt__Builders_commonKt.launch(CoroutineScopeKt.MainScope(), {EC}, {DEF}, new Job1(btClient, null));", 0),
    ("launch, mask 2: the context is given, only start is default",
     "BuildersKt__Builders_commonKt.launch$default(scope, Dispatchers.getIO(), null, block, 2, null);",
     f"BuildersKt__Builders_commonKt.launch(scope, Dispatchers.getIO(), {DEF}, block);", 0),
    ("split, mask 6, a comma inside the array literal",
     'List l = StringsKt__StringsKt.split$default((CharSequence) time, new String[]{","}, false, 0, 6, (Object) null);',
     'List l = StringsKt__StringsKt.split((CharSequence) time, new String[]{","}, false, 0);', 0),
    ("contains, mask 2",
     'if (StringsKt__StringsKt.contains$default((CharSequence) name, (CharSequence) "Tribit", false, 2, (Object) null)) {',
     'if (StringsKt__StringsKt.contains((CharSequence) name, (CharSequence) "Tribit", false)) {', 0),
    ("asLiveData: the overload chosen by the cast and the long literal",
     "LiveData d = FlowLiveDataConversions.asLiveData$default(flow, (CoroutineContext) null, 0L, 3, (Object) null);",
     f"LiveData d = FlowLiveDataConversions.asLiveData(flow, {EC}, 5000L);", 0),
    ("nested replace inside replace",
     'String t = StringsKt__StringsJVMKt.replace$default(StringsKt__StringsJVMKt.replace$default(a, "#", "1", false, 4, null), "$", "2", false, 4, null);',
     'String t = StringsKt__StringsJVMKt.replace(StringsKt__StringsJVMKt.replace(a, "#", "1", false), "$", "2", false);', 0),
    ("a fully qualified owner, as jadx writes it when the simple name clashes",
     'String s = kotlin.text.StringsKt__StringsJVMKt.replace$default(a, "-", "", false, 4, (Object) null);',
     'String s = kotlin.text.StringsKt__StringsJVMKt.replace(a, "-", "", false);', 0),
    ("Tribit's own member function: the first argument is the instance",
     "ViewModelDeviceBts.queryFireVersion$default(viewModelDeviceBts4, this, str2, packageName2, this.version, false, 16, null);",
     "viewModelDeviceBts4.queryFireVersion(this, str2, packageName2, this.version, false);", 0),
    ("lastIndexOf, mask 6: startIndex default is lastIndex - not a constant, left as it is",
     'int i = StringsKt__StringsKt.lastIndexOf$default((CharSequence) str, ".", 0, false, 6, (Object) null);',
     'int i = StringsKt__StringsKt.lastIndexOf$default((CharSequence) str, ".", 0, false, 6, (Object) null);', 1),
]

failed = 0
for title, src, want, want_left in CASES:
    report = []
    got = clean_text(HEAD + src, JAR, report, "case")[len(HEAD):]
    ok = got == want and len(report) == want_left
    failed += not ok
    print(("ok  " if ok else "FAIL") + f"  {title}" + ("" if ok else f"\n      got:  {got}\n      want: {want}\n      left: {report}"))
print(f"{len(CASES) - failed} of {len(CASES)} cases pass")
sys.exit(1 if failed else 0)
