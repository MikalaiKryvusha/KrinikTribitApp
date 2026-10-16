# Krinik Tribit — External structure map

> **The EXTERNAL map: what the project looks like from the outside** — directories, files, and who references whom.
> Companion: `PROJECT_ARCHITECTURE_INTERNAL_MAP.md` (the logical model). **Living reference — never DONE-tagged.**

---

## The tree

```
KrinikTribit/
├── patches/apply.py        # the six smali/resource patches of the fork (each fails on a missing anchor)
├── build.sh                # decode → patch → rebuild → zipalign → sign the whole split set with one key
├── design/                 # icon.svg (source of the launcher icon), icon-preview.webp
├── researches/             # 01 Play reviews (+ scripts), 02 languages, 03 pains of their app + speaker protocol
├── testcases/              # TC_fork_titan.md — the device case set; reports/ — run reports by date
├── tools/                  # apktool.jar, jadx/ (local, ignored) · unwire-owner-word-hooks.mjs (tracked)
├── HOUSE_RULES.md          # owner's rules, the Titan stand, tools, machine dossier
├── STATUS.md · GOAL.md · MASTER_PLAN.md · the KAIF canon docs · plans/ bugs/ ideas/ …
├── .kaif/ .claude/ .agents/ .grok/ .cline/ .roo/ .clinerules/   # KAIF machinery and skills (5 agent systems)
│
│   — local only, never in git (proprietary or secret) —
├── native/                 # OWN git repo (private remote MikalaiKryvusha/KrinikTribitNative): Tribit's apktool tree with
│                           #   our fixes as native code (HOUSE_RULES R9); build.sh builds from it
├── original-apk/           # the official split APKs pulled from the tablet
├── decompiled/             # jadx sources of base.apk (read-only evidence)
├── work/base/              # apktool tree the patches run on (rebuilt from scratch by build.sh)
├── out/signed/             # the installable result: adb install-multiple out/signed/*.apk
├── keys/                   # the fork's signing key (created by build.sh)
└── diagnostics/            # crash logs from the tablet
```

## What each part is

| Path | What it is | Depends on / references |
|------|-----------|-------------------------|
| `app/` | OUR app (Kotlin + Compose, `com.kriniks.tribit`): `protocol/` codec, Blast 2 commands, EQ, settings, settings file (JVM tests in `app/src/test`), `link/` SPP socket + `SpeakerViewModel`, `ui/` screens; `src/debug` — debug tools and the ear | `researches/11` §3 (protocol), KARTUN's theme; `gradlew.bat assembleDebug` / `assembleRelease` (R8, key from `.env`) |
| `native/` (private repo) | Tribit 5.0.0 decoded by apktool + our fixes; new fixes are commits here; `krinik-app/` - Tribit's speaker photos for OUR app (`res/`, `photos/`) | `build.sh` copies it into `work/base/` without `krinik-app/`; `app/build.gradle.kts` takes `krinik-app/res` |
| `app/src/photostub/` | the drawn stand-in of the speaker photo for a build without `native/` | `app/build.gradle.kts` |
| `design/mockups-v1.html` | the mock-up sheet (A + A accepted, `interviews/interview_003`) | `tools/shoot-mockups.mjs` → `design/mockups-v1/*.webp` |
| `tools/fetch_speaker_images.py` | anonymous new-device guest → Tribit's two catalogs → every picture into `design/photos/` (ignored) | `HOUSE_RULES.md` R2, exception 2 |
| `researches/12_tribit_blast2_inventory.md` | the parity inventory of Tribit's Blast 2 screens, 110 rows | `decompiled/` |
| `patches/apply.py` | patches 1–36 (how `native/` commit 2 was made) and the variant step `--variant` | `work/base/` (written by `build.sh`) |
| `build.sh` | the fork's build | `original-apk/`, `tools/apktool.jar`, `patches/apply.py`, SDK build-tools 36.0.0 |
| `researches/03_tribit_app_pains.md` | the pain list + protocol notes; code quotes point into `decompiled/` and `work/base/` | `01_play_reviews.md`, `diagnostics/` |
| `researches/01_play_reviews/make-reviews-md.mjs` | generates `01_play_reviews.md` from the ignored raw JSON beside it | `play-reviews-raw.json` (local) |
| `testcases/TC_fork_titan.md` | 15 device cases + a control case for patches 1–6 | `HOUSE_RULES.md` §3, `out/signed/` |

## Cross-references & dependency rules

- Nothing tracked may contain Tribit's code or APK bytes; tracked docs quote code by path and line only.
- `researches/01_play_reviews.md` is generated — edit the script, re-run it.
- Skill mirrors in `.agents/ .grok/ .cline/ .roo/` re-sync from `.claude/skills/` — edit only the canon copy.

## Entry points

`STATUS.md` → `HOUSE_RULES.md` → `researches/03_tribit_app_pains.md` → `patches/apply.py` + `build.sh` → `testcases/TC_fork_titan.md`.

---

> Keep this map honest: a new top-level directory (the own app's Gradle project) gets its row the day it appears.
