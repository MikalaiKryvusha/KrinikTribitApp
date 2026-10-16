# План 07 — эпик 04, фаза 3, шаг 1: главный экран A и эквалайзер A в приложении

> **Created:** 2026-10-16 · **Parent:** `plans/04_EPIC_own_app.md` → «Фазы», row 3 «Красота, экраны, языки» (anchor: «макеты на
> одном листе — выбор владельца») · **Status:** 🔧 in work 2026-10-16 ≈ 19:55 +03:00 · **Outbound:** —

## Goal vector (Achieve)

**Pain.** The owner, 2026-10-16 ≈ 19:05: the app's design is «простой не интересный, не похож на оригинальное приложение
Tribit и не использует лучшие подходы из KARTUN». **Where we want to be.** The home screen and the EQ screen on the A51 look
as the accepted mock-ups A + A (`design/mockups-v1.html`, `interviews/interview_003` — «Макеты А А приняты» ≈ 19:30) with
the owner's later corrections (same interview, «Приёмка и следующие правки»), every value still the speaker's answer.

## Acceptance criteria

1. Situation: the Blast 2 is connected, playing, volume 10, EQ «Рок». Action: the user opens the app. Result: the A51
   screenshot matches A-home row by row (inventory below). Check: `testcases/reports/<date>_phase3_screens.md` with the
   shot beside `design/mockups-v1/A-home.webp`.
2. Same for the EQ screen against A-eq, A-custom, A-full-port, A-full-land, A-new, A-export.
3. Rotating the phone on the full-screen editor keeps the link: no `closed` / `connected` pair in `adb logcat -s KT.Link:D`.
4. A preset made by «+» survives an app restart: a file in `files/presets/` (`run-as … ls files/presets`).

## Parity inventory — no row, no code

| # | Element (mock-up) | Behaviour | In the app now? | Step |
|---|---|---|---|---|
| H1 | Logo «Krinik Tribit» with a pink K, gear button right (owner ≈ 19:31) | gear opens app Settings | text title + a row | 2 |
| H2 | Speaker drawing on a pink glow, light rings | drawn by us (`interviews/interview_004` open: photo or drawing) | no | 2 |
| H3 | Name + pills «Подключена», battery icon + % | values from the speaker, «—» until answered | text lines | 2 |
| H4 | Player card: volume slider 0..31 with the number; prev · big pink «Пауза/Играть» (from C) · next | prev/next = cmd 2 [1]/[2] | slider + outlined button | 2–3 |
| H5 | EQ strip full width: icon, «Эквалайзер», preset name, response curve with ten band labels | opens EQ | a row | 2 |
| H6 | Light strip: icon, «Подсветка», mode | the mode choice inside the strip | a choice row | 2 |
| H7 | Speaker settings strip: icon, title, what is inside | opens speaker settings | a row | 2 |
| H8 | The not-connected faces (permission, BT off, waiting, failed) | unchanged texts, new card look | card faces | 2 |
| E1 | Graph card: name, «Сейчас на колонке», curve, ten band labels; a preset's graph only shows (owner ≈ 19:5x) | — | no | 4 |
| E2 | Preset cards two per row, each with its curve; the speaker's preset pink-bordered with a tick | tap = select | list rows | 4 |
| E3 | «Пользовательский» first, pink-violet fill, «+» (owner ≈ 19:30) | «+» = new preset dialog | no | 5 |
| E4 | Custom presets as files in the app's folder (owner ≈ 19:4x), cards after «Пользовательский» | tap = send its bands (cmd 11) | no | 5 |
| E5 | Custom selected: the graph is the editor - knobs, value over each band, the band under the finger pink | release sends cmd 11 | ten sliders | 6 |
| E6 | Pencil = rename a named preset; name ≤ 15 characters (interview 002 Q4) | centred dialog | no | 5 |
| E7 | Expand = full-screen editor, portrait and landscape; the link survives rotation | `configChanges` | no | 6 |
| E8 | «Новый эквалайзер» dialog: name, counter «0 / 15», all ten bands at 0 dB (owner ≈ 19:4x) | Создать / Отмена | no | 5 |
| E9 | Import / Export pinned at the bottom; Export = centred dialog «Сохранить в файл» / «Поделиться файлом» | JSON file (`ideas/01`) | three rows in a card | 7 |

## Steps

- [x] 1. Shared pieces: vector icons from the sheet (`res/drawable/ic_*.xml`), `PrimaryButton`, `RoundIconButton`,
      `Strip`, `CenterDialog`, the response curve (monotone cubic, `CurveMathTest`).
- [x] 2. Home A (H1–H8) + the speaker drawing — seen on the A51 (`testcases/reports/2026-10-16_phase3_screens.md`).
- [ ] 3. Prev / next commands in `SpeakerViewModel` — written; not pressed (volume 9, sound only at 1–2).
- [x] 4. EQ graph card + preset cards (E1, E2) — seen; preset names by Tribit's Blast 2 code (owner 19:55 «x-3d где???»).
- [ ] 5. Custom presets (E3, E4, E8 seen; E6 rename not walked).
- [x] 6. The editor on the graph and on the full screen; `configChanges` (E5, E7) — rotation with 0 link lines.
- [ ] 7. Import / Export (E9) — the dialog seen; save / share / import of this build not walked.
- [x] 8. Strings by the portrait (R10): lint 0; §7B 24 strings, 6 findings rewritten.
- [ ] 9. A51 run — `testcases/reports/2026-10-16_phase3_screens.md`, verdict partial.
- [ ] 10. The parity inventory of Tribit's own Blast 2 screens (`researches/12`) — every row checked against our app.

**Owner's rule in this step:** «стиль Material 3 - всё верно» · «используем нативные материалы и стили» (chat 2026-10-16
≈ 19:52 +03:00) — native Material 3 components and their own look (the slider thumb stays Material's), `HOUSE_RULES.md` R11.

## Risks

- (a) Rotation with `configChanges`: a screen that reads the orientation once would not re-layout - every layout reads
  the current constraints (`BoxWithConstraints`). (b) A named preset and the speaker's one custom slot: the app knows which
  named preset is on the speaker only while it remembers the last one sent; after a restart «Пользовательский» is marked.
  (c) Old firmware (±8 dB): the graph range comes from `Eq.offset`.

## Decisions made without the owner

- `[AI]` icons as vector drawables (KARTUN's way), no icon library.
- `[AI]` Export writes the EQ only (the existing settings file with no light); Import reads old files with light too.
