"""Krinik Tribit App - smali patches for com.thousandshores.tribit 5.0.0 (versionCode 5000).

Usage:  python -I patches/apply.py <apktool-decoded-dir>

Every patch finds its anchor by exact text and fails loudly (exit 1) when the anchor is missing,
so a new Tribit version never gets a half-applied fork. Run on a FRESH `apktool d` output.
"""
import pathlib
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
    print("all patches applied")
