# Исследование 06 — что присылает сервер Tribit и без чего приложение не обойдётся

> **Создан:** 2026-10-16 · **Родитель:** researches/03_tribit_app_pains.md (разделы 9–10) · **Статус:** разведка · **Вовне:** —
>
> Приказ владельца: «изучим, что такого незаменимого блять и ценного присылает сервер». Только чтение
> декомпиляции, **ни одного запроса к серверам Tribit**. Пути кода — от
> `decompiled/jadx-base/sources/com/thousandshores/tribit/` (если не сказано иное), smali — `work/base/smali_classes5/`.

## Ответ одной строкой

Незаменимо одно: **файлы прошивки** (и список изменений к ним). Управлению колонкой по Bluetooth сервер
не нужен вовсе: ни один запрос не участвует в связи с колонкой, список поддерживаемых моделей зашит в APK.
Всё остальное — машина аккаунта, облачная копия того, что и так лежит в телефоне, картинки и
справка, тексты интерфейса, телеметрия. Режут это пять заслонов, и все пять снимаются патчем.

---

## 1. Перечень: что приложение вызывает

**Как считали** (скрипты только читают файлы, лежат в черновике сессии):

```
cd D:/work/ai_sandbox/KrinikTribit                                               # скрипты лежат в tools/recon/
python -I tools/recon/endpoints.py        decompiled/jadx-base/sources   # пути api-*, Retrofit, зашитые URL
python -I tools/recon/callsites.py        decompiled/jadx-base/sources   # вызов EasyHttp → модель запроса
python -I tools/recon/models_used.py      decompiled/jadx-base/sources   # какие модели вообще создаются
python -I tools/recon/resp_types.py       decompiled/jadx-base/sources   # модель → тип ответа
python -I tools/recon/thirdparty_hosts.py decompiled/jadx-base/sources   # хосты внутри чужих SDK
```

**Итог подсчёта:**

- Retrofit в своём коде не используется (0 аннотаций). Сеть идёт через EasyHttp (`com.hjq.http`):
  каждая модель из `http/model/` реализует `IRequestApi.getApi()`.
- Моделей запросов 57, строк-путей 54. Это 53 пути плюс вариант `produCateByClientPre` для их
  предрелизной среды.
- Вызовов `EasyHttp.get/post/delete` в своём коде 85.
- Создаются в коде 51 модель, 6 мёртвых (`EqSet`, `EquipCategory`, `FaceBookLogin`, `WxLogin`,
  `PostUiMode`, `QueryRating`).
- Живых путей **48**, реально уходят в сеть **47**. Аналитика `synchPointStaticTribit` собирается, но
  `UpdateUtils.postPoint` пустой (`utils/UpdateUtils.java:67`), так что эти события не отправляются.
- Хост `https://gateway.tribit.com/` (`http/server/ReleaseServer.java:10`). Тестовый
  `testingtribit.1000shores.cn` включается только флагом `IS_TEST`.
- Сеть настроена так (`TribitApp.initNetWork`): повтор 3 раза с паузой 14 с, и только при таймауте
  (`com/hjq/http/callback/BaseCallback.java:75`). Сертификаты не проверяются вообще: доверие ко всем
  (`com/hjq/http/ssl/HttpSslFactory.java:47-49`, `UnSafeTrustManager`) и `generateUnSafeHostnameVerifier`.

### Таблица (все пути от `gateway.tribit.com/`; класс — см. раздел 2)

| Кл. | Путь | Шлёт | Возвращает | Экран / кто зовёт | Где |
|---|---|---|---|---|---|
| B | `api-equip/thirdApi/equip-anon/produCateByClient` | — | `List<ProductInfo>`: productId, имя, модель, URL логотипов, `productFaqUrl`, `isUpgrad`, тексты удачной/неудачной прошивки | главный экран при старте; кэш в LitePal и SP `<имя>info` | `ViewModelMainNew.java:309`, `ViewModelCheck.java:50` |
| B | `…/equip-anon/queryAllThridProducts` | — / `productName` | `List<SupportInfo>` (те же поля) / `List<ProductFaqBean>` (ссылки FAQ и инструкции JSON-ом) | диалог «поддерживаемые устройства», тексты после прошивки; кнопки FAQ на экране колонки | `ViewModelMainNew.java:508`, `ViewModelDeviceBts.java:815` |
| B | `…/equip-anon/secondCategorys` | id категории | `List<CategoryBean>`: категория, картинка, модели | «не нашли устройство» / помощь | `ViewModelCheck.java:89` |
| B | `…/equip-anon/categorys` | — | — | **мёртвый** | `http/model/EquipCategory.java:32` |
| C | `api-app/api/checkFirmwareUpgrade` | os=2, версия прошивки, пакет, `Tribit`, язык, имя модели | `AppVersionBean.lastUpgradeInfo`: versionName/Code, changeLog, **`ossUrl`** (файл прошивки), size, upgradeIsForce | экран колонки, «информация об устройстве» | `ViewModelDeviceBts.java:428`, `ViewModelDeviceInfo.java:370` |
| C | `api-app/api/otaHistoryUpRecords` | модель | `List<UpgradeBean>` — история прошивок | информация об устройстве | `ViewModelDeviceInfo.java:821` |
| D | `api-uaa/oauth/token` | grant_type=password, client `Tribit/Tribit`, email, **пароль в строке URL**, язык, модель телефона | `LoginBean`: access_token, expires_in | вход, тихий перевход | `ViewModelLogin.java:309`, `ViewModelMainNew.java:616`, модель `EmailLogin.java:104` |
| D | `api-user/…/tribit-users/visitorLoginOfTribit` | **MAC или ANDROID_ID**, язык, модель, канал, версия, ОС | `LoginBean`: username, loginToken | «Visitor Login», автогость на заставке | `modulelogin/viewmodel/ViewModelFirst.java:137`, `ViewModelMainNew.java:669` |
| D | `…/tribit-users/whetherLogAnoLocat` | email, модель, токен | `Boolean` «вошёл с другого телефона» | после «Invalid access token» | `ViewModelMainNew.java:570` |
| D | `api-uaa/oauth/remove/token` | токен | — | «Выйти» | `modulemine/viewmodel/ViewModelMine.java:232` |
| D | `api-uaa/…/googleLogin/checkGoogleEmailAccBingsTribit` | email Google | `ThirdLoginBindCheck` | вход через Google | `ViewModelLogin.java:142` |
| D | `…/faceLogin/…`, `…/weiXinLogin/…` | — | — | **мёртвые** (SDK Facebook и WeChat в APK нет) | `FaceBookLogin.java:44`, `WxLogin.java:44` |
| D | `…/tribit-users/getUserOfSpNeerInfoTribit` · `saveOrUpdateBySpNeerTribit` | email · ник, аватар, страна | `UserInfoBean` | профиль | `ViewModelLogin.java:195`, `ViewModelMine.java:70,179` |
| D | `checkEmailAccountRegTribit` · `checkEmailCodeTribit` · `resendVerCodeByRegTribit` · `saveUserAccountRegBySpNeTribit` | email, код, пароль в URL, телефон | `Object` / `LoginBean` | регистрация | `ViewModelRegister.java:145,273,299`, `ViewModelVerifaicationCode.java:177,225` |
| D | `checkThridEmailAccountRegTribit` · `saveUAccountThridByBindsTribit` | email Google, пароль | `BindEmailResultBean` | привязка Google к email | `ViewModelBindEmail.java:57`, `ViewModelSetNewPassword.java:171` |
| D | `checkEmailBackPwdTribit` · `resendVerCodeByBackPwdTribit` · `backPwdByAccountSpNeTribit` | email, код, новый пароль | `Object` | «забыли пароль» | `ViewModelForgetPassword.java:91,119,170` |
| D | `checkApplyCancellationTribit` · `checkCancelEmailCodeTribit` · `checkCancelPwdAndReportTribit` · `thridsDayWithinDoTribit` | email, код, пароль, причина | `Object` / `LoginBean` | удаление аккаунта и отмена удаления в течение 30 дней | `ViewModelSettings.java:112`, `ViewModelVerifaicationCode.java:249,288`, `ViewModelSetNewPassword.java:314`, `ViewModelLogin.java:486` |
| E | `api-app/api/lang/getLangInfoBySchemaOrLangKey` | `Tribit`, язык | словарь `ключ → строка` в SharedPreferences | **каждый запуск**, заставка; настройки | `ViewModelFirst.java:72`, `ViewModelSettings.java:143` → подробно в researches/04 |
| F | `api-app/api/userFeedback/saveUserFeedBackRecordTribit` | текст, email или MAC/ANDROID_ID, телефон, ОС, язык, прошивка | — | «обратная связь» | `ViewModelFeedBack.java:181`, `utils/DateUtils.java:886,950` |
| F | `…/userFeedback/autoReportErrorLogTribit` | ссылка на **logcat своего процесса** (500 строк) | — | при отправке отзыва | `utils/DateUtils.java:435,474` |
| F | `api-file/uploadtoken/getUploadToken` | md5 файла | токен Qiniu → загрузка в облако Qiniu | фото и видео отзыва, аватар, логи | `ViewModelFeedBack.java:88`, `ViewModelMine.java:112` |
| F | `api-app/api/message/getUserOfMsgRecords` · `getFeedMsgDetailsByFeedId` · `msgInfoNoShow` · `saveUserReplayMsgRecord` | id | переписка с поддержкой | «сообщения» | `ViewModelMessage.java:87,132`, `ViewModelMessageDetail.java:70,166` |
| F | `api-app/thirdApi/evaluser/synchEvalUserTribit` | оценка | `RatingBean` | диалог «оцените нас» | `utils/DialogDefault.java:378` |
| F | `api-usertrain/thirdApi/point/synchPointStaticTribit` | код события, версия, email, модель | — | собирается, **не уходит** (`postPoint` пуст) | `utils/UpdateUtils.java:67,238` |
| F | `…/evaluser/getEvalUserTribit`, `…/gestureuser/synchGestureUserTribit` | — | — | **мёртвые** | `QueryRating.java:23`, `PostUiMode.java:33` |
| G | `api-app/api/checkUpgrade` | версия **приложения**, пакет, канал | `LastUpgradeInfo`, `upgradeIsForce` | старт главного экрана, настройки | `ViewModelMainNew.java:446`, `ViewModelSettings.java:58` |
| G | `api-nebulacloud/token?externalUserId=` | id пользователя | `AiToekn` → SDK Nebula AI | экраны AI-перевода | `ai/viewmodel/ViewModelAi.java:114` |
| G | `api-equip/thirdApi/equalizer/getUserDeviceEqualizerByAccTribit` · `synchDeviceEqualizerTribit` · `sortDeviceEqualizerTribit/` · `removeDeviceEqualizer/` | email, productId, MAC колонки, 10 полос | `List<EqualizerBean>` | облачная копия своих эквалайзеров | `ViewModelEqlist.java:91,244,280`, `utils/UpdateUtils.java:569` |
| G | `api-equip/thirdApi/persound/getUserPerSoundsTribit` · `synchPerSoundTribit` · `sortPerSoundTribit` · `removePerSound/` | email, MAC, профиль L/R | `List<SoundBean>` | облачная копия профилей слуха (Audiodo) | `ViewModelSoundManager.java:67,103,136,168`, `ViewModelSound.java:71,110` |
| G | `api-equip/…/equip-anon/synchSpnerUserEquipsTribit` · `userUnbindingDeviceTribit` · `getUserEquipBySpAccountTribit` | email, **MAC колонки**, имя, прошивка, модель телефона | `DeviceSynchBean` / `List<DeviceBean>` | привязка колонки к аккаунту; список устройств для формы отзыва | `ViewModelDeviceBts.java:507,541`, `utils/UpdateUtils.java:493,538`, `ViewModelFeedBack.java:253` |

**Вне шлюза** (адреса зашиты в код или приходят в ответе):

- Файл прошивки по `ossUrl` из ответа: качается FileDownloader'ом в `utils/ui/dialog/DeviceUpdateNewDialog.java:730`.
- Картинки моделей по URL из `ProductInfo`, грузит Glide.
- Облако Qiniu (адрес внутри SDK).
- Nebula AI: `https://nebulacloud.zen110.com/` (`ViewModelAi.java:88,96`, SDK `com/qianan/sdk`) и
  `wss://translate.nebula-ai.net` (`activity_ai_main.xml:7`).
- Справка в WebView: `https://gtwt.1000shores.cn/tribit_help_{zh,en}/` (`utils/UpdateUtils.java:415`,
  `DeviceHelpNewActivity.java:362`, `MineFragment.java:477`).
- Политика конфиденциальности и условия: `saasadmin.tribit.com/tribit_privacypolicy/…` (`utils/ui/PrivateTextUtil.java:344-353`).
- Простые ссылки, которые открывает сам пользователь: `tribit.com`, `audiodo.com`, Google Play, `sj.qq.com`.

---

## 2. Классы: что от чего зависит

| Класс | Путей (живых) | Суть |
|---|---:|---|
| **A** управление колонкой по BT | **0** | Ни одного. Всё управление идёт по Bluetooth |
| **B** каталог моделей | 4 (3) | имена, картинки, ссылки FAQ, тексты после прошивки |
| **C** прошивка | 2 (2) + файл | что прошивать и откуда скачать |
| **D** аккаунт | 22 (20) | вход, гость, регистрация, пароли, удаление, «вошёл с другого телефона» |
| **E** тексты | 1 | см. researches/04 |
| **F** телеметрия и поддержка | 11 (8, уходят 7) | отзывы, логи, переписка, оценка, события |
| **G** прочее | 13 (13) | проверка версии приложения, AI-токен, облачная копия EQ, слуха и списка колонок |

**A — проверено.** Поддержка модели не зависит от сервера:

- Список из 25 имён зашит в `com/thousandshores/bluetoothlib/utils/DeviceConstant.java:10-11`.
  `isSupportedDevice` (`:13`) — простой `switch` по имени.
- По этому списку фильтруется поиск (`bluetoothlib/BtClient.java:359,377`) и выбирается подключение
  (`MainNewActivity.java:3240`).
- Тип экрана берётся из `devicePage` (`:145`), десять полос эквалайзера — из `isEqSize10` (`:218`).
- Протокол, UUID и пресеты лежат в коде (03, раздел «протокол»; `EqButton56Activity:343,366`).
- Список своих колонок локальный: `queryEquipList` → `localEquipList` → LitePal `DeviceBean`
  (`ViewModelMainNew.java:269-287`).
- Свои эквалайзеры и профили слуха тоже локальные: `EqualizerBean` и `SoundBean` наследуют
  `LitePalSupport`, у эквалайзера флаг `needUpload`.

**B — проверено жёстко.** Из ответа каталога код берёт четыре вещи:

- картинку модели: `DeviceSearchNewAdapter.java:50`, `UpdateUtils.deviceImage:218`. Без неё
  показывается заглушка `R.mipmap.ic_deviceloading`;
- `productId` для облачных запросов: `DateUtils.getProductId:517`. Если каталога нет, подставляется
  зашитый `"1336582235599065105"`;
- ссылки FAQ: `BtsInfoNewActivity.java:2014`;
- тексты «прошивка удалась/не удалась»: `DeviceUpdateNewDialog.java:660`, `UpgradeFailedPopup.java:150`.

Флаг `isUpgrad` код не читает. Без сети каталог берётся из LitePal (`ViewModelMainNew.java:293-306`).
Картинок моделей в APK нет ни одной (в `res/` по маске имён — ноль). Параметров протокола, пресетов и
конфигурации модели **с сервера не приходит**.

**C.** Цепочка обновления прошивки:

1. `checkFirmwareUpgrade` возвращает `ossUrl`.
2. `DeviceUpdateNewDialog.downloadFile:707` качает zip.
3. `startDfu:823` распаковывает его.
4. `BtsInfoActivity.onStartDfu:1770` → `setDfuFile` передаёт файл в OTA-движок: Jieli
   (`com/jieli/jl_bt_ota`), Bluetrum (`com/bluetrum/fota`) или Qualcomm GAIA (`com/qualcomm/qti`).

Шьётся по Bluetooth, сервер нужен только как источник файла. В диалоге уже есть ветка «файл задан
через `uri`» (`DeviceUpdateNewDialog.java:717-724`), которая обходит скачивание.

---

## 3. Заслоны: где приложение отказывается работать

Запускается `modulelogin/activity/FirstActivity`. Новый интерфейс включён: `SConfig.IS_NEW_UI_SHOW = true`
(`constant/SConfig.java:11`), `is_new_ui` по умолчанию `true`. Поэтому реальный путь идёт через
`FirstNewActivity`, `LoginNewActivity` и `MainNewActivity`.

| # | Заслон | Где | Что видит человек |
|---|---|---|---|
| З1 | Заставка ждёт словарь языка **при каждом запуске**: при включённой сети дальше пускает только по `stringResult == 1` | `FirstNewActivity.java:153-161,182`; `ViewModelFirst.java:72-112` | Сервер висит — заставка до ~80 с (4 попытки по 10 с таймаута OkHttp + 3 паузы по 14 с; оценка по конфигу): это и есть «server timed out». Сервер ответил без данных — `setValue(2)` (`ViewModelFirst.java:81`), тост `getStringResources …`, **заставка навсегда** |
| З2 | Нет токена: без сети не пускает, с сетью тихо создаёт гостя на MAC или ANDROID_ID | `FirstNewActivity.java:221-232,249-265` | Без сети тост «Network connection failed. Please check your network.», остаётся на заставке. С сетью при ошибке тост «login failed» |
| З3 | Первый запуск: «START» один раз ставит `is_agree_private` и открывает вход. Все три кнопки входа (email, Google, «Visitor Login») требуют сети | `FirstNewActivity.java:190-191`; `LoginNewActivity.java:357-371,404-408,497-498` | Без их сервера войти в приложение впервые нельзя совсем, даже гостем. Согласие спрашивают **один раз**, а не при каждом запуске; после очистки данных — снова |
| З4 | Выброс на вход **в любой момент** по тексту ответа сервера | `http/model/RequestHandler.java:103-140` | «Offsite access token» (вошли с другого телефона) — стирает токены, экран входа. «Full authentication» — стирает токены **и гостевой токен**, экран входа. «Invalid access token» — `ReloginEvent` → `MainNewActivity.java:645` → `whetherLogAnoLocat`: если `true`, открывается **старый** `LoginActivity` (`ViewModelMainNew.java:581-587`). Это механизм 74 отзывов «разлогинивает». Аккаунт односеансовый: вход со второго телефона выбивает первый |
| З5 | Принудительное обновление приложения | `MainNewActivity.java:233-242,489`; `utils/ui/dialog/AppUpdateNewDialog.java:49` | Если `upgradeIsForce == 1`, окно обновления без крестика и не закрывается касанием. Кнопка ведёт в Google Play: **наш форк заменили бы оригиналом** |
| З6 | Гость урезан | `utils/DialogDefault.java:111-121` (`checkLoginType`) | «You can't use this function without registration…» — только в профиле, отзыве и безопасности (`MineFragment.java:88,240`, `FeedBackNewActivity.java:136`, `UserInfoNewActivity.java:117`). **Колонку гость не теряет** |

После входа без сети работает всё: список колонок, управление, свои эквалайзеры. Ошибки сети в
этих местах просто печатаются в лог (`ViewModelDeviceBts.java:439-442,838-842`).

Попутно о том, что получает сервер:

- Пароль хранится в SharedPreferences как Base64 под ключом `token_word` — для тихого перевхода
  (`ViewModelLogin.java:330`, `ViewModelMainNew.java:608-616`).
- Пароль уходит **строкой URL** (`EmailLogin.java:104`, то же `SaveEmailAccount`, `BackPassWord`,
  `SaveAccountThrid`).
- Сертификаты TLS не проверяются (раздел 1), то есть пароль перехватывается в любой чужой Wi-Fi.
- Логирование EasyHttp включено (`setLogEnabled(true)`).

---

## 4. Чужие SDK, которые звонят наружу (манифест и код)

| SDK | Что делает | Где | Живой? |
|---|---|---|---|
| Firebase Analytics + Measurement | события, рекламный ID (`AD_ID`, `ACCESS_ADSERVICES_*`), `app-measurement.com`, `googleadservices` | манифест: `AppMeasurement*`, `AnalyticsConnectorRegistrar` | да, включается сам (выключателя `*_collection_*` в манифесте нет) |
| Firebase Crashlytics + Sessions | крэши, сессии (`firebase-settings.crashlytics.com`) | `CrashlyticsRegistrar`, `FirebaseSessionsRegistrar` | да |
| Firebase In-App Messaging | сервер может показать всплывающее окно в приложении | `FirebaseInAppMessaging*Registrar` | да |
| Firebase Cloud Messaging | пуш; ссылка `PushMessage_Page_Url` сохраняется и открывается | `http/server/MyFirebaseMessagingService.java:80`, `MainNewActivity.java:606`, `FirstNewActivity.java:166` | да |
| Firebase Installations, ABT, datatransport | ID установки, A/B-тесты, транспорт | манифест | да |
| Google Sign-In (`gms.auth`) | вход через Google | `modulelogin/thirdlogin/GoogleLoginManager.java` | да. В нашей подписи **не заработает** (03) |
| Google Places, Maps (`maps.googleapis.com`) | автодополнение адреса | `AutocompleteActivity` в манифесте | компонент есть, вызова в своём коде не нашли |
| Qiniu | загрузка файлов в китайское облако | `TribitApp.onCreate` → `QiniuUploadManager.init()` | да, при отзыве и аватаре |
| Nebula AI (`com/qianan/sdk`) | AI-перевод, токен через шлюз | `ai/viewmodel/ViewModelAi.java:88-114` | да, на экранах AI |
| FileDownloader (liulishuo) | качает прошивку | `TribitApp.fileDownload` | да |
| Umeng, Bugly, DoKit, Flutter, LeakCanary | — | `TribitApp.java:84-107`: `initUmSdk`, `initBugly`, `doKitInit`, `flutterInit` **пустые**; `LeakCanary` — заглушка `DISABLED`; от Umeng остался только `UMENG_CHANNEL` | **мертвы** |
| Facebook, WeChat | — | строка `facebook_app_id` есть, SDK нет | мертвы |
| hjq Logcat | окно логов поверх приложения | `com.hjq.logcat.*` в манифесте | наружу не звонит; в релизе выглядит странно |
| Audiodo, Jieli, Bluetrum, Qualcomm GAIA | профиль слуха, OTA | ключ лицензии Audiodo локальный (`TribitApp.initApis`) | зашитых адресов в их коде не нашли |

---

## 5. Вердикт и патчи

### Что незаменимо, что вшить, что резать

| Класс | Вердикт | Почему |
|---|---|---|
| A | **Сервер не нужен** | всё по Bluetooth, список моделей в APK |
| B | **Вшивать незачем, можно резать** | без каталога теряются только картинки моделей (заглушка уже в APK) и ссылки FAQ. Снимок каталога без запроса к их серверу не получить, а для одной колонки владельца он не нужен. Если захочется картинку — нарисовать свою иконку |
| C | **Единственное незаменимое** | файлы прошивки есть только у них. Оставить как явную кнопку «проверить прошивку», которую нажимает сам владелец, либо прошивать своим файлом через готовую ветку `uri` |
| D | **Резать** | аккаунт ничего не даёт колонке. Нужен только чтобы пройти З2–З4 |
| E | **Решает researches/04** | — |
| F | **Резать целиком** | никакой пользы владельцу, наружу уходят MAC, email и логи |
| G | **Резать** | проверка версии опасна для форка (З5). AI — чужой сервис. Облачная копия EQ и слуха дублирует локальную БД |

### Патчи на заслоны (smali в `work/base/smali_classes5/com/thousandshores/tribit/`)

1. **П-офлайн-вход (З2, З3)** — `modulelogin/activity/FirstNewActivity.smali`, метод
   `checkToken()V`: всегда вызывать `ViewModelFirst.startMainActivity()`; если токена нет, сначала
   положить локальный фиктивный через `AccountTokenManager.insertOrUpdate` и `login_type="2"`. Так
   же — `onCreate$lambda$1` (кнопка START): сразу на главный экран, минуя `LoginNewActivity`.
   *Риск:* средний. Любой оставшийся запрос с фиктивным токеном получит «Full authentication», и тогда
   сработает З4 — поэтому только вместе с П-без-выброса. Экран `PermissionNewActivity` при первом
   входе пропадёт; разрешения BT спросит экран колонки — проверить на Титане.
2. **П-без-заставки-языка (З1)** — там же, `onCreate`: ветку `NetworkUtils.isConnected()` →
   `getStringResources` заменить на `showAgree()`. *Риск:* низкий для работы, но тексты сервера
   пропадут (решение — в 04).
3. **П-без-выброса (З4)** — `http/model/RequestHandler.smali`, `requestSuccess`: убрать три ветки
   `resp_msg.contains(...)` (`:103-140`), возвращать `fromJson`. Плюс `MainNewActivity.deviceDelete(ReloginEvent)`
   → `return-void`. Попутно уходит NPE: `resp_msg.contains` при пустом `resp_msg`. *Риск:* низкий,
   облачные функции молча перестанут работать при протухшем токене.
4. **П-без-обновлений (З5)** — `ViewModelMainNew.smali`, `checkUpdate(LifecycleOwner;String)V` →
   `return-void`; то же в `modulemine/viewmodel/ViewModelSettings` (вызов `:58`). *Риск:* нулевой.
   **Нужен в любом случае, иначе их сервер уведёт пользователя на оригинал.**
5. **П-тишина (F, G, Firebase)** — `http/server/ReleaseServer.smali`, `getHost()`:
   вернуть `https://127.0.0.1/`. Все 47 запросов падают мгновенно (`ConnectException`), без 80-секундных
   ожиданий. В манифест добавить `firebase_analytics_collection_deactivated=true`,
   `firebase_crashlytics_collection_enabled=false`, `firebase_messaging_auto_init_enabled=false`,
   удалить регистраторы In-App Messaging и разрешение `AD_ID`.
   *Риск:* средний — вместе с шлюзом умирает и **проверка прошивки (C)**. Если её оставлять, вместо
   подмены хоста глушить по одному: `UpdateUtils.syncDevice`, `postEqInfo`, `DateUtils.uploadLogcat`,
   `ViewModelMainNew.getDeviceList/querySupportDevices` → `return-void`.
6. **П-прошивка-по-кнопке (C, необязательно)** — оставить `ViewModelDeviceBts.queryFireVersion`, но
   вызывать его только по нажатию. Либо дать выбор файла и отдать `uri` в `DeviceUpdateNewDialog`
   (ветка `:717`). *Риск:* высокий — кирпич колонки. Только с образом прошивки, снятым заранее, и
   отдельным решением владельца.

**Минимальный набор, чтобы приложение жило без сервера и без аккаунта:** П-офлайн-вход,
П-без-заставки-языка, П-без-выброса, П-без-обновлений. Это четыре метода, все из своего кода Tribit,
чужие библиотеки не трогаются. П-тишина — следующим шагом, когда владелец решит судьбу прошивки.
