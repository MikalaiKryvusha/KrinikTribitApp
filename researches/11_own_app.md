# Research 11 — our own Krinik Tribit app: requirements, the speaker protocol, the industry

> **Created:** 2026-10-16 (the owner, chat 15:24 +03:00: «Сворачиваем план на суть C» · «Делаем по плану C») ·
> **Parent:** `MASTER_PLAN.md` phases 2–3, `researches/03` (protocol notes), `researches/08` (beauty), `researches/10`
> (tools for reading their code) · **Status:** rung 1 of `/plan-epic` for `plans/04_EPIC_own_app.md`; requirements and local
> state written 2026-10-16 ≈ 15:35 +03:00; protocol recon and industry sweep delegated, pending; KARTUN's answer pending ·
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
   shifted +12; RFCOMM `0CF12D31-FAC3-4553-BD80-D6832E7B3119`; BLE `0000ffa0`/`ffa1`/`ffa2`. To be verified for bts56.
4. **Stand:** A51 (Android 13) on USB with StormBox Blast 2 bonded and connected; the Titan belongs to KARTUN's session
   (`HOUSE_RULES.md` §3).
5. **Their behaviour observed on the A51** (reports of 2026-10-16): speaker page, settings rows, EQ «New Custom», firmware
   check on tap — the reference for our main path; their logs print speaker answers (e.g. «自动关机-- false», EXP-0009).

## 3. The speaker protocol of Blast 2 (bts56)

Pending — delegated code recon with verbatim quotes, mechanically checked before use.

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

## 5. Findings → implications → forks

Pending.
