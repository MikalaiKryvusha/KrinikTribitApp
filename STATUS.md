# Krinik Tribit — текущий статус

> Главный документ передачи работы следующей сессии: читай перед каждой задачей, обновляй при каждом значимом
> изменении. STATUS — сводка «сейчас»; закрытое переезжает дословно в `PROJECT_HISTORY.md`.
> Принцип мышления — `PHILOSOPHY.md`; рабочий канон — `AGENT_GUIDE.md`; стенд и правила владельца — `HOUSE_RULES.md`.

Последняя сессия: 2026-10-16 13:47 — 15:4x +03:00 (resume → патчи 31–36 → нативный код в приватном `native/` → эпик
«код Tribit на Java» → решение владельца 15:24 «Делаем по плану C»: своё приложение с нуля), закрыта мягко по слову
владельца 15:36 «нужно будет через 10 минут доводить до логического среза, и передавать работы в новый чат». Подробности
сессии — `PROJECT_HISTORY.md`, запись 13:47.

Неисправленные ложные утверждения: нет. Исправлены на месте: «закрыта мягко по таймеру часа» в шапке STATUS (сессия
продолжилась по слову «продолжаем работу, не закрываем чат»); «ни одной догадки» у чистильщика `$default` — строковые
значения по умолчанию угадывались (`joinToString`), исправлено в `tools/kotlin_defaults.py` и в `plans/03_epic03_phase2…`;
контраст «2,3 и 6,4» в комментарии патча 31 (посчитано: 2,61 и 6,73).

---

## Первым делом в новом чате

**Эпик 04 — своё приложение Krinik Tribit с нуля** (`MASTER_PLAN.md`, вариант C; образец — KARTUN по дизайну и
скорости). Идёт первая ступень `/plan-epic` — разведка `researches/11_own_app.md`:

1. **§3 «Протокол Blast 2» пуст.** Разведку протокола семейства `bts56` по коду Tribit (транспорт, UUID, формат пакета,
   таблица команд с дословными цитатами `файл:строка`) вёл субагент закрытой сессии — его отчёт пропал вместе с ней.
   Повторить: читать `decompiled/jadx-base/sources/com/thousandshores/tribit/moduledevice/bts56/`,
   `…/viewmodel/ViewModelDeviceBts`, `…/bluetoothlib/`; опора — `researches/03` §«Что известно про протокол колонки»;
   каждую цитату сверить скриптом с файлом.
2. **Ответ агента KARTUN.** Вопросы по UI/UX (дизайн-система, скорость, навигация, руководство, ошибки, инструменты
   снимков) ушли 15:29 сессии `kartun-1a` с адресом ответа `kriniktribit-7d` — эта сессия закрыта. Новый чат: спросить
   заново (`SendMessage` к живой сессии KARTUN из `ListAgents`) или прочитать код KARTUN сам (`D:\work\ai_sandbox\KARTUN`,
   только чтение): `app/src/main/kotlin/com/kriniks/kartun/ui/` — `AboutScreen.kt`, `ManualScreen.kt`, `Common.kt`.
3. **§5 выводы и развилки → мета-план `plans/04_EPIC_own_app.md`** (вектор цели, критерии, фазы: разведка → главный путь
   на Blast 2 → красота → прошивка и модели → релиз), закоммитить до кода; затем план первой фазы.
4. **Решить до первой сборки своего приложения:** debug каркаса и debug запасного пути — один пакет
   `com.kriniks.tribit.debug` (`app/build.gradle.kts` и `patches/apply.py` `DEBUG_PACKAGE`); предложение — пакет запасного
   пути переименовать.
5. **Вопрос владельцу (в `interviews/`):** на главном экране каркаса заголовок «От людей для людей»
   (`app/src/main/res/values-ru/strings.xml`), а в комментарии патча 17 записано слово владельца «сделано людьми для людей -
   убрать» (о тексте их приложения) — оставить ли его в своём приложении.

## Где мы сейчас

- **Своё приложение** — `app/` (Kotlin + Compose, в git с `e07e2c3`): один экран-активность, тема и шрифты KARTUN,
  «О приложении», «Отладка» только в debug; Bluetooth ещё нет. Первая сборка была на Титане 2026-10-16 00:01.
- **Запасной путь — починенный Tribit** (`MASTER_PLAN.md` фаза 1 ✅): исправления 1–36 плюс нативные правки живут в
  `native/` (приватный `MikalaiKryvusha/KrinikTribitNative`, `HOUSE_RULES.md` R9); `bash build.sh debug|release` собирает из
  него; на A51 стоит debug 15:11. Чек-лист жалоб — `plans/02`. Новые функции туда не идут, только блокирующие исправления.
- **Инструменты чтения кода Tribit** (`researches/10`, свёрнутый эпик `plans/03`): jadx-выгрузка `work/jadx-gradle`, jar
  классов `work/spike/tribit-all.jar` (dex2jar), `tools/gen_r.py`, `tools/decompile_clean.py` (вызовы Kotlin `$default`),
  гибридная сборка Java-классов Tribit в `native/src/` (`AboutActivity` — первый, счётчик `tools/native_src_count.py`).
- **Отраслевые выводы для своего приложения** (`researches/11` §4): Android 12+ — поиск с `neverForLocation`; Android
  8–11 — без геолокации только уже сопряжённые колонки (`getBondedDevices`); RFCOMM — `cancelDiscovery()` до `connect()`,
  ввод-вывод не в главном потоке; образцы устройства кода — OpenSCQ30, Gadgetbridge; скорость — Baseline Profiles, R8.
- **Стенд:** A51 по USB (`R58N615KXZZ`) с колонкой StormBox Blast 2; Титан отдан сессии KARTUN.
- **KAIF** 2.8 + предрелиз 2.9; хуки «⏩» сняты — `wire-hooks` **не запускать** (`AGENT_GUIDE.md` → Notes from the human).

## Где продолжить (после «Первым делом»)

1. **Как гонять стенды** — `HOUSE_RULES.md` §3 и §6. A51: `C:\Android\Sdk\platform-tools\adb.exe -s R58N615KXZZ`, UI-агент
   на порту 8379, `KT_SERIAL=R58N615KXZZ KT_PORT=8379 python testcases\snap.py …`. **Голый `adb` не вызывать** (EXP-0006).
   Перед сборкой оболочка не стоит внутри `work/`. Перед коммитом — `python -I tools/check_ctrl_chars.py` и
   `python -I tools/check_tested_ticks.py`. Текст с обратной косой чертой — только через файлы (EXP-0007: в этой сессии
   страж поймал его дважды).
2. **Git:** одна команда — одно действие (`HOUSE_RULES.md` R8); `native/` — свой репозиторий: `git -C native …`.
3. **Сборка своего приложения:** `.\gradlew.bat assembleDebug` (PowerShell, `JAVA_HOME` = JDK 21,
   `GRADLE_USER_HOME=C:\Android\gradle-home`; `testcases/reports/2026-10-16_first_debug_build.md`).
4. **Права:** `.claude/settings.local.json` (вне git) разрешает adb из SDK и скрипты стенда; `reboot`, `tcpip`, `kill-server`
   запрещены.

## ❓ Ждёт владельца

- Название на ярлыке: «KRINIK TRIBIT» заглавными или «Krinik Tribit» (R3, R6)?
- Принять `GOAL.md`, `MASTER_PLAN.md` (пометки `[AI]`); вычитать README.
- Релиз: публиковать ли в GitHub APK запасного пути, в котором код компании Tribit?
- Лицензия репозитория (у KARTUN — MIT)?

## Открытые баги (запасной путь)

- `bugs/01_eq_custom_preset_name_and_list.md` — свой пресет EQ: второй вытесняет первый. 🔴 OPEN.
- `bugs/02_autooff_switch_shows_on_before_speaker_answers.md` — «Автоматическое выключение» показано включённым, пока
  колонка не ответила. 🔴 OPEN, S2.
- `bugs/03_tls_accepts_any_certificate.md` — TLS их клиента принимал любой сертификат (S1). 🔧 исправление 30 включено;
  отказ поддельному сертификату не наблюдался.
- Остальные дефекты запасного пути — `plans/02_play_complaints_checklist.md` → «Баги проекта».
