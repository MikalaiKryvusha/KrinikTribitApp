# План 06 — эпик 04, фаза 2: эквалайзер, подсветка, настройки колонки

> **Created:** 2026-10-16 · **Parent:** `plans/04_EPIC_own_app.md` → «Фазы», row 2 «Эквалайзер, подсветка, настройки
> колонки» · **Status:** 🔧 in work 2026-10-16 16:43 +03:00; steps 1–5 ✅ 16:54 (`testcases/reports/2026-10-16_eq.md`, `…_light.md`) · **Outbound:** —

## Goal vector (Achieve)

**Pain.** The equalizer is the top complaint after connection (`researches/01`: «эквалайзер не сохраняется» — 117 reviews;
their app crashes on its own custom EQ — `GOAL.md`). Our app shows only battery, volume and play.

**Where we want to be.** On the A51 the user picks a preset or sets the custom 10-band EQ, switches the light, and changes
the speaker settings (auto shutdown, sleep timer, voice prompts, volume indicator, mic boost, anti-howl); every value on
screen is the speaker's answer; the speaker's own buttons move what the screen shows.

## Acceptance criteria

1. **Preset.** Situation: connected, preset Default. Action: the user taps «Rock». Result: the EQ card reads «Rock»; the log
   shows `TX EA 0F 04 05 16 12 08 04 06 12 18 14 0E 0C …` and an answer of the speaker; after re-opening the app the card
   still reads «Rock». Check: `logcat -s KT.Link` lines in the run report.
2. **Custom EQ.** The user drags band 1K to +6 dB and releases; the speaker gets cmd 11 with 10 bytes, band 6 = 18 (wire =
   dB + 12); the state read 21 returns id 7 with the same gains. Check: log + `SpeakerFramesTest` fixture from that frame.
3. **Light on/off** by cmd 12; the speaker's 85 notice moves the switch. Check: log + screen.
4. **Settings rows** read their state on open (16, 15, 49, 51, 98, 100) and write it (3, 14, 48, 52, 97, 99); auto
   shutdown decodes «0 = on» (`researches/11` §3.6). Check: each row — the set packet, the re-read answer, the screen.
5. **Codec under tests.** Every new send and parse has a byte-exact JVM test; the first frame of each new reply from the
   speaker becomes a fixture.
6. **Texts by the portrait** (`HOUSE_RULES.md` R10): `kaif-voice-lint check` 0 hits + a clean §7B pass before the build
   reaches the owner.

## Steps

- [x] 1. Protocol: firmware flags from 88 («new» dsp > 10074, «new EQ» dsp > 10095); presets table (id, name, gains) from
      `researches/11` §3.6; `setPreset(id)` (cmd 4 [id, 10 gains]), `setCustom(gains dB)` (cmd 11, 10 bytes, dB + 12 / + 8),
      `queryEq()` (21); parse 21/82 → `Eq(id, gains)`. Tests.
- [x] 2. Command layer (`plans/05` step 9, `researches/11` §4b.3): the speaker echoes each command — wait for the echo of
      the same cmd up to 500 ms × attempt, 3 attempts; one command in flight; sliders send on release only (their app
      does the same, §3.6 «Pacing»).
- [x] 3. EQ screen: preset list + the custom 10-band editor (±12 dB on «new», ±8 on old), KARTUN components; the home
      card shows the current preset and opens the screen. Strings by the portrait.
- [x] 4. Device run on the A51 (sound only at volume 1–2, `HOUSE_RULES.md` §3): criteria 1–2; the «Blast traditional» id
      8 vs 9 question answered by the speaker's 21 reply. Run report.
- [x] 5. Light: on/off (12, 20, 85) on the home card. Device run.
- [ ] 6. Settings screen of the speaker: the six rows of criterion 4. Device run.
- [ ] 7. The open check of phase 1 (`plans/05` step 8): the owner powers the speaker off and on → «Ожидание колонки» →
      connected by itself.
- [ ] 7a. **The ear through the A51 microphone — presence and loudness only.** The owner 16:49: «микрофон в А51 плохой, ты
      не сможешь оценить качество работы жквалайзера» · 16:50: «микрофон в А51 качества такого, чтобы услышать вообще, есть
      звук, или нет, меняется громкость, или нет». A debug-only tool in «Отладка»: play a test tone at volume 1–2, log the
      microphone level (`KT.Ear`) — sound present yes/no, level up/down after a volume change. The EQ sound is the owner's
      ear; the EQ state is the speaker's reply (21 / 82). `RECORD_AUDIO` in the debug manifest only.
- [ ] 8. `ideas/01` JSON export/import of EQ and light — after 3 and 5 work on the speaker.

## Risks

- (а) A wrong gain byte puts a band at ±12 dB — loud. Defence: tests on every table row; device runs at volume 1–2.
- (а) «Blast traditional» sent as 8, read back as 9 in their code. Defence: send 8, read 21, show what the speaker says.
- (б) Custom EQ saved only on the speaker; the speaker keeps one custom slot (id 7). Saving several named presets in the
  app is a product question — `interviews/` when step 3 reaches it.

## Decisions made without the owner

Filled at closing.
