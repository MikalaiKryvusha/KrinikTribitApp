<a name="english"></a>

<p align="center">
  <img src="design/icon.svg" alt="Krinik Tribit: a pink square with a black three-loop knot drawn in one stroke" width="160">
</p>

<h2 align="center">Krinik Tribit</h2>

<p align="center">
  <a href="#english"><img src="https://img.shields.io/badge/English-2C7BE5?style=for-the-badge" alt="English"></a>
  &nbsp;
  <a href="#russian"><img src="https://img.shields.io/badge/Русский-C0392B?style=for-the-badge" alt="Русский"></a>
  &nbsp;
  <a href="#chinese"><img src="https://img.shields.io/badge/中文-E67E22?style=for-the-badge" alt="中文"></a>
</p>

<p align="center"><b>Our own app for Tribit speakers — made by people, for people</b><br>
Open source · No crashes · No location · Tablets and big screens · Proper translations</p>

<p align="center">
  <a href="#en-1"><img src="https://img.shields.io/badge/platform-Android-3DDC84.svg" alt="Platform: Android"></a>
  <a href="#en-1"><img src="https://img.shields.io/badge/speakers-Tribit-FF1A8C.svg" alt="Speakers: Tribit"></a>
  <a href="#en-4"><img src="https://img.shields.io/badge/status-early_development-orange.svg" alt="Status: early development"></a>
  <a href="https://github.com/MikalaiKryvusha/KAIF"><img src="https://img.shields.io/badge/framework-KAIF-7F52FF.svg" alt="Framework: KAIF"></a>
</p>

<p align="center"><a href="https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.kriniks.tribit%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FMikalaiKryvusha%2FKrinikTribitApp%22%2C%22author%22%3A%22MikalaiKryvusha%22%2C%22name%22%3A%22Krinik%20Tribit%22%2C%22additionalSettings%22%3A%22%7B%7D%22%7D"><img src="docs/get-it-on-obtainium-en.svg" height="72" alt="Get it on Obtainium"></a></p>

[Читать по-русски →](#russian) · [阅读中文 →](#chinese)

**Krinik Tribit** is our own app for Tribit Bluetooth speakers, written from scratch in Kotlin and Jetpack Compose: not
a clone and not a patch of the official app. It finds the paired speaker with location turned off, needs no account and
has no internet permission, so it talks only to the speaker. It was born on the author's tablet, where the official
Tribit app version 5.0.0 crashed on «create my EQ», demanded location to find a speaker and cut off the bottom of its
screens.

**History.** In October 2026 the first line of work repaired the official Tribit app 5.0.0; section 1 lists what it
fixed, and those fixes are the requirements our own app is built to. That line is closed: its tools were removed from
this repository on 2026-11-07, and its history stays in git.

Sections: [1 What it fixes](#en-1) · [2 What hurts in the official app](#en-2) · [3 Download](#en-3) ·
[4 Roadmap](#en-4) · [5 Build it yourself](#en-5) · [6 Project map](#en-6) · [7 Legal and credits](#en-7).

<a name="en-1"></a>

### 1. What it fixes

What the first line of work fixed in the official app 5.0.0 (history, see above):

1. «Create my EQ» no longer crashes the app: a preset name without a number is skipped.
2. The speaker is found and connected with location turned off — both on the permission screens and inside the
   Bluetooth library that used to refuse the scan.
3. Every screen fits whole on a phone and a tablet, at any system display size.
4. Texts live in resource files and are translated by people; the server's broken texts and the Chinese left in the
   code are replaced with ours.
5. Screens are laid out for tablets and landscape.
6. The password field accepts letters, digits and symbols.
7. The app is named «Krinik Tribit» and has its own pink icon.
8. There is no forced-update window. That window had no close button, sent the user to Google Play and installed the
   official Tribit app over Krinik Tribit.
9. Firebase is switched off: Krinik Tribit collects no analytics, does not read the advertising ID and receives no push
   messages; Crashlytics report collection is off. The app does not declare the advertising-ID permission.

**Privacy.** Krinik Tribit respects the privacy of personal data and the GDPR. We are against usage tracking through
Firebase and the Tribit server. The Tribit server must not learn who uses the app, and we are building Krinik Tribit so
that the Tribit server cannot identify a person.

Our own app has no internet permission at all, so it sends nothing to the Tribit server or anywhere else. The first line
of work, in the official app:

- Done and checked on a Samsung A51: Firebase is off; the app has no Firebase analytics, no advertising ID and no push
  messages.
- Done and checked on a Samsung A51: the app talks to the Tribit server only as an anonymous guest. The guest ID, the
  phone model and the Android version in its requests are random, picked once at install; no real value of the phone
  reached a request in the check. Only four kinds of requests go to the Tribit server: the guest sign-in, the speaker
  catalog, the firmware check (on the user's tap) and the language dictionary. Cloud copies of EQ presets and the support
  form are gone; the screens a user reaches no longer link to Tribit's site.

<a name="en-2"></a>

### 2. What hurts in the official app

The official Tribit app has 2,648 recent Google Play reviews in 33 locales. The complaints Krinik Tribit answers:

| Complaint in Google Play reviews | Reviews | Of them 1–2★ |
|---|---:|---:|
| The app does not connect to the speaker or does not find it | 366 | 302 |
| Crashes, does not open, hangs on the logo | 159 | 124 |
| Cannot sign up or sign in | 126 | 107 |
| A custom equalizer cannot be created or saved | 117 | 65 |
| Location is required; tablets without GPS ask for it forever | 72 | 63 |
| The language is missing or badly translated | 72 | 24 |
| Tablets: does not install, does not work, landscape layout breaks | 63 | 47 |
| The app depends on Tribit's server | 63 | 37 |

The full list of 28 complaint themes is in [researches/01_play_reviews.md](researches/01_play_reviews.md) (in Russian).

<a name="en-3"></a>

### 3. Download

Krinik Tribit is released on the [Releases](https://github.com/MikalaiKryvusha/KrinikTribitApp/releases) page;
[Obtainium](https://github.com/ImranR98/Obtainium) (the button at the top) installs it from GitHub Releases and keeps it
updated. Android 13 or newer. Krinik Tribit has its own package (`com.kriniks.tribit`), so it installs beside the
official Tribit app.

<a name="en-4"></a>

### 4. Roadmap

| # | Step | State |
|---|---|---|
| 1 | Research: 2,648 Google Play reviews, the languages to translate into, the pains of the official app | ✅ done |
| 2 | The official app with our fixes, the first line of work (closed 2026-11-07): no crash on «create my EQ», no location, no account (an anonymous guest), no Firebase, no links to Tribit, TLS checked again — run on a Samsung A51 with a StormBox Blast 2 | ✅ done |
| 3 | Our own app from scratch: research of the speaker protocol and of how good Bluetooth apps are built | 🔧 in progress |
| 4 | Our own app on a StormBox Blast 2: find and connect without location and without a server; battery, volume, equalizer, light, speaker settings | 🔲 planned |
| 5 | Design, every screen size, English and Russian by hand | 🔲 planned |
| 6 | Firmware updates and other speaker models | 🔲 planned |
| 7 | Two builds and the first signed release on GitHub | 🔲 planned |

<a name="en-5"></a>

## Build it yourself

The ready APK is behind the button at the top. The commands below are for Windows PowerShell; on Linux and macOS use
`./gradlew` instead of `.\gradlew.bat`.

### Requirements

- JDK 21.
- The Android SDK with platform 37 (`compileSdk 37`); Gradle finds it through `ANDROID_HOME` or `sdk.dir` in
  `local.properties`. No NDK: the app is Kotlin and Jetpack Compose only.
- Git.

### Get the code

```powershell
git clone https://github.com/MikalaiKryvusha/KrinikTribitApp
cd KrinikTribitApp
```

### Build

```powershell
$env:JAVA_HOME = 'C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot'   # your JDK 21
.\gradlew.bat assembleDebug                   # Debug Krinik Tribit: app/build/outputs/apk/debug/app-debug.apk
.\gradlew.bat assembleRelease                 # Krinik Tribit (R8): app/build/outputs/apk/release/
```

### Signing a release

The release key stays outside git: `.env` in the project root and the `keys/` folder are both in `.gitignore`. Create
your own release key, for example:

```powershell
mkdir keys
keytool -genkeypair -keystore keys/krinik-tribit-app-release.jks -storetype PKCS12 -alias krinik-tribit -keyalg RSA -keysize 4096 -validity 10950
```

Then write its four values into `.env`:

```ini
KT_RELEASE_STORE_FILE=keys/krinik-tribit-app-release.jks
KT_RELEASE_STORE_PASSWORD=...
KT_RELEASE_KEY_ALIAS=krinik-tribit
KT_RELEASE_KEY_PASSWORD=...
```

The store path is relative to the project root, with forward slashes. With `.env` in place, `assembleRelease` signs the
APK with this key; without it, the release APK stays unsigned (`app-release-unsigned.apk`). The debug build always uses
the SDK's debug key. A PKCS12 store has one password for the store and the key. Keep a copy of the key outside the
project: a release signed with another key does not install over the previous one.

### Project notes

- No native code of our own: the app is Kotlin and Jetpack Compose, built by Gradle alone.
- No `INTERNET` permission: the app talks only to the speaker, over Bluetooth (`BLUETOOTH_CONNECT`).
- FreeDroidWarn comes from JitPack, the other libraries from Google Maven and Maven Central; the first build needs
  network access to them.
- Speaker photos: the build takes them from the private folder `native/krinik-app/res` when it is present, otherwise
  from `app/src/photostub/res`, a drawn stand-in under the same name. A clone of this repository builds with the
  stand-in.
- Two builds install side by side: Debug Krinik Tribit (`com.kriniks.tribit.debug`) and Krinik Tribit
  (`com.kriniks.tribit`). Android 13 or newer.

<a name="en-6"></a>

### 6. Project map

| Path | What lives there |
|---|---|
| `app/` | our app: Kotlin, Jetpack Compose; the speaker protocol, the screens, the settings file |
| `docs/` | the Obtainium button and the font licences |
| `researches/` | the Google Play reviews, the languages, the pains of the official app (in Russian) |
| `testcases/` | what to check on the tablet and how (in Russian) |
| `design/` | the icon source |

<a name="en-7"></a>

### 7. Legal and credits

1. Krinik Tribit is not affiliated with Tribit or Thousandshores. Tribit is their trademark.
2. [apktool](https://apktool.org) and [jadx](https://github.com/skylot/jadx) were used to read the official app for the
   research and, on the first line of work, to patch it; they are not part of this repository.
3. The project is run with [KAIF](https://github.com/MikalaiKryvusha/KAIF), a framework for work with an AI agent.

Author: Mikalai Kryvusha (Krinik).

---

<a name="russian"></a>

<p align="center">
  <img src="design/icon.svg" alt="Krinik Tribit: розовый квадрат с чёрным узлом из трёх петель, нарисованным одним штрихом" width="160">
</p>

<h2 align="center">Krinik Tribit</h2>

<p align="center"><b>Наше собственное приложение для колонок Tribit, сделанное людьми для людей</b><br>
Открытый код · Без вылетов · Без геолокации · Планшеты и большие экраны · Нормальные переводы</p>

<p align="center">
  <a href="#ru-1"><img src="https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Android-3DDC84.svg" alt="Платформа: Android"></a>
  <a href="#ru-1"><img src="https://img.shields.io/badge/%D0%BA%D0%BE%D0%BB%D0%BE%D0%BD%D0%BA%D0%B8-Tribit-FF1A8C.svg" alt="Колонки: Tribit"></a>
  <a href="#ru-4"><img src="https://img.shields.io/badge/%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D0%B5-%D1%80%D0%B0%D0%BD%D0%BD%D1%8F%D1%8F_%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0-orange.svg" alt="Состояние: ранняя разработка"></a>
  <a href="https://github.com/MikalaiKryvusha/KAIF"><img src="https://img.shields.io/badge/%D1%84%D1%80%D0%B5%D0%B9%D0%BC%D0%B2%D0%BE%D1%80%D0%BA-KAIF-7F52FF.svg" alt="Фреймворк: KAIF"></a>
</p>

<p align="center"><a href="https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.kriniks.tribit%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FMikalaiKryvusha%2FKrinikTribitApp%22%2C%22author%22%3A%22MikalaiKryvusha%22%2C%22name%22%3A%22Krinik%20Tribit%22%2C%22additionalSettings%22%3A%22%7B%7D%22%7D"><img src="docs/get-it-on-obtainium-ru.svg" height="72" alt="Скачать через Obtainium"></a></p>

[Read in English →](#english) · [阅读中文 →](#chinese)

Приложение **Krinik Tribit** написано с нуля на Kotlin и Jetpack Compose как наше собственное приложение для колонок
Tribit: это не клон и не патч официального приложения. Оно находит сопряжённую колонку при выключенной геолокации и не
требует аккаунта. Разрешения на интернет у приложения нет: оно общается только с колонкой. Родилось оно на планшете
автора: там официальное приложение Tribit версии 5.0.0 падало на кнопке «создать свой EQ», требовало геолокацию для
поиска колонки и обрезало низ своих экранов.

**История.** В октябре 2026 года первая линия работы чинила официальное приложение Tribit 5.0.0; в разделе 1
перечислено, что она исправила, и эти исправления стали требованиями к нашему приложению. Эта линия закрыта: её
инструменты убраны из репозитория 2026-11-07, история осталась в git.

Разделы: [1 Что исправлено](#ru-1) · [2 Что болит в официальном приложении](#ru-2) · [3 Скачать](#ru-3) ·
[4 Дорожная карта](#ru-4) · [5 Собрать самому](#ru-5) · [6 Карта проекта](#ru-6) ·
[7 Правовая информация и благодарности](#ru-7).

<a name="ru-1"></a>

### 1. Что исправлено

Что первая линия работы исправила в официальном приложении 5.0.0 (история, см. выше):

1. Кнопка «создать свой EQ» больше не роняет приложение: имя пресета без номера пропускается.
2. Колонка находится и подключается при выключенной геолокации — и на экранах разрешений, и внутри библиотеки
   Bluetooth, которая раньше отказывалась искать.
3. Каждый экран целиком помещается на телефоне и планшете при любом системном масштабе.
4. Тексты лежат в файлах ресурсов и переведены людьми; кривые тексты с сервера и китайский, оставленный в коде,
   заменены нашими.
5. Экраны свёрстаны под планшет и альбомную ориентацию.
6. Поле пароля принимает буквы, цифры и символы.
7. Приложение называется «Krinik Tribit», у него своя розовая иконка.
8. Окна обязательного обновления нет. Это окно не закрывалось, вело в Google Play и ставило официальное приложение
   Tribit поверх Krinik Tribit.
9. Firebase выключен: Krinik Tribit не собирает аналитику, не читает рекламный идентификатор и не получает пуши,
   сбор отчётов Crashlytics выключен. Разрешения на рекламный идентификатор в приложении нет.

**Приватность.** Krinik Tribit уважает приватность личных данных и GDPR. Мы против отслеживания метрик через Firebase
и сервер Tribit. Сервер Tribit не должен узнать, кто пользуется приложением, и мы делаем так, чтобы сервер Tribit не смог
установить личность человека.

У нашего приложения нет разрешения на интернет: оно ничего не отправляет ни серверу Tribit, ни куда-либо ещё.
Первая линия работы, в официальном приложении:

- Сделано и проверено на Samsung A51: Firebase выключен, аналитики Firebase, рекламного идентификатора и пушей в
  приложении нет.
- Сделано и проверено на Samsung A51: приложение обращается к серверу Tribit только анонимным гостем. ID гостя, модель
  телефона и версия Android в его запросах случайные, выбираются один раз при установке; ни одно настоящее значение
  телефона в проверке в запросы не попало. К серверу Tribit уходят только четыре вида запросов: вход гостя, каталог
  колонок, проверка прошивки (по нажатию пользователя) и словарь языка. Облачных копий пресетов эквалайзера и формы
  поддержки больше нет; экраны, до которых доходит пользователь, не ведут на сайт Tribit.

<a name="ru-2"></a>

### 2. Что болит в официальном приложении

У официального приложения Tribit 2648 свежих отзывов в Google Play в 33 локалях. Жалобы, на которые отвечает Krinik
Tribit:

| Жалоба в отзывах Google Play | Отзывов | Из них 1–2★ |
|---|---:|---:|
| Приложение не подключается к колонке или не находит её | 366 | 302 |
| Вылетает, не открывается, зависает на логотипе | 159 | 124 |
| Не удаётся зарегистрироваться или войти | 126 | 107 |
| Свой эквалайзер нельзя создать или сохранить | 117 | 65 |
| Требует геолокацию; планшеты без GPS просят её бесконечно | 72 | 63 |
| Нет нужного языка или перевод кривой | 72 | 24 |
| Планшеты: не ставится, не работает, ломается альбомная вёрстка | 63 | 47 |
| Приложение зависит от сервера Tribit | 63 | 37 |

Полный список из 28 тем жалоб — [researches/01_play_reviews.md](researches/01_play_reviews.md).

<a name="ru-3"></a>

### 3. Скачать

Krinik Tribit выходит на странице [Releases](https://github.com/MikalaiKryvusha/KrinikTribitApp/releases);
[Obtainium](https://github.com/ImranR98/Obtainium) (кнопка в начале страницы) ставит его из GitHub Releases и сам
обновляет. Нужен Android 13 или новее. У Krinik Tribit свой пакет (`com.kriniks.tribit`): приложение ставится рядом с
официальным приложением Tribit.

<a name="ru-4"></a>

### 4. Дорожная карта

| № | Шаг | Состояние |
|---|---|---|
| 1 | Разведка: 2648 отзывов Google Play, языки перевода, боли официального приложения | ✅ сделано |
| 2 | Официальное приложение с нашими исправлениями, первая линия работы (закрыта 2026-11-07): без вылета на «создать свой эквалайзер», без геолокации, без аккаунта (анонимный гость), без Firebase, без переходов на Tribit, TLS вновь с проверкой — прогнано на Samsung A51 с колонкой StormBox Blast 2 | ✅ сделано |
| 3 | Своё приложение с нуля: разведка протокола колонки и того, как устроены хорошие приложения для Bluetooth | 🔧 в работе |
| 4 | Своё приложение на StormBox Blast 2: найти и подключить без геолокации и без сервера; заряд, громкость, эквалайзер, подсветка, настройки колонки | 🔲 в плане |
| 5 | Дизайн, экраны любого размера, английский и русский руками | 🔲 в плане |
| 6 | Обновление прошивки и другие модели колонок | 🔲 в плане |
| 7 | Две сборки и первый подписанный релиз на GitHub | 🔲 в плане |

<a name="ru-5"></a>

## Собрать самому

Готовый APK можно поставить кнопкой в начале страницы. Команды ниже написаны для Windows PowerShell; в Linux и macOS
вместо `.\gradlew.bat` пишите `./gradlew`.

### Что нужно

- JDK 21.
- Android SDK с платформой 37 (`compileSdk 37`); Gradle находит его через `ANDROID_HOME` или `sdk.dir` в
  `local.properties`. NDK не нужен: приложение написано только на Kotlin и Jetpack Compose.
- Git.

### Получить код

```powershell
git clone https://github.com/MikalaiKryvusha/KrinikTribitApp
cd KrinikTribitApp
```

### Собрать

```powershell
$env:JAVA_HOME = 'C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot'   # ваш JDK 21
.\gradlew.bat assembleDebug                   # Debug Krinik Tribit: app/build/outputs/apk/debug/app-debug.apk
.\gradlew.bat assembleRelease                 # Krinik Tribit (R8): app/build/outputs/apk/release/
```

### Подписать релиз

Ключ релиза хранится вне git: `.env` в корне проекта и папка `keys/` стоят в `.gitignore`. Создайте свой ключ релиза,
например:

```powershell
mkdir keys
keytool -genkeypair -keystore keys/krinik-tribit-app-release.jks -storetype PKCS12 -alias krinik-tribit -keyalg RSA -keysize 4096 -validity 10950
```

Затем впишите его четыре значения в `.env`:

```ini
KT_RELEASE_STORE_FILE=keys/krinik-tribit-app-release.jks
KT_RELEASE_STORE_PASSWORD=...
KT_RELEASE_KEY_ALIAS=krinik-tribit
KT_RELEASE_KEY_PASSWORD=...
```

Путь к хранилищу указывается от корня проекта, через прямые косые. Когда `.env` на месте, `assembleRelease` подписывает
APK этим ключом; без него APK релиза остаётся неподписанным (`app-release-unsigned.apk`). Debug-сборка всегда
подписывается отладочным ключом SDK. У хранилища PKCS12 один пароль на хранилище и ключ. Храните копию ключа вне
проекта: релиз, подписанный другим ключом, не встанет поверх предыдущего.

### Особенности проекта

- Своего нативного кода нет: приложение написано на Kotlin и Jetpack Compose и собирается одним Gradle.
- Разрешения `INTERNET` нет: приложение общается только с колонкой по Bluetooth (`BLUETOOTH_CONNECT`).
- FreeDroidWarn приходит с JitPack, остальные библиотеки с Google Maven и Maven Central; первой сборке нужен доступ к
  ним по сети.
- Фото колонок сборка берёт из приватной папки `native/krinik-app/res`, если она есть, иначе из
  `app/src/photostub/res`, где лежит нарисованная замена с тем же именем. Клон этого репозитория собирается с заменой.
- Две сборки ставятся рядом: Debug Krinik Tribit (`com.kriniks.tribit.debug`) и Krinik Tribit (`com.kriniks.tribit`).
  Нужен Android 13 или новее.

<a name="ru-6"></a>

### 6. Карта проекта

| Путь | Что там |
|---|---|
| `app/` | наше приложение на Kotlin и Jetpack Compose: протокол колонки, экраны, файл настроек |
| `docs/` | кнопка Obtainium и лицензии шрифтов |
| `researches/` | отзывы Google Play, языки, боли официального приложения |
| `testcases/` | что и как проверять на планшете |
| `design/` | исходник иконки |

<a name="ru-7"></a>

### 7. Правовая информация и благодарности

1. Krinik Tribit не связан с Tribit и Thousandshores. Tribit — их товарный знак.
2. [apktool](https://apktool.org) и [jadx](https://github.com/skylot/jadx) служили для чтения официального приложения в
   разведке, а на первой линии работы и для его патчей; в репозиторий они не входят.
3. Проект ведётся по [KAIF](https://github.com/MikalaiKryvusha/KAIF) — фреймворку работы с ИИ-агентом.

Автор: Николай Кривуша (Krinik).

---

<a name="chinese"></a>

<p align="center">
  <img src="design/icon.svg" alt="Krinik Tribit：粉色方块上一笔画成的黑色三环结" width="160">
</p>

<h2 align="center">Krinik Tribit</h2>

<p align="center"><b>我们自己的 Tribit 音箱应用——由人打造，为人服务</b><br>
开源 · 不闪退 · 无需定位 · 适配平板和大屏 · 通顺的翻译</p>

<p align="center">
  <a href="#zh-1"><img src="https://img.shields.io/badge/%E5%B9%B3%E5%8F%B0-Android-3DDC84.svg" alt="平台：Android"></a>
  <a href="#zh-1"><img src="https://img.shields.io/badge/%E9%9F%B3%E7%AE%B1-Tribit-FF1A8C.svg" alt="音箱：Tribit"></a>
  <a href="#zh-4"><img src="https://img.shields.io/badge/%E7%8A%B6%E6%80%81-%E6%97%A9%E6%9C%9F%E5%BC%80%E5%8F%91-orange.svg" alt="状态：早期开发"></a>
  <a href="https://github.com/MikalaiKryvusha/KAIF"><img src="https://img.shields.io/badge/%E6%A1%86%E6%9E%B6-KAIF-7F52FF.svg" alt="框架：KAIF"></a>
</p>

<p align="center"><a href="https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.kriniks.tribit%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FMikalaiKryvusha%2FKrinikTribitApp%22%2C%22author%22%3A%22MikalaiKryvusha%22%2C%22name%22%3A%22Krinik%20Tribit%22%2C%22additionalSettings%22%3A%22%7B%7D%22%7D"><img src="docs/get-it-on-obtainium-en.svg" height="72" alt="Get it on Obtainium"></a></p>

[Read in English →](#english) · [Читать по-русски →](#russian)

**Krinik Tribit** 是我们自己的 Tribit 蓝牙音箱应用，用 Kotlin 和 Jetpack Compose 从零编写：不是官方应用的克隆，也不是补丁。
关闭定位也能找到已配对的音箱，无需账号，也没有联网权限，因此只与音箱通信。这个项目始于作者的一台平板：在那台平板上，
官方 Tribit 应用 5.0.0 版一点「创建我的 EQ」就闪退，搜索音箱必须开定位，界面底部还被裁掉。

**历史。** 2026 年 10 月，第一条工作线修复了官方 Tribit 应用 5.0.0；第 1 节列出了它修复的内容，这些修复成为我们自己应用的需求。
这条工作线已经结束：它的工具已于 2026-11-07 从本仓库移除，历史保留在 git 中。

目录：[1 修复内容](#zh-1) · [2 官方应用的问题](#zh-2) · [3 下载](#zh-3) · [4 路线图](#zh-4) · [5 自己构建](#zh-5) ·
[6 项目结构](#zh-6) · [7 法律声明与致谢](#zh-7)。

<a name="zh-1"></a>

### 1. 修复内容

第一条工作线在官方应用 5.0.0 中修复的内容（历史，见上文）：

1. 点「创建我的 EQ」不再闪退：不带编号的预设名会被跳过。
2. 关闭定位也能找到并连接音箱——无论是权限界面，还是以前拒绝搜索的内置蓝牙库。
3. 无论系统显示大小如何，每个界面都能在手机和平板上完整显示。
4. 文字放在资源文件里，由人工翻译；服务器下发的错误文字和代码里残留的中文都换成了我们的文字。
5. 界面适配平板和横屏。
6. 密码框接受字母、数字和符号。
7. 应用名为「Krinik Tribit」，有自己的粉色图标。
8. 没有强制更新窗口。该窗口没有关闭按钮，会跳转到 Google Play，并用 Tribit 官方应用覆盖 Krinik Tribit。
9. Firebase 已关闭：Krinik Tribit 不收集分析数据，不读取广告标识符，也不接收推送；Crashlytics 报告收集已关闭。应用不再申请广告标识符权限。

**隐私。** Krinik Tribit 尊重个人数据隐私和 GDPR。我们反对通过 Firebase 和 Tribit 服务器追踪使用数据。Tribit 服务器不应知道谁在使用本应用，我们正在让 Tribit 服务器无法识别用户身份。

我们自己的应用完全没有联网权限，因此不会向 Tribit 服务器或其他任何地方发送数据。第一条工作线在官方应用中：

- 已完成并在 Samsung A51 上验证：Firebase 已关闭，应用中没有 Firebase 分析、广告标识符和推送。
- 已完成，并已在 Samsung A51 上验证：应用只以匿名访客身份访问 Tribit 服务器。请求中的访客 ID、手机型号和 Android 版本均为随机值，在安装时选定一次；验证中没有任何真实的手机数据进入请求。发往 Tribit 服务器的请求只有四类：访客登录、音箱目录、固件检查（由用户点击触发）和语言词典。均衡器预设的云端副本和反馈表单已移除；用户能打开的界面不再跳转到 Tribit 网站。

<a name="zh-2"></a>

### 2. 官方应用的问题

官方 Tribit 应用在 Google Play 上有 2648 条近期评论，覆盖 33 个语言区域。Krinik Tribit 针对的抱怨：

| Google Play 评论中的抱怨 | 评论数 | 其中 1–2★ |
|---|---:|---:|
| 连不上音箱或找不到音箱 | 366 | 302 |
| 闪退、打不开、卡在启动标志 | 159 | 124 |
| 无法注册或登录 | 126 | 107 |
| 无法创建或保存自定义均衡器 | 117 | 65 |
| 必须开定位；没有 GPS 的平板会一直索要 | 72 | 63 |
| 缺少所需语言或翻译很差 | 72 | 24 |
| 平板：装不上、用不了、横屏布局错乱 | 63 | 47 |
| 应用依赖 Tribit 服务器 | 63 | 37 |

全部 28 类抱怨见 [researches/01_play_reviews.md](researches/01_play_reviews.md)（俄文）。

<a name="zh-3"></a>

### 3. 下载

Krinik Tribit 在 [Releases](https://github.com/MikalaiKryvusha/KrinikTribitApp/releases) 页面发布；
[Obtainium](https://github.com/ImranR98/Obtainium)（页面顶部的按钮）会从 GitHub Releases 安装并自动更新它。需要 Android 13
或更高版本。Krinik Tribit 使用自己的包名（`com.kriniks.tribit`），可以与官方 Tribit 应用并存。

<a name="zh-4"></a>

### 4. 路线图

| # | 步骤 | 状态 |
|---|---|---|
| 1 | 调研：2648 条 Google Play 评论、翻译语言、官方应用的问题 | ✅ 已完成 |
| 2 | 带有我们修复的官方应用（第一条工作线，已于 2026-11-07 结束）：「创建自定义均衡器」不再闪退，无需定位，无需账号（匿名访客），无 Firebase，不跳转到 Tribit，重新校验 TLS——已在 Samsung A51 和 StormBox Blast 2 上运行 | ✅ 已完成 |
| 3 | 从零编写我们自己的应用：调研音箱协议以及优秀蓝牙应用的做法 | 🔧 进行中 |
| 4 | 我们的应用支持 StormBox Blast 2：无需定位、无需服务器即可查找并连接；电量、音量、均衡器、灯光、音箱设置 | 🔲 计划中 |
| 5 | 设计、适配所有屏幕尺寸、人工翻译英文和俄文 | 🔲 计划中 |
| 6 | 固件更新和其他音箱型号 | 🔲 计划中 |
| 7 | 两个版本以及 GitHub 上的首个签名正式版 | 🔲 计划中 |

<a name="zh-5"></a>

## 自己构建

页面顶部的按钮可以直接安装现成的 APK。下面的命令适用于 Windows PowerShell；在 Linux 和 macOS 上请把 `.\gradlew.bat`
换成 `./gradlew`。

### 需要什么

- JDK 21。
- 带有平台 37（`compileSdk 37`）的 Android SDK；Gradle 通过 `ANDROID_HOME` 或 `local.properties` 中的 `sdk.dir` 找到它。
  不需要 NDK：应用只用 Kotlin 和 Jetpack Compose 编写。
- Git。

### 获取代码

```powershell
git clone https://github.com/MikalaiKryvusha/KrinikTribitApp
cd KrinikTribitApp
```

### 构建

```powershell
$env:JAVA_HOME = 'C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot'   # 你的 JDK 21
.\gradlew.bat assembleDebug                   # Debug Krinik Tribit：app/build/outputs/apk/debug/app-debug.apk
.\gradlew.bat assembleRelease                 # Krinik Tribit（R8）：app/build/outputs/apk/release/
```

### 签署发布版

发布密钥保存在 git 之外：项目根目录的 `.env` 和 `keys/` 文件夹都在 `.gitignore` 中。创建你自己的发布密钥，例如：

```powershell
mkdir keys
keytool -genkeypair -keystore keys/krinik-tribit-app-release.jks -storetype PKCS12 -alias krinik-tribit -keyalg RSA -keysize 4096 -validity 10950
```

然后把它的四个值写入 `.env`：

```ini
KT_RELEASE_STORE_FILE=keys/krinik-tribit-app-release.jks
KT_RELEASE_STORE_PASSWORD=...
KT_RELEASE_KEY_ALIAS=krinik-tribit
KT_RELEASE_KEY_PASSWORD=...
```

密钥库路径相对于项目根目录，使用正斜杠。有 `.env` 时，`assembleRelease` 用这把密钥给 APK 签名；没有时，发布版 APK 保持未签名
（`app-release-unsigned.apk`）。调试版始终使用 SDK 的调试密钥。PKCS12 密钥库的库密码和密钥密码是同一个。请在项目之外保存一份
密钥副本：用另一把密钥签名的发布版无法覆盖安装之前的版本。

### 项目说明

- 没有我们自己的原生代码：应用用 Kotlin 和 Jetpack Compose 编写，只用 Gradle 构建。
- 没有 `INTERNET` 权限：应用只通过蓝牙（`BLUETOOTH_CONNECT`）与音箱通信。
- FreeDroidWarn 来自 JitPack，其他库来自 Google Maven 和 Maven Central；首次构建需要能访问它们的网络。
- 音箱照片：如果存在私有文件夹 `native/krinik-app/res`，构建就从那里取照片，否则使用 `app/src/photostub/res` 中同名的手绘
  替代图。克隆本仓库后会使用替代图构建。
- 两个版本可以并存安装：Debug Krinik Tribit（`com.kriniks.tribit.debug`）和 Krinik Tribit（`com.kriniks.tribit`）。需要
  Android 13 或更高版本。

<a name="zh-6"></a>

### 6. 项目结构

| 路径 | 内容 |
|---|---|
| `app/` | 我们的应用（Kotlin、Jetpack Compose）：音箱协议、界面、设置文件 |
| `docs/` | Obtainium 按钮和字体许可证 |
| `researches/` | Google Play 评论、翻译语言、官方应用的问题（俄文） |
| `testcases/` | 在平板上检查什么、怎么检查（俄文） |
| `design/` | 图标源文件 |

<a name="zh-7"></a>

### 7. 法律声明与致谢

1. Krinik Tribit 与 Tribit 及 Thousandshores 没有任何关联。Tribit 是其商标。
2. [apktool](https://apktool.org) 和 [jadx](https://github.com/skylot/jadx) 曾用于在调研中读取官方应用，并在第一条工作线中修补它；它们不包含在本仓库中。
3. 本项目使用 [KAIF](https://github.com/MikalaiKryvusha/KAIF)（一个与 AI 智能体协作的框架）管理。

作者：Mikalai Kryvusha (Krinik)。
