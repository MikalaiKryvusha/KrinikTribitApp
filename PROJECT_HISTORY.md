# Krinik Tribit — Project History (the chronicle)

> The APPEND-ONLY chronicle of how this project lived and grew: closed sessions, shipped phases,
> releases, big decisions in the order they happened. This is where `STATUS.md` sheds its past —
> STATUS stays a short live summary of NOW; everything finished moves HERE (the "bonsai trim" step
> of `/end-chat-soft`).
>
> **Not required reading.** This file is NOT part of `/resume`'s canon set and not in the
> before-every-task minimum — open it only when you actually need the archaeology: how a decision
> came to be, what an old phase contained, when something shipped.
>
> **Chronicle rules (ADR discipline):**
> - **Append-only, newest on top.** A recorded entry is never edited to say something else —
>   history that can be rewritten is not history. Corrections come as NEW entries that reference
>   and supersede the old one.
> - An entry moves here VERBATIM from `STATUS.md` when its work closes — move, don't rewrite;
>   the entry already carries its dates, counters and file pointers.
> - Entries mention versions and dates freely — a chronicle legitimately speaks of old versions,
>   and the update machinery's stale-claims scan knows to leave this file alone.
> - When the file grows unwieldy, split by era: keep the newest era here, move older ones to
>   `PROJECT_HISTORY_<era>.md` files, and leave a one-line index at the top of this file
>   (the pattern large changelogs use).
>
> Living document — never DONE-tagged.

---

## Entries (newest first)

### 2026-10-15 23:0x–23:3x +03:00 — сессия форка: шесть патчей Tribit 5.0.0, разведка, статус до KAIF ✅

Перенесено дословно из `STATUS.md` (коммит `ec4de5f`) при развёртывании KAIF 2026-10-15; пути `research/…` с тех пор переехали: `research/play-reviews.md` → `researches/01_play_reviews.md`, `research/languages.md` → `researches/02_languages.md`, `research/pains.md` → `researches/03_tribit_app_pains.md`, `research/test-plan.md` → `testcases/TC_fork_titan.md`.

````markdown
# Krinik Tribit — статус

> Форк официального приложения Tribit (`com.thousandshores.tribit` 5.0.0, versionCode 5000) под себя:
> чиним крэши, обрезанный интерфейс, обязательную геолокацию, переводы. Правки — мелкие патчи smali и
> ресурсов через apktool. Репозиторий: https://github.com/MikalaiKryvusha/KrinikTribitApp (публичный).

Сессия: 2026-10-15 23:0x–23:3x +03:00, закрыта по слову владельца «закрываем чат» (фильтр безопасности
Anthropic мешал работе в этом чате).

---

## Где мы сейчас

**Собрана и подписана первая сборка**, на устройство ещё НЕ ставилась. Всё, что ниже — `[NOT-TESTED]`:
проверено только тем, что apktool собрал APK и apksigner принял подпись.

Готово в `patches/apply.py` (6 патчей, каждый ищет якорь по точному тексту и падает с exit 1, если якоря нет):

1. **Крэш эквалайзера.** `EqUtil.getUnnameEq` делила имя пресета по «-» и читала `[1]` без проверки длины →
   `IndexOutOfBoundsException: Index: 1, Size: 1` при нажатии «создать свой EQ». Патч: такие имена пропускаются.
   Источник: `diagnostics/crash-2026-10-15.txt`, 7 одинаковых падений 21:49–21:50.
2. **Геолокация не требуется — ПОЛОВИНА РАБОТЫ.** `PairHelper.getMustType()` возвращал `["GPS","Bluetooth"]`;
   теперь только `["Bluetooth"]`, а `getGpsEnabled()`/`getLocationEnabled()` возвращают `true`. Это снимает
   заслон в трёх экранах разрешений (`PermissionActivity:373`, `PermissionNewActivity:374`,
   `CheckSearchConditionActivity:400` — там `checkToActivity()` пускал дальше только при `getMustEnable()`).

   **⚠ Второй заслон, ещё НЕ снят** (нашёл субагент-ревизор, цитаты проверены): встроенная библиотека
   `com.bhm.ble` сама отказывается сканировать при выключенной геолокации —
   `BleScanRequest.java:140`: `if (!bleUtil.isGpsOpen(...) && needCheckGps) { ... callScanFail(GPSDisable); return; }`,
   без всякой проверки версии Android. Включает это сам Трибит: `TribitApp.java:229` —
   `.setNeedCheckGps(true)`. Поиск колонки (`BtClient.bleScan` → `DeviceSearchNewActivity:366`,
   `DeviceSearchingActivity:400`) упирается именно сюда. **Патч 7 в новом чате:** поменять в smali
   `TribitApp` аргумент `setNeedCheckGps` с `true` на `false` (ищи `invoke-virtual ... setNeedCheckGps`,
   перед ним `const/4 vN, 0x1` → `0x0`). Без этого на планшете без GPS колонка по-прежнему не найдётся.

   Заодно: в манифесте `ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION` объявлены без `maxSdkVersion`
   (строки 53–58), поэтому старая логика жива и на Android 12+; экраны `CheckSearchConditionActivity:326`
   и `PermissionNewActivity:136` ещё и просят эти разрешения через XXPermissions — после патча 7 проверить,
   не мешают ли они.
3. **Интерфейс под масштабом экрана.** `BaseActivity.attachBaseContext` рисует экраны в родной плотности
   панели (`DENSITY_DEVICE_STABLE`), размеры в dp пересчитываются. Причина обрезки: на Титане ручной масштаб
   480 dpi поверх панели 320 dpi, экран для приложений сжимается до 533dp (телефонный), низ карточек уезжает.
4. **Имя приложения** — «Krinik Tribit» (слово владельца).
5. **Иконка** — векторная, фон `#FF1A8C` (розовый Криника), их знак перерисован одним замкнутым штрихом;
   источник `design/icon.svg`, превью `design/icon-preview.webp`.
6. **Пароли с символами.** `android:digits` разрешал только буквы и цифры, а `RegexUtils.isPassword` требовал
   `[0-9A-Za-z]{6,18}`. Теперь разрешены печатные ASCII-символы; правило «не только цифры, не только буквы»
   и длина 6–18 остались.

**⚠ Собранный APK отстал от патчей.** `out/signed/*.apk` собран ДО того, как был написан патч 6: в дереве
`work/base` патчи 1–5 есть, шестого (символы в пароле) нет (проверено чтением `work/base/res/values/strings.xml`
и `RegexUtils.smali` — там прежний набор букв и цифр и прежнее выражение `[0-9A-Za-z]{6,18}`). Первое дело в
новом чате — `bash build.sh` заново: он декодирует оригинал с нуля и накладывает все шесть.

Сам код патча 6 агент-ревизор проверил и признал верным: в smali экранирование `\\x21` читается как один
обратный слеш, Java видит `\x21`, «_» (0x5F) попадает в диапазон, запрет «только цифры / только буквы» остаётся.

---

## Где продолжить

0. **ПЕРВЫМ ДЕЛОМ — развернуть KAIF в этом проекте** (слово владельца 2026-10-15 ≈ 23:4x: «задание в тот
   проект первым делом агенты - развернуть КАИФ 2.8 и 2.9 WIP, а затем уже приниматься за разработку
   Krinik Tribit»). Версия — как в KARTUN: 2.8 + предрелиз 2.9 (сборка `a63c651356bc`, коммит истока
   `610b18a`), рабочий язык русский, сфера programming. Образец развёртывания и одиннадцать пунктов
   адаптации — `D:\work\ai_sandbox\KARTUN\KAIF_FRAMEWORK.md`. Хуки `pretool-owner-word` и
   `stop-owner-answer` владелец в KARTUN снял — здесь их тоже не ставить
   (`KARTUN/tools/unwire-owner-word-hooks.mjs`). Этот `STATUS.md` и файлы `research/` после развёртывания
   разложить по местам KAIF: боли → `bugs/`, план проверки → `testcases/`, разведка → `researches/`.
1. **Пересобрать (`bash build.sh`) — сборка отстала от патчей, см. выше.** Затем поставить на Титан и
   пройти по `research/test-plan.md` (15 случаев + контрольный). Нужно слово владельца на удаление оригинала: подпись
   другая, рядом они не живут (`HOUSE_RULES.md` KARTUN, R1 — чужие приложения на планшете не трогать).
   ```
   adb -s 192.168.1.3:5555 uninstall com.thousandshores.tribit   # ждёт слова владельца
   adb -s 192.168.1.3:5555 install-multiple out/signed/*.apk
   ```
   Проверить по очереди: виден ли эквалайзер целиком · не падает ли «создать свой EQ» · работает ли поиск
   колонки без геолокации · видна ли кнопка регистрации (владелец её не находил — скорее всего тот же
   обрез) · принимает ли поле пароля «_» · имя и иконка на рабочем столе.
2. **Пересобрать после правок:** `bash build.sh` (apktool decode → патчи → сборка → zipalign → подпись
   одним ключом всех сплитов; ключ создаётся сам в `keys/`, вне git).
3. **Ответ по аудиту кода.** Фоновый агент писал `research/code-audit.md` (скептический разбор: крэши,
   вёрстка, геолокация, переводы + ревизия моих 6 патчей). На момент закрытия файл не дописан — перезапустить.
4. **Развилка, ждёт владельца: А или Б.**
   - **А** — дальше латать их приложение. Альбомная ориентация открывается правкой манифеста, но вёрстка
     остаётся их: сотни XML под телефон, каждый экран чинить вслепую по smali. Рефакторинг невозможен —
     декомпилированный код не собирается как исходник.
   - **Б** (рекомендация агента) — своё приложение на Kotlin + Compose, адаптивная вёрстка, стиль Криника,
     без геолокации и обязательного аккаунта. Протокол колонки разобран наполовину: пакет
     `EA <длина> <команда> <данные> <контрольная сумма>` (`Bts52Util.buildPacket`), эквалайзер — команды 4
     и 11, громкость — 13, свет — 12/52, батарея — 6; усиление полос едет со сдвигом +12 (`EqUtil.getBts56GainArray`).
     Канал: RFCOMM `0CF12D31-FAC3-4553-BD80-D6832E7B3119` (у StormBox Micro 2 свой), BLE — служба `0000ffa0`,
     запись `0000ffa1`; у части моделей `00002000`/`00002002`/`00002003`.
5. **README на трёх языках** (слово владельца): русский, английский, китайский — что это починенная сборка,
   которая не падает, с адаптивным интерфейсом, нормальными переводами и без обязательной геолокации.
   Сейчас в README только английский.
6. **Переводы — файлами ресурсов НЕ чинятся** (разбор субагента, цитаты в `research/pains.md` §6).
   Приложение не использует `values-ru/strings.xml`: выбор языка кладёт код в `app_language` и
   **скачивает тексты с их сервера** (`ViewModelSettings:135` → `api-app/api/lang/getLangInfoBySchemaOrLangKey`),
   а настоящий Locale не ставит никогда. В APK один набор строк — `values/strings.xml`, 1673 строки;
   русские 254 строки из `split_config.ru.apk` все до единой принадлежат библиотекам Google. Плюс
   много текста зашито прямо в код и разметку, часто по-китайски (целый экран
   `activity_device_help_new.xml`, названия пресетов эквалайзера `EqButton56Activity:343,366`).
   **Нормальный перевод возможен только в своём приложении (вариант Б).** Языки — `research/languages.md`:
   обязательно английский, русский, немецкий, португальский (Бразилия), испанский; дальше японский,
   тайский, французский, итальянский, польский, турецкий.
7. **«О приложении»** со ссылками на GitHub Криника — как в KARTUN (слово владельца, не начато).

---

## Что известно про их сервер

Проверок подписи приложения, Play Integrity, SafetyNet и привязки сертификатов в коде нет; в
`network_security_config.xml` разрешён даже открытый трафик. Значит, вход и регистрация по почте у нашей
сборки должны работать так же, как у оригинала. Вход через Google и Facebook, скорее всего, не будет:
он привязан к отпечатку их подписи. **Владелец запретил делать запросы на их сервер** («не делаем запросы
на сервер», 2026-10-15 ≈ 23:3x) — разрешение на скрипт запросов снято, сам скрипт удалён.

---

## Документы проекта

- `research/pains.md` — **все боли одним списком**: что чинить, в каком состоянии, с цитатами кода.
- `research/test-plan.md` — **что проверить** на Титане: 15 случаев плюс контрольный, команды, куда писать отчёт.
- `research/play-reviews.md` — 2648 отзывов Google Play по 28 темам (сырые данные и скрипты сбора рядом, вне git).
- `research/languages.md` — на какие языки переводить и почему.
- `patches/apply.py` — сами патчи; `build.sh` — сборка и подпись; `design/icon.svg` — иконка.

## Жалобы пользователей (2648 отзывов Google Play, `research/play-reviews.md`)

Первая десятка тем: не подключается к колонке (366, из них 302 — оценки 1–2★) · модель не поддерживается
(279) · общее недовольство (188) · вылетает или не открывается (159) · не удаётся зарегистрироваться (126) ·
не хватает функций (118) · эквалайзер не сохраняется (117) · избыточные разрешения (92) · после обновления
прошивки хуже (88) · устаревший UX (81). Геолокация — 72 отзыва, планшеты — 63, переводы — 72.

## Открытые вопросы к владельцу

- ❓ Удалить оригинальный Трибит с Титана, чтобы поставить нашу сборку?
- ❓ Развилка А или Б (пункт 4 выше)?
````
