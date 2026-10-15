<p align="center">
  <img src="design/icon.svg" alt="Krinik Tribit: a pink square with a black three-loop knot drawn in one stroke" width="200">
</p>

<h1 align="center">Krinik Tribit</h1>

<p align="center">
  <a href="#english"><img src="https://img.shields.io/badge/English-2C7BE5?style=for-the-badge" alt="English"></a>
  &nbsp;
  <a href="#russian"><img src="https://img.shields.io/badge/Русский-C0392B?style=for-the-badge" alt="Русский"></a>
  &nbsp;
  <a href="#chinese"><img src="https://img.shields.io/badge/中文-E67E22?style=for-the-badge" alt="中文"></a>
</p>

---

<a name="english"></a>

<h2 align="center">Krinik Tribit</h2>

<p align="center"><b>The Tribit speaker app, fixed — by people, for people</b><br>
Open source · No crashes · No location · Tablets and big screens · Proper translations</p>

<p align="center">
  <a href="#en-1"><img src="https://img.shields.io/badge/platform-Android-3DDC84.svg" alt="Platform: Android"></a>
  <a href="#en-1"><img src="https://img.shields.io/badge/speakers-Tribit-FF1A8C.svg" alt="Speakers: Tribit"></a>
  <a href="#en-4"><img src="https://img.shields.io/badge/status-early_development-orange.svg" alt="Status: early development"></a>
  <a href="https://github.com/MikalaiKryvusha/KAIF"><img src="https://img.shields.io/badge/framework-KAIF-7F52FF.svg" alt="Framework: KAIF"></a>
</p>

[Читать по-русски →](#russian) · [阅读中文 →](#chinese)

**Krinik Tribit** is the official Tribit speaker app with its defects fixed. It controls every Tribit speaker the
official app knows — and it does not crash, finds the speaker with location turned off, fits every screen on a phone
and a tablet, and speaks proper English and Russian. It was born on the author's tablet, where the official Tribit app
version 5.0.0 crashed on «create my EQ», demanded location to find a speaker and cut off the bottom of its screens.

Sections: [1 What it fixes](#en-1) · [2 What hurts in the official app](#en-2) · [3 Download](#en-3) ·
[4 Roadmap](#en-4) · [5 Build it yourself](#en-5) · [6 Project map](#en-6) · [7 Legal and credits](#en-7).

<a name="en-1"></a>

### 1. What it fixes

1. «Create my EQ» no longer crashes the app: a preset name without a number is skipped.
2. The speaker is found and connected with location turned off — both on the permission screens and inside the
   Bluetooth library that used to refuse the scan.
3. Every screen fits under an enlarged system display size: screens are drawn at the panel's native pixel density.
4. Texts live in resource files and are translated by people; the server's broken texts and the Chinese left in the
   code are replaced with ours.
5. Screens are laid out for tablets and landscape.
6. The password field accepts letters, digits and symbols.
7. The app is named «Krinik Tribit» and has its own pink icon.

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

Download the APK from the [Releases](https://github.com/MikalaiKryvusha/KrinikTribitApp/releases) page: one signed APK
for every 64-bit Android device. Remove the official Tribit app first (the signature differs), install Krinik Tribit
and use it. The first release comes with step 7 of the roadmap.

<a name="en-4"></a>

### 4. Roadmap

| # | Step | State |
|---|---|---|
| 1 | Research: 2,648 Google Play reviews, the languages to translate into, the pains of the official app | ✅ done |
| 2 | Patches: the EQ crash, location in both places, screens under display zoom, password symbols, name, icon | ✅ written, not yet tested on a device |
| 3 | The first patched build on the author's tablet with a StormBox Blast 2 | 🔧 next |
| 4 | Texts: ours in resource files instead of the server's and the hard-coded ones; English and Russian by hand | 🔧 research |
| 5 | Layouts for tablets and landscape | 🔧 research |
| 6 | Crashes, lost connections, what the Tribit server is really needed for | 🔧 research |
| 7 | Debug and release builds, the first signed release on GitHub | 🔲 planned |

<a name="en-5"></a>

### 5. Build it yourself

The repository holds the patches and the build script; you bring the official APK from your own device. You need
Git Bash on Windows, JDK 21, the Android SDK platform-tools (`adb`) and build-tools `36.0.0`, Python 3 and
[apktool](https://apktool.org) saved as `tools/apktool.jar`. `build.sh` looks for JDK 21 and build-tools at their
default Windows paths; point it elsewhere with `JAVA_HOME_KRINIK` and `ANDROID_BUILD_TOOLS`.

```bash
adb shell pm path com.thousandshores.tribit      # where the split APKs of the official app live
adb pull <each path> original-apk/                # base.apk and every split_*.apk
bash build.sh                                     # decode, patch, rebuild, sign the whole set with one key
adb uninstall com.thousandshores.tribit           # the signature differs, so the original has to go first
adb install-multiple out/signed/*.apk
```

Signing in with email works as before. Signing in with Google or Facebook most likely does not: those logins are bound
to Tribit's own signature.

<a name="en-6"></a>

### 6. Project map

| Path | What lives there |
|---|---|
| `patches/` | the patches to the official app, each one fails if its place in the code has moved |
| `build.sh` | the build: decode, patch, rebuild, align, sign |
| `researches/` | the Google Play reviews, the languages, the pains of the official app (in Russian) |
| `testcases/` | what to check on the tablet and how (in Russian) |
| `design/` | the icon source |

<a name="en-7"></a>

### 7. Legal and credits

1. Krinik Tribit is not affiliated with Tribit or Thousandshores. Tribit is their trademark.
2. [apktool](https://apktool.org) and [jadx](https://github.com/skylot/jadx) are the tools used to read and patch the
   official app; they are not part of this repository.
3. The project is run with [KAIF](https://github.com/MikalaiKryvusha/KAIF), a framework for work with an AI agent.

Author: Mikalai Kryvusha (Krinik).

---

<a name="russian"></a>

<h2 align="center">Krinik Tribit</h2>

<p align="center"><b>Приложение для колонок Tribit, исправленное — от людей для людей</b><br>
Открытый код · Без вылетов · Без геолокации · Планшеты и большие экраны · Нормальные переводы</p>

<p align="center">
  <a href="#ru-1"><img src="https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Android-3DDC84.svg" alt="Платформа: Android"></a>
  <a href="#ru-1"><img src="https://img.shields.io/badge/%D0%BA%D0%BE%D0%BB%D0%BE%D0%BD%D0%BA%D0%B8-Tribit-FF1A8C.svg" alt="Колонки: Tribit"></a>
  <a href="#ru-4"><img src="https://img.shields.io/badge/%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D0%B5-%D1%80%D0%B0%D0%BD%D0%BD%D1%8F%D1%8F_%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0-orange.svg" alt="Состояние: ранняя разработка"></a>
  <a href="https://github.com/MikalaiKryvusha/KAIF"><img src="https://img.shields.io/badge/%D1%84%D1%80%D0%B5%D0%B9%D0%BC%D0%B2%D0%BE%D1%80%D0%BA-KAIF-7F52FF.svg" alt="Фреймворк: KAIF"></a>
</p>

[Read in English →](#english) · [阅读中文 →](#chinese)

**Krinik Tribit** — официальное приложение для колонок Tribit с исправленными дефектами. Оно управляет всеми колонками
Tribit, которые знает официальное приложение, и при этом не падает, находит колонку при выключенной геолокации,
показывает каждый экран целиком на телефоне и планшете и говорит на нормальном английском и русском. Родилось оно на
планшете автора: там официальное приложение Tribit версии 5.0.0 падало на кнопке «создать свой EQ», требовало геолокацию
для поиска колонки и обрезало низ своих экранов.

Разделы: [1 Что исправлено](#ru-1) · [2 Что болит в официальном приложении](#ru-2) · [3 Скачать](#ru-3) ·
[4 Дорожная карта](#ru-4) · [5 Собрать самому](#ru-5) · [6 Карта проекта](#ru-6) ·
[7 Правовая информация и благодарности](#ru-7).

<a name="ru-1"></a>

### 1. Что исправлено

1. Кнопка «создать свой EQ» больше не роняет приложение: имя пресета без номера пропускается.
2. Колонка находится и подключается при выключенной геолокации — и на экранах разрешений, и внутри библиотеки
   Bluetooth, которая раньше отказывалась искать.
3. Каждый экран помещается при увеличенном системном масштабе: экраны рисуются в родной плотности пикселей панели.
4. Тексты лежат в файлах ресурсов и переведены людьми; кривые тексты с сервера и китайский, оставленный в коде,
   заменены нашими.
5. Экраны свёрстаны под планшет и альбомную ориентацию.
6. Поле пароля принимает буквы, цифры и символы.
7. Приложение называется «Krinik Tribit», у него своя розовая иконка.

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

Скачайте APK на странице [Releases](https://github.com/MikalaiKryvusha/KrinikTribitApp/releases): один подписанный APK
для всех 64-битных Android-устройств. Сначала удалите официальное приложение Tribit (подпись другая), затем установите
Krinik Tribit и пользуйтесь. Первый релиз выходит с шагом 7 дорожной карты.

<a name="ru-4"></a>

### 4. Дорожная карта

| № | Шаг | Состояние |
|---|---|---|
| 1 | Разведка: 2648 отзывов Google Play, языки перевода, боли официального приложения | ✅ сделано |
| 2 | Патчи: вылет на эквалайзере, геолокация в обоих местах, экраны при масштабе, символы в пароле, название, иконка | ✅ написаны, на устройстве пока не проверены |
| 3 | Первая патченая сборка на планшете автора с колонкой StormBox Blast 2 | 🔧 следующий |
| 4 | Тексты: наши в файлах ресурсов вместо серверных и зашитых в код; английский и русский руками | 🔧 разведка |
| 5 | Вёрстка под планшет и альбомную ориентацию | 🔧 разведка |
| 6 | Вылеты, обрывы подключения, что из присланного сервером Tribit нужно приложению | 🔧 разведка |
| 7 | Сборки debug и release, первый подписанный релиз на GitHub | 🔲 в плане |

<a name="ru-5"></a>

### 5. Собрать самому

В репозитории лежат патчи и скрипт сборки; официальный APK вы берёте со своего устройства. Нужны Git Bash под Windows,
JDK 21, Android SDK platform-tools (`adb`) и build-tools `36.0.0`, Python 3 и [apktool](https://apktool.org), сохранённый
как `tools/apktool.jar`. `build.sh` ищет JDK 21 и build-tools по стандартным путям Windows; другие пути задаются
переменными `JAVA_HOME_KRINIK` и `ANDROID_BUILD_TOOLS`.

```bash
adb shell pm path com.thousandshores.tribit      # где лежат части APK официального приложения
adb pull <каждый путь> original-apk/              # base.apk и каждый split_*.apk
bash build.sh                                     # разобрать, пропатчить, собрать, подписать весь набор одним ключом
adb uninstall com.thousandshores.tribit           # оригинал нужно удалить первым, так как подпись другая
adb install-multiple out/signed/*.apk
```

Вход по почте работает как раньше. Вход через Google и Facebook, вероятно, не сработает: он привязан к подписи Tribit.

<a name="ru-6"></a>

### 6. Карта проекта

| Путь | Что там |
|---|---|
| `patches/` | патчи к официальному приложению; каждый падает, если его место в коде сдвинулось |
| `build.sh` | сборка: разобрать, пропатчить, собрать, выровнять, подписать |
| `researches/` | отзывы Google Play, языки, боли официального приложения |
| `testcases/` | что и как проверять на планшете |
| `design/` | исходник иконки |

<a name="ru-7"></a>

### 7. Правовая информация и благодарности

1. Krinik Tribit не связан с Tribit и Thousandshores. Tribit — их товарный знак.
2. [apktool](https://apktool.org) и [jadx](https://github.com/skylot/jadx) — инструменты, которыми официальное приложение
   читается и патчится; в репозиторий они не входят.
3. Проект ведётся по [KAIF](https://github.com/MikalaiKryvusha/KAIF) — фреймворку работы с ИИ-агентом.

Автор: Николай Кривуша (Krinik).

---

<a name="chinese"></a>

<h2 align="center">Krinik Tribit</h2>

<p align="center"><b>修好了的 Tribit 音箱应用——来自大家，服务大家</b><br>
开源 · 不闪退 · 无需定位 · 适配平板和大屏 · 通顺的翻译</p>

<p align="center">
  <a href="#zh-1"><img src="https://img.shields.io/badge/%E5%B9%B3%E5%8F%B0-Android-3DDC84.svg" alt="平台：Android"></a>
  <a href="#zh-1"><img src="https://img.shields.io/badge/%E9%9F%B3%E7%AE%B1-Tribit-FF1A8C.svg" alt="音箱：Tribit"></a>
  <a href="#zh-4"><img src="https://img.shields.io/badge/%E7%8A%B6%E6%80%81-%E6%97%A9%E6%9C%9F%E5%BC%80%E5%8F%91-orange.svg" alt="状态：早期开发"></a>
  <a href="https://github.com/MikalaiKryvusha/KAIF"><img src="https://img.shields.io/badge/%E6%A1%86%E6%9E%B6-KAIF-7F52FF.svg" alt="框架：KAIF"></a>
</p>

[Read in English →](#english) · [Читать по-русски →](#russian)

**Krinik Tribit** 是修好了缺陷的官方 Tribit 音箱应用。它能控制官方应用支持的所有 Tribit 音箱，而且不闪退、关闭定位也能找到音箱、
在手机和平板上完整显示每个界面，英文和俄文翻译也通顺自然。这个项目始于作者的一台平板：在那台平板上，官方 Tribit 应用 5.0.0 版
一点「创建我的 EQ」就闪退，搜索音箱必须开定位，界面底部还被裁掉。

目录：[1 修复内容](#zh-1) · [2 官方应用的问题](#zh-2) · [3 下载](#zh-3) · [4 路线图](#zh-4) · [5 自行构建](#zh-5) ·
[6 项目结构](#zh-6) · [7 法律声明与致谢](#zh-7)。

<a name="zh-1"></a>

### 1. 修复内容

1. 点「创建我的 EQ」不再闪退：不带编号的预设名会被跳过。
2. 关闭定位也能找到并连接音箱——无论是权限界面，还是以前拒绝搜索的内置蓝牙库。
3. 放大系统显示大小后，每个界面都能完整显示：界面按屏幕原生像素密度绘制。
4. 文字放在资源文件里，由人工翻译；服务器下发的错误文字和代码里残留的中文都换成了我们的文字。
5. 界面适配平板和横屏。
6. 密码框接受字母、数字和符号。
7. 应用名为「Krinik Tribit」，有自己的粉色图标。

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

在 [Releases](https://github.com/MikalaiKryvusha/KrinikTribitApp/releases) 页面下载 APK：一个签名的 APK，适用于所有 64 位
Android 设备。先卸载官方 Tribit 应用（签名不同），再安装 Krinik Tribit 即可使用。首个正式版随路线图第 7 步发布。

<a name="zh-4"></a>

### 4. 路线图

| # | 步骤 | 状态 |
|---|---|---|
| 1 | 调研：2648 条 Google Play 评论、翻译语言、官方应用的问题 | ✅ 已完成 |
| 2 | 补丁：均衡器闪退、两处定位要求、显示缩放下的界面、密码符号、应用名、图标 | ✅ 已写好，尚未在设备上实测 |
| 3 | 在作者的平板和 StormBox Blast 2 上运行第一个补丁版本 | 🔧 下一步 |
| 4 | 文字：用资源文件里我们的文字替换服务器下发和代码写死的文字；英文和俄文人工翻译 | 🔧 调研中 |
| 5 | 平板和横屏布局 | 🔧 调研中 |
| 6 | 闪退、断连，以及 Tribit 服务器到底用来做什么 | 🔧 调研中 |
| 7 | debug 和 release 两个版本，GitHub 上的首个签名正式版 | 🔲 计划中 |

<a name="zh-5"></a>

### 5. 自行构建

本仓库包含补丁和构建脚本；官方 APK 请从你自己的设备上导出。需要 Windows 上的 Git Bash、JDK 21、Android SDK
platform-tools（`adb`）和 build-tools `36.0.0`、Python 3，以及保存为 `tools/apktool.jar` 的 [apktool](https://apktool.org)。
`build.sh` 默认在 Windows 的标准路径下查找 JDK 21 和 build-tools；路径不同时，用环境变量 `JAVA_HOME_KRINIK` 和
`ANDROID_BUILD_TOOLS` 指定。

```bash
adb shell pm path com.thousandshores.tribit      # 官方应用各个 APK 分包所在的位置
adb pull <每个路径> original-apk/                 # base.apk 和每个 split_*.apk
bash build.sh                                     # 解包、打补丁、重新打包、用同一把密钥给整组签名
adb uninstall com.thousandshores.tribit           # 签名不同，必须先卸载原版
adb install-multiple out/signed/*.apk
```

邮箱登录照常可用；Google 和 Facebook 登录很可能不行，因为它们绑定了 Tribit 自己的签名。

<a name="zh-6"></a>

### 6. 项目结构

| 路径 | 内容 |
|---|---|
| `patches/` | 官方应用的补丁；代码位置一旦变动，补丁会报错退出 |
| `build.sh` | 构建：解包、打补丁、重新打包、对齐、签名 |
| `researches/` | Google Play 评论、翻译语言、官方应用的问题（俄文） |
| `testcases/` | 在平板上检查什么、怎么检查（俄文） |
| `design/` | 图标源文件 |

<a name="zh-7"></a>

### 7. 法律声明与致谢

1. Krinik Tribit 与 Tribit 及 Thousandshores 没有任何关联。Tribit 是其商标。
2. [apktool](https://apktool.org) 和 [jadx](https://github.com/skylot/jadx) 是用来读取和修补官方应用的工具，不包含在本仓库中。
3. 本项目使用 [KAIF](https://github.com/MikalaiKryvusha/KAIF)（一个与 AI 智能体协作的框架）管理。

作者：Mikalai Kryvusha (Krinik)。
