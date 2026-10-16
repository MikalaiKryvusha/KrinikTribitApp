# План 05 — эпик 04, фаза 1: связь с Blast 2

> **Created:** 2026-10-16 · **Parent:** `plans/04_EPIC_own_app.md` → «Фазы», row 1 «Связь с Blast 2» · **Status:** 🔧 in
> work 2026-10-16 16:05 +03:00; steps 1–7 ✅ 16:31 (`testcases/reports/2026-10-16_own_app_connection.md`, pass) · **Outbound:** —

## Goal vector (Achieve)

**Pain.** `app/` shows «Колонка не подключена» and a disabled button: the own app does not talk to the speaker at all.

**Where we want to be.** On the A51 with location off, Krinik Tribit finds the bonded Blast 2, opens SPP, and shows its
battery, volume (settable) and play/pause — with every packet both ways in the debug log, and a codec covered by
byte-exact JVM tests.

## Acceptance criteria

1. **Found and connected without location.** Situation: A51, location off, Blast 2 bonded and A2DP-connected. Action: the
   user opens Debug Krinik Tribit and grants «Устройства поблизости». Result: the card reads «Tribit StormBox Blast 2» with a
   battery percentage. Check: `dumpsys package com.kriniks.tribit.debug | grep -i location` prints nothing; a WebP shot in
   the run report.
2. **Volume both ways.** Situation: connected, speaker volume V. Action: the user drags the slider to 10. Result: the
   speaker gets louder/quieter audibly; the log shows `TX EA 05 0D 0A 06` and the slider reads 10 after re-open. Check:
   `logcat -s KT.Link` lines in the report.
3. **Codec under tests.** Scale: commands of this phase with a byte-exact test · Meter: `.\gradlew.bat testDebugUnitTest`
   · Target: version, battery, volume get/set, play/pause, framer split/merge/resync/checksum — all green, and the framer
   test seen red on a broken framer.
4. **No main-thread I/O, socket always closed.** Check: leaving the app (`am force-stop` excluded) closes the socket — log
   line `KT.Link closed`; `StrictMode` in debug reports no disk/network on main.

## Inventory — Blast 2 functions of this phase

`researches/11` §3.3 is the source; a row is closed only by an observed speaker answer.

| Function | Send | Expected answer | Our status |
|---|---|---|---|
| Firmware version | `EA 05 01 00 F0` | cmd 1, string | ✅ `EA 08 01 72 1A 07 18 9E` → «26/7/24_11.4» |
| Battery % | 6 [1] | cmd 6, 0–100 | ✅ `EA 05 06 1E 13` → 30 % |
| Volume get | 18 [0] | cmd 18, 0–31 | ✅ `EA 05 12 09 0A` → 9 |
| Volume set | 13 [v] | echo or none | ✅ echo `EA 05 0D 0A 06` + unsolicited 84 `EA 05 54 0A 4D` in the same read |
| Play / pause | 2 [4 / 3] | — / state 19 | ✅ echo `02 04` / `02 03`; state 19 = 1 after play, 2 after pause |
| (unsolicited) | — | — | 88 `EA 05 58 62` (DSP version 98) at connect; 85 `EA 05 55 04` after volume set — phase 2 rows |

## Steps

- [x] 1. `protocol/Packet.kt` — `encode(cmd, payload)` (empty payload → one 0x00, len = payload + 4, sum = low byte) and
      `Framer` (stream → packets by len; resync on a byte ≠ 0xEA; checksum checked and flagged, not yet enforced — their
      app never checks it, we learn from real frames first). Tests in `app/src/test`.
- [x] 2. `protocol/Blast2.kt` — command ids and builders/parsers for the inventory rows. Tests byte-exact.
- [x] 3. `link/SpeakerLink.kt` — bonded device lookup (both spellings, case-insensitive), SPP socket on `Dispatchers.IO`,
      `connect()` after `cancelDiscovery()`, reader loop → `Framer`, writer, `close()` in `finally`; debug log `KT.Link`
      TX/RX hex.
- [x] 4. Manifest: `BLUETOOTH_CONNECT` only. `[AI]` A bonded speaker needs no scan; `BLUETOOTH_SCAN` with
      `neverForLocation` comes only if the owner wants in-app pairing (Blast 2 must be paired in Android's Bluetooth
      settings for A2DP anyway; their app opens SPP only for a bonded, A2DP-connected device — `researches/11` §3.1).
- [x] 5. `SpeakerViewModel` + Home card: states «нет разрешения» → «колонка не сопряжена» (button to Android's Bluetooth
      settings) → «подключение» → connected (battery, volume slider 0..31, play/pause). Strings ru + en.
- [x] 6. Build, install on A51, walk criteria 1–2; run report `testcases/reports/2026-10-16_own_app_connection.md`;
      inventory rows filled from the log. ✅ 16:20 — `testcases/reports/2026-10-16_own_app_connection.md` (location-off run and StrictMode ✅ 16:29; StrictMode found a 115 ms disk read, fixed).
- [x] 7. Twin of their old app: with `com.kriniks.tribit.old` holding SPP, our connect fails → the card says so (risk (б)). ✅ 16:31 — refused in 83 ms, the failure card; after closing it «Подключить» connects.

### Steps 8–11 — Bluetooth done right (the owner's recon 16:28, `researches/11` §4b)

- [ ] 8. **Follow the speaker's link while the app is visible** (§4b.1–2): a receiver for ACL and A2DP connection changes,
      registered in onStart, removed in onStop; at start `getProfileProxy(A2DP).getConnectedDevices()`. Bonded Blast 2
      without A2DP → state «Включите колонку» (no SPP attempt, no 12 s blocking connect); A2DP up → open SPP by itself; ACL
      down → `close()` at once and back to waiting. No blind retry loop.
- [ ] 9. **Command layer** (§4b.3): the Blast 2 echoes every command — the echo is the ACK; send the next command of a type
      after its echo or a timeout (500 ms × attempt, 3 attempts); unsolicited packets (84, 85, 88) on their own path; the
      full state re-read after every connect (already: startup queries).
- [ ] 10. **Errors that say what to do** (§4b.5): channel refused → close the other app (done, step 7); command timeout →
      the speaker does not answer; texts by the portrait (R10).
- [ ] 11. **Measure** (§4b.6, INFERRED): does an open SPP keep the Blast 2 from its auto-shutdown? Until measured the link
      lives only while the app is visible.

Test basis for 8: A51 + Blast 2 — speaker off → card «Включите колонку»; speaker on → connected without a tap; speaker off
while connected → back to the waiting card within the ACL disconnect; log `KT.Link`.

## Risks

See the epic. Phase-specific: (а) the speaker answers with a checksum of another rule → the framer flags it; we read the
real frames before enforcing. (б) Volume set has no echo → re-query 18 after set.

## Decisions made without the owner

Filled at closing.
