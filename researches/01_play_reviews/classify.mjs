// Multilingual keyword classifier for Tribit Play reviews.
// Usage: node classify.mjs raw.json out.json [sampleTheme]
import fs from 'node:fs';

const raw = JSON.parse(fs.readFileSync(process.argv[2] || 'raw.json', 'utf8'));
const R = raw.reviews;

const rx = (s) => new RegExp(s, 'iu');

// ---- model detection ----
const MODELS = [
  ['StormBox Blast 2', 'blast ?2|sbb2|blast2|brast 2|blas 2|бласт ?2|блест 2|stormbox blast v5|blast \\(?gen ?2|tribit 2\\b'],
  ['StormBox Blast (1)', 'blast ?1\\b|blast \\(?one|blast 90|90 ?w|storm ?blast(?! ?2)|stormbox blast(?! ?2)|storm box blast(?! ?2)|strom ?box blast(?! ?2)|blaster|x blast|tribit blast(?! ?2)|the blast\\b|blast box|blast unit|stormapp blast|stormbit|бласт(?! ?2)|blast(?! ?2)'],
  ['StormBox Micro 2', 'micro ?2|micro2|micra 2|микро ?2|mico 2|sb ?micro 2|micros\\b'],
  ['StormBox Micro (1)', 'micro ?1\\b|micro \\(1st|micro box 1|stormbox micro(?! ?2)|storm ?box micro(?! ?2)|strombox micro(?! ?2)|микра 1'],
  ['StormBox Mini+', 'mini ?\\+|mini ?plus|mini \\+'],
  ['StormBox Mini', 'storm ?box mini(?! ?\\+| ?plus)|strombox mini(?! ?\\+| ?plus)|storm mini|stormbox mini\\b(?! ?\\+| ?plus)'],
  ['StormBox Pro', 'storm ?box pro|strombox pro|storm pro|stormbox pro|strom ?box pro'],
  ['StormBox 2', 'storm ?box ?2\\b(?!.*micro)|strombox ?2\\b|stormbox2|storm box 2|ic-bts30|шторм бокс 2'],
  ['StormBox Flow', 'flow\\b'],
  ['StormBox Lava', 'lava\\b'],
  ['StormBox Max', 'stormbox max\\b|storm box max\\b'],
  ['StormBox 360', '360'],
  ['StormBox (1, без номера)', 'storm ?box 1\\b|stormbox 1\\b|сторм бокс\\b|stormbox (?:speaker|\\(previously|still|not available|device)|tribit stormbox(?! ?(?:2|micro|mini|pro|blast|flow|lava|max|360))'],
  ['XSound Go', 'x ?sound ?go|soundgo|sound go|xsoundgo|x go speaker|bts20|bts38|xsound go'],
  ['XSound Plus 2', 'x ?sound ?plus ?2|xsound\\+ ?2|x sound\\+2|sound plus 2'],
  ['XSound Plus (1)', 'x ?sound ?plus(?! ?2)|tribit plus\\b'],
  ['XSound Mega', 'x ?sound ?mega|xsound maga|tribit mega|mega\\b'],
  ['XSound Surf', 'surf'],
  ['MaxSound Plus', 'max ?sound ?plus|soundmax plus|maxsound'],
  ['Pocket Go', 'po[ck]?[qk]?u?et ?go|pocketgo|poket go|poquet go'],
  ['ThunderBox', 'thunderbox'],
  ['PartyBox', 'party ?box'],
  ['FlyBuds 3 / 3S', 'fly ?bu[dt]s? ?3|flybud3|flybit 3|tribit 3 (?:ear)?buds|tribit3|solarbuds|flybuds f 3'],
  ['FlyBuds C1 / C1 Pro', 'c1 ?pro|fly ?buds ?c1|\\bc1\\b'],
  ['FlyBuds C2', 'c2\\b'],
  ['XFree Go / Tune', 'x ?free ?(go|tune)|xfre go'],
  ['QuietPlus', 'quiet ?plus'],
  ['MoveBuds H1', 'movebuds|h1 headphones'],
];
const modelRx = MODELS.map(([n, p]) => [n, rx(p)]);

// ---- themes ----
// each theme: id, title, test(text, review) -> bool
const T = [];
const add = (id, title, fixable, re, extra) => T.push({ id, title, fixable, re: re ? rx(re) : null, extra });

add('unsupported', 'Модель не поддерживается приложением / нет в списке / убрали поддержку', 'частично',
  "not (?:yet )?supported|isn'?t supported|doesn'?t support|does not support|no support|not support|unsupported|no software support|no app support|not listed|isn'?t listed|not in the list|not on the list|not included|isn'?t included|wasn'?t included|not on your list|not available|no option for|add (?:the )?(?:model|support|device)|add tribit|support (?:for|to) |please add|pls include|please include|make it for|when will .{0,30}support|still no .{0,20}support|compatib|not even supported|removed from compatible|не поддерж|поддержк[аи] (?:колонки|xsound)|нет в списке|колонки в списке нет|не все колонки|не для каждого|nicht unterstützt|nicht kompatibel|unterstützen sie|nicht alle produkte|keine appunterstützung|no es compatible|no tiene casi modelos|soportar al|agregen la compatibilidad|compatibilidad|não tem suporte|non compatible|incompatible|uniquement pour|non trova|nie widz|tidak suport|not suport|x suport|no auppoerted|kurang lengkap|tidak ada|不支持|分哪一個產品|only (?:compatible|for|shows) .{0,30}(?:product|device|model)|only what 5 products|very limited devices|doesn'?t have the devices|does not include any devices|doesn'?t have the tribit|don'?t have the tribit|my (?:tribit )?(?:speaker|device) (?:is )?not (?:supported|listed|compatible)|device not supported|my device not supported|why (?:your app )?(?:no|did not|didn'?t) support|not campatible|not compatable|was not on the list|nothing yet for|yok\\b|keine unterstützung|не входят в программу|no stormbox mini support|need to suoport|worst compatibility|where (?:is|are) (?:the |my )?(?:stormbox|flybuds|xsound|x sound)|still waiting for the update|waiting for my device|not showing\\.?\\?|no show tribit|not lidted|please consider|ni aparece|can'?t be found within|no compability|support für|plan to include|join all models|unterstützen täte|nur für 2|ne fonctionne pas avec|impossible d'ajouter|không support|need new update for|para cuando estará listo|pueden poner para|aren'?t synced|suddenly aren'?t supported|solo me apareció un modelo");

add('connect', 'Приложение не подключается к колонке / «Connection failed» / не находит устройство', 'частично',
  "connect|conect|conet|connt|pair|parinh|does(?:n'?t| not) (?:find|detect|recogni[sz]e|see|identify|pick up)|can'?t (?:find|see|detect)|cannot (?:find|detect)|could not add|unable to add|not able to add|can'?t add|cannot add|won'?t add|refuses to add|never finds|doesn'?t identify|not recogni|app (?:doesn'?t|does not|fails to) (?:show|find|see)|f>nd|подключ|соедин|не видит|не находит|сопряж|синхрониз|conectar|conecta|vincul|emparej|no (?:lo )?encuentra|no se conecta|não conecta|não encontrou|não reconhece|nao conecta|conex[aã]o|verbind|findet|erkennt|erkennung|connexion|connecter|détecter|appairer|associ|connett|non trova|non si connette|połącz|nie widzi|wykrywa, ale|nie dodaje|bağlan|baglan|เชื่อม|kết nối|không tìm|連|连|接続|sambung|tak dapat|nag connect|ไม่เจอ|error connection|connection error|connection failed|bluetooth pairing error|try again n try again|reconnecting|lost connection|不能用");

add('login_forced', 'Обязательный аккаунт/логин (зачем регистрация?)', 'да',
  "why (?:do (?:i|you|we) )?(?:need|have) (?:to )?(?:an? )?(?:account|login|log in|sign|register)|need(?:s)? (?:a )?login|login needed|requires? (?:a |mandatory )?(?:login|sign|account|registration|personal)|mandatory login|registration required|sign[- ]?in,? just|forc(?:e|ed|ing) (?:users )?(?:to )?(?:create|log|sign|register)|have to sign into|sign up,? so i did|don'?t want (?:to )?(?:sign|register|log)|refuse to log|unless you register|without (?:going|creating|an account)|account (?:is )?(?:required|needed)|wants a login|login screen is soo annoying|login pop ?up|pedir login|nicht mit mir|zwangsregistrierung|kontozwang|anmeldung erforderlich|account wird benötigt|registrierung|anmelden|zachem|зачем.{0,40}(?:регистр|аккаунт|логин|авториз)|без регистрации|регистрироваться|обязательно регистр|registro|registrarse|loggin|logearse|registrar|criar uma conta|fazendo login|ficar logando|rejestracji|wymuszona rejestracja|zaloguj|login.{0,20}(?:what for|why)|why can'?t it just work|data mining|sign up and login is required|tourist mode|guest|visitor|as a guest|ลงทะเบียน|регистрац|авторизац|ログイン|cuenta|compte|registration");

add('login_relog', 'Постоянно разлогинивает / логин и согласие с условиями при каждом запуске', 'да',
  "(?:log(?:in|ged)?|sign|terms).{0,40}(?:every ?time|each time|every single time|everytime|evertime|eveytime|again and again|all the time|every day|daily|repeatedly|keeps|constantly|over and over|100000 times)|(?:every ?time|each time|everytime|always|keeps?|frequently|constantly|often|quite often|sometimes).{0,40}(?:log ?in|log(?:ging|s|ged)? (?:me )?out|logout|sign(?:ed)? (?:back )?in|re-?login|asks? (?:for |me to )?(?:login|log|sign))|log(?:s|ged|ging)? (?:me )?out|logout|kicks me out|asking to sign back in|sign back in|forced to log in|login (?:pop ?up )?keeps|expired|logged in (?:a |on )?(?:different|another)|other device|another device|different device|already registered on another|кажд\\w* раз.{0,30}(?:вход|логин|учётн|аккаунт|авториз)|выкидывает из аккаунта|постоянно (?:слетает|требует)|слетает|регулярно требует входа|очень часто просит авторизац|просит авторизац|бросает.{0,10}аккаунт|throws me out of my account|re-login|toda hora|o tempo todo|vez ou outra tem que ficar logando|logar novamente|cada vez .{0,20}(?:loggear|iniciar)|se borra la cuenta|jedes mal|ทุกครั้ง|เกือบทุกครั้ง|log in แทบทุกครั้ง|ต้องล็อคอินใหม่|login lagi|minta log in berkali|za każdym razem|keeps logging|logged out by itself|log back into|re-?enter|każe się logować ponownie");

add('login_broken', 'Не удаётся зарегистрироваться/войти (код не приходит, пароль, регион, Google, «другое устройство»)', 'да',
  "can'?t (?:even )?(?:log|sign|register|create|make)|cannot (?:log|sign|register|create)|could(?:n'?t| not) (?:even )?(?:log|sign|register|create)|unable to (?:log|sign|register|create)|not able to (?:log|sign|register|create)|won'?t (?:let (?:me|you) )?(?:log|sign)|wouldn'?t let me sign|impossible to register|login (?:fail|error)|failed login|failure to log|login failure|longin failed|fails to login|doesn'?t (?:even )?let me (?:register|log|sign|make)|doesn'?t log you in|code (?:not|never)|never (?:received|get|got) .{0,30}(?:code|email|mail)|(?:security|confirmation|verification|activation|id) code|send code|receive code|get(?:ting)? (?:the )?code|code sent|password (?:has|format|field)|special character|only support number|strong passwords|password is only|select (?:your )?region|choose (?:a )?region|region|country|countries|log ?in with (?:gmail|google|facebook)|login via google|google pass|data parsing error|error 400|400 code|bad request|account (?:was )?(?:locked|gesperrt)|email (?:already|nicht|not)|email .{0,30}(?:registered|verifi)|logged in a different|не (?:могу|смог|получается) (?:войти|зарегистр|создать)|не авторизует|не даёт войти|не работает регистрация|не заходит в аккаунт|код авторизации|получить код|не удаётся|регион при регистрации|anmeldung (?:nicht|schlägt)|nicht registrieren|kein einloggen|login schlägt|verifizierungsmail|passwort|keine imternetverbindung|no puedo (?:entrar|iniciar)|no deja (?:registrarse|iniciar|entrar)|imposible registrarse|me rechaza mi correo|como creo una cuenta|ya no deja iniciar|não (?:consigo|estou conseguindo) (?:logar|fazer o log|entrar|efetuar)|não faz login|não está fazendo login|não consegue logar|não está enviando o código|impossible de m'enregistrer|impossible de me connecter après|non ci si riesce a registrare|nie da się utworzyć|ลงทะเบียนไม่ได้|ลงทะเบียนในแอพไม่ได้|ログインできません|can'?t login|cant login|cant log in|can'?t sign in|cannot login|i cant register|not able to create an account|unable to sign up|unable tot sign up|can'?t sign up|cannot create account|sign-up and login is required, but does not work|couldn'?t even log in|login failed|confirm\" button doesn'?t react|confirm. button|press(?:ing)? connect does nothing|the email section will not let me");

add('server', 'Зависимость от сервера/интернета: «server timed out», «server connection abnormal», нет офлайн-режима', 'да',
  "server|сервер|servidor|serveur|serwer|time ?d? out|timed out|abnormal|annormal|offline|off-line|оффлайн|офлайн|интернет|internet|without (?:an )?internet|sin conexión|bez internetu|ohne internet|internet connection|network|\\bred no|conexão com o servidor|login service|fora do ar|server down|servers are down|ไม่มีเน็ต|jaringan|wlan|mobilnetz|vpn|need an internet|need to be connected to your servers|server response");

add('crash_noopen', 'Вылетает / не открывается / зависает на логотипе или «Loading»', 'да',
  "crash|keeps stopping|keep stopping|always stopping|sigue (?:sin funcionar|fallando)|stopping|closes? (?:automatically|on its own|itself|the entire app|before opening)|closing on its own|quits|exit\\b|freez|frozen|\\bhang|hanging|abrir|nem abre|starten|fucionar|dejó de funcionar|dejo de funcionar|przestała działać|go past the login screen|no (?:puedo|me deja|hay manera de) entrar|ni siquiera me deja entrar|nunca entra|não consigo (?:mais )?entrar|ni se puede ingresar|เข้าไปตั้งค่าไม่ได้|error al abrir|nicht mal mehr|stuck (?:on|at) (?:the )?(?:logo|loading|starting|splash|yellow)|forever loading|keeps loading|loading (?:and loading|forever|status|screen)|perpetual load|indefinitely loading|infinitely|loads infinitely|stays at .loading|just loads|only loads|load(?:s|ing)? forever|nothing loads|doesn'?t (?:even )?(?:open|launch|load|start)|does not open|won'?t (?:even )?(?:open|load|start|launch)|wont open|not open(?:ing)?|cannot open|can'?t open|can not open|unable to open|app not opening|black screen|pantalla negra|yellow screen|żółty ekran|не открывается|не запускается|перестало (?:открываться|запускаться|загружаться|работать)|не загружается|не грузит|вылета|зависа|висит|виснет|повисло|не заходит|no (?:me )?(?:quiere )?abr|no abre|por q no me habr|se cierra|cierra sola|congelada|não abre|nao abre|não carrega|não sai do|parou de funcionar|trava|keluar sendiri|tak boleh buka|tak dapat buka|tidak bisa buka|stürzt|absturz|startet .{0,20}nicht|lädt (?:die app )?nicht|lädt nicht mehr|plante|si chiude|nie (?:chcę się )?załad|nie ładuje|zawiesza|เปิดไม่ได้|เด้งออก|เข้าไม่ได้|เข้าใช้งานไม่ได้|เข้ายาก|開不|閃退|forces close|force close|only tribit logo shown then exit|nothing happen when i try to open|click, nothing happens|keeps closing|freezes my phone|unresponsive|doesn'?t respond|not responding|sl[uo]w to load|hängen");

add('slow', 'Долгий запуск / тормозит / лагает', 'да',
  "slow|takes? (?:way )?(?:too |a lot of |so )?(?:long|time|ages|forever|\\d+)|seconds? to open|secs? to open|10-15|20-25|5-10 seconds|\\blag|laggy|lagging|input delay|taking too much time|hard to open|time to open|delay|медленн|долго|тупит|тормоз|лаги|lento|langsam|wolno|wolne działanie|ช้า|很慢|好很慢|loads slow|boot|takes too much time");

add('location', 'Требует геолокацию/GPS; на устройствах без GPS (планшеты) бесконечно просит «Location Access»', 'да',
  "location|gps|геолок|геодан|местополож|местоположен|standort|ubicaci[oó]n|localiza|localisation|localização|lokaliz|lokasi|posizione|ตำแหน่ง|位置|konum|\\bgeo");

add('tablet', 'Планшеты: не ставится из Play / не работает / ломается альбомная вёрстка; складные и DeX', 'да',
  "tablet|tablette|tableta|tabletu|tab ?s\\d|tab a\\d?|galaxy tab|tab\\b|\\b(?:mi|honor|redmi|poco|xiaomi|mate|magic ?|huawei|lenovo|realme|aldocube) ?pad|pad \\d|pad pro|pad se|magicpad|планшет|landscape|альбомн|foldable|fold ?3|unfolded|складн|dex\\b|chromebook|horizontal tablet|tab\\.");

add('privacy', 'Избыточные разрешения / сбор данных / «шпионское ПО» / реклама', 'да',
  "privacy|private|personal (?:data|info|information|details)|data (?:collect|mining)|collect(?:s|ing|ion)? .{0,20}(?:data|info)|spy|шпион|steal|leak|selling|sell(?:ing)? (?:it|ur|your)|resold|invasive|intrusive|too many permissions|permissions? (?:which|that)? ?(?:are|is)? ?not (?:required|necessary|needed)|excessive permissions|all (?:the|those) permissions|unnecessary|contacts|call history|phone records|camera|\\bmic\\b|credit card|\\bads\\b|advertis|реклам|werbung|publicidad|personal info|why do (?:you|they) need (?:my )?info|need info|info about me|my info|данн(?:ые|ых)|daten|datos personales|données|dados|dane osobowe|berechtigung|разрешени|permiso|permission|uprawnie|ovlaštenja|permisos|threat|chinese (?:app|servers|spyware|product)|tracker|datenschutz|wanze|phone home|nouvel ordre|renseignements");

add('eq_custom', 'EQ: свой эквалайзер нельзя создать/редактировать/сохранить; пресеты пропадают, сбрасываются, «Unnamed EQ»', 'да',
  "(?:custom|own|personali[sz]|benutzerdef|eigene|selbst erstellte|своего|свой|своём|свою|personaliz|castum|costum|自定义|自定義|unnamed|preset|пресет|presets|predetermin|preestablec|ecualizaciones|equalizações|edit|create|delet|save|sav(?:ed|ing)|lösch|borr|apag|удал|созда|сохран|редакт|editar|не настро|ปรับ eq|เพิ่ม eq|tambah).{0,60}(?:eq|equali|эквалайз|ecualiz|equaliz|égaliseur|korektor|aquliser|quliser|equelizer)|(?:eq|equali|эквалайз|ecualiz|equaliz|égaliseur|aquliser|quliser|equelizer).{0,80}(?:custom|own|personaliz|benutzer|unnamed|edit|creat|delet|sav|lösch|borr|apag|удал|созда|сохран|редакт|disappear|removes|reset|setzt sich|zurück|keeps (?:deleting|coming)|forget|forgets|non-?responsive|no effect|doesn'?t (?:work|show|light|load)|not (?:working|possible|show|load)|can'?t|cannot|не могу|недоступн|не помогает|用不了|不能|ไม่ขึ้น|error|bug|broken|messed|sounds? the same|same|одинаков|igual|gleich|no (?:se )?aplican|xbass off|turn them off|cuts in and out|stack up|second profile|line profile|names don'?t save|frequenc)|unnamed eq|custom eq|custom equali|preset[- ]?eq(?:ualizer)? doesn'?t|no eq presets|eq presets visible|can'?t open the preset|present eq|equalizer (?:is |was )?not (?:visible|show)|перестал отображаться эквалайзер|no aparecen los modos de equalización|não consigo acessar o equalizador|equalizador não funciona|eq не|eq 不能|ecualizador suena igual|xbass|x-bass|рок и парти настройки одинаковы|rock funktioniert nicht|equalizer setting on this app. no presets|can'?t adjust the equalizer while|equaliser .{0,30}reduces|wait(?:ing)? for the eq to load|eq setting page|changing the eq settings|eq (?:is )?non-responsive|isn'?t loading the eq|loose all your settings|lose all (?:your )?settings|doesn'?t remember anything|не сохраняет настройки|переключаются эквалайзеры|ปรับ eq ไม่ได้|eq ไม่ได้");

add('eq_limited', 'EQ: мало полос/диапазон (12–13 кГц, ±6 дБ), полосы custom ≠ пресетам, мало пресетов, нужен Bass/Mid/Treble', 'частично',
  "(?:eq|equali|эквалайз|ecualiz|equaliz|égaliseur|aquliser|quliser|geq|peq).{0,80}(?:limited|limit|more (?:bands|presets|options|setting)|band|полос|hz|khz|db|±|range|basic|minimal|poor|small|маленьк|weak|detailed|more flexib|options|lacks|lack|не хватает|mais|más|mehr|больше|regler|limiter|genre|harman|metal|vocal|treble|bass, ?mid)|(?:more|additional|new) (?:eq|equali[sz]er|preset)|lacks customisation of equaliser|limited (?:on the )?eq|eq is okay|eq ux|horizontal scrolling for the eq|12 ?khz|13 ?khz|16 ?k ?hz|\\+-6db|different frequenc|regulierbar|reverb|loudness|маленький эквалайзер|need more equaliser|equaliser settings are poor|preset (?:eq )?genre|download more equalizers|bass ,mid and treble");

add('fw_update_fail', 'Обновление прошивки через приложение падает / зависает («Unzip success») / не предлагается', 'частично',
  "unzip|(?:firmware|firware|firmare|fw\\b|прошивк|микропрограмм|software update|softwareupdate|update (?:my|the) (?:speaker|device|stormbox|micro|blast|flybuds)|update firmware|upgrade firmware|firmware upgrade|firmware update|firmwareupdate|обновление колонки|обновить колонку|actualiz\\w* (?:la |el )?(?:bocina|firmware)|atualizar a minha|mettre a jour (?:l'enceinte|le logiciel)|update devices|อัพเดทเฟิร์มแวร์|อัพ ?fw|update stormbox micro|can,t update|can'?t update|cannot update|not able to update firmware|неделю|снова не могу обновить|не обновляется|aktualisier).{0,80}(?:fail|stuck|eternity|never|doesn'?t|does not|won'?t|not (?:work|possible|offered|able)|unable|can'?t|cannot|abbricht|schlägt|fehl|не заканчивается|не обнов|no me deja|no actualiza|se queda|não consegui|incapable|ne change rien|redemande|ไม่ได้|again and again|always shows failed|everytime|every time|no option|no options|newest|latest version|rollback|confusing|30 mins|not seamless|tricky|1\\.2\\.8)|firmware upgrade don'?t work|upgrade firmware don'?t work|firmware update does not work|firware update fails|update fails|update failed|не обновляется с|обновление колонки начинается но не заканчивается|wrost app firmware update failed|can'?t update the firmware|cannot update firmware|not able to update firmware|ya no actualiza el firmware|can'?t upgrade|unable to connect and update|can't update stormbox|neither can update their firmware|не могу обновить|incapable de mettre|quiero actualizar y se queda|no me actualiza la bocina|impossibilité de mettre a jour|das software update schlägt");

add('fw_sound_worse', 'После обновления прошивки звук/громкость/бас/батарея/подсветка стали хуже; нет отката', 'нет (прошивка); откат — только если есть образы',
  "(?:update|upgrade|обновлен|обнов|actualizaci|atualiza|aktualiz|mise à jour|apdet|update|อัพเดท|cập nhật|прошивк).{0,80}(?:bass|бас|bajo|grave|sub|sound|звук|sonido|som\\b|klang|son\\b|volume|громк|laut|loud|quiet|тише|baixo|baixou|lower|louder|battery|батаре|bateria|batería|akku|light|подсветк|led|luz|lumi|เบส|เสียง|suara|âm|boomy|muddy|хуже|worse|pior|peor|schlechter|ruined|destroyed|destruiu|estragou|убили|испортили|perdeu|losing|lost|bajo el volumen|stutter|заика|beep|cuts)|downgrade|roll ?back|откат|voltar (?:para|pra) (?:a |uma )?(?:versão|atualização)|volver a la versión|eliminar la última actualización|previous (?:version|tuning|firmware)|old tuning|firmware antigo|vers[ãa]o anterior|версии 11|11\\.0|v11|actualización 11|11\\.4|deliberately lowered|душите колонку");

add('lang', 'Нет нужного языка (рус., порт., исп., польск., индонез., тайск., тур., яп.) / кривой перевод', 'да',
  "language|idioma|sprache|langue|język|lingua|bahasa (?:indonesia|ind)|ภาษา|日本ご|日本語|türkçe|turkce|русск|на английском|англ|in english|only english|only one language|un solo idioma|em inglês|en ingl[eé]s|auf englisch|nur englisch|alles nur auf englisch|bleibt trotzdem auf englisch|translat|перевод|übersetz|traduc|tradu[çc]|tłuma|polskiego|portugu[eê]s|en español|em português|no entiendo|não entendo inglês|шахт|mensagem em inglês|tamil");

add('ui_layout', 'Вёрстка: кнопки под навигационной панелью, не влезает в экран, альбомная ориентация, складные, «назад» закрывает приложение', 'да',
  "navigation (?:bar|buttons)|nevigation|nav bar|bottom buttons|buttons at the bottom|hidden behind|overlap|cut off|обрез|doesn'?t show entire screen|not show entire screen|landscape|альбомн|foldable|unfolded|folds?\\b|dex\\b|pressing back|back (?:arrow|button) .{0,40}(?:closes|takes me out)|takes me out of the app|kicks? (?:me )?(?:back )?to (?:the )?main|pantalla (?:principal|de inicio)|vuelve|goes back to the main screen|saca a pantalla|optimi[sz]e to foldable|formatierungsfehler|looks bad in tablet|не влез");

add('ux_design', 'UX/дизайн: устаревший, запутанный, «сырое» приложение, нет инструкций и справки', 'да',
  "\\bui\\b|interface|интерфейс|design|дизайн|outdated|old ?fashion|material ?3|5 years ago|grafica troppo antica|clunky|confus|запутан|complicated|komplizi|complicad|complicado|сложн|intuitiv|intuat|user friendly|hard to use|difficult|not intuitive|thrown together|looks like (?:a )?chinese|less refined|asthetic|unfinished|не фертиг|fühlt sich nicht fertig|instruction|manual|инструкц|help cent|help centre|guide|no help|empty|minimal\\.|icon|иконк|nicht intuitiv|usability|ใช้ยาก|使いずらい|ux");

add('battery_ind', 'Индикатор заряда в приложении неточен (шаг 10%, скачет, 0% на зарядке)', 'частично',
  "(?:battery|батар|bateria|batería|batterie|akku|baterai|ladestand|porcentaje|percentage|percent|процент|pin seviyesi).{0,80}(?:fluctuat|jump|accurate|accuracy|inaccurate|incorrect|wrong|abnormal|buggy|irregular|10 en 10|10% steps|10%-schritt|10% schritten|in 10%|de 10|10 em 10|sube|descalibrad|скач|прыга|не корректно|неточн|0%|shows (?:only )?\\d|show(?:s|ing)? full|marca 0|real %|unitário|bailan|20% to 100%|drop|from 80|100 to 88|keeps (?:falling|rising)|correctly|readings|indicator|индикатор|no battery|not showing|not visible|isn'?t visible|nicht|не показ|не показывает|não aparece|zeigt|level|status|consumption)|battery (?:status|indicator|level|percentage|readings)|batt(?:ery)? life,? (?:so|but)|seeing battery|see (?:the )?(?:battery|charge)|заряд на второй|ver la carga|porcentagem da bateria|battery information only|battery status to be seen|индикатора аккумулятора|показывает что колонка на зарядке");

add('timer', 'Таймер автовыключения: неверное отображение (21/22/23 ч), выключает по умолчанию, нет нужных значений', 'да',
  "auto ?-?shut ?down|shutdown|shut down timer|countdown|timer|таймер|автовыключ|auto[- ]?off|hibernate|turn off timer|sleep timer|apagado autom|desligamento temporário|電源オフ|abschalt|ausschalt|15 minutes");

add('volume_ctrl', 'Громкость в приложении: не синхронна с телефоном/колонкой, крупный шаг, писк на 100%, ползунок «прыгает»', 'частично',
  "(?:volume|громк|volumen|lautst|głośn|volume bar|slider|ползун|регулятор|шкала).{0,60}(?:sync|syncing|slider|step|шаг|beep|ping|pip|percent|процент|percentual|porcentaje|pops? up|jumps|bar\\b|не совпад|no coincide|не плавно|резк|smooth|coarse|step size|1~15|1~60|grober|stufen|input lag|doesn'?t go down|tap 1 per 1|tombol min plus|min plus|individual earbuds|channels|kanalların|indicator|en cuanto|led|светит|leds|mostrador|nível)|volume (?:indicator|level) works wrong|beeps when you hit 100|volume bar keep randomly|volume bar still pops|volume slider now longer|barra del volume|регулировка громкости без информации|очень резкая настройка громкости|volume (?:from|of) (?:my )?phone and|volume is only audible|1~15");

add('multi', 'Две колонки / стерео / Party / мультипоинт: приложение видит одну, нельзя управлять обеими, глючит при переключении', 'частично',
  "stereo|стерео|tws|party ?mode|пати|два (?:колонки|устройства)|две колонки|двух колонок|two speakers|2 speakers|both (?:my )?(?:tribit )?speakers|both speakers|both of them|second speaker|2nd speaker|other speaker|one speaker|одна колонка|individual speaker|each speaker|dos altavoces|2 caixas|2 stormbox|2 micros|two devices|2 devices|multi ?-?point|multipoint|multi device|2 phones|two phones|другом устройстве|on other devices|other phone|3 phones|across devices|between devices|sync across|alternar bocinas|2 parlantes|stereopaar|стереопар|соединить.{0,20}колонк|pair more than 2|tws mode|tws modo");

add('state', 'Приложение «теряет» уже подключённую колонку: показывает Connect/Reconnecting/«Bluetooth disconnected», выкидывает на главный экран', 'да',
  "already connected|is already connected|it is connected|it'?s connected|even (?:though|when) (?:it'?s|it is|i am|i'm|my speaker is) (?:already )?(?:connected|paired|playing)|shows? (?:as )?(?:the )?(?:.connect.|connected|paired)|says (?:it'?s |that )?(?:not connected|connection failed|unable)|showing (?:as )?(?:paired|device not connected|connection failed)|shows? (?:me )?connection failed|still showing|reconnecting|bluetooth (?:gets |is )?disconnected|desactiv[oó] el bluetooth|bağlantısı kesildi|kicks? (?:me )?(?:back )?to (?:the )?main|goes back to the main screen|saca a pantalla|me manda a la pantalla principal|forgets? .{0,20}(?:partially|speaker|stormbox)|keep forgetting|doesn'?t recogni[sz]e it anymore|fails to show it|thinks one speaker is not connected|drops off your connected device list|подключена и играет, но|не видит подключения|подключена.{0,20}не видит|connected (?:to|on|with) (?:my )?(?:phone|bluetooth).{0,60}(?:app|not)|paired (?:and|but|with).{0,40}(?:app|not connected)|music is playing but the app|still playing.{0,30}app|работает.{0,20}приложение не видит|apps? (?:doesn'?t|does not|didn'?t) (?:show|see|recogni)|showing device not connected|connected n functions|desconectando sozinho|disconnect(?:ed|ing)? .{0,30}(?:as soon as|when) i open");

add('features', 'Не хватает функций: выкл./вкл. колонки из приложения, виджеты, режимы подсветки, переназначение кнопок/жестов, заряд в шторке, кнопка mute', 'частично',
  "power (?:off|on) button|shutdown button|turn (?:the )?(?:speaker|unit|device|it) (?:on|off)|switch on the speaker|turn on (?:my )?(?:speaker|stormbox|remotely)|on or off my stormbox|выключ\\w* колонк|включение выключение|ligar ?/ ?desligar|función play|widget|виджет|light(?:s|ing)? (?:mode|pattern|option|control|customi)|more light|подсветк|\\bleds?\\b|luz|luces|lumière|lumi|rgb|button|кнопк|botón|tombol|gesture|жест|touch control|touchpad|sensor|game mode|mute|\\bmic(?:rophone)?\\b|avvisi|eko|echo|эхо|reverb|playlist|song list|list of the songs|notification|шторк|тре[ея]|white noise|on and off sound|звук запуска|ansagen|voice prompt|announcement|avisos iniciais|prompt volume|ton(?:e)?s? deaktiv|mode tf|sd card|tf card|transparency|\\banc\\b|codec|ldac|aptx|password .{0,20}(?:secure|stormbox)|bt security|any tom dick");

add('help_support', 'Поддержка/обратная связь: форма фидбэка не работает («productModel is empty»), нет ответа, пустой Help Center', 'да',
  "feedback|support (?:team|center|centre)|help cent|help centre|no response|not respond|не отвеча|без ответа|no answer|productmodel|customer service|служба поддержки|support doesn'?t|getting nowhere contacting|reached out|contacted|техподдерж|в поддержке|no help|can not get any support|support tribit|dissatisfactory response|kontakt|e-mail-adresse kann ich mich wenden|emailing you");

add('hw_quality', 'Железо/гарантия: батарея колонки/наушников деградирует, один наушник, поломки (не приложение)', 'нет (железо)',
  "warranty|гаранти|garant|battery (?:failed|died|issue|problem|won'?t|not working|drain|charging stuck|consumption)|won'?t (?:hold a )?charge|not charge|no longer charge|stuck at 60|right (?:won'?t|ear)|left (?:earbud|side)|one (?:earbud|side|of the earbud)|only one will work|один наушник|sağ kulaklık|blew|ripped|damaged|broke|stopped working suddenly|faulty|defect|брак|сломал|turns? off when|goes off after|turn off without|not sound quality|tear in a speaker|beeps in between|underwater|reparo|repair|degrad|не держит|der akku|auricular derecho|bateria (?:da minha|não dura)|a bateria|battery (?:went|life)|колонка (?:выключается|не включ)|can'?t switch on|dura 3 horas|descarregando|consumo de bateria|recharge every day|drains|charge for|charged it|30% battery even after|bateria piorou|bateria se|destruiu a bateria|battery from 80|stand ?by");

add('dsp_sound', 'Звук/тюнинг колонки: бас проседает на высокой громкости, мало громкости/баса, мутные средние (DSP/железо)', 'нет (прошивка/железо)',
  "(?:bass|бас|grave|graves|bajos?|basse|เบส|subgrave).{0,60}(?:decreas|drop|low|weak|missing|мало|пропал|просел|хуже|struggl|muddy|захлёб|ограничивает|ogranicza|diminui|piorou|estourando|rocando|baixo|fraco|too (?:much|low)|избыточн|много|boomy|бубн|долбит|не убирается|suddenly)|(?:above|over|после|from|à partir|a partir|acima|при|quando|cuando|once i increase|reaches?) .{0,20}(?:\\d0 ?%|half|половин|mitad).{0,60}(?:bass|бас|grave|bajo|volume|sound|treble|громк|sonar)|(?:not (?:as )?loud|не громк|тише|quieter|volume (?:not|is only)|не так громк|weniger laut|nicht mehr so laut|bajo el volumen|som (?:mais )?baixo|sem presença|soando baixo|no tiene volumen|не слышно|mid(?:s|dle)? and high|средн\\w* и высок|средние и высокие|высокие урезан|agudo|treble|clarity|clareza|médios|harmon|distort|muffled|stutter|заика|crackl|cracking)");

add('generic', 'Общее недовольство без конкретики («не работает», «мусор», «useless»)', '—', null, null);

// ---- run ----
function versionBucket(v) {
  if (!v) return 'unknown';
  const m = parseInt(v.split('.')[0], 10);
  if (m <= 1) return '1.x';
  return `${m}.x`;
}

const results = [];
for (const r of R) {
  const text = (r.text || '').replace(/\s+/g, ' ').trim();
  const t = text.toLowerCase();
  const themes = [];
  // strip server-connection phrases so they don't count as speaker connection
  const tConn = t.replace(/server connection|connection (?:to|with) (?:the |their |tribit )?server\w*|conexão com o servidor|internet connection|connection is abnormal|server communication/g, ' ');
  for (const th of T) {
    if (!th.re) continue;
    const src = th.id === 'connect' ? tConn : t;
    if (th.re.test(src)) themes.push(th.id);
  }
  // 4-5*: count only when the text carries a complaint marker
  const COMPLAINT = /\b(but|however|except|please|pls|fix|bug|issue|problem|can'?t|cannot|not|no|won'?t|doesn'?t|wish|only|need|annoy|fail)\b|не |нет |но |однако|исправ|пожалуйста|aber|bitte|nicht|pero|por favor|mas |não|porém|tolong|แต่|ช่วย|solo|só |falta|lacks?|missing|без /i;
  if (r.score >= 4 && !COMPLAINT.test(t)) themes.length = 0;
  // tablet-only "not compatible" should not count as model unsupported
  const models = modelRx.filter(([, re]) => re.test(t)).map(([n]) => n);
  if (themes.includes('unsupported') && themes.includes('tablet') && models.length === 0 && !/speaker|колонк|model|device not supported|buds|headphones|наушник/i.test(t)) {
    themes.splice(themes.indexOf('unsupported'), 1);
  }
  // models that are model-ish but generic word collisions: drop StormBox Blast (1) if Blast 2 matched
  let ms = models;
  if (ms.includes('StormBox Blast 2')) ms = ms.filter((m) => m !== 'StormBox Blast (1)');
  if (ms.includes('StormBox Micro 2')) ms = ms.filter((m) => m !== 'StormBox Micro (1)');
  if (ms.includes('StormBox Mini+')) ms = ms.filter((m) => m !== 'StormBox Mini');
  if (ms.includes('XSound Plus 2')) ms = ms.filter((m) => m !== 'XSound Plus (1)');
  if (ms.some((m) => m.startsWith('StormBox ') && m !== 'StormBox (1, без номера)')) ms = ms.filter((m) => m !== 'StormBox (1, без номера)');
  // historically unsupported models + "doesn't work with my X" and nothing else -> unsupported
  const HIST_UNSUP = ['XSound Go', 'MaxSound Plus', 'XSound Plus (1)', 'FlyBuds 3 / 3S', 'FlyBuds C1 / C1 Pro', 'XFree Go / Tune', 'StormBox Mini', 'StormBox Pro', 'StormBox Micro (1)', 'StormBox (1, без номера)', 'XSound Mega', 'XSound Surf', 'StormBox 360', 'QuietPlus', 'MoveBuds H1', 'ThunderBox'];
  if (r.score <= 3 && !themes.includes('unsupported') && ms.some((m) => HIST_UNSUP.includes(m)) &&
      /(?:not|n'?t|nie|не|no|não|nicht|ne|ไม่)\s?.{0,20}(?:work|funcion|funktion|fonctionne|работ|do anything|connect|support)|where|waiting|wish this app worked|not showing|no show|ni aparece|can'?t (?:be found|link)|consider|please|pls|add|para cuando|pueden poner|plan to|nicht|sync/i.test(t) &&
      themes.filter((x) => !['connect', 'features'].includes(x)).length === 0) {
    themes.push('unsupported');
  }
  // a review that is a complaint (1-3*) with no theme -> generic
  if (r.score <= 3 && themes.length === 0) themes.push('generic');
  results.push({ id: r.id, score: r.score, date: r.date, version: r.version, vb: versionBucket(r.version), lang: r._lang, text, themes, models: ms, thumbsUp: r.thumbsUp });
}

fs.writeFileSync(process.argv[3] || 'classified.json', JSON.stringify({ themes: T.map(({ id, title, fixable }) => ({ id, title, fixable })), results }, null, 1));

// ---- stats ----
const neg = results.filter((x) => x.score <= 2);
const mid = results.filter((x) => x.score === 3);
const pos = results.filter((x) => x.score >= 4);
console.log('1-2*:', neg.length, ' 3*:', mid.length, ' 4-5*:', pos.length);
const rows = [];
for (const th of T) {
  const a12 = neg.filter((x) => x.themes.includes(th.id));
  const a3 = mid.filter((x) => x.themes.includes(th.id));
  const a45 = pos.filter((x) => x.themes.includes(th.id));
  const all13 = [...a12, ...a3];
  const recent = all13.filter((x) => x.vb === '4.x' || x.vb === '5.x').length;
  const last12 = all13.filter((x) => x.date >= '2025-10-15').length;
  rows.push({ id: th.id, n13: all13.length, n12: a12.length, share12: (100 * a12.length / neg.length).toFixed(1), n45: a45.length, recent, last12 });
}
rows.sort((a, b) => b.n13 - a.n13);
console.table(rows);

const sample = process.argv[4];
if (sample) {
  const hits = results.filter((x) => x.score <= 3 && x.themes.includes(sample));
  for (const h of hits) console.log(`${h.score}* ${h.date.slice(0, 10)} v${h.version || '-'} ${h.lang} [${h.models.join(',')}] | ${h.text.slice(0, 220)}`);
}
