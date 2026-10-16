# Research 11 — our own Krinik Tribit app: requirements, the speaker protocol, the industry

> **Created:** 2026-10-16 (the owner, chat 15:24 +03:00: «Сворачиваем план на суть C» · «Делаем по плану C») ·
> **Parent:** `MASTER_PLAN.md` phases 2–3, `researches/03` (protocol notes), `researches/08` (beauty), `researches/10`
> (tools for reading their code) · **Status:** rung 1 of `/plan-epic` for `plans/04_EPIC_own_app.md`; requirements and local
> state 15:35, industry 15:36, the Blast 2 protocol 15:40 (24 of 24 quotes checked) ; KARTUN's answer 15:45 (§4a) — rung 1 complete ·
> **Outbound:** forks → `interviews/`; questions to the KARTUN session (sent 15:29)

## 1. Requirements — the owner's words

- Own app, from scratch, step by step (`MASTER_PLAN.md` journal, 2026-10-16 15:24): «слушай, я начинаю подозревать, что
  новое приложегние снуля было бы проще написать...» · «Сворачиваем план на суть C» · «Делаем по плану C».
- The model is KARTUN (15:27): «ориентируйся на KARTUN, оно классно сделано, мне нравится» · «и дизайн, и как быстро
  работает» · «можешь с агентом KARTUN проконсультироваться, правда, он не сможет тебя проконсультирвоать по работе с
  Блютуз, но UI/UX у него классный получается».
- Code quality (14:31): «пишем чистый, красивый, эффективный нативный код с комментариями, как велит КАИФ, и тестируем» ·
  in Java and Kotlin (14:36).
- Vision (`GOAL.md`): «своё приложение Krinik Tribit с фиксами от ЛЮДЕЙ ДЛЯ ЛЮДЕЙ, правильное, работающее, качественное,
  удобное»; privacy: «сервер трибит НЕ ДОЛЖЕН следить за пользователем» · «мы ПРОТИВ отслеживания метрик через Фаербейз и
  сервер Трибит»; beauty: «UI/UX нужно делать красивым» and the design-scheme rule of 11:18; success lines 1–7 (no crash,
  no location, every screen size, texts in resources, About with GitHub, README in 3 languages, one universal APK).
- Standing decisions that carry over (journal): no account; firmware check only on the user's tap (interview_001 Q2 = A);
  name limits — speaker 25, equalizer 15 (interview_002 Q4); white bold text on pink buttons (Q2 = B); a user guide in the
  app's settings with «clear data = new guest» (Q3) — in our app «no account, no guest» makes that line moot; EQ and light
  settings as JSON import/export (`ideas/01`); two builds debug/release with different keys (R6).

## 2. Local state (read 2026-10-16)

1. **`app/` scaffold** (in git since `e07e2c3`): single activity, Compose, navigation by a saved enum
   (`MainActivity.kt`), KARTUN's theme tokens and fonts (`ui/theme/Theme.kt`), `Page`/`Card`/`SettingsRow` (`ui/Screens.kt`),
   About with the GitHub links, the «Отладка» screen in debug only (`src/debug` / `src/nodebug`); versions of KARTUN
   (`gradle/libs.versions.toml`: AGP 9.4.1, Kotlin 2.4.21, Compose BOM 2026.09.00); manifest without permissions yet.
   First debug build ran on the Titan 2026-10-16 00:01 (`testcases/reports/2026-10-16_first_debug_build.md`).
2. **Package clash:** the scaffold's debug is `com.kriniks.tribit.debug` — the same as the patched Tribit's debug variant
   (`patches/apply.py` `DEBUG_PACKAGE`); one of them has to move.
3. **Protocol notes** (`researches/03` §«Что известно про протокол колонки», from `Bts52Util`): packet `EA <len> <cmd>
   <data…> <sum>`, len = data + 4, sum = low byte of the sum of the previous bytes; commands 1 version · 4 EQ (preset + 10
   bands) · 6 battery · 11 custom EQ · 12 light mode · 13 volume · 18 volume query · 21 EQ state · 52 brightness; EQ gains
   shifted +12; RFCOMM `0CF12D31-FAC3-4553-BD80-D6832E7B3119`; BLE `0000ffa0`/`ffa1`/`ffa2` — for Blast 2 corrected in §3.1 (SPP `00001101-…`).
4. **Stand:** A51 (Android 13) on USB with StormBox Blast 2 bonded and connected; the Titan belongs to KARTUN's session
   (`HOUSE_RULES.md` §3).
5. **Their behaviour observed on the A51** (reports of 2026-10-16): speaker page, settings rows, EQ «New Custom», firmware
   check on tap — the reference for our main path; their logs print speaker answers (e.g. «自动关机-- false», EXP-0009).

## 3. The speaker protocol of Blast 2 (bts56)

Recovered from the decompiled code 2026-10-16 by a delegated recon; 24 key quotes checked mechanically against the files
(`python -I work/spike/check_quotes.py`: 24 of 24 stand where cited). Paths: **J** = `decompiled/jadx-base/sources/com/thousandshores/`,
**S** = smali of `work/base/` (used where jadx broke), **B** = `J/bluetoothlib/spaker/Bts52Util.java` (Blast and Blast 2 share
it; there is no Bts56Util). VERIFIED = quote present; INFERRED = reasoned.

**3.1 Family and transport.**
- The family is chosen by the exact Bluetooth name: `J/tribit/MainNewActivity.java:1074` `if (blueName.equals("Tribit
  StormBox Blast 2")) {`. A second spelling `"TRIBIT StormBox Blast 2"` exists (`J/bluetoothlib/utils/DeviceConstant.java:62`)
  and goes down other paths — match both, case-insensitively.
- **Control channel: Classic RFCOMM on the standard SPP UUID** `00001101-0000-1000-8000-00805f9b34fb` (`S/…/BtClient.smali:11533`;
  `J/bluetoothlib/BtClient.java:590`) — NOT `0CF12D31-…` from `researches/03`. Opened by
  `createRfcommSocketToServiceRecord(uuid)` + `connect()` after cancelling discovery (`BtClient.java:686–692`).
- Reading: one `read()` of up to 1 024 bytes is taken as one packet (`J/bluetoothlib/ReadThread.java:36,43`); no framing, no
  checksum check — two replies in one read are parsed as one. On a socket error a fake packet of 10 zero bytes is injected
  and the screen reads it as «disconnected» (`ReadThread.java:88`, `Bts56ControlActivity.java:2083`).
- Finding: classic discovery + the bonded list (`DeviceSearchNewActivity.java:573` `bondedDevices()`); no BLE scan for Blast 2
  (BLE scan only for the Jieli models). «Connected» = A2DP/Headset profile connected for a bonded device named «Tribit…»
  (`J/bluetoothlib/BlueToothReceiver.java:220`); SPP is opened only then (`Bts56ControlActivity.java:1270`).
- Reconnect: not bonded → `createBond()`; bonded → connect after 200 ms; budget 3 retries (`Bts56ControlActivity.java:2109–2184`);
  a repeat connect within 5 s is ignored (`BtClient.java:189` `this.CONNECT_DEBOUNCE_MS = 5000L;`).
- BLE GATT (`0000ffa0`/`ffa1` write/`ffa2` notify) only for the DSP firmware update (`BtClient.java:1347,1570`).

**3.2 Packet.** `EA <len> <cmd> <payload…> <sum>`; `len` = payload + 4 (the whole packet); `sum` = low byte of the sum of all
previous bytes (`B:318–338`). A command without payload still carries one 0x00 byte, `len` = 5 (`B:311–312`); e.g. volume query
= `EA 05 12 00 01` (INFERRED by arithmetic). Reply: byte 2 = command, payload = bytes 3…len-2 (`B:373–376`); dispatch needs
byte 0 = 0xEA (`Bts56ControlActivity.java:2015`). Version string `p1/p2/p3_<p0/10.0>` — a DOUBLE division in smali
(`S/…/Bts52Util.smali:2191` `div-double/2addr`), jadx shows an integer one.

**3.3 Commands** (decimal; send built by **B**; every row VERIFIED unless marked):

| Feature | Send | Reply / meaning |
|---|---|---|
| Firmware version | 1 [0] (`B:37`) | string, see 3.2 (`ViewModelDeviceBts.java:708`) |
| BTS56C sub-variant | 101 (`B:307`) | payload[0] == 1 → BTS56C (`B:454`) |
| Battery % | 6 [1] (`B:41`) | 0–100 shown (`Bts56ControlActivity.java:1569`) |
| Charging state | 8 [1] (`B:45`) | value meaning not found |
| Partner (TWS) battery | 96 [0] (`B:49`) | shown when > 0 |
| Volume get / set | 18 [0] (`B:53`) / 13 [v] (`B:57`) | range 0..31 (`Bts56ControlActivity.java:1269` `setMax(31)`) |
| Play / pause / prev / next | 2 [4/3/1/2] (`B:66`; `Bts56ControlActivity.java:1054–1111`) | 3 = pause, 4 = play INFERRED; state get 19 |
| EQ preset | 4 [id, 10 gains] (`B:111–118`) | presets: 1 default, 2 XBass, 3 Audiobook, 4 Classical, 5 Rock, 6 Jazz, 7 custom, 9 Blast trad, 10 Live, 11 Podcast (`PageUtil.java:280+`); id 8 vs 9 for «Blast trad» disagrees between send and read — check on the speaker |
| EQ state get | 21 (`B:97`) | payload[0] = preset id, then gains |
| Custom EQ | 11 [10 gains] (`B:140`) | bands 40, 62, 125, 250, 500, 1K, 2K, 4K, 8K, 16K (`Bts56Constant`); wire = dB + 12 (±12 dB, new firmware) or dB + 8 (±8 dB, old) (`EqUtil.java:3241,3243`; smali `Eq56DetailActivity.smali:4621,4634` — jadx swaps them) |
| EQ button | set 71 [count, index, type, 10 gains] (`B:275`), get 72 (`B:259`) | custom slot type 0xFE |
| Light mode | 12 [1/2/3 on, 4 off] (`B:78–80`) | get 20; unsolicited 85 |
| Light colour bar/left/right | 54/55/56 [mode, R, G, B] | read 61: 3 × [mode, R, G, B, brightness] |
| Light brightness | 57/58/59 [mode, value] | value range not found |
| Light rhythm / colour mode / reset | 53 / 62, 68, 69 (1 single, 2 rotation, 3 seven-colour) / 73 | reads 67, 63, 70 |
| Auto shutdown | 3 [1 on / 2 off] (`B:158,160`) | get 16; reply 0 means ON (`Bts56InfoActivity.java:1189`) |
| Sleep timer | 14 [hour, min] (`B:148`) | off = 255, 255; get 15 |
| Voice prompts | 48 [5 flags] (`B:183`) | get 49 → «a,b,c,d,e» |
| Volume indicator | 52 [0/1] (`B:92`) | get 51 |
| Mic boost / anti-howl | 97 [0/1] / 99 [0/1] | get 98 / 100 |
| Shutdown | 50 (`B:191`) | — |
| Factory reset | 7 [1] (`B:170`) | — |
| Rename | **no Bluetooth command** | their app keeps the name in its database and syncs it to their server (`Bts56InfoActivity.java:2749`) |
| DSP version | request not found | reply 88 (`Bts56ControlActivity.java:524`) |

**3.4 Firmware generations.** «New» Blast 2 = DSP version > 10074 or BTS56C (`Bts56ControlActivity.java:527`): ±12 dB EQ, full
preset gains, mic/anti-howl rows; «old» = ±8 dB, presets as flat values. Startup sequence of their app: version → BTS56C →
charge → battery with 100/100/50 ms gaps (`J/bluetoothlib/BtClient$deviceInfo$3.java`).

**3.5 Server vs Bluetooth.** Over Bluetooth: everything in 3.3 and the preset list itself (local constants,
`EqUtil.getEqPre`). Server only: firmware and DSP update check (`api-app/api/checkFirmwareUpgrade`), the firmware file, the
product catalog and pictures, device bind/sync (where their «rename» goes), FAQ, cloud EQ.

## 4. Industry

Collected by a delegated web sweep 2026-10-16; the four lines marked ✔ were re-read on developer.android.com by me.

1. **Permissions without location.** Android 12+: `BLUETOOTH_SCAN` with `usesPermissionFlags="neverForLocation"` and
   `BLUETOOTH_CONNECT`; «If you include `neverForLocation` …, some BLE beacons are filtered from the scan results» ✔. Android
   11 and lower: «`ACCESS_FINE_LOCATION` is necessary because, on Android 11 and lower, a Bluetooth scan could potentially be
   used to gather information about the location of the user» ✔. CompanionDeviceManager scans «without requiring the
   location permission» ✔ — but «companion device pairing requires Location Services to be enabled» and «doesn't create
   connections on its own» ✔ (https://developer.android.com/develop/connectivity/bluetooth/bt-permissions,
   https://developer.android.com/develop/connectivity/bluetooth/companion-device-pairing). Already-paired devices come from
   `getBondedDevices()` (https://developer.android.com/develop/connectivity/bluetooth/find-bluetooth-devices).
2. **RFCOMM:** `cancelDiscovery()` before `connect()`; `connect()` blocks (≈ 12 s timeout) — off the main thread; always
   `close()` (https://developer.android.com/develop/connectivity/bluetooth/connect-bluetooth-devices). No discovery while
   connected (find-devices page). A2DP state through `getProfileProxy(…, BluetoothProfile.A2DP)`
   (https://developer.android.com/develop/connectivity/bluetooth/profiles).
3. **BLE GATT** (if a family needs it): one operation at a time, a queue (https://punchthrough.com/android-ble-operation-queue/);
   Nordic Android-BLE-Library, BSD-3-Clause (https://github.com/NordicSemiconductor/Android-BLE-Library).
4. **Prior art — reverse-engineered audio apps:** OpenSCQ30 (Soundcore; Rust core + Kotlin/Compose; protocol, connection
   backends incl. a mock, device models — separate layers; GPL-3.0, https://github.com/Oppzippy/OpenSCQ30), Gadgetbridge
   (AGPL-3.0, https://codeberg.org/Freeyourgadget/Gadgetbridge; JVM tests assert encoded requests as hex), FreeBuddy
   (Apache-2.0, https://github.com/TheLastGimbus/FreeBuddy; fake transport + exact frame assertions). No public Tribit
   protocol work was found (GitHub search «tribit»). Licences: we read their architecture, we copy no GPL code.
5. **Compose speed:** release build with R8 (full mode default since AGP 8.0), Baseline + Startup Profiles («about 30%»
   from the first launch), no heavy work in `Application.onCreate`, stable/immutable state, keyed lazy lists
   (https://developer.android.com/develop/ui/compose/performance,
   https://developer.android.com/topic/performance/baselineprofiles/overview,
   https://developer.android.com/topic/performance/vitals/launch-time).
6. **Anti-patterns:** connecting while discovery runs; socket I/O on the main thread; asking `ACCESS_FINE_LOCATION` on 12+;
   GATT calls without a queue; not closing the socket or the profile proxy.

## 4a. The model — KARTUN (the answer of the KARTUN session, 2026-10-16 ≈ 15:45 +03:00; every path checked by reading)

All paths under `D:\work\ai_sandbox\KARTUN` (read-only for us).

1. **Design system — copy first:** `app/src/main/kotlin/com/kriniks/kartun/ui/theme/Theme.kt` (tokens: #FF1A8C on
   near-black, Unbounded headings, Manrope text, shapes; every colour from `MaterialTheme.colorScheme`, no per-file colour
   constants) · `ui/Common.kt` (`RoundIconButton`, `PrimaryButton`, `SecondaryButton`, `Pill`, `SectionLabel` with its (i),
   `InfoButton`/`InfoDialog` — centred dialogs, never bottom sheets: the owner's word there) · `ui/SettingsScreen.kt` (rows,
   groups) · `ui/AboutScreen.kt` (`Group`/`LinkGroup` cards) · `ui/ModelsScreen.kt` (cards, badges, filter chips). Style recon:
   `researches/01_krinikcam_style_and_stack.md`.
2. **Speed:** single activity, Compose, no navigation library; heavy work off the main thread (one engine thread,
   `EngineThread.kt`); display bitmaps pre-scaled; R8 + resource shrinking in release (`app/build.gradle.kts`:
   `isMinifyEnabled = true`, `isShrinkResources = true`). No baseline profiles and no startup measurement — our app adds
   both (§4.5) and measures.
3. **Navigation:** an own tiny router — a `Screen` enum in `UpscaleViewModel.kt`, `back()` maps a screen to its parent,
   `MainActivity.kt` switches on it, `BackHandler` per screen; `enableEdgeToEdge` + `WindowInsets.systemBars` /
   `statusBarsPadding` / `navigationBarsPadding` per screen. Our scaffold already follows it (`MainActivity.kt`, `Page`).
4. **User guide:** `ui/ManualScreen.kt` renders `res/raw/manual.md` (`raw-ru/`) with a small markdown of its own; lesson —
   plan the screenshots in from day one with a shooting tool.
5. **Rakes not to repeat:** EXP-0024 (a tap script pressed into the owner's other app — `tools/titan-tap.mjs` refuses
   unless our app is focused); EXP-0030 (screen-off tests lock the owner's device — run last, check the keyguard); EXP-0027
   (heredocs eat backslashes — write scripts with the file tool; our EXP-0007 is the same class); a padding computed from an
   unmeasured size went negative and crashed (`ResultScreen.kt` «Never below zero»); the owner's word goes into a comment
   next to the code.
6. **Tooling:** the UI agent (`C:\Android\private\ui-agent\`, one quoted string per command, SDK platform-tools first in
   PATH); WebP shots (R4); mock-ups `design/*.html` shot by `tools/shoot-mockups.mjs`; README shots `tools/shoot-readme.mjs`.
   Stand: the A51 is entirely ours (KARTUN does not support Android 13); KARTUN uses the Titan at `100.99.111.48:5555`.

## 5. Findings → implications → forks

**Findings.**
1. Blast 2 is controlled entirely over Classic SPP with a small, now documented packet format; nothing on the main path needs
   Tribit's server (§3.5). Only firmware does.
2. Their Bluetooth layer has defects our app must not copy: no framing and no checksum check (§3.1, §3.2), the 10-zero packet
   used as a disconnect signal, discovery on a path that needs location.
3. Location: on Android 12+ a `neverForLocation` scan; on 8–11 only bonded devices work without location (§4.1). Blast 2 is
   an A2DP speaker — the user pairs it in the phone's Bluetooth settings anyway, and their app opens SPP only for a
   bonded, A2DP-connected device (§3.1).
4. The architecture of the mature open apps (§4.4): transport · protocol codec · device model · UI as separate layers, a
   fake transport and byte-exact tests on the JVM.

**Implications for the epic.**
1. Layers: `transport` (SPP socket on its own coroutine, reader that frames by `len`, writer queue, `close()` always) ·
   `protocol` (pure Kotlin codec of §3.2–3.3, JVM tests with byte fixtures) · `device` (Blast 2 model: firmware generation,
   EQ ±12/±8, presets) · `ui` (Compose on the scaffold, KARTUN's tokens).
2. The main path: list bonded «Tribit StormBox Blast 2» devices (both spellings) → open SPP when A2DP is connected → the
   startup queries of §3.4 → the speaker page. No location permission on any API level; a Blast 2 that is not paired gets
   a hint to pair it in Bluetooth settings (Android 8–11) or a `neverForLocation` scan (12+).
3. Fixtures from the real speaker: their debug app on the A51 logs speaker answers (EXP-0009), and our own app logs every
   frame in debug — captured frames become the protocol tests.
4. Rename: there is no speaker command — a name in our app is a local label only (fork below).
5. Speed: R8 release, Baseline/Startup Profiles, nothing heavy at start — measured like KARTUN (its answer pending).

**Open forks for the owner** (→ `interviews/`):
1. Rename: a local label in our app only (the speaker keeps its own Bluetooth name) — or drop the rename row.
2. Android 8–11 without location: bonded devices only (pair in system settings) — accepted, or also offer the CDM path
   that needs the system Location toggle on.
3. The scaffold's «От людей для людей» title against the owner's earlier «сделано людьми для людей - убрать».
