# Прогон 2026-10-16 — первая debug-сборка Krinik Tribit на Титане

## 1. Work

Первая сборка своего приложения (слово владельца 2026-10-16 ≈ 00:00 +03:00: «и попробуйте собрать stage первую
сборку» · «debug вернее, не стейдж» · «стейджа не будет у нас»); основа проверки — правило R6 `HOUSE_RULES.md` (название
«Debug Krinik Tribit», кнопка отладочного раздела в настройках) и строка 3 успеха `GOAL.md` (экран целиком на планшете).

## 2. Contour

ПК владельца (Windows 11, JDK 21, Gradle 9.8.1, AGP 9.4.1) → APK `app/build/outputs/apk/debug/app-debug.apk`
(12 045 357 байт) → планшет HEADWOLF Titan 1, Android 16 (API 36), `192.168.1.3:5555`, масштаб 480 dpi поверх панели 320 dpi,
язык ru-BY. Колонка не участвовала: поиска колонки в сборке нет.

## 3. Runs


1. 2026-10-16 00:01 +03:00 — `.\gradlew.bat assembleDebug --console=plain` (PowerShell, `JAVA_HOME` = JDK 21,
   `GRADLE_USER_HOME=C:\Android\gradle-home`): BUILD SUCCESSFUL in 42s.
2. 00:01 — `aapt2 dump badging`: пакет `com.kriniks.tribit.debug`, `application-label:'Debug Krinik Tribit'`,
   `native-code: 'arm64-v8a' 'armeabi-v7a' 'x86' 'x86_64'`.
3. 00:02 — `adb -s 192.168.1.3:5555 install -r …app-debug.apk` → `Success`; `am start -n
   com.kriniks.tribit.debug/com.kriniks.tribit.MainActivity`; `pidof` → 18637.
4. 00:02 — касания: «Настройки» (`input tap 256 1242`), «Отладка» (`input tap 400 660`, место из `uiautomator dump`);
   перед касанием — проверка, что сверху приложение Krinik Tribit (`dumpsys activity activities`).

## 4. Checks


- Hygiene: сборка Gradle зелёная; метка и пакет APK сверены `aapt2`.
- Functional run: пройден путь пользователя на Титане — запуск → главный экран → «Настройки» → «Отладка»; прочитаны три
  снимка экрана.
  1. Главный экран: заголовок «Krinik Tribit», карточка «Колонка не подключена» с честной кнопкой «Поиск колонки появится в
     следующей сборке» (неактивна), карточка «От людей для людей», строка «Настройки»; кириллица и шрифты Unbounded/Manrope
     на месте — pass.
  2. «Настройки»: строки «О приложении» и «Отладка» (кнопка отладочного раздела по правилу R6) — pass.
  3. «Отладка»: сборка `com.kriniks.tribit.debug · 0.1 (1) · debug`, Android 16 (API 36), HEADWOLF Titan 1, arm64-v8a,
     экран 533 × 853 dp · 1600 × 2560 px, плотность 480 dpi при панели 320 dpi, ru-BY — pass.
- Не проверено: экран «О приложении» и переход по ссылкам GitHub; альбомная ориентация; сборка `release` и её подпись;
  установка на 32-битное и x86-устройство.

## 5. Found

Дефектов приложения нет. Грабля стенда: Git Bash переписывает путь устройства `/sdcard/…` в путь Windows —
лечится `MSYS_NO_PATHCONV=1` (`HOUSE_RULES.md` §4).

## 6. Traces

`testcases/reports/shots/2026-10-16_home.webp`, `…_settings.webp`, `…_debug.webp`.

## 7. Verdict

Partial — путь главный экран → настройки → отладка пройден на Титане; «О приложении», альбомная ориентация и
`release` не проверены.
