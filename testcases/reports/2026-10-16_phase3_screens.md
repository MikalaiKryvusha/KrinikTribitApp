# Test run report — phase 3, step 1: home A and EQ A in the app (plans/07)

**Created:** 2026-10-16 20:05 +03:00 · **Run by:** the agent (Claude Opus 5.5) · **Version/build:** debug
`com.kriniks.tribit.debug`, builds 19:49, 19:53, 19:55, 19:57, 20:03 (app-debug.apk)

## 1. Work

The home screen and the EQ screen rebuilt by the accepted mock-ups A + A (`design/mockups-v1.html`,
`interviews/interview_003`) with the owner's corrections: full-width strips, the big «Пауза», the EQ response on the home
strip; the EQ graph that only shows for Tribit's presets and edits a custom one; «Пользовательский» first in colour with «+»;
custom presets as files; the full-screen editor in portrait and landscape; Import / Export. Basis: the parity inventory of
`plans/07_epic04_phase3_screens.md` (rows H1–H8, E1–E9).

## 2. Contour

Samsung A51 (`R58N615KXZZ`, Android 13, 1080×2400, font 1.1) on USB with the StormBox Blast 2 bonded and connected
(battery 30 %, volume 9, paused, light off). REAL WORLD: accumulated — the speaker as the owner left it (custom EQ, then
Rock set by this run), the app's data from earlier runs of the day; data and machine — the owner's speaker on the stand
phone; path — the user's taps on the A51 screen (`adb shell input`), the speaker's answers read in `KT.Link`.

## 3. Runs

| # | Moment | Command | Exit / outcome |
|---|---|---|---|
| 1 | 2026-10-16 19:49 +03:00 | `.\gradlew.bat assembleDebug testDebugUnitTest` | 0 · 45 JVM tests, 0 failures |
| 2 | 2026-10-16 19:50 +03:00 | `adb install -r app-debug.apk` · `am start -S -W …MainActivity` · `screencap` | home shot 1, EQ shot 2 |
| 3 | 2026-10-16 19:50 +03:00 | `adb shell input swipe 631 793 631 668 600` (editor, band 1K) | **fail**: the page scrolled, no TX |
| 4 | 2026-10-16 19:53 +03:00 | same swipe after the gesture fix | TX `EA 0E 0B 0C 0C 0C 0C 0C 12 0C 0C 0C 0C 81`, RX 21 `07 … 12 …` |
| 5 | 2026-10-16 19:56 +03:00 | expand tap; `wm user-rotation lock 1`; `logcat -d -s KT.Link:D \| wc -l` | landscape editor, 0 link lines |
| 6 | 2026-10-16 19:58 +03:00 | «+» tap, `input text Vecher`, «Создать»; `run-as … cat files/presets/1792169890393.json` | file written, TX flat custom |
| 7 | 2026-10-16 19:58 +03:00 | `am force-stop` · `am start` · EQ | «Vecher» read back from its file |
| 8 | 2026-10-16 19:59 +03:00 | tap «Рок»; tap «Экспорт» | TX 4 `05 …`, RX 21 `05`; export dialog |
| 9 | 2026-10-16 20:04 +03:00 | build 20:03, home scrolled | strips; the settings line cut at 2 lines (fixed to 3, not re-shot) |

## 4. Checks

- Hygiene: `testDebugUnitTest` 45/45 (new: `CurveMathTest` 4 - the curve never leaves the band range, proved against the
  old Catmull-Rom; `UserPresetTest` 4); `kaif-voice-lint check values-ru/strings.xml` 0 findings; §7B by a subagent:
  24 strings, 6 findings, all rewritten.
- Functional run: the user's path on the A51 with the speaker, the screen and `KT.Link` read:
  1. H1–H8 home: logo with the pink K, the gear, the drawn speaker (rings grey - the light is off), «Подключена», battery
     30 %, the player card (volume 9, «Играть», prev/next buttons), the EQ strip with the response of the speaker's EQ,
     the light strip with the mode choice, the speaker settings strip — pass (shots 1, 13–15).
  2. E1 a preset's graph only shows: «Рок» with small dots, no knobs, no expand button — pass (shot 11).
  3. E2 preset cards with their curves, the speaker's preset ticked (RX 21 id 5) — pass (shot 11).
  4. E3 «Пользовательский» first in colour with «+» — pass (shots 2, 9).
  5. E5 the graph edits a custom EQ: band 1K to +6, the speaker answers id 7 with +6 at 1K — pass after the fix (run 4).
  6. E7 full screen portrait and landscape, rotation without a reconnect (0 `KT.Link` lines) — pass (shots 4–5).
  7. E8 «Новый эквалайзер»: counter, «Создать» off while empty, 0 dB on all bands, the file in `files/presets/` — pass.
  8. E4 the preset survives a restart — pass; after the restart «Пользовательский» is marked, as plans/07 risk (b) says.
  9. E9 the export dialog — pass for the dialog; «Сохранить в файл» / «Поделиться» / «Импорт» on this build — not walked.
  10. E6 rename — not walked. Prev / next — not pressed: volume 9, the owner allows sound at 1–2 only (HOUSE_RULES §3).

## 5. Found

1. The editor inside the scrolling page lost the vertical drag to the scroll (run 3) — fixed: the editor consumes the touch.
2. Black title on the full-screen editor (no content colour outside `Page`) — fixed.
3. Long names cut («Пользовательск…», «Пользова…») — fixed by the smaller title and the name row.
4. Three preset names differ from Tribit's app for the Blast 2 (owner 19:55 «x-3d где???»): «X-3D», «XBass Off
   (V8.6/V7.4)», «XBass (V8.6/V7.4)» — fixed by their code; the full inventory is `researches/12`.
5. Stand: I turned the A51 with `wm` without reading its mode first; the native auto-rotate was restored from
   `testcases/reports/2026-10-16_a51_stand.md` (EXPERIENCE).

## 6. Traces

`testcases/reports/2026-10-16_phase3_screens/1_home.webp` … `15_home_strips.webp`; the TX/RX lines quoted in Runs.

## 7. Verdict

partial — every walked row passed; rename, save / share / import on this build, prev / next and the last 3-line fix are
not walked.
