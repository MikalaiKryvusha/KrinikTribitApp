# Research 10 — Tribit's own code as Java/Kotlin source that builds with Gradle

> **Created:** 2026-10-16 (the owner, chat 14:25–14:36 +03:00: «отныне работаем не патчами, а пишем чистый, красивый,
> эффективный нативный код с комментариями, как велит КАИФ, и тестируем» · «Можно в нативный код переграть? есть такие
> инструменты?» · «чтобы ты блять на Джава писал и на котлине») · **Parent:** `HOUSE_RULES.md` R9 (`native/`),
> `MASTER_PLAN.md` journal 14:25–14:38 · **Status:** rung 1 of `/plan-epic`; local recon and the compile spike done
> 2026-10-16 14:46 +03:00, industry sweep 14:52 +03:00 · **Outbound:** the meta-plan `plans/03_EPIC_java_source.md` (next);
> forks for the owner → `interviews/`

## 1. The ask and its fit

- **Owner's words** (above): fixes are written as clean native code with comments and tested; in Java and Kotlin, not in smali.
- **Fit:** `GOAL.md` «правильное, работающее, качественное, удобное»; `MASTER_PLAN.md` phase 4 «кривой код»; R9 (`native/` is the
  private working tree, the public repo stays a storefront).
- **Constraint (owner, 14:38):** new Tribit versions are not merged — read them and re-implement what has value. So a one-way
  conversion is acceptable: the source does not have to stay re-derivable from future APKs.

## 2. Local recon — what the APK holds (measured, not recalled)

Commands (all outputs outside git, `work/`):
`tools/jadx/bin/jadx.bat --export-gradle -d work/jadx-gradle work/merged.apk` ·
`tools/dex2jar/dex-tools-2.4.38/d2j-dex2jar.bat -o work/spike/tribit-all.jar work/merged.apk` (release 2.4.38 of
github.com/ThexXTURBOXx/dex2jar, sha256 `5d88e269…54e5c` equal to GitHub's digest) ·
`python -I work/spike/gen_r.py native/res/values/public.xml work/spike/gen <5 packages>` ·
`python -I work/spike/compile_spike.py`.

1. **Size by owner of the code** (jadx export, 32 334 Java files in all): Compose 14 409 · `com/google` 4 788 ·
   **`com/thousandshores` 2 006 (Tribit's own)** · media3 1 163 · kotlin/reflect 958 · RxJava 769 · AndroidX core 557 ·
   speaker-chip SDKs `com/qualcomm` 325, `com/jieli` 178, `com/bluetrum` 160, BLE `com/bhm` 84 · EasyHttp `com/hjq` 260.
2. **Libraries carry their Maven coordinates:** 108 `META-INF/*.version` files (e.g. `androidx.core:core:1.13.1`,
   `androidx.activity:activity:1.8.0`). The chip SDKs have none.
3. **jadx markers:** 1 396 files «Code decompiled incorrectly», 532 «Method dump skipped» across the APK; in
   `com/thousandshores` 281 of 2 006 files carry one of the two.
4. **R is not in the APK.** R8 inlined the resource ids and dropped the R classes; jadx rebuilds `R.java` from
   `resources.arsc`, and its `R.java` of `com.thousandshores.tribit` does not parse (jadx printed its own stack trace in place
   of the empty constructors, line 115). apktool's `res/values/public.xml` holds the same ids: 11 423 ids in 19 types.

## 3. The compile spike — Tribit's code against the app's own classes

Setup: sources = jadx's `com/thousandshores` without its R files, plus R generated from `public.xml` for the five Tribit
packages; classpath = `android.jar` (API 36) + `tribit-all.jar` (every class of the APK, dex2jar); `javac` 21,
`-source 17 -target 17`. The libraries are not compiled at all — they stay the APK's own bytecode.

| Pass | Files | Errors | Files with errors |
|---|---|---|---|
| parse | 1 950 | 29 | 10 |
| type check (the rest) | 1 940 | 4 661 | 959 |

Earlier passes, kept for the trail: without any R — 23 743 errors in 1 232 files (16 113 «package R does not exist»);
with jadx's R files — 17 458 (its `R.java` fails to parse).

Errors by kind (type-check pass, top): 2 131 «cannot find symbol» · 733 «method does not override or implement a method
from a supertype» · 196 «Object cannot be converted to EqualizerBean…» · 182 «TtmlNode is not public» · 51 «not an
enclosing class: MutableLiveData» · 44 «anonymous Runnable cannot be converted».

The missing symbols (top): `launch$default` 503 · `replace$default` 423 · `split$default` 294 · `contains$default` 195 ·
`…constructor-impl` mangled names (`m6833constructorimpl` 98, `m6823…` 32, `m4943…` 22) · `asLiveData$default` 73. These
are Kotlin's synthetic and name-mangled members: they exist in the bytecode, `javac` does not see synthetic members from
source. **A mechanical rewrite closes this family:** `StringsKt.replace$default(s, a, b, false, 4, null)` →
`StringsKt.replace(s, a, b, false)` (the mask argument says which defaults were used).

After the phase-2 cleaner (`tools/decompile_clean.py`, defaults read from the APK's bytecode by
`tools/kotlin_defaults.py`), 2026-10-16 15:21: **3 136 errors in 923 files** (−1 525); of the four top functions' 1 995
`$default` calls 19 remain, all with a non-literal mask in code jadx failed to decompile.

## 4. Industry sweep

Collected by a delegated web recon 2026-10-16; the three maintainer quotes were re-read by `gh issue view` (marked ✔).

1. **Recompiling a decompiled app is a small-app practice.** jadx maintainers: «Decompiling an apk with Jadx and then
   recompiling it with Android Studio only works for small and simple apps» ✔ (https://github.com/skylot/jadx/issues/947) ·
   «Edit java code is pointless because in most case it is not possible to recompile app» ✔
   (https://github.com/skylot/jadx/issues/1959) · a recompile feature closed as not planned ✔
   (https://github.com/skylot/jadx/issues/2215). The `--export-gradle` template leaves `dependencies {}` empty
   (https://raw.githubusercontent.com/skylot/jadx/master/jadx-core/src/main/resources/export/android/app.build.gradle.tmpl).
   No public success story for an app of this size was found.
2. **Decompilers are lossy by measurement:** the best of 8 Java decompilers gave syntactically correct output for 84 % of
   classes and semantically equivalent output for 78 % (https://arxiv.org/abs/1908.06895) — on javac-built Java, not Kotlin.
3. **Kotlin blockers:** coroutine state machines are not valid source and must be rewritten as `suspend` code
   (https://kotlinlang.org/spec/asynchronous-programming-with-coroutines.html); inline functions arrive expanded at every
   call site (https://jdriven.com/blog/2023/09/Kotlin-Discovered-Inline-Functions/); data binding classes are generated
   from `<layout>` XML that the shipped APK no longer has (https://juejin.cn/post/6844904146059935757).
4. **The proven hybrid is DexPatcher's model:** classes written in Java against the original APK's symbols, built into the
   APK (https://www.xda-developers.com/dexpatcher-patch-android-apks-using-java/); its Gradle plugin stopped at AGP 4.0
   (https://github.com/DexPatcher/dexpatcher-gradle/releases), so the tooling is ours to build.
5. **Pitfalls named by the sources:** a duplicate class is resolved to the FIRST copy, so the original smali must be deleted
   (https://android.googlesource.com/platform/art/+/de7b436); d8 needs the whole app on `--classpath` and keeps the 64K
   reference limit per dex (https://developer.android.com/tools/d8); Kotlin `-api-version` is pinned to the bundled stdlib
   (https://kotlinlang.org/docs/compiler-reference.html); apktool keeps resource ids equal to the original APK
   (https://apktool.org/blog/apktool-1.0.0).
6. **Security:** jadx before 1.5.6 lets a crafted `versionName` inject Groovy into the exported `build.gradle`
   (CVE-2026-42049, https://app.opencve.io/cve/CVE-2026-42049). Ours is 1.5.1 (`tools/jadx/lib/jadx-1.5.1-all.jar`); the
   exported file carries `versionName "5.0.0"`, and Gradle was never run on it — update jadx before any Gradle run.

## 5. Findings → implications

0. **Our spike agrees with the industry:** a one-shot «whole app compiles» is the path the jadx maintainers call
   small-app-only, and our count (4 661 type errors after R, plus Kotlin coroutines and data binding) says the same. The
   class-by-class hybrid (§4 item 4) is the proven path; the whole-code conversion becomes its END STATE, reached class by
   class.

1. **Only Tribit's own code needs to become source.** The libraries stay the APK's bytecode (classpath jar for `javac`,
   their dex inside the APK); 108 of them could later become Maven dependencies by their `.version` files.
2. **R is generated, never decompiled:** from apktool's `public.xml` (ids equal to the APK's), later by aapt2 in Gradle.
3. **A large part of the errors is mechanical:** the Kotlin `$default` / mangled-name family is ≈ 1 650 of 4 661 by the
   counts above and goes by a script; what remains (≈ 3 000) is per-file work — decompiler damage in lambdas, generics and
   inner classes. How many files it touches after the script is the next measurement.
4. **The hybrid path looks open from day one:** 981 of 1 940 type-checked files have no error of their own, so a class
   we fix can compile against `tribit-all.jar` (`javac` wrote no classes in this spike — it stops at errors; compiling one
   such class alone and running it on the A51 is the proof still owed); its smali leaves `native/`, its class goes into
   our dex.

## 6. Open forks for the owner

- Whole-code conversion first (every one of 1 950 files compiles before any new fix) or class by class (a class becomes
  source when a fix touches it) — to be asked in `interviews/` with the numbers above.
