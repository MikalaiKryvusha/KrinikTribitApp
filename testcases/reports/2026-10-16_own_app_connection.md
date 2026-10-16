# Прогон 2026-10-16 — своё приложение подключается к Blast 2

## 1. Work

Фаза 1 эпика 04, `plans/05_epic04_phase1_connection.md`: критерии приёмки 1–4 и строки инвентаря (версия, заряд, громкость,
воспроизведение). Основа ожиданий — протокол из кода Tribit (`researches/11_own_app.md` §3), строка 2 успеха `GOAL.md`.

## 2. Contour

ПК владельца (Windows 11, JDK 21, Gradle 9.8.1) → `app/build/outputs/apk/debug/app-debug.apk` (`com.kriniks.tribit.debug`)
→ Samsung A51 SM-A515F, Android 13, `R58N615KXZZ` по USB → колонка StormBox Blast 2 `AC:B1:EE:89:B5:37`, сопряжена и
подключена по A2DP. Геолокация на A51 включена (`location_mode` = 3): приложение её не запрашивает, разрешений геолокации в
пакете нет. Запасной путь `com.kriniks.tribit.old` остановлен (`am force-stop`).

## 3. Runs

1. 16:12–16:20 +03:00 — `.\gradlew.bat assembleDebug testDebugUnitTest --console=plain`, `adb -s R58N615KXZZ install -r …`.
2. 16:17 — `am start -S -n com.kriniks.tribit.debug/com.kriniks.tribit.MainActivity`; касание «Разрешить» (540, 698), в
   системном окне «Разрешить» (540, 2071) — координаты из `uiautomator dump`; `logcat -s KT.Link:D`.
3. 16:17:51 — касание ползунка громкости на отметке 10 (386, 605).
4. 16:18:15 и 16:18:30 — «Играть», затем «Пауза» (540, 762).
5. 16:19–16:20 — открыть, «Домой», открыть, «Назад»; последний билд — открыть, «Назад».

6. 16:27–16:29 — `cmd location set-location-enabled false` → `is-location-enabled` false; `am start -S`; журнал `KT.Link` и
   `logcat --pid` с `StrictMode` (debug); после исправления находки 4 — повтор; `set-location-enabled true` → true.
7. 16:29–16:31 — «Old Krinik Tribit»: START → разрешение «Устройства поблизости» → «Нет» на уведомления → «Tap to Add Device» →
   «Go to Connect» → экран колонки «30%» (канал SPP у него); открыть наше приложение; затем `am force-stop
   com.kriniks.tribit.old` и «Подключить» (540, 756).

Перед каждым касанием — проверка, что сверху `com.kriniks.tribit.debug` (`dumpsys activity activities`).

## 4. Checks

- Hygiene: `testDebugUnitTest` — 16 из 16 (PacketTest 8, Blast2Test 5, SpeakerFramesTest 3); тест нарезчика покраснел на
  мутанте «одно чтение — один пакет» и позеленел на исходнике.
- Functional run: путь пользователя на A51 с настоящей колонкой, прочитаны журнал `KT.Link` и семь снимков.
  1. Без разрешения — карточка «Доступ к колонке», кнопка «Разрешить» — pass (`1_permission.webp`).
  2. Системное окно «Устройства поблизости» → «Разрешить» → `BLUETOOTH_CONNECT: granted=true`; других разрешений в пакете нет — pass.
  3. Подключение за 0,5 с (`connecting` 16:17:30.204 → `connected` 16:17:30.707); карточка «Tribit StormBox Blast 2»,
     «Заряд: 30 %», «Громкость: 9 из 31» — pass (`3_connected.webp`).
  4. Громкость 10: `TX EA 05 0D 0A 06`, ответ `RX EA 05 0D 0A 06 EA 05 54 0A 4D` (два пакета одним чтением), повторный запрос
     `RX EA 05 12 0A 0B`; экран «Громкость: 10 из 31»; системная шкала громкости телефона сдвинулась вместе — pass
     (`4_volume.webp`). Громкость на слух не проверена.
  5. «Играть»: `RX EA 05 02 04 F5`, состояние 19 → 1, кнопка стала «Пауза»; «Пауза»: `RX EA 05 02 03 F4`, состояние 19 → 2 —
     pass (`5_play.webp`, `6_pause.webp`). Плеера на телефоне не было, звук не шёл (`mIsPlaying: false`).
  6. «Домой» и «Назад» закрывают связь (`closed`), возврат подключает вновь — pass после исправления (находка 2).
  7. Контрольные суммы всех ответов колонки сошлись с правилом `researches/11` §3.2: строк `checksum mismatch` нет.
  8. `logcat -b crash` — строк с `kriniks` нет.
  9. Геолокация телефона выключена: подключение 16:27:21.699, заряд пришёл; разрешений геолокации в пакете нет — pass
     (`8_location_off.webp`).
  10. `StrictMode` (debug): после исправления находки 4 — 0 строк `StrictMode` у процесса приложения — pass.
  11. Канал SPP держит «Old Krinik Tribit»: наш `connect()` получил отказ за 83 мс (16:30:39.079 → `closed` .162), карточка
      «Связь с колонкой не установлена или прервалась… закройте его.» с кнопкой «Подключить» — pass (`9_busy_channel.webp`).
      После закрытия запасного пути «Подключить» → `connected` за 0,7 с, заряд пришёл — pass (`10_after_retry.webp`).
- Не проверено: выключенный Bluetooth; несопряжённая колонка; отказ в разрешении.

## 5. Found

1. Тексты карточек были написаны без портрета владельца, в том числе «Геолокация не нужна.» и карточка «Без геолокации, без
   аккаунта…». Владелец отверг их в 16:12. Тексты переписаны по `AUTHOR_STYLOMETRY.md`, проверены `kaif-voice-lint check`
   (0 попаданий) и проходом §7B субагентом (5 правок); правило — `HOUSE_RULES.md` R10.
2. После «Назад» сокет оставался открытым: с Android 12 «Назад» на корневом экране уводит приложение в фон, `onCleared` не
   вызывается. Исправлено: `MainActivity.onStop` → `SpeakerViewModel.stop()`.
3. Колонка сама присылает команду 84 со значением громкости (`EA 05 54 0A`) и команду 85 (`EA 05 55 04`, подсветка по
   `researches/11` §3.3). Пока приложение их только пишет в журнал; строки инвентаря фазы 2.
4. `StrictMode`: первый `getSystemService(BluetoothManager)` читает диск в главном потоке — 114 и 117 мс. Исправлено: поиск
   адаптера и сопряжённой колонки (`SpeakerViewModel.lookUp`) идёт на `Dispatchers.IO`.

## 6. Traces

`testcases/reports/2026-10-16_own_app_connection/` — `1_permission.webp`, `2_system_dialog.webp`, `3_connected.webp`,
`4_volume.webp`, `5_play.webp`, `6_pause.webp`, `7_final.webp`, `8_location_off.webp`, `9_busy_channel.webp`,
`10_after_retry.webp`; кадры колонки — `app/src/test/…/SpeakerFramesTest.kt`.

## 7. Verdict

partial — исправлено 2026-10-16 17:17 по проходу судьи (было «pass»): критерии 1, 3, 4 и шаг 7 `plans/05` наблюдались на A51
с настоящей колонкой; критерий 2 — по ответу колонки и шкале телефона, «громче или тише на слух» не наблюдалось.
