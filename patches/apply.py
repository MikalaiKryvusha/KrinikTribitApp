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
        '    <group android:scaleX="0.0371" android:scaleY="0.0371"\n'
        '        android:translateX="18.05" android:translateY="17.14">\n'
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
    '    <group android:scaleX="0.0371" android:scaleY="0.0371"\n'
    '        android:translateX="18.05" android:translateY="17.14">\n'
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


# --- Patch 8: no account - the app opens on the main screen ------------------------------------------------
# Owner 2026-10-16 ≈ 09:16 +03:00: «аккаунт не нужен» · «выпиливаем НАХУЙ аккаунты» (MASTER_PLAN decision journal).
# Play complaints 11 «why an account» (77) and 17 «needs their server» (63). The splash sends a user without a token to
# autoLogin (a guest account made on their server from the MAC / ANDROID_ID, no network - no entry), and START opens
# LoginNewActivity (researches/06 З2, З3). Fix: checkToken always ends in ViewModelFirst.startMainActivity (a stored
# token still goes into the Authorization header, as before); START marks the agreement and calls checkToken instead
# of opening the login screen. Requests without a token are answered «Full authentication» - patch 9 keeps the user.
# [TESTED: 2026-10-16 · A51: START -> main screen without login - BUT the speaker page never opens: their gateway answers
# «Full authentication» to the device catalog without a token (Found 0 of testcases/reports/2026-10-16_wave1.md). NOT applied.]
CHECK_TOKEN = """
.method private final checkToken()V
    .locals 4

    invoke-static {}, Lcom/thousandshores/tribit/database/datamanager/AccountTokenManager;->getInstance()Lcom/thousandshores/tribit/database/datamanager/AccountTokenManager;

    move-result-object v0

    invoke-virtual {v0}, Lcom/thousandshores/tribit/database/datamanager/AccountTokenManager;->getAccountToken()Lcom/thousandshores/tribit/database/entity/TokenInfo;

    move-result-object v0

    if-eqz v0, :krinik_main

    invoke-virtual {v0}, Lcom/thousandshores/tribit/database/entity/TokenInfo;->getAccess_token()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :krinik_main

    invoke-static {}, Lcom/hjq/http/EasyConfig;->getInstance()Lcom/hjq/http/EasyConfig;

    move-result-object v0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Bearer "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const-string v2, "Authorization"

    invoke-virtual {v0, v2, v1}, Lcom/hjq/http/EasyConfig;->addHeader(Ljava/lang/String;Ljava/lang/String;)Lcom/hjq/http/EasyConfig;

    :krinik_main
    iget-object v0, p0, Lcom/thousandshores/tribit/modulelogin/activity/FirstNewActivity;->mViewModel:Lcom/thousandshores/tribit/modulelogin/viewmodel/ViewModelFirst;

    if-nez v0, :krinik_vm

    const-string v0, "mViewModel"

    invoke-static {v0}, Lkotlin/jvm/internal/Intrinsics;->throwUninitializedPropertyAccessException(Ljava/lang/String;)V

    return-void

    :krinik_vm
    invoke-virtual {v0}, Lcom/thousandshores/tribit/modulelogin/viewmodel/ViewModelFirst;->startMainActivity()V

    return-void
.end method
"""


def patch_no_account():
    p = smali("com.thousandshores.tribit.modulelogin.activity.FirstNewActivity")
    replace_method(p, ".method private final checkToken()V", CHECK_TOKEN)
    # START: the button's context is the splash activity; call its checkToken. Any other context keeps the old path.
    h = ".method private static final onCreate$lambda$1(Landroid/view/View;)V"
    replace_method(p, h, h + START_HANDLER)
    print("ok  8 no account: splash and START open the main screen")


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
# [NOT-TESTED]
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

    const-string v0, "/equalizer/"

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    if-nez v0, :yes

    const-string v0, "/persound/"

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    if-nez v0, :yes

    const-string v0, "/userFeedback/"

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    return v0

    :yes
    const/4 v0, 0x1

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


# --- Patch 22: the device base inside the APK ------------------------------------------------------------------
# Owner 2026-10-16 ≈ 11:00 +03:00: «скачай БД из ГУГЛ телефонов, кладемм внутрь АПК» · «но чтобы не больше 1 мб файл весил»
# (MASTER_PLAN decision journal). patches/assets/krinik_devices.txt (`Brand|Model` per line, built by
# tools/devices/make_device_base.py from Google Play's supported-devices list) goes to assets/krinik/devices.txt; the
# request rewriting that picks a random device from it once per install is the next step (plans/01 §5).
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
    # patch_no_account()  # breaks the speaker page without a token - see its marker; needs a local catalog first
    patch_no_account_ui()
    patch_no_relogin()
    patch_no_forced_update()
    patch_firebase_off()
    patch_no_cloud()
    patch_device_base()
    if "--debug" in sys.argv[2:]:
        variant_debug()
    print("all patches applied")
