# Прогон 2026-10-16 — release своего приложения: R8, подпись, холодный старт

## 1. Work

Критерий 4 эпика `plans/04_EPIC_own_app.md` (холодный старт не медленнее KARTUN — 522 мс на Титане, `researches/11` §4a.7);
слово владельца ≈ 17:27 +03:00: «ключ подписи релиз сборки в .env, вне гита» · «и релиз зборки обязатно в R8»
(`HOUSE_RULES.md` R6, пункты 4–5).

## 2. Contour

`app/build/outputs/apk/release/app-release.apk` (R8 + сжатие ресурсов, ключ `keys/krinik-tribit-app-release.jks`, путь и
пароли — `.env`, всё вне git) → Samsung A51, Android 13, `R58N615KXZZ`; рядом стоит `com.kriniks.tribit.debug`. Колонка Blast 2.

## 3. Runs

1. 17:26 — `.\gradlew.bat assembleRelease`: 2 200 326 байт (без R8 — 23 429 781 байт, сборка 17:25).
2. 17:26 — `adb install -r app-release.apk`; `am start -S -W -n <пакет>/com.kriniks.tribit.MainActivity` трижды для release и
   трижды для debug.
3. 17:27 — release: «Разрешить» → системное окно «Разрешить» (путь пользователя), карточка колонки.
4. 17:28 — после переноса ключа в `.env`: `keystore.properties` удалён, APK удалён и собран заново; `apksigner verify --print-certs`.

## 4. Checks

- Hygiene: сборка release зелёная; подпись `CN=Krinik Tribit, O=Krinik` у APK 17:28:46, собранного только из `.env`.
- Functional run: прочитаны `TotalTime` и экран release.
  1. Холодный старт release: 870 мс (первый запуск после установки — система ещё компилирует код), 419 мс, 430 мс; debug —
     1 741, 1 742, 1 694 мс. 419–430 мс на A51 меньше 522 мс KARTUN на Титане (устройства разные) — pass с этой оговоркой.
  2. Release с R8 подключается к колонке: «Заряд: 30 %», «Громкость: 9 из 31»; `logcat -b crash` — 0 строк — pass
     (`1_release_connected.webp`).
- Не проверено: release на Титане (то же устройство, что у KARTUN); Baseline Profile; эквалайзер и настройки в release.

## 5. Found

none

## 6. Traces

`testcases/reports/2026-10-16_release_speed/1_release_connected.webp`.

## 7. Verdict

pass — release с R8 подписан ключом из `.env`, стартует за 419–430 мс и работает с колонкой; сравнение с KARTUN — на разных
устройствах.
