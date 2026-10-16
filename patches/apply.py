"""Krinik Tribit App - smali patches for com.thousandshores.tribit 5.0.0 (versionCode 5000).

Usage:  python -I patches/apply.py <apktool-decoded-dir>

Every patch finds its anchor by exact text and fails loudly (exit 1) when the anchor is missing,
so a new Tribit version never gets a half-applied fork. Run on a FRESH `apktool d` output.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None


def smali(cls):
    """Find the smali file of a class across smali, smali_classes2..N."""
    rel = cls.replace(".", "/") + ".smali"
    hits = list(ROOT.glob("smali*/" + rel))
    if len(hits) != 1:
        sys.exit(f"FAIL: class {cls}: found {len(hits)} files")
    return hits[0]


def method_span(text, header):
    """Return (start, end) of a method whose .method line starts with `header`."""
    start = text.find(header)
    if start < 0 or text.find(header, start + 1) >= 0:
        sys.exit(f"FAIL: method header not unique/found: {header}")
    end = text.find(".end method", start)
    return start, end + len(".end method")


def replace_in_method(path, header, old, new):
    text = path.read_text(encoding="utf-8")
    s, e = method_span(text, header)
    body = text[s:e]
    if body.count(old) != 1:
        sys.exit(f"FAIL: anchor found {body.count(old)}x in {header}:\n{old}")
    path.write_text(text[:s] + body.replace(old, new) + text[e:], encoding="utf-8")


def replace_method(path, header, new_method):
    text = path.read_text(encoding="utf-8")
    s, e = method_span(text, header)
    path.write_text(text[:s] + new_method.strip("\n") + text[e:], encoding="utf-8")


def add_method(path, marker, new_method):
    """Insert a new method; refuse if a method with `marker` already exists."""
    text = path.read_text(encoding="utf-8")
    if marker in text:
        sys.exit(f"FAIL: {path.name} already has {marker}")
    path.write_text(text.rstrip("\n") + "\n\n" + new_method.strip("\n") + "\n", encoding="utf-8")


# --- Patch 1: crash in EqUtil.getUnnameEq (IndexOutOfBoundsException: Index: 1, Size: 1) -------------
# The app scans custom EQ names that contain "Unnamed EQ-", splits by "-" and reads [1] blindly, then
# parseInt()s the digits. A name with no part after "-" or no digits crashed the EQ screen on
# "create custom EQ". Fix: skip such names (continue the loop) instead of crashing.
# [NOT-TESTED]
def patch_unnamed_eq_crash():
    p = smali("com.thousandshores.tribit.utils.EqUtil")
    h = ".method public final getUnnameEq(Ljava/util/ArrayList;)Ljava/lang/String;"
    replace_in_method(p, h,
        "    move-result-object v4\n\n    invoke-interface {v4, v2}, Ljava/util/List;->get(I)Ljava/lang/Object;",
        "    move-result-object v4\n\n"
        "    invoke-interface {v4}, Ljava/util/List;->size()I\n\n"
        "    move-result v6\n\n"
        "    const/4 v5, 0x2\n\n"
        "    if-lt v6, v5, :cond_0\n\n"
        "    invoke-interface {v4, v2}, Ljava/util/List;->get(I)Ljava/lang/Object;")
    replace_in_method(p, h,
        "    move-result-object v4\n\n    .line 9124\n    invoke-static {v4}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I",
        "    move-result-object v4\n\n"
        "    invoke-virtual {v4}, Ljava/lang/String;->isEmpty()Z\n\n"
        "    move-result v6\n\n"
        "    if-nez v6, :cond_0\n\n"
        "    .line 9124\n    invoke-static {v4}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I")
    print("ok  1 getUnnameEq crash")


# --- Patch 2: location is not required -----------------------------------------------------------------
# PairHelper.getMustType() listed "GPS" next to "Bluetooth" as a precondition for finding the speaker, so
# tablets without GPS / with location off could not connect. On Android 12+ BLE scan runs on BLUETOOTH_SCAN
# (declared neverForLocation in the manifest), location is not needed. Fix: only Bluetooth is required,
# and the GPS / location probes report "on" so no screen blocks on them.
# [NOT-TESTED]
def patch_no_location():
    p = smali("com.thousandshores.tribit.helper.PairHelper")
    replace_method(p, ".method public final getMustType()[Ljava/lang/String;", """
.method public final getMustType()[Ljava/lang/String;
    .locals 3

    const/4 v0, 0x1

    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "Bluetooth"

    aput-object v2, v0, v1

    return-object v0
.end method""")
    for name in ("getGpsEnabled", "getLocationEnabled"):
        replace_method(p, f".method public final {name}()Z", f"""
.method public final {name}()Z
    .locals 1

    const/4 v0, 0x1

    return v0
.end method""")
    print("ok  2 location not required")


# --- Patch 3: UI fits the screen under system display zoom -----------------------------------------------
# With an enlarged system "display size" (Titan 1: 480 dpi over a 320 dpi panel) Tribit's screens do not
# scroll and their bottoms are cut off (the EQ among them). Fix: every activity of the app (all extend
# BaseActivity) renders at the panel's stable density; screen size in dp is rescaled to match, so
# resource qualifiers (sw600dp, w600dp) see the real tablet.
# [NOT-TESTED]
def patch_stable_density():
    p = smali("com.thousandshores.tribit.base.BaseActivity")
    add_method(p, ".method protected attachBaseContext(Landroid/content/Context;)V", """
.method protected attachBaseContext(Landroid/content/Context;)V
    .locals 5

    invoke-virtual {p1}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getConfiguration()Landroid/content/res/Configuration;

    move-result-object v0

    new-instance v1, Landroid/content/res/Configuration;

    invoke-direct {v1, v0}, Landroid/content/res/Configuration;-><init>(Landroid/content/res/Configuration;)V

    iget v2, v0, Landroid/content/res/Configuration;->densityDpi:I

    sget v3, Landroid/util/DisplayMetrics;->DENSITY_DEVICE_STABLE:I

    if-le v2, v3, :keep

    iput v3, v1, Landroid/content/res/Configuration;->densityDpi:I

    iget v4, v0, Landroid/content/res/Configuration;->screenWidthDp:I

    mul-int/2addr v4, v2

    div-int/2addr v4, v3

    iput v4, v1, Landroid/content/res/Configuration;->screenWidthDp:I

    iget v4, v0, Landroid/content/res/Configuration;->screenHeightDp:I

    mul-int/2addr v4, v2

    div-int/2addr v4, v3

    iput v4, v1, Landroid/content/res/Configuration;->screenHeightDp:I

    iget v4, v0, Landroid/content/res/Configuration;->smallestScreenWidthDp:I

    mul-int/2addr v4, v2

    div-int/2addr v4, v3

    iput v4, v1, Landroid/content/res/Configuration;->smallestScreenWidthDp:I

    invoke-virtual {p1, v1}, Landroid/content/Context;->createConfigurationContext(Landroid/content/res/Configuration;)Landroid/content/Context;

    move-result-object p1

    :keep
    invoke-super {p0, p1}, Lme/yokeyword/fragmentation/SupportActivity;->attachBaseContext(Landroid/content/Context;)V

    return-void
.end method""")
    print("ok  3 stable density in BaseActivity")


# --- Patch 4: the fork's name on the launcher -------------------------------------------------------------
# The owner named the fork "Krinik Tribit" (chat 2026-10-15 23:1x). The launcher label is @string/app_name.
# [NOT-TESTED]
def patch_app_name():
    p = ROOT / "res/values/strings.xml"
    text = p.read_text(encoding="utf-8")
    old = '<string name="app_name">Tribit</string>'
    if text.count(old) != 1:
        sys.exit("FAIL: app_name anchor")
    p.write_text(text.replace(old, '<string name="app_name">Krinik Tribit</string>'), encoding="utf-8")
    print("ok  4 app name Krinik Tribit")


# --- Patch 5: vector launcher icon in Krinik pink ---------------------------------------------------------
# The owner: "Иконку красим в фирменный розовый цвет криника" · "их иконку вектором перерисовываем"
# (chat 2026-10-15 23:1x). Tribit's mark redrawn as ONE closed stroke: three loops on an equilateral
# triangle of centres (r = 160, stroke 80 in a 1932 grid), lines tangent at 60 degrees; source of truth
# design/icon.svg. Adaptive icon (API 26+) picks mipmap-anydpi-v26 over the yellow PNGs.
# [NOT-TESTED]
ICON_PATH = ("M508,734 L1430,734 A160,160 0 1 0 1291.4,494 L830.4,1293 "
             "A160,160 0 1 0 1107.6,1293 L646.6,494 A160,160 0 1 0 508,734 Z")
# Placement in the 108-unit icon: the mark has 3-fold symmetry about the centroid of its loop centres (508,574),
# (1430,574), (969,1373) -> (969, 840.3); that point goes to the centre (54,54) of the launcher circle. Owner 2026-10-16
# 12:00 +03:00: «иконку нашу нужно перерендерить. Сейчас не по центру круга логотип» · «а нужно по уцентру поставить» -
# the old translate centred the bounding box, which put the symmetry centre 5.7 units high. Farthest stroke point from
# the centre: (532.5 + 160 + 40) x 0.0371 = 27.2 < 33, inside the adaptive-icon safe zone. Same values in design/icon.svg.
ICON_SCALE = "0.0371"
ICON_TX = "18.05"   # 54 - 0.0371 x 969
ICON_TY = "19.98"   # owner 13:33 «B вариант по иконке»: midway between the bounding box (17.14) and the symmetry centre (22.82)


def patch_icon():
    res = ROOT / "res"
    (res / "mipmap-anydpi-v26").mkdir(exist_ok=True)
    (res / "mipmap-anydpi-v26/ic_launcher.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/krinik_icon_bg"/>\n'
        '    <foreground android:drawable="@drawable/krinik_ic_launcher_fg"/>\n'
        '    <monochrome android:drawable="@drawable/krinik_ic_launcher_fg"/>\n'
        '</adaptive-icon>\n', encoding="utf-8")
    (res / "drawable/krinik_ic_launcher_fg.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    android:width="108dp" android:height="108dp"\n'
        '    android:viewportWidth="108" android:viewportHeight="108">\n'
        f'    <group android:scaleX="{ICON_SCALE}" android:scaleY="{ICON_SCALE}"\n'
        f'        android:translateX="{ICON_TX}" android:translateY="{ICON_TY}">\n'
        f'        <path android:pathData="{ICON_PATH}"\n'
        '            android:fillColor="#00000000" android:strokeColor="#0D0D0D"\n'
        '            android:strokeWidth="80" android:strokeLineJoin="round"/>\n'
        '    </group>\n'
        '</vector>\n', encoding="utf-8")
    colors = res / "values/colors.xml"
    text = colors.read_text(encoding="utf-8")
    if "krinik_icon_bg" in text:
        sys.exit("FAIL: krinik_icon_bg already present")
    colors.write_text(text.replace("</resources>",
        '    <color name="krinik_icon_bg">#FF1A8C</color>\n</resources>'), encoding="utf-8")
    print("ok  5 vector pink icon")


# --- Patch 6: passwords may contain symbols ---------------------------------------------------------------
# The owner could not type "_" in a password (chat 2026-10-15 23:3x). Two client-side gates: every password
# field carries android:digits="@string/password_digis" (letters and digits only), and RegexUtils.isPassword
# matches ^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,18}$. Fix: printable ASCII symbols allowed in both; the
# 6-18 length and "not only digits, not only letters" rules stay. Whether the SERVER accepts symbols is
# not verified yet (probe request blocked; to be checked by a real registration on the Titan).
# [NOT-TESTED]
PASSWORD_DIGITS = ("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                   "_!#$%&amp;()*+,-./:;=?@[]^{|}~")


def patch_password_symbols():
    p = ROOT / "res/values/strings.xml"
    text = p.read_text(encoding="utf-8")
    old = '<string name="password_digis">0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ</string>'
    if text.count(old) != 1:
        sys.exit("FAIL: password_digis anchor")
    p.write_text(text.replace(old, f'<string name="password_digis" formatted="false">{PASSWORD_DIGITS}</string>'),
                 encoding="utf-8")
    r = smali("com.thousandshores.tool.utils.RegexUtils")
    t = r.read_text(encoding="utf-8")
    old_re = 'const-string v0, "^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,18}$"'
    if t.count(old_re) != 1:
        sys.exit("FAIL: password regex anchor")
    r.write_text(t.replace(old_re, 'const-string v0, "^(?![0-9]+$)(?![a-zA-Z]+$)[\\\\x21-\\\\x7E]{6,18}$"'),
                 encoding="utf-8")
    print("ok  6 password symbols")


# --- Patch 7: the Bluetooth library does not demand location either ------------------------------------
# Patch 2 lifted location from the permission screens, but the bundled BLE library refuses to scan on its own:
# BleScanRequest.java:140 fails the scan with GPSDisable when location is off and needCheckGps is set, with no
# Android-version check; TribitApp.initBle sets it: `.setNeedCheckGps(true)` (TribitApp.java:229). Fix: pass false.
# The `true` lives in register v3, which is ALSO the 1 of setMaxConnectNum(1) and of the connect retry count -
# so v3 is not touched: a fresh `const/4 v1, 0x0` right before the call carries the false (v1 is free there:
# it already held 0 for setStopScanWhenStartConnect two lines above).
# [NOT-TESTED]
def patch_ble_no_gps_check():
    p = smali("com.thousandshores.tribit.TribitApp")
    replace_in_method(p, ".method public final initBle()V",
        "    invoke-virtual {v0, v3}, Lcom/bhm/ble/attribute/BleOptions$Builder;->setNeedCheckGps(Z)Lcom/bhm/ble/attribute/BleOptions$Builder;",
        "    const/4 v1, 0x0\n\n"
        "    invoke-virtual {v0, v1}, Lcom/bhm/ble/attribute/BleOptions$Builder;->setNeedCheckGps(Z)Lcom/bhm/ble/attribute/BleOptions$Builder;")
    print("ok  7 BLE library: no location check")


# --- Patch 11: every screen fits the whole design, portrait and landscape ----------------------------------
# AndroidAutoSize (me.jessyan.autosize, design 375x667 dp in the manifest meta-data) sets the density of every
# screen to screenWidthPx / 375 - "base on width". On the Titan that is 4.27 px/dp in portrait, ~600 dp of height
# for a 667 dp design (the bottoms of 17-20 screens fall off), and 6.83 px/dp in landscape, ~230 dp of height
# (researches/05 section 1). No own screen implements CustomAdapt/CancelAdapt (0 files), so the global
# AutoSizeConfig.isBaseOnWidth() decides for all of them. Fix: base on width only when width is the tighter side,
#   screenW * designH <= screenH * designW   -> width;   otherwise -> height,
# so the density is min(w/375, h/667) and the whole design fits: Titan portrait 3.84 px/dp (417 x 667 dp),
# landscape 2.4 px/dp (1067 x 667 dp); a phone taller than 16:9 keeps base-on-width exactly as before.
# [NOT-TESTED]
def patch_autosize_fit():
    p = smali("me.jessyan.autosize.AutoSizeConfig")
    cfg = "Lme/jessyan/autosize/AutoSizeConfig;"
    replace_method(p, ".method public isBaseOnWidth()Z", f"""
.method public isBaseOnWidth()Z
    .locals 3

    invoke-virtual {{p0}}, {cfg}->getScreenWidth()I

    move-result v0

    invoke-virtual {{p0}}, {cfg}->getDesignHeightInDp()I

    move-result v1

    mul-int/2addr v0, v1

    invoke-virtual {{p0}}, {cfg}->getScreenHeight()I

    move-result v1

    invoke-virtual {{p0}}, {cfg}->getDesignWidthInDp()I

    move-result v2

    mul-int/2addr v1, v2

    if-gt v0, v1, :base_on_height

    const/4 v2, 0x1

    return v2

    :base_on_height
    const/4 v2, 0x0

    return v2
.end method""")
    print("ok 11 AutoSize fits the whole design")


# --- Patch 16: every screen scrolls when it does not fit --------------------------------------------------
# The owner: «они не скролятся у них нихуя» · «не масштабируются». 42 own screens have no scrolling container and all
# are DataBinding screens, so their XML cannot be wrapped (the binding casts its root). BaseActivity.onCreate calls
# our krinik.ScrollFix.wrap(activity, root) right after it stores rootView: the root is moved into a ScrollView
# (fillViewport) unless the screen already scrolls or must fill the window. The class is compiled from
# patches/java/krinik/ScrollFix.java by build.sh into an extra classesN.dex of the APK (Android loads every dex).
# [NOT-TESTED]
def patch_scroll_fix():
    p = smali("com.thousandshores.tribit.base.BaseActivity")
    store = "    iput-object v0, p0, Lcom/thousandshores/tribit/base/BaseActivity;->rootView:Landroid/view/View;\n"
    text = p.read_text(encoding="utf-8")
    header = next((h for h in (".method public onCreate(Landroid/os/Bundle;)V", ".method protected onCreate(Landroid/os/Bundle;)V") if h in text), None)
    if header is None:
        sys.exit("FAIL: BaseActivity.onCreate not found")
    replace_in_method(p, header, store,
        store + "\n    invoke-static {p0, v0}, Lkrinik/ScrollFix;->wrap(Landroid/app/Activity;Landroid/view/View;)V\n")
    print("ok 16 screens scroll when they do not fit")


# --- Patch 18: no location permission on Android 12+ -------------------------------------------------------
# Found on the Titan 2026-10-16 01:01: after patches 2 and 7 the permission screen still stopped on «Enable Location ->
# Go to set» - PermissionNewActivity.checkToActivity also demands the APP's ACCESS_FINE_LOCATION permission (isLocation),
# and the same check sits in PermissionActivity, CheckSearchConditionActivity, PairHelper, the search screens.
# The manifest already declares BLUETOOTH_SCAN neverForLocation, so the platform does not need location on API 31+.
# Every own call of ContextCompat.checkSelfPermission (com/thousandshores/**) goes through krinik.Perm.check
# (patches/java/krinik/Perm.java): location reads as granted on API 31+, all else is the real check.
# [NOT-TESTED]
def patch_location_permission():
    old = "Landroidx/core/content/ContextCompat;->checkSelfPermission(Landroid/content/Context;Ljava/lang/String;)I"
    new = "Lkrinik/Perm;->check(Landroid/content/Context;Ljava/lang/String;)I"
    calls = files = 0
    for p in ROOT.glob("smali*/com/thousandshores/**/*.smali"):
        t = p.read_text(encoding="utf-8")
        n = t.count(old)
        if n:
            p.write_text(t.replace(old, new), encoding="utf-8")
            calls += n
            files += 1
    if calls < 20:
        sys.exit(f"FAIL: expected ~25 checkSelfPermission calls in own code, found {calls}")
    print(f"ok 18 location permission not demanded on Android 12+ ({calls} calls in {files} files)")


# --- Patch 17: Krinik's brand - pink instead of yellow, «KRINIK TRIBIT», vector logos -----------------------
# The owner (chat 2026-10-16 ≈ 00:40–01:00 +03:00): «желтные цветна меняем на нашу дизайн схему с розовым» ·
# «назваение везде меняем на KRINIK TRIBIT» · «мы вектором сверстаем свои» · «так е и где нужно сверстаем изображения» ·
# «векторные» · «при тапах по кнопкам странный увет кнопки» · «сделано людьми для людей - убрать» · about the splash:
# «как у них было на главном экране, чтобы был узнаваем их флоу».
#   a. The app's yellow -> Krinik pink: named colours (opaque and the 80 % pressed one) and every yellow literal in the
#      app's own layouts/drawables/styles with ANY alpha kept as is (#7FFFE900 pressed -> #7FFF1A8C); amber #FFC107
#      too. Library palettes (quantum_*, m3_*, material_*, abc_*) stay untouched.
#   b. Splash keeps Tribit's own background (their flow stays recognisable): the yellow logo, «TRIBIT» and the slogan
#      baked into app_start_up.png are painted out with the background colour (ImageMagick, feathered mask), and the
#      vector logo tile and «KRINIK TRIBIT» as real text stand in their place.
#   c. Login: the «TRIBIT» logo PNG -> vector mark + «KRINIK TRIBIT»; the «Войти» button was anchored below the one-line
#      «* » marker instead of the three-line hint and covered it - now anchored below the hint (tv_title1).
#   d. Registration: «TRIBIT» -> «KRINIK TRIBIT» on its own line under the welcome text (it was squeezed to the right of
#      it); the big grey Tribit watermark -> our vector mark at low opacity.
# [NOT-TESTED]
PINK_RGB = "ff1a8c"
YELLOW_RGB = ("ffe900", "ffeb00", "ffd700", "ffea38", "ffc107")
YELLOW_COLOURS = ("common_button_enableed_bg", "common_button_enableed_80_bg", "et_foucused_color",
                  "text_et_undeline_focus", "color_upgrade_now")
BRAND = "KRINIK TRIBIT"
# Area of app_start_up.png (1125 x 2436) holding Tribit's baked logo, name and slogan, and the background colour there.
SPLASH_LOGO_BOX = "270,700 855,1235"
SPLASH_BG = "rgb(13,13,12)"
MARK_GROUP = (
    f'    <group android:scaleX="{ICON_SCALE}" android:scaleY="{ICON_SCALE}"\n'
    f'        android:translateX="{ICON_TX}" android:translateY="{ICON_TY}">\n'
    f'        <path android:pathData="{ICON_PATH}"\n'
    '            android:fillColor="#00000000" android:strokeColor="{stroke}"\n'
    '            android:strokeWidth="80" android:strokeLineJoin="round"/>\n'
    '    </group>\n')


def _sub_once(path, old, new, what):
    t = path.read_text(encoding="utf-8")
    if t.count(old) != 1:
        sys.exit(f"FAIL: {what} anchor found {t.count(old)}x")
    path.write_text(t.replace(old, new), encoding="utf-8")


def patch_brand():
    import subprocess
    res = ROOT / "res"
    # a. colours
    colors = res / "values/colors.xml"
    t = colors.read_text(encoding="utf-8")
    for name in YELLOW_COLOURS:
        hits = re.findall(rf'<color name="{name}">#([0-9a-fA-F]{{2}})([0-9a-fA-F]{{6}})</color>', t)
        if len(hits) != 1 or hits[0][1].lower() not in YELLOW_RGB:
            sys.exit(f"FAIL: colour {name}: {hits}")
        alpha, rgb = hits[0]
        t = t.replace(f'<color name="{name}">#{alpha}{rgb}</color>', f'<color name="{name}">#{alpha}{PINK_RGB}</color>')
    colors.write_text(t, encoding="utf-8")
    lit = re.compile(r"#([0-9a-f]{2})?(" + "|".join(YELLOW_RGB) + r")\b", re.I)
    files = [p for d in ("layout", "drawable", "drawable-v21", "drawable-v24") for p in (res / d).glob("*.xml")] + [res / "values/styles.xml"]
    changed = 0
    for p in files:
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        s2 = lit.sub(lambda m: "#" + (m.group(1) or "") + PINK_RGB, s)
        if s2 != s:
            p.write_text(s2, encoding="utf-8")
            changed += 1
    if changed < 15:
        sys.exit(f"FAIL: yellow literals found in only {changed} files (expected ~20)")
    # yellow colour strings in the app's own code (the EQ chart line "#FFE900" and ~30 more files)
    code_lit = re.compile(r'(const-string(?:/jumbo)? [vp]\d+, ")#([0-9a-fA-F]{2})?(' + "|".join(YELLOW_RGB) + r')(")', re.I)
    code_files = 0
    for p in ROOT.glob("smali*/com/thousandshores/**/*.smali"):
        s = p.read_text(encoding="utf-8")
        s2 = code_lit.sub(lambda m: f"{m.group(1)}#{(m.group(2) or '').upper()}{PINK_RGB.upper()}{m.group(4)}", s)
        if s2 != s:
            p.write_text(s2, encoding="utf-8")
            code_files += 1
    if code_files < 20:
        sys.exit(f"FAIL: yellow colour strings in code found in only {code_files} files (expected ~30)")

    # vector drawables: the logo tile (pink rounded square + black mark) and the white mark
    (res / "drawable/krinik_logo_tile.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">\n'
        '    <path android:fillColor="#FF1A8C" android:pathData="M24,0 H84 A24,24 0 0 1 108,24 V84 A24,24 0 0 1 84,108 H24 A24,24 0 0 1 0,84 V24 A24,24 0 0 1 24,0 Z"/>\n'
        + MARK_GROUP.replace("{stroke}", "#0D0D0D") + '</vector>\n', encoding="utf-8")
    (res / "drawable/krinik_mark_white.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">\n'
        + MARK_GROUP.replace("{stroke}", "#FFFFFF") + '</vector>\n', encoding="utf-8")

    s = res / "values/strings.xml"
    _sub_once(s, "</resources>", f'    <string name="krinik_brand" translatable="false">{BRAND}</string>\n</resources>', "strings end")

    # b. splash: Tribit's background with their baked logo painted out, our vector logo and name on top
    png = res / "mipmap-xxhdpi/app_start_up.png"
    if not png.exists():
        sys.exit("FAIL: app_start_up.png missing")
    mask = png.with_name("krinik_mask.png")
    x1y1, x2y2 = SPLASH_LOGO_BOX.split()
    for cmd in (["magick", str(png), "-fill", "black", "-colorize", "100", "-fill", "white", "-draw",
                 f"roundrectangle {x1y1} {x2y2} 90,90", "-blur", "0x40", str(mask)],
                ["magick", str(png), "(", "+clone", "-fill", SPLASH_BG, "-colorize", "100", ")", str(mask),
                 "-composite", str(png)]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"FAIL: ImageMagick: {r.stderr.strip()[:200]}")
    mask.unlink()
    first = res / "layout/activity_first_new.xml"
    old = '<ImageView android:layout_width="fill_parent" android:layout_height="fill_parent" android:src="@mipmap/app_start_up" android:scaleType="centerCrop" />'
    _sub_once(first, old, old + '\n'
        '    <LinearLayout android:orientation="vertical" android:gravity="center_horizontal" android:layout_gravity="center" '
        'android:layout_width="wrap_content" android:layout_height="wrap_content" android:layout_marginBottom="@dimen/dp_160">\n'
        '        <ImageView android:layout_width="@dimen/dp_100" android:layout_height="@dimen/dp_100" android:src="@drawable/krinik_logo_tile" />\n'
        '        <TextView android:textSize="26.0sp" android:textStyle="bold" android:textColor="#ffffffff" android:layout_width="wrap_content" '
        'android:layout_height="wrap_content" android:layout_marginTop="@dimen/dp_20" android:letterSpacing="0.06" android:text="@string/krinik_brand" />\n'
        '    </LinearLayout>', "splash image")

    # c. login: logo, and the button anchored below the hint
    login = res / "layout/activity_login_new.xml"
    _sub_once(login,
        '<ImageView android:layout_width="@dimen/dp_148" android:layout_height="@dimen/dp_60" android:layout_marginLeft="@dimen/dp_20" '
        'android:layout_marginTop="@dimen/dp_56" android:layout_marginBottom="@dimen/dp_2" android:src="@mipmap/ic_login_icon" />',
        '<LinearLayout android:orientation="horizontal" android:gravity="center_vertical" android:layout_width="wrap_content" '
        'android:layout_height="@dimen/dp_60" android:layout_marginLeft="@dimen/dp_20" android:layout_marginTop="@dimen/dp_56" '
        'android:layout_marginBottom="@dimen/dp_2">\n'
        '            <ImageView android:layout_width="@dimen/dp_44" android:layout_height="@dimen/dp_44" android:src="@drawable/krinik_mark_white" />\n'
        '            <TextView android:textSize="22.0sp" android:textStyle="bold" android:textColor="#ffffffff" android:layout_width="wrap_content" '
        'android:layout_height="wrap_content" android:layout_marginLeft="@dimen/dp_10" android:letterSpacing="0.06" android:text="@string/krinik_brand" />\n'
        '        </LinearLayout>', "login logo")
    t = login.read_text(encoding="utf-8")
    btn = re.search(r'<Button [^>]*android:id="@id/btn_login"[^>]*>', t)
    if not btn or btn.group(0).count('android:layout_below="@id/tv_title"') != 1:
        sys.exit("FAIL: login button anchor")
    login.write_text(t.replace(btn.group(0), btn.group(0).replace('android:layout_below="@id/tv_title"',
                                                                    'android:layout_below="@id/tv_title1"')), encoding="utf-8")

    # d. registration: the name on its own line, our watermark
    reg = res / "layout/activity_register_new.xml"
    _sub_once(reg, 'android:layout_marginLeft="@dimen/dp_10" android:layout_marginTop="@dimen/dp_8" android:text="TRIBIT" '
                   'android:layout_toRightOf="@id/tv_title1" android:layout_below="@id/tv_title" />',
                   'android:layout_marginLeft="@dimen/dp_20" android:layout_marginTop="@dimen/dp_8" android:text="@string/krinik_brand" '
                   'android:layout_below="@id/tv_title1" />', "registration title")
    _sub_once(reg, 'android:src="@mipmap/ic_register_icon"', 'android:src="@drawable/krinik_mark_white" android:alpha="0.12"',
              "registration watermark")
    print(f"ok 17 brand: pink in {changed} res files + {code_files} code files + {len(YELLOW_COLOURS)} colours, {BRAND}, splash/login/registration")


# --- Patch 8a: the splash does not wait for their language dictionary --------------------------------------
# Play complaint 4 «stuck on the logo» (159 reviews). FirstNewActivity.onCreate: with network on it first asks their
# server for strings (ViewModelFirst.getStringResources) and goes on only when the answer sets 1; an empty answer, a
# «no data» answer (2) or a slow server keeps the logo forever or up to ~80 s (researches/05 §3.3, researches/06 З1).
# Fix: the network check jumps straight to showAgree() - the offline branch the app already has. Strings stay as
# shipped in the APK; server texts are wave 2 (plans/01 §3).
# [TESTED: 2026-10-16 · A51: dictionary requests 2 -> 0; NOT applied - the login screen turned English · testcases/reports/2026-10-16_wave1.md]
def patch_splash_no_dictionary_wait():
    p = smali("com.thousandshores.tribit.modulelogin.activity.FirstNewActivity")
    replace_in_method(p, ".method public onCreate(Landroid/os/Bundle;)V",
        "    invoke-static {}, Lcom/thousandshores/tool/utils/NetworkUtils;->isConnected()Z\n\n"
        "    move-result p1\n\n"
        "    if-eqz p1, :cond_11\n",
        "    goto :cond_11\n")
    # Twin: FirstActivity (the launcher activity) runs the same branch before handing over to FirstNewActivity.
    # TWINS: searched `ViewModelFirst;->getStringResources` callers - 2 sites, both patched.
    p = smali("com.thousandshores.tribit.modulelogin.activity.FirstActivity")
    replace_in_method(p, ".method public onCreate(Landroid/os/Bundle;)V",
        "    invoke-static {}, Lcom/thousandshores/tool/utils/NetworkUtils;->isConnected()Z\n\n"
        "    move-result v1\n\n"
        "    if-eqz v1, :cond_10\n",
        "    goto :cond_10\n")
    print("ok  8a splash: no wait for the server dictionary (FirstActivity, FirstNewActivity)")


# --- Patch 8: no account - an anonymous guest that carries nothing of the person or the phone --------------------
# Owner 2026-10-16 ≈ 09:16 +03:00: «аккаунт не нужен» · «выпиливаем НАХУЙ аккаунты»; 10:45 (interviews/interview_001 Q1 = C):
# «работаем с сервером трибит анонимным аккаунтом без передачи им данных о пользователе, девайс ид и прочее»; 11:00 «ДА,
# принято» - guest ID random per install, model + Android a random real pair picked once per install (MASTER_PLAN journal).
# Play complaints 11 «why an account» (77) and 17 «needs their server» (63). Their gateway answers «Full authentication»
# to the speaker catalog without a token (testcases/reports/2026-10-16_wave1.md, Found 0), so the guest login stays - the
# splash already logs a user without a token in as a guest (FirstNewActivity.checkToken -> autoLogin -> loginGuest), only
# START opens LoginNewActivity (researches/06 З2, З3). Fix, three parts:
#  1. START marks the agreement and calls the splash's checkToken (the guest path) instead of the login screen;
#  2. the VistitorLogin constructor - the one class all four loginGuest sites build - takes emailAccount, logMobModel and
#     operSystem from krinik.Anon instead of MAC/ANDROID_ID, Build.MODEL and the real Android version; EasyHttp builds both
#     the URL and the JSON body from these fields (seen in diagnostics/2026-10-16_a51_easyhttp_visitor.log);
#  3. FireUpgrade sends their original packageName (owner 11:00), so the debug package name never leaves the phone.
# Everything else of the account (profile, device list sync, statistics) is cut by krinik.Gate (patch 20).
# [TESTED: 2026-10-16 · A51 clean install: START -> guest -> main -> speaker page -> EQ, no login screen, no crash;
# packageName com.thousandshores.tribit in checkFirmwareUpgrade; anon_check.py 0 real values · testcases/reports/2026-10-16_patch8_anon.md]
ANON_FIELDS = [  # (constructor parameter register, field, krinik.Anon method)
    ("p1", "emailAccount", "id"),
    ("p3", "logMobModel", "model"),
    ("p6", "operSystem", "os"),
]


def patch_no_account():
    p = smali("com.thousandshores.tribit.modulelogin.activity.FirstNewActivity")
    # START: the button's context is the splash activity; call its checkToken. Any other context keeps the old path.
    h = ".method private static final onCreate$lambda$1(Landroid/view/View;)V"
    replace_method(p, h, h + START_HANDLER)

    v = smali("com.thousandshores.tribit.http.model.VistitorLogin")
    ctor = ".method public constructor <init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V"
    for reg, field, method in ANON_FIELDS:
        put = f"    iput-object {reg}, p0, Lcom/thousandshores/tribit/http/model/VistitorLogin;->{field}:Ljava/lang/String;\n"
        replace_in_method(v, ctor, put,
            f"    invoke-static {{}}, Lkrinik/Anon;->{method}()Ljava/lang/String;\n\n    move-result-object {reg}\n\n" + put)

    f = smali("com.thousandshores.tribit.http.model.FireUpgrade")
    put = "    iput-object p3, p0, Lcom/thousandshores/tribit/http/model/FireUpgrade;->packageName:Ljava/lang/String;\n"
    replace_in_method(f, ".method public constructor <init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V",
        put, f'    const-string p3, "{ORIGINAL_PACKAGE}"\n\n' + put)
    print("ok  8 no account: START -> anonymous guest; guest login and firmware check carry krinik.Anon values only")


START_HANDLER = """
    .locals 3

    move-object v2, p0

    sget-object p0, Lcom/thousandshores/tribit/utils/ui/PrivateTextUtil;->INSTANCE:Lcom/thousandshores/tribit/utils/ui/PrivateTextUtil;

    invoke-virtual {p0}, Lcom/thousandshores/tribit/utils/ui/PrivateTextUtil;->isFastClick()Z

    move-result p0

    if-eqz p0, :krinik_done

    invoke-static {}, Lcom/thousandshores/tool/utils/SPUtils;->getInstance()Lcom/thousandshores/tool/utils/SPUtils;

    move-result-object p0

    const-string v0, "is_agree_private"

    const/4 v1, 0x1

    invoke-virtual {p0, v0, v1}, Lcom/thousandshores/tool/utils/SPUtils;->put(Ljava/lang/String;Z)V

    invoke-virtual {v2}, Landroid/view/View;->getContext()Landroid/content/Context;

    move-result-object p0

    instance-of v0, p0, Lcom/thousandshores/tribit/modulelogin/activity/FirstNewActivity;

    if-eqz v0, :krinik_old

    check-cast p0, Lcom/thousandshores/tribit/modulelogin/activity/FirstNewActivity;

    invoke-direct {p0}, Lcom/thousandshores/tribit/modulelogin/activity/FirstNewActivity;->checkToken()V

    return-void

    :krinik_old
    const-class p0, Lcom/thousandshores/tribit/modulelogin/activity/LoginNewActivity;

    invoke-static {p0}, Lcom/thousandshores/tool/utils/ActivityUtils;->startActivity(Ljava/lang/Class;)V

    :krinik_done
    return-void
.end method
"""


# --- Patch 19: no account in the interface - the profile has no «Register/Log in» row ---------------------------
# Owner 2026-10-16 ≈ 09:19 +03:00: «выпиливаем НАХУЙ аккаунты». MineActivity.afterCreate shows rlRegister («Зарегистрироваться/
# Войти») when DialogDefault.checkLoginType says «not logged in» and rlName otherwise; with patch 8 nobody logs in, so the
# row would invite to the screens we removed. Fix: that branch hides rlRegister the way the logged-in branch does (v0 = 8,
# GONE). Other entries to the login screens (DeviceFragment, MainNewActivity, «forgot password») - next step of plan 01 §4б.
# [TESTED: 2026-10-16 · A51: profile shows neither «Зарегистрироваться/Войти» nor «Установите псевдоним» · testcases/reports/2026-10-16_wave1.md]
def patch_no_account_ui():
    p = smali("com.thousandshores.tribit.modulemine.activity.MineActivity")
    replace_in_method(p, ".method public afterCreate(Landroid/os/Bundle;)V",
        "->rlRegister:Landroid/widget/RelativeLayout;\n\n    invoke-virtual {p1, v3}, Landroid/view/View;->setVisibility(I)V",
        "->rlRegister:Landroid/widget/RelativeLayout;\n\n    invoke-virtual {p1, v0}, Landroid/view/View;->setVisibility(I)V")
    # Without an account login_type keeps its default "1" (DialogDefault.checkLoginType: "1" = registered, "2" = guest
    # with «register» dialogs), so the profile takes the logged-in branch and shows rlName «Установите псевдоним» - an
    # account entry too (observed on the A51). That branch hides rlName as well.
    replace_in_method(p, ".method public afterCreate(Landroid/os/Bundle;)V",
        "->rlName:Landroid/widget/RelativeLayout;\n\n    invoke-virtual {p1, v3}, Landroid/view/View;->setVisibility(I)V",
        "->rlName:Landroid/widget/RelativeLayout;\n\n    invoke-virtual {p1, v0}, Landroid/view/View;->setVisibility(I)V")
    print("ok 19 no account UI: profile without 'Register/Log in' and nickname rows")


# --- Patch 9: their server never throws the user out to the login screen -----------------------------------
# Play complaint 12 «keeps logging me out» (74 reviews). RequestHandler.requestSuccess reads resp_msg of every answer:
# «Offsite access token» and «Full authentication» wipe the tokens and open the login screen, «Invalid access token»
# posts ReloginEvent (researches/06 З4). Fix: right after the answer is parsed, return it - the three branches are
# skipped (also the NPE of resp_msg.contains on an empty resp_msg). Cloud functions fail quietly on a stale token.
# [NOT-TESTED] the throw-out itself (needs a server answer we cannot provoke); the user path runs without crashes - testcases/reports/2026-10-16_wave1.md
def patch_no_relogin():
    p = smali("com.thousandshores.tribit.http.model.RequestHandler")
    replace_in_method(p, ".method public requestSuccess(",
        "    instance-of p3, p1, Lcom/thousandshores/tribit/bean/BaseData;\n\n"
        "    if-eqz p3, :cond_f\n",
        "    goto :cond_f\n")
    print("ok  9 no relogin: server answers are returned as parsed")


# --- Patch 10: no forced update ---------------------------------------------------------------------------
# ViewModelMainNew.checkUpdate asks their server for the latest version and shows a dialog without a close button
# that leads to Google Play, where the «update» replaces Krinik Tribit with the original (researches/06 З5). The
# settings screen has its own manual check (ViewModelSettings.checkUpdate). Fix: both methods return at once.
# [TESTED: 2026-10-16 · A51: «Проверка обновлений» -> 0 EasyHttp lines, no dialog; the same process logged 7 other requests · testcases/reports/2026-10-16_wave1.md]
EMPTY_VOID = "    .locals 0\n\n    return-void\n.end method"


def patch_no_forced_update():
    p = smali("com.thousandshores.tribit.ViewModelMainNew")
    h = ".method public final checkUpdate(Landroidx/lifecycle/LifecycleOwner;Ljava/lang/String;)V"
    replace_method(p, h, h + "\n" + EMPTY_VOID)
    s = smali("com.thousandshores.tribit.modulemine.viewmodel.ViewModelSettings")
    h2 = ".method public final checkUpdate(Landroidx/lifecycle/LifecycleOwner;Ljava/lang/String;Z)V"
    replace_method(s, h2, h2 + "\n" + EMPTY_VOID)
    print("ok 10 no forced update: both checkUpdate return at once")


# --- Patch 20: no cloud copy of EQ and sound profiles, no support form and no error-log upload -------------------
# Owner 2026-10-16 ≈ 09:21 +03:00: «копия эквалайзеров в облаке и форма поддержки - не нужно это нахуй». Their gateway
# has 10 such endpoints under three paths: api-equip/thirdApi/equalizer/... (get, sync, sort, remove), .../persound/...
# (the same four for hearing profiles), api-app/api/userFeedback/... (the support form and autoReportErrorLogTribit, the
# silent log upload). Fixed by form, in ONE place: an OkHttp interceptor in the app's only client (TribitApp, EasyConfig)
# fails these requests on the phone with an IOException - EasyHttp's onHttpFail path, which the app already handles;
# presets stay in the local database. Every cut is logged under the tag KrinikNoCloud (observable on the device).
# [NOT-TESTED] the cut itself (A51: only the user path without crashes - testcases/reports/2026-10-16_wave1.md)
# Widened 2026-10-16 with patch 8 (owner 10:45 «только сообщаем, какая колонка просит прошивку и настроек»): the decision
# moved into krinik.Gate (patches/java) - an ALLOW list of their API paths; the three paths above are cut by it as well.
# [TESTED: 2026-10-16 · A51: the profile request cut on the phone, allowed paths passed · testcases/reports/2026-10-16_patch8_anon.md]
NO_CLOUD_SMALI = """
.class public final Lkrinik/NoCloud;
.super Ljava/lang/Object;
.source "NoCloud.smali"

# implements
.implements Lokhttp3/Interceptor;


.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static cut(Ljava/lang/String;)Z
    .locals 1

    invoke-static {p0}, Lkrinik/Gate;->cut(Ljava/lang/String;)Z

    move-result v0

    return v0
.end method

.method public intercept(Lokhttp3/Interceptor$Chain;)Lokhttp3/Response;
    .locals 3

    invoke-interface {p1}, Lokhttp3/Interceptor$Chain;->request()Lokhttp3/Request;

    move-result-object v0

    invoke-virtual {v0}, Lokhttp3/Request;->url()Lokhttp3/HttpUrl;

    move-result-object v1

    invoke-virtual {v1}, Lokhttp3/HttpUrl;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lkrinik/NoCloud;->cut(Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :blocked

    invoke-interface {p1, v0}, Lokhttp3/Interceptor$Chain;->proceed(Lokhttp3/Request;)Lokhttp3/Response;

    move-result-object v0

    return-object v0

    :blocked
    const-string v2, "KrinikNoCloud"

    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    new-instance v0, Ljava/io/IOException;

    const-string v2, "Krinik Tribit: cloud request cut on the phone"

    invoke-direct {v0, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
.end method
"""


def patch_no_cloud():
    target = ROOT / "smali_classes5" / "krinik" / "NoCloud.smali"
    if target.exists():
        sys.exit("FAIL: krinik/NoCloud.smali already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(NO_CLOUD_SMALI.lstrip("\n"), encoding="utf-8")
    p = smali("com.thousandshores.tribit.TribitApp")
    t = p.read_text(encoding="utf-8")
    old = "    new-instance v2, Lokhttp3/OkHttpClient$Builder;\n\n    invoke-direct {v2}, Lokhttp3/OkHttpClient$Builder;-><init>()V\n"
    if t.count(old) != 1:
        sys.exit("FAIL: OkHttpClient.Builder anchor in TribitApp")
    p.write_text(t.replace(old, old +
        "\n    new-instance v3, Lkrinik/NoCloud;\n\n    invoke-direct {v3}, Lkrinik/NoCloud;-><init>()V\n\n"
        "    invoke-virtual {v2, v3}, Lokhttp3/OkHttpClient$Builder;->addInterceptor(Lokhttp3/Interceptor;)Lokhttp3/OkHttpClient$Builder;\n"),
        encoding="utf-8")
    print("ok 20 no cloud: equalizer/, persound/, userFeedback/ requests cut on the phone (log tag KrinikNoCloud)")


# --- Patch 21: Firebase out - no analytics with the advertising ID, no Crashlytics, no pushes ------------------
# Owner 2026-10-16 ≈ 09:21 +03:00: «Firebase: аналитика с рекламным идентификатором (разрешение AD_ID), Crashlytics,
# пуши - выпиливаем нахуй» (MASTER_PLAN decision journal). The libraries stay in the APK (their registrars are looked up
# by FirebaseApp; cutting them crashes getInstance() calls) - Firebase's own documented switches turn collection off:
# analytics deactivated, ad-id collection off, Crashlytics off, messaging and in-app messaging auto-init off. The ad
# permissions and the push entry points (our receiver of FCM, the FCM service, the instance-id receiver) leave the
# manifest; the token request in MainNewActivity/MainActivity.onResume goes too (it would still register the phone).
# [TESTED: 2026-10-16 · A51 vs control: FirebaseMessaging log lines 67 -> 0, «App measurement deactivated», «Sessions SDK disabled», no ad/push permissions, no crash · testcases/reports/2026-10-16_wave1.md]
FIREBASE_OFF = (
    '        <meta-data android:name="firebase_analytics_collection_deactivated" android:value="true"/>\n'
    '        <meta-data android:name="google_analytics_adid_collection_enabled" android:value="false"/>\n'
    '        <meta-data android:name="google_analytics_default_allow_ad_personalization_signals" android:value="false"/>\n'
    '        <meta-data android:name="firebase_crashlytics_collection_enabled" android:value="false"/>\n'
    '        <meta-data android:name="firebase_messaging_auto_init_enabled" android:value="false"/>\n'
    '        <meta-data android:name="firebase_inapp_messaging_auto_data_collection_enabled" android:value="false"/>\n')
AD_PERMISSIONS = ["com.google.android.c2dm.permission.RECEIVE", "com.google.android.gms.permission.AD_ID",
                  "android.permission.ACCESS_ADSERVICES_ATTRIBUTION", "android.permission.ACCESS_ADSERVICES_AD_ID"]
PUSH_BLOCKS = [  # (opening line fragment, closing tag) - each removed whole, exactly once
    ('<service android:exported="true" android:name="com.thousandshores.tribit.http.server.MyFirebaseMessagingService">', "</service>"),
    ('<receiver android:exported="true" android:name="com.google.firebase.iid.FirebaseInstanceIdReceiver"', "</receiver>"),
    ('<service android:directBootAware="true" android:exported="false" android:name="com.google.firebase.messaging.FirebaseMessagingService">', "</service>"),
]
FCM_TOKEN = re.compile(
    r"    invoke-static \{\}, Lcom/google/firebase/messaging/FirebaseMessaging;->getInstance\(\)Lcom/google/firebase/messaging/FirebaseMessaging;\n"
    r"(?:.*\n){1,16}?"
    r"    invoke-virtual \{v0, v1\}, Lcom/google/android/gms/tasks/Task;->addOnCompleteListener\(Lcom/google/android/gms/tasks/OnCompleteListener;\)Lcom/google/android/gms/tasks/Task;\n")


def patch_firebase_off():
    m = ROOT / "AndroidManifest.xml"
    t = m.read_text(encoding="utf-8")
    for perm in AD_PERMISSIONS:
        t = _drop_line(t, f'<uses-permission android:name="{perm}"/>', perm)
    for opening, closing in PUSH_BLOCKS:
        s = t.find(opening)
        if s < 0 or t.find(opening, s + 1) >= 0:
            sys.exit(f"FAIL: manifest block not found once: {opening[:70]}")
        s = t.rfind("\n", 0, s) + 1
        e = t.find(closing, s) + len(closing) + 1
        t = t[:s] + t[e:]
    anchor = '        <meta-data android:name="UMENG_CHANNEL"'
    if t.count(anchor) != 1:
        sys.exit("FAIL: UMENG_CHANNEL anchor for the Firebase switches")
    t = t.replace(anchor, FIREBASE_OFF + anchor)
    m.write_text(t, encoding="utf-8")
    for cls in ("com.thousandshores.tribit.MainNewActivity", "com.thousandshores.tribit.MainActivity"):
        p = smali(cls)
        s = p.read_text(encoding="utf-8")
        s2, n = FCM_TOKEN.subn("", s)
        if n != 1:
            sys.exit(f"FAIL: FCM token block in {cls}: {n}")
        p.write_text(s2, encoding="utf-8")
    print(f"ok 21 Firebase off: 6 switches, {len(AD_PERMISSIONS)} ad/push permissions and {len(PUSH_BLOCKS)} push entries removed, no FCM token")


def _drop_line(text, line, what):
    full = "    " + line + "\n"
    if text.count(full) != 1:
        sys.exit(f"FAIL: manifest line not found once: {what}")
    return text.replace(full, "")


# --- Patch 23: no error letters by e-mail ----------------------------------------------------------------------
# Found 2026-10-16 while closing patch 8: EqExceptionMonitor.handleException (an EQ error) calls sendExceptionEmail, which
# mails the phone's MANUFACTURER + MODEL, the Android version, the saved e-mail and the latest log file over SMTP
# (smtp.163.com:465) - outside OkHttp, so krinik.Gate never sees it. Owner 2026-10-16 10:52 +03:00: «мы ПРОТИВ
# отслеживания метрик через Фаербейз и сервер Трибит»; 09:21 the error-log upload went with the support form (patch 20).
# Fix: sendExceptionEmail returns at once; the local copy (saveExceptionToLocal) stays on the phone.
# TWINS: searched `mail.smtp` in their code (decompiled/) - 1 site, this one.
# [NOT-TESTED]
def patch_no_error_mail():
    p = smali("com.thousandshores.tribit.utils.audio.EqExceptionMonitor")
    h = ".method public final sendExceptionEmail(Lcom/thousandshores/tribit/utils/audio/EqExceptionMonitor$ExceptionInfo;)V"
    replace_method(p, h, h + "\n" + EMPTY_VOID)
    print("ok 23 no error mail: EqExceptionMonitor.sendExceptionEmail returns at once")


# --- Patch 24: the speaker name on a device card wraps instead of ending in «…» ---------------------------------
# Owner 2026-10-16 11:43 +03:00 (chat, on «Tribit StormBox Blas…» of the Add Device card): «название нужно переносить на
# две+ строки, чтобы помещалось». The name TextView tv_name of the new device cards is singleLine with a fixed 26 dp
# height. Class inventory (2026-10-16, `grep tv_name res/layout/item_device*.xml`): item_device_new (main screen),
# item_device_search_new (Add Device), item_device_list_new - the three with singleLine; the other five item_device*
# already wrap. Fix by form, for the class: singleLine -> maxLines 3, height -> wrap_content.
# [TESTED: 2026-10-16 · A51 main screen: two balanced lines, no ellipsis; Add Device card not seen · testcases/reports/2026-10-16_patch8_anon.md]
NAME_CARDS = ["item_device_new", "item_device_search_new", "item_device_list_new"]
NAME_MAX_LINES = 3  # «две+» - two lines fit the longest names seen; a third keeps a long rename visible


def patch_card_name_wrap():
    for name in NAME_CARDS:
        p = ROOT / "res" / "layout" / f"{name}.xml"
        t = p.read_text(encoding="utf-8")
        tags = re.findall(r'<TextView [^>]*android:id="@id/tv_name"[^>]*>', t)
        if len(tags) != 1:
            sys.exit(f"FAIL: tv_name in {name}: {len(tags)}")
        old = tags[0]
        if old.count('android:singleLine="true"') != 1 or old.count('android:layout_height="@dimen/dp_26"') != 1:
            sys.exit(f"FAIL: tv_name of {name} is not the singleLine 26 dp row")
        # balanced: «Tribit StormBox / Blast 2» instead of «Tribit StormBox Blast / 2» (A51 11:56, snapshot 17_main_wrap)
        new = (old.replace('android:singleLine="true"',
                           f'android:maxLines="{NAME_MAX_LINES}" android:breakStrategy="balanced"')
                  .replace('android:layout_height="@dimen/dp_26"', 'android:layout_height="wrap_content"'))
        p.write_text(t.replace(old, new), encoding="utf-8")
    print(f"ok 24 card name wraps up to {NAME_MAX_LINES} lines: {', '.join(NAME_CARDS)}")


# --- Patch 25: the firmware check runs on a tap only ------------------------------------------------------------
# Owner 2026-10-16 10:45 +03:00 (interviews/interview_001 Q2 = A): «По кнопке «Проверить прошивку» в настройках колонки»;
# its check: «при открытии страницы колонки нет checkFirmwareUpgrade; после нажатия — ровно один». The decision lives in
# krinik.Firmware (patches/java): each of the two sinks is renamed to krinikQueryFireVersion and a same-named wrapper asks
# Firmware.allowBts/allowInfo first; TribitApp.onCreate installs the activity watcher that turns the «Версия прошивки» row
# into the button. Recon - plans/01 §4б item 6 (26 call sites, 13 families, 2 sinks, 14 layouts with the row).
# [TESTED: 2026-10-16 · A51 Blast 2 (bts56 only): page open -> 0 checkFirmwareUpgrade; row tap -> 2 (main + DSP) and
# their «latest version» message · testcases/reports/2026-10-16_patch8_anon.md] - earphone sink (ViewModelDeviceInfo) not run
FIRMWARE_SINKS = [  # (class, parameter descriptor, gate method, last parameter register)
    ("com.thousandshores.tribit.moduledevice.viewmodel.ViewModelDeviceBts",
     "Landroidx/lifecycle/LifecycleOwner;Ljava/lang/String;Ljava/lang/String;IZ", "allowBts", "p5"),
    ("com.thousandshores.tribit.moduledevice.viewmodel.ViewModelDeviceInfo",
     "Landroidx/lifecycle/LifecycleOwner;Ljava/lang/String;Ljava/lang/String;I", "allowInfo", "p4"),
]


def patch_firmware_on_tap():
    for cls, params, gate, last in FIRMWARE_SINKS:
        p = smali(cls)
        t = p.read_text(encoding="utf-8")
        header = f".method public final queryFireVersion({params})V"
        if t.count(header) != 1 or "krinikQueryFireVersion" in t:
            sys.exit(f"FAIL: firmware sink header in {cls}")
        desc = "L" + cls.replace(".", "/") + ";"
        wrapper = (
            f"{header}\n"
            "    .locals 1\n\n"
            f"    invoke-static/range {{p0 .. {last}}}, Lkrinik/Firmware;->{gate}(Ljava/lang/Object;Ljava/lang/Object;"
            "Ljava/lang/String;Ljava/lang/String;I" + ("Z" if last == "p5" else "") + ")Z\n\n"
            "    move-result v0\n\n"
            "    if-eqz v0, :krinik_dropped\n\n"
            f"    invoke-virtual/range {{p0 .. {last}}}, {desc}->krinikQueryFireVersion({params})V\n\n"
            "    :krinik_dropped\n"
            "    return-void\n"
            ".end method\n\n")
        t = t.replace(header, f".method public final krinikQueryFireVersion({params})V")
        t = t.replace(f".method public final krinikQueryFireVersion({params})V",
                      wrapper + f".method public final krinikQueryFireVersion({params})V", 1)
        p.write_text(t, encoding="utf-8")
    a = smali("com.thousandshores.tribit.TribitApp")
    replace_in_method(a, ".method public onCreate()V",
        "    invoke-super {p0}, Landroid/app/Application;->onCreate()V\n",
        "    invoke-super {p0}, Landroid/app/Application;->onCreate()V\n\n"
        "    invoke-static {p0}, Lkrinik/Firmware;->install(Landroid/app/Application;)V\n")
    print("ok 25 firmware check on tap only: 2 sinks gated by krinik.Firmware, the firmware version row is the button")


# --- Patch 26: the «on» switch of the speaker settings in Krinik pink -----------------------------------------
# Owner 2026-10-16 11:54 +03:00 (chat, on the yellow switch «Индикатор громкости»): «не по нашей дизайн сжеме» · «схеме».
# The switch of every speaker settings row is two PNGs set by DateUtils.updateView1: ic_eqbutton (off) and
# ic_eqbutton_checked (on: dark track, solid #FFEB00 knob, edges blended into the track). Recolour per pixel, so the
# blended edges follow: yellowness a = (G - B) / 235 (0 on the neutral track, 1 on the knob), out = in + a x (pink - yellow)
# = (R, G - 209a, B + 140a). The other yellow PNGs of plans/02 (56 names) need an eye on each - not in this patch.
# [TESTED: 2026-10-16 · histogram: knob 1672 px #FF1A8C, track unchanged; A51 settings «Индикатор громкости» pink
# (shot 44_settings_pink) · testcases/reports/2026-10-16_patch8_anon.md]
PINK_PNGS = ["mipmap-xxhdpi/ic_eqbutton_checked.png"]
# Knob #FFEB00 -> #FF1A8C: G - 209, B + 140 (HOUSE_RULES R3). Yellowness from the ORIGINAL pixel; G - B up to 4/255 counts
# as neutral (the track is (33,33,31) and must stay as is). Each channel is computed in its own clone, then combined.
YELLOWNESS = "clamp(((g-b)*255-4)/231)"


def patch_pink_switch():
    import subprocess
    for rel in PINK_PNGS:
        png = ROOT / "res" / rel
        if not png.exists():
            sys.exit(f"FAIL: {rel} missing")
        cmd = ["magick", str(png),
               "(", "-clone", "0", "-fx", "r", ")",
               "(", "-clone", "0", "-fx", f"g-{YELLOWNESS}*209/255", ")",
               "(", "-clone", "0", "-fx", f"b+{YELLOWNESS}*140/255", ")",
               "(", "-clone", "0", "-alpha", "extract", ")",
               "-delete", "0", "-channel", "RGBA", "-combine", str(png)]
        if subprocess.run(cmd).returncode != 0:
            sys.exit(f"FAIL: recolour {rel}")
        hist = subprocess.run(["magick", str(png), "-format", "%c", "histogram:info:-"], capture_output=True, text=True).stdout
        if "#FFEB00" in hist.upper() or "#FF1A8C" not in hist.upper():
            sys.exit(f"FAIL: {rel} still yellow or not pink")
    print(f"ok 26 pink switch: {len(PINK_PNGS)} PNG recoloured yellow -> #FF1A8C")


# --- Patch 27: the settings title is «Настройки», the speaker name on the line below ------------------------------
# Owner 2026-10-16 12:41 +03:00 (chat, on «НастройкиTribit StormBox Blast 2»): «Заголовок экрана просто Настройки» ·
# «Отдельной строкой ниже название колонки». Class inventory: 26 sites, each `const vN, 0x7f120551` (R.string.settings)
# + ResourceUtils.getString (a `.line` may stand between), in the 13 *Info*Activity classes and their showNameEditDialog
# listeners - every one appends the speaker name. They call krinik.Title.settings (their text + a line break) instead;
# the two other users of R.string.settings (BtsControlActivity, DeviceControlActivity) stay. The 12 settings headers
# (a 44 dp row: iv_back, tv_title, help) grow with the two lines: height wrap_content, minHeight 44 dp.
# [TESTED: 2026-10-16 · A51 Blast 2 settings: «Настройки» / «Tribit StormBox Blast 2» in two lines (shot 47) · testcases/reports/2026-10-16_patch8_anon.md] - the other 12 families not opened
SETTINGS_TITLE = re.compile(
    r"(const (v\d+), 0x7f120551\n\n(?:    \.line \d+\n)?    )"
    r"invoke-static \{\2\}, Lcom/thousandshores/tool/utils/ResourceUtils;->getString\(I\)Ljava/lang/String;")
SETTINGS_TITLE_SITES = 26
SETTINGS_HEADER = re.compile(
    r'(<LinearLayout [^>]*)android:layout_height="@dimen/dp_44"([^>]*>\s*<ImageView android:id="@id/iv_back"[^>]*>\s*'
    r'<TextView [^>]*android:id="@id/tv_title")')
SETTINGS_HEADERS = 12


def patch_settings_title():
    n = 0
    for p in ROOT.glob("smali*/com/thousandshores/tribit/moduledevice/*/*Info*.smali"):
        t = p.read_text(encoding="utf-8")
        t2, k = SETTINGS_TITLE.subn(r"\1invoke-static {\2}, Lkrinik/Title;->settings(I)Ljava/lang/String;", t)
        if k:
            p.write_text(t2, encoding="utf-8")
            n += k
    if n != SETTINGS_TITLE_SITES:
        sys.exit(f"FAIL: settings title sites {n}, expected {SETTINGS_TITLE_SITES}")
    h = 0
    for p in ROOT.glob("res/layout/activity_*info*.xml"):
        t = p.read_text(encoding="utf-8")
        t2, k = SETTINGS_HEADER.subn(r'\1android:layout_height="wrap_content" android:minHeight="@dimen/dp_44"\2', t)
        if k:
            p.write_text(t2, encoding="utf-8")
            h += k
    if h != SETTINGS_HEADERS:
        sys.exit(f"FAIL: settings headers {h}, expected {SETTINGS_HEADERS}")
    print(f"ok 27 settings title: name on the second line ({n} sites, {h} headers grow)")


# --- Patch 28: the back button «<» drawn smaller, the same place to tap -------------------------------------------
# Owner 2026-10-16 12:41 +03:00: «Кнопки < можноменьше размером». Class: every ImageView iv_back of 32 x 32 dp in the app's
# layouts (43 of them, 2026-10-16; four more are 20 dp already, one wrap_content). A 6 dp padding draws the arrow at
# 20 dp inside the same 32 dp view - the touch area does not shrink (it is already below Material's 48 dp).
# [TESTED: 2026-10-16 · A51: smaller arrow on the speaker settings screen (shot 47) · testcases/reports/2026-10-16_patch8_anon.md] - other screens not looked at
BACK_BUTTON = re.compile(r'(<ImageView android:id="@id/iv_back" android:layout_width="@dimen/dp_32" '
                         r'android:layout_height="@dimen/dp_32")(?![^>]*padding)')
BACK_BUTTONS = 43


def patch_smaller_back():
    n = 0
    for p in ROOT.glob("res/layout/*.xml"):
        t = p.read_text(encoding="utf-8")
        t2, k = BACK_BUTTON.subn(r'\1 android:padding="@dimen/dp_6"', t)
        if k:
            p.write_text(t2, encoding="utf-8")
            n += k
    if n != BACK_BUTTONS:
        sys.exit(f"FAIL: back buttons {n}, expected {BACK_BUTTONS}")
    print(f"ok 28 back button drawn at 20 dp in {n} layouts")


# --- Patch 29: no «Сообщить о проблеме? Перейти» on the connection-help page -------------------------------------
# Owner 2026-10-16 ≈ 09:21 +03:00: «копия эквалайзеров в облаке и форма поддержки - не нужно это нахуй» (MASTER_PLAN
# journal). The help page of the speaker search (activity_device_help_new, seen on the A51 11:57, shot 19_add_wrap) links
# to FeedBackNewActivity through tv_problem + tv_problem_go; both go. TWINS: searched `FeedBackNewActivity.class|
# FeedBackActivity.class` - 5 classes: DeviceHelpNewActivity (this patch), MineActivity, MineFragment, DialogDefault,
# WebViewHelpActivity - the other four are listed in plans/02 for the next step; sending is cut by krinik.Gate anyway.
# [TESTED: 2026-10-16 · A51: help page of the search without the support line (shot 49_help_no_support) · testcases/reports/2026-10-16_patch8_anon.md]
HELP_SUPPORT_VIEWS = ["tv_problem", "tv_problem_go"]


def patch_no_support_link():
    p = ROOT / "res/layout/activity_device_help_new.xml"
    t = p.read_text(encoding="utf-8")
    for vid in HELP_SUPPORT_VIEWS:
        tag = re.findall(rf'<TextView [^>]*android:id="@id/{vid}"[^>]*>', t)
        if len(tag) != 1 or "android:visibility" in tag[0]:
            sys.exit(f"FAIL: {vid} in activity_device_help_new")
        t = t.replace(tag[0], tag[0].replace("<TextView ", '<TextView android:visibility="gone" ', 1))
    p.write_text(t, encoding="utf-8")
    print("ok 29 help page: no link to the support form")


# --- Patch 31: white bold text, 19 sp and up, on every pink-filled button ----------------------------------------
# Owner 2026-10-16 13:32 +03:00: «B вариант по кнопкам» (interviews/interview_002 Q2 = B: white text on our #FF1A8C, the
# label bigger and bolder, «от 19 px жирным» - WCAG large text needs 3:1, white on #FF1A8C is 3.63:1). Class inventory
# 2026-10-16 (scratch scan of res/layout: every widget whose background selector is pink-filled in its default state):
# 88 buttons and text views + 3 icon buttons (PINK_CONTAINER) in 11 selectors, their text was black #040A07 / #333333 at 13-17 dp. Outline buttons (shape_eq_waite,
# shape_eq_edit: pink text on dark) and buttons pink only when selected (btn_text_size, btn_register_prepare) stay as they are.
# The disabled state of btn_normal/btn_labble_save was Tribit's darkened yellow #B1A200 (patch 17 missed it: not in its
# yellow list) - white on it is 2.61:1; it becomes pink darkened the same way (x 0.695) #B1125F, white on it 6.73:1
# (WCAG relative luminance, computed by a script 2026-10-16).
# [TESTED: 2026-10-16 · A51: «Выключение» of the speaker settings white bold on pink (shot 04_settings) ·
# testcases/reports/2026-10-16_patch31_32.md] - the disabled state and the screens off our path not opened
PINK_FILLED = ("btn_normal", "btn_login_new", "btn_login", "btn_hearing_yes", "btn_eq_button", "btn_labble_save",
               "update_bg_new_version", "shape_ai_checked", "btn_quick_new", "btn_start", "btn_sound_manager")
PINK_BUTTONS = 88
BUTTON_TEXT_SP = 19.0
DISABLED_PINK = "b1125f"
PINK_BUTTON_TAG = re.compile(r'<[\w.]*(?:Button|TextView) [^>]*android:background="@drawable/(' + "|".join(PINK_FILLED) + r')"[^>]*>')
# Three pink buttons are a RelativeLayout around an icon + a TextView (layout_no_device «add», two webview feedback rows):
# the label goes white the same way, the black icon is tinted white.
PINK_CONTAINER = re.compile(r'(<RelativeLayout [^>]*android:background="@drawable/(?:' + "|".join(PINK_FILLED) +
                            r')"[^>]*>\s*<LinearLayout [^>]*>\s*<ImageView )([^>]*>\s*)(<TextView [^>]*>)')
PINK_CONTAINERS = 3


def _bigger_bold_white(tag, dimens):
    """One widget tag: white text, bold, at least BUTTON_TEXT_SP."""
    tag = re.sub(r' android:textColor="[^"]*"', "", tag)
    tag = re.sub(r' android:textStyle="[^"]*"', "", tag)
    size = re.search(r' android:textSize="([^"]*)"', tag)
    if size:
        v = size.group(1)
        if v.startswith("@dimen/"):
            v = dimens.get(v.split("/")[1], "0")
        num = float(re.match(r"[\d.]+", v).group(0)) if re.match(r"[\d.]+", v) else 0.0
        if num < BUTTON_TEXT_SP:
            tag = tag.replace(size.group(0), f' android:textSize="{BUTTON_TEXT_SP}sp"')
    else:
        tag = tag.replace(" ", f' android:textSize="{BUTTON_TEXT_SP}sp" ', 1)
    return tag.replace(" ", ' android:textColor="#ffffffff" android:textStyle="bold" ', 1)


def patch_pink_buttons_white_text():
    res = ROOT / "res"
    dimens = dict(re.findall(r'<dimen name="([^"]+)">([^<]+)</dimen>', (res / "values/dimens.xml").read_text(encoding="utf-8")))
    n = c = 0
    for p in res.glob("layout*/*.xml"):
        t = p.read_text(encoding="utf-8")
        t2, k = PINK_BUTTON_TAG.subn(lambda m: _bigger_bold_white(m.group(0), dimens), t)
        t2, kc = PINK_CONTAINER.subn(lambda m: m.group(1) + 'android:tint="#ffffffff" ' + m.group(2)
                                     + _bigger_bold_white(m.group(3), dimens), t2)
        if k or kc:
            p.write_text(t2, encoding="utf-8")
            n += k
            c += kc
    if n != PINK_BUTTONS or c != PINK_CONTAINERS:
        sys.exit(f"FAIL: pink buttons {n} (expected {PINK_BUTTONS}), containers {c} (expected {PINK_CONTAINERS})")
    _sub_once(res / "values/colors.xml", '<color name="common_button_enableed_55_bg">#ffb1a200</color>',
              f'<color name="common_button_enableed_55_bg">#ff{DISABLED_PINK}</color>', "disabled button colour")
    for d in ("shape_leable_disable_button", "shape_normal_button_enable", "shape_normal_button_not"):
        p = res / f"drawable/{d}.xml"
        t = p.read_text(encoding="utf-8")
        p.write_text(re.sub("b1a200", DISABLED_PINK, t, flags=re.I), encoding="utf-8")
    print(f"ok 31 pink buttons: white bold text >= {BUTTON_TEXT_SP:g} sp on {n} widgets + {c} icon buttons, "
          f"disabled #{DISABLED_PINK.upper()}")


# --- Patch 32: no way out to Tribit - our user guide, our GitHub ---------------------------------------------------
# Owner 2026-10-16 13:32 +03:00: «ни на какую поддерку Трибита и на их сайт, форумы - мы не ведем из Krinik Tribit. Убираем
# это. В О приложении будет ссылка на GH Криника»; 13:38 +03:00 (interviews/interview_002 Q3): the user guide in the app
# tells that «очистить данные приложения» starts a new anonymous guest. Inventory 2026-10-16 (decompiled sources, grep of
# tribit.com|saasadmin|1000shores|startWithUrl|FeedBack*Activity.class):
#   a. help center (gtwt.1000shores.cn/tribit_help_*): MineActivity, MineFragment, DeviceHelpNewActivity .goHelpCenter and
#      UpdateUtils.goDeviceHelp (the «?» of 17 speaker and earphone pages, plus their FAQ URLs from the server) - all four
#      open krinik.Guide instead: our guide from assets/krinik/guide_<ru|en>.html in their own web view screen;
#   b. profile rows «Tribit.com» (ll_mian_page) and «Rate us» (ll_evaluate, the store page) - gone; the «help center» row
#      is labelled «Руководство пользователя» (krinik.Guide.title);
#   c. About: Tribit's logo -> our tile; their privacy/terms links (saasadmin.tribit.com) - gone; «Contact:
#      support@tribit.com» -> our GitHub as a link;
#   d. not touched: the login/registration privacy links (screens unreachable without an account, patch 8), the support
#      form of WebViewHelpActivity (reached only through goDeviceHelp, now the guide), DialogDefault -> FeedBackActivity
#      (sending cut by krinik.Gate), «About Audiodo» (not Tribit).
# [TESTED: 2026-10-16 · A51: profile without Tribit.com / Rate us, the guide row and the Blast 2 «?» open guide_ru.html
# with 0 requests, About shows our tile and the GitHub link (opened in Chrome) · testcases/reports/2026-10-16_patch31_32.md]
# - MineFragment, the other 16 «?» families and guide_en.html not opened
GUIDE_DIR = pathlib.Path(__file__).resolve().parent / "assets" / "krinik"
GUIDE_FILES = ("guide_ru.html", "guide_en.html")
GUIDE_OPEN = "    .locals 0\n\n    invoke-static {}, Lkrinik/Guide;->open()V\n\n    return-void\n.end method"
HELP_ENTRIES = [
    ("com.thousandshores.tribit.modulemine.activity.MineActivity", ".method private final goHelpCenter()V"),
    ("com.thousandshores.tribit.modulemine.fragment.MineFragment", ".method private final goHelpCenter()V"),
    ("com.thousandshores.tribit.moduledevice.activity.DeviceHelpNewActivity", ".method public final goHelpCenter()V"),
    ("com.thousandshores.tribit.utils.UpdateUtils", ".method public final goDeviceHelp(Ljava/lang/String;Ljava/util/ArrayList;)V"),
]
HELP_CENTER_LABEL = re.compile(
    r"(const (v\d+), 0x7f1202e7\n\n(?:    \.line \d+\n)?    )"   # R.string.help_center
    r"invoke-static \{\2\}, Lcom/thousandshores/tool/utils/ResourceUtils;->getString\(I\)Ljava/lang/String;")
CONTACT_EMAIL = re.compile(
    r"(const (v\d+), 0x7f1201c6\n\n(?:    \.line \d+\n)?    )"   # R.string.contact_email
    r"invoke-static \{\2\}, Lcom/thousandshores/tool/utils/ResourceUtils;->getString\(I\)Ljava/lang/String;")


def _view_attr(path, view_id, old, new):
    """Edit one attribute of the single tag with android:id=@id/<view_id>."""
    t = path.read_text(encoding="utf-8")
    tags = re.findall(rf'<[\w.]+ [^>]*android:id="@id/{view_id}"[^>]*>', t)
    if len(tags) != 1 or old not in tags[0]:
        sys.exit(f"FAIL: {view_id} in {path.name}: {len(tags)} tag(s) or no «{old}»")
    path.write_text(t.replace(tags[0], tags[0].replace(old, new, 1)), encoding="utf-8")


def patch_no_tribit_links():
    for name in GUIDE_FILES:
        data = (GUIDE_DIR / name).read_bytes()
        if b"KRINIK TRIBIT" not in data or b"github.com/MikalaiKryvusha/KrinikTribitApp" not in data:
            sys.exit(f"FAIL: guide {name} has no title or no GitHub link")
        target = ROOT / "assets" / "krinik" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    # a. every help-center entry opens our guide
    for cls, header in HELP_ENTRIES:
        replace_method(smali(cls), header, header + "\n" + GUIDE_OPEN)
    # b. profile
    mine = smali("com.thousandshores.tribit.modulemine.activity.MineActivity")
    t, k = HELP_CENTER_LABEL.subn(r"\1invoke-static {\2}, Lkrinik/Guide;->title(I)Ljava/lang/String;", mine.read_text(encoding="utf-8"))
    if k != 1:
        sys.exit(f"FAIL: profile help label sites {k}, expected 1")
    mine.write_text(t, encoding="utf-8")
    layout = ROOT / "res/layout/activity_mine.xml"
    _view_attr(layout, "ll_mian_page", 'android:visibility="visible"', 'android:visibility="gone"')
    _view_attr(layout, "ll_evaluate", "<LinearLayout ", '<LinearLayout android:visibility="gone" ')
    # c. About
    about = ROOT / "res/layout/activity_about.xml"
    _view_attr(about, "iv_logo", 'android:src="@mipmap/ic_logo_tribit"', 'android:src="@drawable/krinik_logo_tile"')
    _view_attr(about, "iv_logo", 'android:layout_width="@dimen/dp_170"', 'android:layout_width="@dimen/dp_60"')
    _view_attr(about, "tv_privacy", "<TextView ", '<TextView android:visibility="gone" ')
    _view_attr(about, "tv_contact", 'android:textColor="@color/text_gray"',
               'android:textColor="#ffff1a8c" android:textColorLink="#ffff1a8c" android:autoLink="web"')
    act = smali("com.thousandshores.tribit.modulemine.activity.AboutActivity")
    t, k = CONTACT_EMAIL.subn(r"\1invoke-static {\2}, Lkrinik/Guide;->github(I)Ljava/lang/String;", act.read_text(encoding="utf-8"))
    if k != 1:
        sys.exit(f"FAIL: About contact sites {k}, expected 1")
    act.write_text(t, encoding="utf-8")
    print(f"ok 32 no Tribit links: {len(HELP_ENTRIES)} help entries -> our guide ({len(GUIDE_FILES)} pages), "
          "profile Tribit.com and Rate us gone, About -> GitHub")


# --- Patch 33: «Руководство пользователя» row in the app settings ------------------------------------------------
# Owner 2026-10-16 13:38 +03:00 (interviews/interview_002 Q3): «в руководстве пользователя, которое ты сделаешь в настройках
# приложения». Patch 32 put the guide behind the profile row and every «?»; this adds a row to the app settings screen
# (activity_settings_new, the group «notifications / clear cache / check for updates»): the same divider and row markup
# as their rows, the label from our string krinik_guide (values: «User guide», values-ru: «Руководство пользователя» -
# a layout @string, so their language dictionary does not touch it), and android:onClick="krinikGuide" - their rows
# already call the activity's onClick(View) this way, so a new public method of SettingsNewActivity serves the tap.
# [TESTED: 2026-10-16 · A51: the row stands under «Проверка обновлений» in their row style, a tap opens the guide
# (shots 08_app_settings, 09_settings_guide) · testcases/reports/2026-10-16_patch31_32.md] - the English label not seen
SETTINGS_LAST_ROW_END = re.compile(
    r'(<RelativeLayout [^>]*android:id="@id/setting_check_update"[^>]*>(?:\s*<(?:TextView|ImageView) [^>]*/>)+\s*</RelativeLayout>)')
GUIDE_ROW = (
    '\n                <android.view.View android:background="@color/color_424242" android:layout_width="fill_parent" '
    'android:layout_height="@dimen/dp_1" />\n'
    '                <RelativeLayout android:gravity="center_vertical" android:paddingLeft="@dimen/dp_15" '
    'android:paddingRight="@dimen/dp_15" android:layout_width="fill_parent" android:layout_height="@dimen/dp_56" '
    'android:onClick="krinikGuide">\n'
    '                    <TextView android:textSize="@dimen/dp_15" android:textColor="@color/white" '
    'android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="@string/krinik_guide" />\n'
    '                    <ImageView android:layout_width="wrap_content" android:layout_height="wrap_content" '
    'android:src="@mipmap/ic_choose_grey" android:layout_alignParentRight="true" />\n'
    '                </RelativeLayout>')
GUIDE_ON_CLICK = """
.method public krinikGuide(Landroid/view/View;)V
    .locals 0

    invoke-static {}, Lkrinik/Guide;->open()V

    return-void
.end method
"""


def patch_settings_guide_row():
    layout = ROOT / "res/layout/activity_settings_new.xml"
    t = layout.read_text(encoding="utf-8")
    t2, k = SETTINGS_LAST_ROW_END.subn(lambda m: m.group(1) + GUIDE_ROW, t)
    if k != 1:
        sys.exit(f"FAIL: settings «check for updates» row found {k}x")
    layout.write_text(t2, encoding="utf-8")
    for d, text in (("values", "User guide"), ("values-ru", "Руководство пользователя")):
        _sub_once(ROOT / "res" / d / "strings.xml", "</resources>",
                  f'    <string name="krinik_guide">{text}</string>\n</resources>', f"{d}/strings.xml end")
    add_method(smali("com.thousandshores.tribit.modulemine.activity.SettingsNewActivity"), "krinikGuide(", GUIDE_ON_CLICK)
    print("ok 33 app settings: \"User guide\" row opens krinik.Guide")


# --- Patch 34: the «connection failed» dialog leads to our guide, never to the support form ------------------------
# Owner 2026-10-16 13:32 +03:00: «ни на какую поддерку Трибита ... мы не ведем из Krinik Tribit. Убираем это.» Found
# 2026-10-16 while closing patch 32: DeviceSearchingActivity -> DialogDefault.showConnectFailedDialog shows their tips
# (ensure_connection_tips) + «\n\n» + not_work_feedback («If the above method does not work, please click the "Feedback"
# button below…») and a positive button «Feedback» that opens FeedBackActivity. Now: the tips alone, the button is
# «Руководство пользователя» (krinik.Guide.title) and opens our guide - its section 1 is about connecting a speaker.
# [NOT-TESTED]
CONNECT_FAILED = ".method public final showConnectFailedDialog(Landroid/content/Context;)V"
FEEDBACK_TEXT = re.compile(
    r"(const (v\d+), 0x7f120296\n\n(?:    \.line \d+\n)?    )"   # R.string.feedback
    r"invoke-static \{\2\}, Lcom/thousandshores/tool/utils/ResourceUtils;->getString\(I\)Ljava/lang/String;")


def patch_connect_failed_dialog():
    p = smali("com.thousandshores.tribit.utils.DialogDefault")
    replace_in_method(p, CONNECT_FAILED, 'const-string v0, "\\n\\n"', 'const-string v0, ""')
    replace_in_method(p, CONNECT_FAILED,
                      "invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n",
                      "")
    text = p.read_text(encoding="utf-8")
    s, e = method_span(text, CONNECT_FAILED)
    body, k = FEEDBACK_TEXT.subn(r"\1invoke-static {\2}, Lkrinik/Guide;->title(I)Ljava/lang/String;", text[s:e])
    if k != 1:
        sys.exit(f"FAIL: «Feedback» button text found {k}x")
    p.write_text(text[:s] + body + text[e:], encoding="utf-8")
    header = ".method public onClick(Lcom/thousandshores/commondialog/dialog/base/BaseDialog;)V"
    replace_method(smali("com.thousandshores.tribit.utils.DialogDefault$showConnectFailedDialog$1"), header,
                   header + "\n" + GUIDE_OPEN)
    print("ok 34 connection-failed dialog: tips only, the button opens our guide")


# --- Patch 35 (release only): no request and answer bodies in the system log -------------------------------------
# researches/09 (dislikes, item 3), plans/02 «Баги проекта»: TribitApp.initNetWork builds EasyHttp with
# setLogEnabled(true) in their store build - every request and answer, the guest token and username included, goes to
# logcat, which other apps with log access and bug-report dumps read. The release build passes false; the debug build
# keeps their log - testcases/anon_check.py reads it to prove no real value of the phone reaches a request.
# [TESTED: 2026-10-16 · A51 release START -> guest -> main: 0 EasyHttp lines of 740 app lines; the debug build of the
# same session logged their bodies (control) · testcases/reports/2026-10-16_patch31_32.md]
HTTP_LOG_ON = ("    const/4 v2, 0x1\n\n    .line 257\n"
               "    invoke-virtual {v1, v2}, Lcom/hjq/http/EasyConfig;->setLogEnabled(Z)Lcom/hjq/http/EasyConfig;")


def patch_release_quiet_http():
    replace_in_method(smali("com.thousandshores.tribit.TribitApp"), ".method public final initNetWork()V",
                      HTTP_LOG_ON, HTTP_LOG_ON.replace("const/4 v2, 0x1", "const/4 v2, 0x0"))
    print("ok 35 release: EasyHttp log off")


# --- Patch 30 (TribitApp.initNetWork): TLS is verified again - no trust-all manager, no always-true hostname check ------------------------
# bugs/03 (S1): TribitApp builds the app's only HTTP client with HttpSslFactory.generateSslConfig() - with no certificates
# it falls back to UnSafeTrustManager (empty checkServerTrusted) - and UnSafeHostnameVerifier (verify -> true): anyone on
# the same network could pose as gateway.tribit.com, firmware answers included. Fix: the two builder calls go; OkHttp then
# checks the certificate chain and the host name against the system trust store (its default).
# [TESTED: 2026-10-16 · A51: dictionary, catalog, speaker page, firmware check all «success», no TLS error · testcases/reports/2026-10-16_patch8_anon.md] - rejection of a forged certificate not observed (no MITM was set up)
TLS_TRUST_ALL = ("    invoke-virtual {v2, v3, v1}, Lokhttp3/OkHttpClient$Builder;->sslSocketFactory(Ljavax/net/ssl/SSLSocketFactory;"
                 "Ljavax/net/ssl/X509TrustManager;)Lokhttp3/OkHttpClient$Builder;\n\n    move-result-object v1\n")
TLS_ANY_HOST = ("    invoke-virtual {v1, v2}, Lokhttp3/OkHttpClient$Builder;->hostnameVerifier(Ljavax/net/ssl/HostnameVerifier;)"
                "Lokhttp3/OkHttpClient$Builder;\n\n    move-result-object v1\n")


def patch_tls_verified():
    p = smali("com.thousandshores.tribit.TribitApp")
    replace_in_method(p, ".method public final initNetWork()V", TLS_TRUST_ALL, "    move-object v1, v2\n")
    replace_in_method(p, ".method public final initNetWork()V", TLS_ANY_HOST, "")
    print("ok 30 TLS verified: no trust-all manager, no always-true hostname verifier")


# --- Patch 22: the device base inside the APK ------------------------------------------------------------------
# Owner 2026-10-16 ≈ 11:00 +03:00: «скачай БД из ГУГЛ телефонов, кладемм внутрь АПК» · «но чтобы не больше 1 мб файл весил»
# (MASTER_PLAN decision journal). patches/assets/krinik_devices.txt (`Brand|Model` per line, built by
# tools/devices/make_device_base.py from Google Play's supported-devices list) goes to assets/krinik/devices.txt; the
# request rewriting that picks a random device from it once per install is krinik.Anon (patch 8).
# [TESTED: 2026-10-16 · build: assets/krinik/devices.txt in the APK, byte-equal to the source (cmp); A51 launch to MainNewActivity, no crash]
DEVICE_BASE = pathlib.Path(__file__).resolve().parent / "assets" / "krinik_devices.txt"
DEVICE_BASE_MAX = 1_000_000


def patch_device_base():
    data = DEVICE_BASE.read_bytes()
    if not data or len(data) > DEVICE_BASE_MAX:
        sys.exit(f"FAIL: device base size {len(data)} (must be 1..{DEVICE_BASE_MAX})")
    target = ROOT / "assets" / "krinik" / "devices.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"ok 22 device base: {data.count(b'\n')} devices, {len(data)} bytes -> assets/krinik/devices.txt")


# --- Dex room: classes5 is full ---------------------------------------------------------------------------------
# Their classes5.dex sits at the 65 536 method-reference limit of one dex: the four new calls of patch 8/20 (krinik.Anon,
# krinik.Gate) made apktool fail with «Unsigned short value out of range: 65536» (2026-10-16 11:37). Android loads every
# classesN.dex of the APK (multidex), so a class may live in any of them. Fix: kotlin-reflect (self-contained, ~thousands
# of methods) moves from smali_classes5 to a new smali_classes6 - room for our patches for a long time.
# [TESTED: 2026-10-16 · build 11:40 passed, our code as classes7.dex; the app ran its whole path on the A51 · testcases/reports/2026-10-16_patch8_anon.md]
DEX_MOVE = ("smali_classes5", "smali_classes6", "kotlin/reflect")


def make_dex_room():
    src = ROOT / DEX_MOVE[0] / DEX_MOVE[2]
    dst = ROOT / DEX_MOVE[1] / DEX_MOVE[2]
    if not src.is_dir() or (ROOT / DEX_MOVE[1]).exists():
        sys.exit(f"FAIL: dex room - {src} missing or {DEX_MOVE[1]} already exists")
    dst.parent.mkdir(parents=True)
    src.rename(dst)
    n = sum(1 for _ in dst.rglob("*.smali"))
    print(f"ok  dex room: {n} classes of {DEX_MOVE[2]} moved {DEX_MOVE[0]} -> {DEX_MOVE[1]}")


# --- Variant: debug — «Debug Krinik Tribit», its own package beside the original ---------------------------
# Owner's rule R6 (HOUSE_RULES.md): two builds, debug named «Debug Krinik Tribit», release «Krinik Tribit», different
# signing keys. The debug build gets its own package so it installs next to the owner's original Tribit and the agent
# tests on the Titan without removing it. apktool's renameManifestPackage renames the manifest package (component
# class names stay); the 7 provider authorities and the one custom permission carry the old package prefix and would
# clash with the installed original, so they are renamed too - the code builds every authority at run time from
# getPackageName() (no smali string holds "com.thousandshores.tribit.<suffix>", checked 2026-10-16), so the renamed
# authorities match. Runs AFTER patch 4 (app name).
# [NOT-TESTED]
DEBUG_PACKAGE = "com.kriniks.tribit.debug"
ORIGINAL_PACKAGE = "com.thousandshores.tribit"


def variant_debug():
    yml = ROOT / "apktool.yml"
    t = yml.read_text(encoding="utf-8")
    if t.count("  renameManifestPackage: null") != 1:
        sys.exit("FAIL: renameManifestPackage anchor")
    yml.write_text(t.replace("  renameManifestPackage: null", f"  renameManifestPackage: {DEBUG_PACKAGE}"), encoding="utf-8")

    m = ROOT / "AndroidManifest.xml"
    t = m.read_text(encoding="utf-8")
    n_auth = t.count(f'android:authorities="{ORIGINAL_PACKAGE}.')
    n_perm = t.count(f'android:name="{ORIGINAL_PACKAGE}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"')
    if n_auth != 7 or n_perm < 1:
        sys.exit(f"FAIL: expected 7 authorities and the receiver permission, found {n_auth} and {n_perm}")
    t = t.replace(f'android:authorities="{ORIGINAL_PACKAGE}.', f'android:authorities="{DEBUG_PACKAGE}.')
    t = t.replace(f'"{ORIGINAL_PACKAGE}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"',
                  f'"{DEBUG_PACKAGE}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"')
    m.write_text(t, encoding="utf-8")

    # Resources keep the original package name: route every Resources.getIdentifier through krinik.Res, which falls
    # back to it (73 Resources.getIdentifier calls routed, about 26-35 of them pass getPackageName(); dialogs showed
    # designer placeholders without it).
    sig = "Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ours = "Lkrinik/Res;->getIdentifier(Landroid/content/res/Resources;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    pat = re.compile(r"invoke-virtual(/range)? \{([^}]*)\}, " + re.escape(sig))
    n = 0
    for p in ROOT.glob("smali*/**/*.smali"):
        t = p.read_text(encoding="utf-8")
        t2, k = pat.subn(lambda m: f"invoke-static{m.group(1) or ''} {{{m.group(2)}}}, {ours}", t)
        if k:
            p.write_text(t2, encoding="utf-8")
            n += k
    if n < 26:
        sys.exit(f"FAIL: expected >= 26 Resources.getIdentifier calls, found {n}")

    s = ROOT / "res/values/strings.xml"
    t = s.read_text(encoding="utf-8")
    old = '<string name="app_name">Krinik Tribit</string>'
    if t.count(old) != 1:
        sys.exit("FAIL: app_name after patch 4")
    s.write_text(t.replace(old, '<string name="app_name">Debug Krinik Tribit</string>'), encoding="utf-8")
    print(f"ok  debug variant: {DEBUG_PACKAGE}, Debug Krinik Tribit, {n} getIdentifier calls via krinik.Res")


if __name__ == "__main__":
    if ROOT is None or not (ROOT / "apktool.yml").exists():
        sys.exit("usage: python -I patches/apply.py <apktool-decoded-dir>")
    patch_unnamed_eq_crash()
    patch_no_location()
    patch_stable_density()
    patch_app_name()
    patch_icon()
    patch_password_symbols()
    patch_ble_no_gps_check()
    patch_autosize_fit()
    patch_scroll_fix()
    patch_brand()
    patch_location_permission()
    # Patch 8a is NOT applied yet: on the A51 (2026-10-16) it removed the dictionary request (2 -> 0) but the login screen
    # of a fresh install turned English - their Russian texts come only from that dictionary. It waits for our values-ru
    # (wave 2, plans/01 §3); a failed request already goes on (onHttpFail sets 1), only a slow server holds the logo.
    # patch_splash_no_dictionary_wait()
    patch_no_account()
    patch_no_account_ui()
    patch_no_relogin()
    patch_no_forced_update()
    patch_firebase_off()
    patch_no_cloud()
    patch_no_error_mail()
    patch_card_name_wrap()
    patch_firmware_on_tap()
    patch_pink_switch()
    patch_settings_title()
    patch_smaller_back()
    patch_no_support_link()
    patch_tls_verified()
    patch_pink_buttons_white_text()
    patch_no_tribit_links()
    patch_settings_guide_row()
    patch_connect_failed_dialog()
    patch_device_base()
    make_dex_room()
    if "--debug" in sys.argv[2:]:
        variant_debug()
    else:
        patch_release_quiet_http()
    print("all patches applied")
