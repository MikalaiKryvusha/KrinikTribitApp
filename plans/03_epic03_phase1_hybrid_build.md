# План 03.1 — фаза 1 эпика 03: гибридная сборка, первый класс Tribit на Java

> **Создан:** 2026-10-16 · **Родитель:** `plans/03_EPIC_java_source.md`, строка фазы 1: «`native/src/` + шаг `build.sh`:
> Java Tribit-классов компилируется против classpath приложения, dex добавляется, smali этих классов удалён» ·
> **Статус:** шаги 1–6 выполнены 2026-10-16 15:01 +03:00 (`testcases/reports/2026-10-16_patch31_32.md` п. 19); фаза ждёт проход судьи · **Вовне:** —

## Вектор цели и приёмка

Класс Tribit живёт в `native/src/` исходником Java и собирается в APK, его smali нет (Achieve).

- **Приёмка** (критерии 1 и 4 эпика): `native/src/com/thousandshores/tribit/modulemine/activity/AboutActivity.java` есть,
  `git -C native ls-files "*AboutActivity.smali"` пусто; A51 debug: «О приложении» показывает версию, «Copyright © 2026
  Thousandshores…» и ссылку на GitHub; путь главный → колонка → настройки без вылетов (`logcat -b crash` — 0 строк).

## Шаги

- [x] 1. `tools/gen_r.py` (из `work/spike/gen_r.py`): R-классы пяти пакетов Tribit из `native/res/values/public.xml` —
      только для компиляции, в APK не идут (R8 вписал ID в код Tribit, своих R-классов в APK нет).
- [x] 2. `build.sh`: после `apktool b` — jar классов собранного APK (`d2j-dex2jar`) как classpath; `javac` для
      `native/src/**/*.java` и `patches/java/**/*.java` вместе против `android.jar` + этого jar + R; d8 с `--classpath`.
- [x] 3. Страж в `build.sh`: класс из `native/src/` при живом smali того же имени (вместе с `$`-вложенными) — сборка падает
      с именем класса (Android берёт первую копию класса, `researches/10` §4 п. 5). Проверить стража на сломанной
      версии: smali на месте → красный.
- [x] 4. `AboutActivity` на Java: чистая версия поведения сегодняшней сборки (версия, GitHub, копирайт), smali удалён в
      коммите `native/`.
- [x] 5. `tools/native_src_count.py` — счётчик переноса: классы `com/thousandshores` исходником / всего.
- [x] 6. Сборка debug, A51: «О приложении» + путь критерия 4; отчёт в `testcases/reports/`.

## Риски

- `javac` видит в jar старый `AboutActivity` — исходник имеет приоритет над classpath (компилятор берёт класс из
  компилируемых файлов); в dex идёт только наш.
- Новые ресурсы `native/` (например `krinik_guide`) не в `public.xml` — исходники фазы 1 ссылаются только на ресурсы из
  `public.xml`; ID новых ресурсов — задача фазы 3.
