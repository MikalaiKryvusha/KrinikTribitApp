# Прогон 2026-10-16 — два пакета на A51: своё приложение и запасной путь

## 1. Work

Разведение пакетов по слову владельца ≈ 15:53 +03:00 («com.kriniks.tribit.debug - так будет называться НАШЕ приложение,
починеное можно переименовать в олд», `MASTER_PLAN.md` журнал; `HOUSE_RULES.md` R9 п. 5): оба debug стоят рядом на одном
телефоне и открываются.

## 2. Contour

ПК владельца (Windows 11, JDK 21) → Samsung A51 SM-A515F, Android 13, `R58N615KXZZ` по USB; колонка Blast 2 сопряжена и
подключена по A2DP (`dumpsys bluetooth_manager`: «(Connected) … Tribit StormBox Blast 2 (00001101-…)»).
Сборки: `out/KrinikTribit-debug.apk` (16:06, 65 771 197 байт), `app/build/outputs/apk/debug/app-debug.apk` (15:47).

## 3. Runs

1. 2026-10-16 16:04–16:06 +03:00 — `bash build.sh debug` → `built: out/KrinikTribit-debug.apk`; `aapt2 dump badging` →
   `package: name='com.kriniks.tribit.old'`, `application-label:'Old Krinik Tribit'`.
2. 16:05 — `.\gradlew.bat assembleDebug --console=plain` → BUILD SUCCESSFUL (up-to-date с 15:47).
3. 16:06 — `adb -s R58N615KXZZ uninstall com.kriniks.tribit.debug` (старый запасной путь) → Success; `install -r` обоих
   APK → Success; `pm list packages` → `com.kriniks.tribit.debug`, `com.kriniks.tribit.old`.
4. 16:07 — `monkey -p com.kriniks.tribit.old -c android.intent.category.LAUNCHER 1`, затем `am start -n
   com.kriniks.tribit.debug/com.kriniks.tribit.MainActivity`; снимки `exec-out screencap | magick … .webp`.

## 4. Checks

- Hygiene: обе сборки зелёные; пакет и подпись запасного пути сверены `aapt2`.
- Functional run: на A51 открыты оба приложения, прочитаны `topResumedActivity` и два снимка.
  1. `com.kriniks.tribit.old` — стартовый экран «KRINIK TRIBIT», кнопка START (`FirstNewActivity`) — pass.
  2. `com.kriniks.tribit.debug` — главный экран своего приложения (`com.kriniks.tribit.MainActivity`) — pass.
  3. `logcat -b crash` — строк с `kriniks` нет — pass.
- Не проверено: путь запасного пути дальше стартового экрана; подпись «Old Krinik Tribit» ждёт подтверждения владельца.

## 5. Found

1. Своё приложение: заголовок карточки «Колонка не подключена» чёрный на тёмной карточке — у `Text` без цвета вне
   `Surface` цвет содержимого по умолчанию чёрный. Исправляется в фазе 1 (`plans/05` шаг 5): `Card` задаёт цвет содержимого.
2. Своё приложение: текст неактивной кнопки «Поиск колонки появится в следующей сборке» обрезан второй строкой в высоте
   52 dp. Кнопка уходит в шаге 5.

## 6. Traces

`testcases/reports/2026-10-16_two_packages/1_old.webp`, `2_own.webp`.

## 7. Verdict

pass — оба пакета стоят рядом и открываются; два дефекта вёрстки своего приложения записаны и идут в шаг 5 `plans/05`.
