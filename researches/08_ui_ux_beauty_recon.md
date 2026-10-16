# Research 08 — beautiful UI/UX for Krinik Tribit: the owner's measure, our style, the tools, the industry

> **Created:** 2026-10-16 · owner's word in chat 2026-10-16 ≈ 11:10 +03:00: «UI/UX нужно делать красивым» · «нужна
> разведка» · «можешь заглянуть в проекты KARTUN. KUMM Svarog - там ии агенты много умеют по дизайнам» ·
> **Parent:** `GOAL.md`, `MASTER_PLAN.md` decision journal (taste class) · **Status:** local recon done 2026-10-16 ≈ 11:15;
> industry section filled from a web sweep 2026-10-16 ≈ 11:25 · **Outbound:** first mock-up sheet to the owner (taste class)

## 1. What «beautiful» means to this owner — already written down, in his own words

Source: `D:\work\ai_sandbox\SvarogsDream\docs\UI_RULEBOOK.md` §0 «Философия прекрасного» and §10а (read-only, another
project of the same owner). His words there: «простота, структура, изящество» · «разведка, философии ЛУЧШИХ дизайнеров
мира» (2026-10-06). The agent's reading he accepted (KUMM memory `svarog-ui-beauty-is-no-seams`): **beauty = the user's eye
never stumbles and never sees a seam of the machinery** — nothing jumps, nothing is cut off, everything answers a touch, the
same thing looks the same everywhere. «Некрасиво» means «fix how it looks», never «remove it» (KUMM EXP-0249).

The seven classes (§10а), carried over to a speaker app — each is a question the agent asks EVERY screen before the owner:

| # | Class (Svarog) | For Krinik Tribit |
|---|---|---|
| K1 | One language in all menus | one set of components and tokens on every screen: the same card, row, slider, button everywhere |
| K2 | Nothing jumps | switching a preset, a tab, a speaker does not move heights, type size or column widths |
| K3 | Touch feedback on everything, in its own tone | every pressable thing answers the touch (ripple / pressed state) in its own colour |
| K4 | The author's idea stays | here the author is Krinik: the pink brand and the dark ground stay; the layout and readability change |
| K5 | Data reads whole | battery, volume, EQ values, firmware versions: never cut off, never under an image, tabular figures |
| K6 | A popup stands by what was touched | dialogs and sheets open from the element that called them, one surface style |
| K7 | Everything translated | not one English or Chinese string on a Russian phone (wave 2, `values-ru`) |

Observed seams of our build today (2026-10-16, A51 and Titan shots in `testcases/reports/shots/`): «В настоящее время нет
сопряжённых Bluetooth-устройств» cut on the left (K5); yellow switches and check marks among the pink (K1, K4); English
labels «Tap to Add Device», «Device Settings», «Sound Effects», «Settings Center» on a Russian phone (K7); the consent line
under the gesture bar in landscape (K5); the splash race that shows English for a fast tap (K7).

## 2. Krinik style — the tokens already used in the owner's Android apps

Source: `D:\work\ai_sandbox\KARTUN\researches\01_krinikcam_style_and_stack.md` §1 (KrinikCam as reference): a near-black UI
with exactly ONE brand accent, acid pink `#FF1A8C`; background `#0D0D0D`; flat dark-grey surfaces; 10dp house radius
(cards, rows), 8dp pills, circle FABs; 16dp horizontal gutter; Material icons, filled, tinted pink; tabular figures for
numbers. Our build already carries the pink (patch 17) and the dark ground of Tribit's screens.

## 3. Tools the owner's other projects already have — reuse, do not re-invent

| Tool (project) | What it gives us |
|---|---|
| `design/kartun-mockups.html` + `tools/shoot-mockups.mjs` (KARTUN; Playwright, 390×900 per screen) | screens drawn in HTML, shot to PNG in one run — the cheapest way to show the owner a variant on our material |
| `design/processing-variants.html` + `tools/shoot-processing-variants.mjs` (KARTUN) | variants A–C of one screen side by side on ONE sheet — the taste-class comparison format |
| KUIPS flow map `design/flow-map.html` built by `D:/work/ai_sandbox/ndim/tools/build-flow-map.mjs` (KARTUN) | the whole user path as one sheet of screens with arrows |
| `tools/blind-sheet.py` (KARTUN) | blind row: candidates under shuffled numbers, the key kept aside — for a verdict without bias |
| `KUMM/researches/svarogs-dream/ui-philosophy-best-designers.md` | the «best designers» sweep (Rams, Saint-Exupéry, …) behind §0 |

Lessons paid in KUMM (EXP-0246, memories `sight-runs-out-offer-variants`, `look-at-what-you-made`): a choice of look is shown
ONLY as a sheet of frames on our own material, opened for the owner — never as an A/B/C question without a picture; the
agent looks at what it made with its own eye first; long chats lose image reading — offer variants, do not tune taste blind.

## 4. Industry — how the leading speaker apps do these screens

Web sweep 2026-10-16 ≈ 11:25 +03:00 by a research subagent. Limits: Google Play pages and m3.material.io did not render for
the tool; a few facts come from search snippets of pages that refused access — marked «snippet». No source was found for
the device page of the B&O, Bose and Marshall apps, nor for any app's dark-theme design.

**How the leading apps present the same screens**

| App | Device page · EQ · other | Source |
|---|---|---|
| JBL Portable / JBL One | battery on the product screen; 4 preset EQs + Custom (5 bands on Go 4); JBL moving speakers into JBL One with a similar layout, EQ and lighting kept | techradar.com/audio/wireless-bluetooth-speakers/jbl-go-4-review · soundguys.com/jbl-is-quietly-switching-its-bluetooth-speakers-to-one-app-161728/ |
| Sony Sound Connect | tabs My Device · Scene · Discover · Menu; My Device shows battery and EQ presets + custom (5 bands + Clear Bass, 2 custom slots — snippet); a home-screen widget with model, battery, EQ | helpguide.sony.net/mdr/2999/v1/en/contents/F002_Using_the_Sound_Connect_app.html · sony-asia.com support 00286844 (snippet) · 00186711 |
| Bose | presets + 3 sliders (bass, mid, treble); a manual setting could not be saved in 2022; sliders readable by VoiceOver | ubergizmo.com/2022/02/bose-qc45-customizable-eqs/amp/ · applevis.com/comment/209109 |
| Soundcore | custom EQ as a curve of dots dragged with a finger; 9 bands on Boom 3i; HearID builds a personal profile; 22 presets | service.soundcore.com (Motion X600 EQ article) · community.eufy.com/t/tune-your-boom-3i-a-quick-guide-to-eq/5817974 · soundcore.com/eu/hearid |
| UE BOOM | named presets («Out Loud», «Intimate» — snippet); volume only through repeated big +/- taps, called «a little dated» | imore.com/ue-boom-3-review · whathifi.com/ultimate-ears/boom/review (snippet) |
| Marshall | sliders + preset drop-down; 5 bands, 3 saved slots | marshall.com support (Minor IV) · techhive.com/article/3639916 |
| Bang & Olufsen | Beosonic: a circle of 4 moods, drag a marker (snippet) | support.bang-olufsen.com 360055532452 (snippet) |

**What users praise and complain about:** a guided, personal EQ is «more engaging than a manual EQ slider» (tomsguide.com,
review of Soundcore headphones); unskippable ads before the controls (community.eufy.com/t/stop-forcing-un/5758781); app
size and AI extras (mwm.ai — secondary); features and volume numbers removed in a redesign — the Sonos 2024 backlash
(stuff.tv/news/why-the-tale-of-sonos-revamped-app-is-a-cautionary-one/); EQ controls vanishing (proforums.harman.com 137015).

**Material 3 / Android guidance:** sliders — standard, **centered** (for ranges around zero: EQ ±dB), range, stops; 48 dp
touch target; content descriptions strongly encouraged (github.com/material-components/material-components-android
docs/components/Slider.md). Type scale of 5 groups × 3 sizes, «you will likely not need all 15»; corner radii 4/8/12/16/24
dp; dark theme elevation by tonal overlays; dynamic colour only on Android 12+ with a fallback, brand colour can stay fixed
or be harmonized (developer.android.com/develop/ui/compose/designsystems/material3 · /develop/ui/views/theming/dynamic-colors).
Dark grey, not pure black (m2.material.io/design/color/dark-theme). Edge-to-edge is enforced for apps targeting SDK 35 on
Android 15 — system-bar, cutout and gesture insets must be handled (developer.android.com/develop/ui/views/layout/edge-to-edge)
— their APK targets SDK 36 (`work/base/apktool.yml`), so edge-to-edge is forced on the Titan (Android 16); the A51
(Android 13) is outside that rule, so the consent line under the gesture bar there has another cause, still unknown. 16 dp phone
margins (m2.material.io/design/layout). Accessibility: text ≥ 4.5:1 (large ≥ 3:1), controls ≥ 3:1 (WCAG 1.4.11), targets
≥ 48×48 dp (developer.android.com/guide/topics/ui/accessibility/apps; w3.org/WAI/WCAG22/Understanding/non-text-contrast).

**Patterns worth adopting for Krinik Tribit:** battery and status at the top of the speaker page (JBL, Sony); presets first,
Custom second (JBL, Sony, Bose, Marshall); **centered sliders with stops** for the 10-band ±dB editor (MDC Slider doc);
named, saved custom presets (Bose criticised for not saving — and our `bugs/01`); the brand pink fixed; edge-to-edge with
proper insets; labelled sliders for screen readers.

**Anti-patterns:** ads or promos before the controls; removing existing features or volume numbers in a redesign; volume
only through repeated +/- taps; extras unrelated to the speaker; a custom EQ that cannot be saved; contrast or touch
targets below the thresholds above.

## 6. The design scheme — the owner's requirements and their checkable form

The owner, 2026-10-16 11:18 +03:00: «нужно чтобы были заметны элементы, контраста текста чтобы хватало, однотипность дизайна в разных местах приложения, общая дизайн схема, с минимальным но достаточным набором правил и компонентов, которые переиспользуются везде по приложению».

[AI] Checkable form (thresholds from standards, not taste):

| Owner's requirement | Rule | Check |
|---|---|---|
| elements are noticeable | every pressable element is at least 48×48 dp and differs from its background by ≥ 3:1 (WCAG 2.1 SC 1.4.11, non-text contrast) | measure the element's bounds in the layout dump; contrast of its colour against the surface |
| enough text contrast | body text ≥ 4.5:1 against its background, large text (≥ 18 sp, or 14 sp bold) ≥ 3:1 (WCAG 2.1 SC 1.4.3) | a contrast script over the token pairs; spot checks on screenshots |
| the same design in different places | every screen uses only the tokens and components of the scheme; a screen with a one-off colour, radius or button style is a defect (class K1) | a grep over the patched resources for colours and dimens outside the token list |
| one scheme, minimal but sufficient | tokens: 2 surfaces + background, 1 accent (`#FF1A8C`), 3 text tones, 1 danger; type scale of 5 sizes; spacing on a 4/8 dp grid (8, 16, 24); radius 10 dp (cards, rows), 8 dp (pills); components: screen header, card, list row, primary button, secondary button, switch, slider, chip/segmented choice, dialog/sheet, empty state — ten | the scheme document lists exactly these; a new component needs a reason in words |
| reused everywhere | the components are applied by the patches as shared styles/drawables, never copied per screen | each component is one resource referenced from many layouts |

The colour values and sizes above are the agent's proposal on top of the Krinik tokens (§2); the first mock-up sheet shows
them to the owner, and his verdict fixes them.[/AI]

## 5. Plan — the first steps (taste class: mock-ups, the owner chooses)

[AI]
1. **The seam sheet:** our current screens of the main path (splash, entry, main, speaker page, sound effects, EQ editor, light,
   speaker settings, app settings) shot on the A51, one sheet, every seam marked with its class K1–K7.
2. **Mock-ups of the speaker page and the EQ editor** — the two screens people use most — in HTML on our material (Blast 2,
   its real battery, presets and bands), 2–3 variants side by side on one sheet, built with the KARTUN shooter.
3. The owner chooses; the chosen variant becomes the reference, and the patches rework the layouts toward it (their screens
   are fixed, not rewritten — `plans/01`).
4. **Testing on devices** — the owner, 2026-10-16 11:19 +03:00: «тестирование макетов и получающегося UI на устройствах, чтобы выглядело красиво». Mock-ups are shot at the dp sizes of our screen profiles
   (`tools/screen_profile.py list`: Titan 533×853, small 360×640, design 375×667, tab7 600×960, and landscape); the
   patched UI is shot on the A51 in the same profiles (`screen_profile.py apply …` + `testcases/snap.py`); one sheet per
   screen puts the chosen mock-up beside the real result; every sheet walks K1–K7 and the contrast check of §6, and the
   run leaves a report in `testcases/reports/`. The owner's eye gives the verdict on beauty; the agent's check gives the
   seams and the numbers first.
[/AI]
