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
>      field-dropped-in-rebuild, renamed-package-identity, own-work-not-recalled -->
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
>
> The `#tags` are **trigger-tags**: before a task, grep by the task's tags and QUOTE the relevant
> lessons in your report (id + one line) — or state "no relevant lessons". An unquoted recall is
> unverifiable; `/fable-judge` checks for this line.
>
> Skill: `/experience` (capture a lesson · recall relevant lessons).

## Entries

### EXP-0001 · 2026-01-01 · ✅ · #example #meta
**Context:** first task after KAIF was deployed into this project (example entry — replace with real ones).
**Tried / did:** wrote the first real lesson here in the canonical format.
**Result:** ✅ — the experience log is live and greppable.
**Lesson:** capture lessons at the level of *approach* (what worked / what to avoid), not defect detail
(that lives in `bugs/`); one short entry beats a long story.   → link: (none)

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
