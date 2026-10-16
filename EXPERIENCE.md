# EXPERIENCE — the agent's accumulated experience

> The agent's growing log of lessons. **Externalized memory of *what works and what doesn't*** — so a
> fresh, context-less session (or an autonomous loop) never repeats a dead end. Consult it BEFORE a task;
> append to it AFTER a meaningful attempt (success **or** failure). Grep, don't scroll.
>
> **Tags live inline on every entry** (not in a central list) — so one grep finds the experiences directly:
> `grep '#loop' EXPERIENCE.md` · `grep -i '#context\|#build' EXPERIENCE.md` · `grep '❌' -A4 EXPERIENCE.md`
> · `grep 'EXP-0007' EXPERIENCE.md`. Reuse an existing tag where one fits (grep to see what's in use).
>
> **Entry format (keep it short and grep-friendly).** Newest on top. Every entry starts with a stable id,
> an ISO date, an outcome marker (`✅` / `❌` / `❌→✅`), and inline `#tags`:
>
> ```
> ### EXP-0001 · 2026-01-01 · ✅ · #tag #area
> class: <slug from the class list below — the UNIT OF RECURRENCE>
> **Context:** one line — what was being done.
> **Tried / did:** the approach, briefly.
> **Result:** ✅/❌ — what happened.
> **Lesson:** the reusable takeaway (the reason this entry exists).   → link: bugs/NN · ideas/NN · plans/NN
> **Repro:** the ready-to-run command/check that verifies or applies the lesson — a weak session
>   executes a pasted command reliably, an essay it won't act on. REQUIRED since 2.1: a lesson
>   with no Repro line is not accepted (field-proven: lessons with a Repro command get executed,
>   essay-lessons get read and ignored). If the lesson genuinely has no command, say what to
>   OBSERVE instead — but say it as an action.
> **Trigger:** for class-level lessons — the decision point that must invoke this lesson, as
>   "writing X → run Y" (the lesson names WHERE it applies, instead of hoping to be remembered).
> **Not for:** the lesson's validity range — where it does NOT apply. A documented lesson is still a
>   hypothesis; applied outside its range it kills good ideas.
> ```
>
> **A lesson that repeats is a lesson that failed as text.** When the same class recurs in NEW code
> after its entry was recorded, the journal has proven insufficient — the lesson MUST become
> executable (a linter rule, a guard, a gate), and the entry gains the line
> `mechanized: <the tool>`. Two strikes → a mechanism, never a third reminder.
>
> **The deadline is RUN, not remembered** (2.7, epic EL; origin issue #69 — a field audit of one
> project's journal: 14 of 15 failure classes recurred AFTER their lesson was written, five lessons
> written 6–17 times in different words, 5.8 % mechanized): `node .kaif/tools/kaif-experience-lint.mjs
> check` reads the `class:` field as the UNIT of recurrence and reddens on the SECOND failure entry of
> one class with no `mechanized:`, naming the class and both entries by id. Two fates clear it, both
> WRITTEN: name the guard in the entry (`mechanized: <the tool>`), or re-check the price once for the
> WHOLE class and declare it — `<!-- class-ok: <slug> — <why it is not cheaply possible> -->` (an empty
> declaration is itself a finding; the declared classes are printed on the summary line and that list
> only shrinks). A third record is never a fate. It also warns when
> `mechanized:` names a command this project does not contain, and when a slug is outside the list
> below; `--shrink EXP-NNNN` collapses a MECHANIZED entry to one line pointing at its guard (shows by
> default, `--yes` writes — the text itself stays in the git history). The command belongs in the
> closing ritual (`/end-chat-soft`).
>
> **The class list of this journal** — a CONTROLLED list, not a closed one: pick a slug from it, and
> when a lesson genuinely brings a new class, add the slug here in the same write (the linter warns
> about an unlisted slug, it never refuses). The starter list below is what a field audit had already
> measured (origin issue #69) — replace and grow it with your project's own classes.
>
> <!-- classes: question-already-answered, guard-not-proven-against-threat, shown-as-link,
>      claim-before-evidence, owner-decision-not-applied, text-in-agents-world,
>      etalon-from-dirty-tree, shell-lied, escaping-layer, twins-missed,
>      field-dropped-in-rebuild, renamed-package-identity, own-work-not-recalled, dex-reference-limit,
>      owner-text-past-portrait, reference-not-inventoried, stand-state-not-read -->
>
> | Class slug | The failure it names |
> |---|---|
> | `question-already-answered` | the owner is asked what his own past word, the goal doc or a run already decided |
> | `guard-not-proven-against-threat` | a guard shipped without being seen red on the threat it claims to stop |
> | `shown-as-link` | showing replaced by a link or a path instead of the thing itself |
> | `claim-before-evidence` | a claim written wider than the observation behind it |
> | `owner-decision-not-applied` | a decision the owner gave is recorded and not carried into the artifact |
> | `text-in-agents-world` | text written for the agent's own world instead of the owner's |
> | `etalon-from-dirty-tree` | a reference/etalon captured from a tree that was not clean |
> | `shell-lied` | the shell or the tool swallowed/rewrote what was passed to it |
> | `escaping-layer` | one escaping level lost between the tool and the file |
> | `twins-missed` | one of two layers/copies moved and the twin stayed behind |
> | `field-dropped-in-rebuild` | a field or section silently lost when an artifact was regenerated |
| `renamed-package-identity` | a renamed application package breaks code that looks things up by the package name |
| `own-work-not-recalled` | a tool or recipe the owner's projects already have was not looked up before the work |
| `dex-reference-limit` | a patch adds method references to a dex that is already at 65 536 and apktool refuses to build |
| `owner-text-past-portrait` | text the owner or the app's user reads was written without the owner's voice portrait loaded |
| `reference-not-inventoried` | screens copied from a reference app without first counting its elements row by row |
| `stand-state-not-read` | the stand's state changed without reading it first, so it cannot be put back |
>
> <!-- class-ok: claim-before-evidence — its machine-checkable part (a ☑ «tested» in plans/02 without a run report) is mechanized by tools/check_tested_ticks.py (EXP-0008); what stays (which observation a sentence in a chat rests on: a probe, a screen, a device log line) lives in replies no tool sees — /fable-judge's claim-wider-than-observation hunt is its check -->
>
> The `#tags` are **trigger-tags**: before a task, grep by the task's tags and QUOTE the relevant
> lessons in your report (id + one line) — or state "no relevant lessons". An unquoted recall is
> unverifiable; `/fable-judge` checks for this line.
>
> Skill: `/experience` (capture a lesson · recall relevant lessons).

## Entries

### EXP-0015 · 2026-10-16 · ❌ · #a51 #stand #rotation
class: stand-state-not-read
none-cheap: `tools/screen_profile.py apply … --land` saves the native rotation before it turns the phone and `reset` restores it; a bare `wm user-rotation lock 1` saves nothing
**Context:** testing the full-screen EQ editor in landscape on the A51.
**Tried / did:** turned the phone with `wm user-rotation lock 1` without reading the mode first; `screen_profile.py reset` had
no saved mode and left it «lock 1». The native mode (auto-rotate on) was found in `testcases/reports/2026-10-16_a51_stand.md`.
**Lesson:** read the stand's state before changing it - or change it only through the tool that saves it.
**Repro:** `adb shell wm user-rotation` before and after.
**Trigger:** any rotation, size or density change on the A51 or the Titan.
**Not for:** the app's own orientation code.

### EXP-0014 · 2026-10-16 · ❌ · #design #reference #inventory #owner
class: reference-not-inventoried
none-cheap: a parity inventory is a document of rows; whether every element of the reference app is in it is the agent's reading of the reference's code and screens - no tool knows the reference
**Context:** the own app's screens for the Blast 2; the owner had asked to follow Tribit's app and KARTUN.
**Tried / did:** phases 1–2 were built from the protocol recon only; the owner 19:05: «простой не интересный, не похож на
оригинальное приложение»; then mock-ups and code A + A - and the owner 19:55: «x-3d где???» · «ты блять изучал оригинальное
приложение Tribit как я тебя просил????????». Tribit names preset 4 «X-3D» and presets 10/11 «XBass Off/XBass (V8.6/V7.4)»
for the Blast 2 (`EqButton56Activity.java:347–375`); our recon table had «X-3D» in a cell and the screens still said «Классика».
**Lesson:** a reference app is read as a countable inventory of ITS screens (element · name as shown · behaviour) BEFORE the
first mock-up; protocol recon is not screen recon. A fact in a recon cell is not applied until a row of the inventory carries it.
**Repro:** `grep -n "X-3D" decompiled/jadx-base/sources/com/thousandshores/tribit/moduledevice/bts56/*.java`
**Trigger:** «ориентируйся на <app>», «как в оригинале», a mock-up of a screen that a reference app already has.
**Not for:** screens the reference app does not have.

### EXP-0013 · 2026-10-16 · ❌→✅ · #claims #judge #android #lifecycle
class: claim-before-evidence
none-cheap: the judge pass is the check - a plan tick or a verdict line names a behaviour no tool can see; the run reports carry «Не проверено» lines, the judge compares them with the verdict
**Context:** phases 1–2 of the own app in one hour; a /fable-judge pass at 17:11 over a4f5ea5..eb69e7d.
**Tried / did:** the judge found: a plan step ticked «one command in flight» while sets went outside the lock; two run
verdicts «pass» wider than their checks; a commit claiming «A2DP up opens the channel by itself» with no run behind it; strings
promising that unproven path. On the device the same hour: Android's system dialogs (save, open, share) stop the activity -
the link closed, a file result arrived to a closed link and a toast said «sent» while nothing was sent.
**Result:** ✅ all fixed or narrowed where they stood (commit 24122f3 lists the corrections).
**Lesson:** a tick is the behaviour seen, not the code written; and any screen that opens a system dialog must survive its own
onStop - a result that arrives while the link is closed waits for the link.
**Repro:** `adb logcat -s KT.Link:D` around a file pick - the TX of the file's EQ comes after `connected`, never before.
**Trigger:** ticking a plan step or writing «pass» → name the run that showed it; adding a system dialog → test the return path.
**Not for:** hygiene results (tests, lint), which are reported as hygiene.

### EXP-0012 · 2026-10-16 · ❌→✅ · #texts #voice #ui #owner
class: owner-text-past-portrait
none-cheap: the machine half runs (`kaif-voice-lint check` on strings.xml, HOUSE_RULES R10); whether a line talks about what is absent is the §7B judgement - the lint was green on «Геолокация не нужна.»
**Context:** the own app's home card strings were written straight into `strings.xml` without loading `AUTHOR_STYLOMETRY.md`.
**Tried / did:** «Геолокация не нужна.» and a card «Без геолокации, без аккаунта, без сервера Tribit…» reached the A51; the owner
16:12: «НАХУЙ ТАКОЕ ПИСАТЬ?» · «ЭТО СКАЗАНО В МОЕМ СТИЛОМЕТРИЧЕСКОМ ЯДРЕ». Rewritten by the portrait (laws З1, З2, З6, ДК4),
lint 0 hits, §7B by a subagent found 5 more (a false «connects by itself», a calque, a claim wider than the code).
**Result:** ✅ strings rewritten; HOUSE_RULES R10 makes app strings owner text.
**Lesson:** UI strings are the owner's text: load the portrait before the first word, say what IS and what to DO; a §7B pass
also checks each string against the code (a hint that promises behaviour the code does not have is a false claim).
**Repro:** `node .kaif/tools/kaif-voice-lint.mjs load` before editing `app/src/main/res/values-ru/strings.xml`, then `check` on it.
**Trigger:** editing `strings.xml` or any text a user of the app reads → load the portrait first.
**Not for:** log tags and code comments.

### EXP-0001 · 2026-01-01 · ✅ · #example #meta
**Context:** first task after KAIF was deployed into this project (example entry — replace with real ones).
**Tried / did:** wrote the first real lesson here in the canonical format.
**Result:** ✅ — the experience log is live and greppable.
**Lesson:** capture lessons at the level of *approach* (what worked / what to avoid), not defect detail
(that lives in `bugs/`); one short entry beats a long story.   → link: (none)

### EXP-0011 · 2026-10-16 · ❌→✅ · #java #decompile #measurement
class: claim-before-evidence
none-cheap: a one-off measurement trap; the spike script (work/spike/compile_spike.py, researches/10 §3) now runs two passes
**Context:** measuring whether jadx's Java of Tribit's code compiles (epic plans/03).
**Tried / did:** the first `javac` run reported 48 errors in 11 files - all parse errors; javac stops before type checking
when any file fails to parse, so the real count was hidden. Excluding the 11 files gave 23 743; generating R from apktool's
public.xml (the APK has no R classes, R8 inlined them) brought it to 4 661 in 959 of 1 940 files.
**Result:** ✅ the number in researches/10 is the type-check count; «48 errors» never reached a document.
**Lesson:** a compiler's error count is a stage count - exclude the files that fail to parse, then count again; and an
R8-built APK has no R classes, generate R from public.xml.
**Repro:** `python -I work/spike/compile_spike.py` (from `work/`) prints «pass 1 … (parse stage)» and «pass 2 …» separately.
**Trigger:** measuring «does it compile» → two passes, parse then types.
**Not for:** single-file compiles, where the first error is the answer.

### EXP-0010 · 2026-10-16 · ❌→✅ · #build #smali #dex
class: dex-reference-limit
mechanized: patches/apply.py make_dex_room (kotlin-reflect moved to smali_classes6; the build fails loudly if the move breaks)
**Context:** patch 8 added four calls (krinik.Anon, krinik.Gate) into classes of smali_classes5.
**Tried / did:** apktool: «Unsigned short value out of range: 65536» while writing a kotlin-reflect method of classes5.
**Result:** ✅ after moving the self-contained kotlin/reflect package into a new smali_classes6 (multidex loads every dex).
**Lesson:** their classes5 sits at the method-reference limit; any new reference there can break the build - room is made
by moving a whole self-contained package to a new smali_classesN, never by trimming their code.
**Repro:** `bash build.sh debug 2>&1 | grep "dex room"` prints «2037 classes of kotlin/reflect moved».
**Trigger:** apktool fails with «out of range: 65536» → check which smali_classesN, move a self-contained package out.
**Not for:** the 64K limit of our own classesN.dex (d8 splits ours by itself).

### EXP-0009 · 2026-10-16 · ❌ · #claims #a51 #speaker
class: claim-before-evidence
none-cheap: which source a state claim rests on (screen vs device log) is judgement; /fable-judge hunts it - like EXP-0003
**Context:** the A51 settings screen showed «Автоматическое выключение» on; I told the owner «автовыключение включено».
**Tried / did:** the app's own log said the speaker answered «自动关机-- false» before and after; the screen showed the
field default (`isShutDown = true`) because the speaker had not answered yet (`bugs/02`).
**Result:** ❌ a false alarm to the owner, corrected in the same reply.
**Lesson:** a switch on their screen is not the speaker's state; the speaker's state is the log line it answers with.
**Repro:** `adb logcat -d --pid <pid> | grep "自动关机--"` - the last line is the speaker's answer.
**Trigger:** writing «the speaker has X on/off» → quote the speaker's log line, or say «the screen shows».
**Not for:** settings the app keeps only on the phone (no speaker answer exists).

### EXP-0008 · 2026-10-16 · ❌ · #claims #a51 #testing
class: claim-before-evidence
mechanized: tools/check_tested_ticks.py (a ☑ tested in plans/02 names an existing run report; proved red on 2 rows)
**Context:** one session on the A51: «patch 8 tested» ticked after seeing the main screen (the speaker page then never
opened); «login does not scroll in landscape» written without a swipe (the line was under the gesture bar, nothing to
scroll); `screen_profile.py` «tested» on the reset while the landscape apply itself no longer rotated the display.
**Tried / did:** each caught by a later run on the real path and corrected where it stood (checklist, reports, marker).
**Result:** ❌ three corrections in one morning.
**Lesson:** tick «tested» only for what the run walked: the user's path to the END of the feature (the speaker page, not
the main screen); an adjective about behaviour («does not scroll») needs the gesture; a tool is tested on its effect
(`mCurrentRotation`), not on the setting it wrote.
**Repro:** `adb shell dumpsys window displays | grep mCurrentRotation` after `screen_profile.py apply … --land` prints ROTATION_90.
**Trigger:** writing ☑ / [TESTED] / «does not X» → name the observation that backs it in the same line.
**Not for:** hygiene results (lint, build), which are reported as hygiene and never ticked as tested.

### EXP-0007 · 2026-10-16 · ❌ · #escaping #python #heredoc
class: escaping-layer
mechanized: tools/check_ctrl_chars.py (proved red on \f and \a, green on all tracked text files)
**Context:** Windows paths written into files through Python strings inside bash heredocs: `C:\adb` → `C:` + BEL,
`testcases\firebase_check.py` → `testcases` + form feed. Exit codes green, the text silently broken; found only by reading back.
**Tried / did:** fixed by a script FILE that writes the lines with explicit `\\`; the first guard missed form feed because
`str.splitlines()` treats it as a line break.
**Result:** ❌ two broken lines in one session (after EXP-0003 named the class) → the guard.
**Lesson:** backslash paths go through the Write/Edit tools, never through a Python string in a heredoc; before a commit run
`python tools/check_ctrl_chars.py`; a scanner splits on `"\n"` only.
**Repro:** `printf 'a\fb\n' > x.md && python tools/check_ctrl_chars.py x.md` exits 1.
**Trigger:** writing a Windows path or any backslash into a file by a script → Write/Edit tool instead; commit → the guard.
**Not for:** binary files (the guard skips them by extension).

### EXP-0006 · 2026-10-16 · ❌ · #adb #powershell #a51 #titan
class: shell-lied
mechanized: tools/screen_profile.py, testcases/snap.py, testcases/run_fork_titan.py (ADB = full SDK path)
**Context:** a PowerShell call ran `adb -s R58N615KXZZ …` and the project scripts without `C:\Android\Sdk\platform-tools`
first in PATH.
**Tried / did:** the bare `adb` resolved to `C:\adb` 1.0.32: «adb server is out of date. killing...»; the SDK server came
back without the A51 until the owner replugged the cable; the run of another session on the Titan lost its link too.
**Result:** ❌ about 10 minutes of the stand lost, the classifier then refused every adb call.
**Lesson:** a known trap of HOUSE_RULES §3 hit a second time — scripts now call adb by the full SDK path; in an ad-hoc
PowerShell line put the SDK first in PATH in the SAME line, or call `C:\Android\Sdk\platform-tools\adb.exe` by path.
**Repro:** `grep -n '"adb"' tools/*.py testcases/*.py` prints nothing.
**Trigger:** writing any adb call → full SDK path, never bare `adb`.
**Not for:** `ui.py` (outside the repo) — it uses PATH; start it only with the SDK first in PATH.

### EXP-0002 · 2026-10-16 · ❌ · #adb #gitbash #titan
class: shell-lied
none-cheap: a per-shell setting; the recipe stands in HOUSE_RULES.md (dossier and the UI-agent row)
**Context:** reading a UI dump on the Titan from Git Bash: `adb shell cat /sdcard/kt.xml`.
**Tried / did:** the command answered «No such file»: Git Bash rewrote `/sdcard/kt.xml` into `C:/Program Files/Git/sdcard/kt.xml`.
**Result:** ❌ one lost step; with `export MSYS_NO_PATHCONV=1` the file was read.
**Lesson:** in Git Bash every device path in an `adb` argument needs `MSYS_NO_PATHCONV=1`; better — drive the Titan with the
UI agent from PowerShell.   → link: `HOUSE_RULES.md` §4

### EXP-0003 · 2026-10-16 · ❌ · #claims #markers #escaping
class: claim-before-evidence
none-cheap: whether a cause was probed before it was named is judgement; /fable-judge hunts it
**Context:** three slips in one session: a chat line «Cyrillic in the heredoc got corrupted» said before any probe (the probe
showed the heredoc intact; the cause was a `\n` escaping slip in my Python); a `[TESTED]` marker written into `add_dex.py`
before the script had ever run; a Windows path `C:\Android\...\ui-agent` inside a Python string literal of a heredoc (`\u`
read as an escape — AGENT_GUIDE "text travels through files", face 3).
**Tried / did:** all caught (a byte probe; a re-read of the file; the interpreter's error) and corrected where they stood.
**Result:** ❌ three corrections; no falsehood left standing.
**Lesson:** the cause is named after the probe, never before it; a fresh file is born `[NOT-TESTED]` and flips only with the run
named; text with backslashes goes into a file written by the Write tool, as a raw string.   → link: `TESTING_FRAMEWORK.md` markers

### EXP-0004 · 2026-10-16 · ❌ · #debug #package #resources
class: renamed-package-identity
**Context:** the debug variant renames the package (`com.kriniks.tribit.debug`) so it installs beside the original.
**Tried / did:** dialogs showed Chinese designer placeholders: the calls of `getIdentifier(name, type, getPackageName())` (about 26-35
of the 73 `getIdentifier` calls) found nothing, because the resource table keeps the original package name.
**Result:** ✅ after routing every `Resources.getIdentifier` through `krinik.Res` with a fallback to the original name.
**Lesson:** after `renameManifestPackage` grep the smali for `getPackageName()` users — `getIdentifier`, authorities,
`PackageManager` lookups — before the first device run.   mechanized: patches/apply.py   → link: `patches/java/krinik/Res.java`

### EXP-0005 · 2026-10-16 · ❌ · #titan #ui-agent #tools
class: own-work-not-recalled
none-cheap: recall of sibling projects' tools is a reading step (AGENT_GUIDE checklist step 2), now recorded in HOUSE_RULES.md §6
**Context:** the first device runs went through `uiautomator dump` (about 3 s a call) and taps by coordinates.
**Tried / did:** the owner pointed at `C:\Android\private\ui-agent\` — already listed in `KARTUN/HOUSE_RULES.md` §6.
**Result:** ✅ with the UI agent a whole flow (splash → login → search → speaker → EQ) ran in seconds per screen.
**Lesson:** before driving a device, read the house rules of the owner's sibling projects for that device (checklist step 2).
→ link: `HOUSE_RULES.md` §6
