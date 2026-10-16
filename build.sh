#!/usr/bin/env bash
# Krinik Tribit - build ONE patched universal APK from the official split APKs.
#   bash build.sh            -> release: «Krinik Tribit», package com.thousandshores.tribit (replaces the original)
#   bash build.sh debug      -> debug:   «Old Krinik Tribit», package com.kriniks.tribit.old (installs beside it;
#                                        com.kriniks.tribit.debug belongs to our own app in app/)
# Steps:
#   1. original-apk/ holds the split APKs pulled from a device (adb shell pm path com.thousandshores.tribit).
#   2. APKEditor merges the splits into one universal APK (work/merged.apk) - a split set cannot change its package,
#      and the owner's release is one APK (GOAL.md, success line 7).
#   3. apktool decodes it fresh, patches/apply.py patches it (debug: + the variant), apktool rebuilds it.
#   4. zipalign + apksigner with the variant's own key (owner's rule R6: different keys for debug and release).
# Output: out/KrinikTribit-<variant>.apk  ->  adb install -r out/KrinikTribit-<variant>.apk
set -euo pipefail
cd "$(dirname "$0")"

VARIANT="${1:-release}"
case "$VARIANT" in release|debug) ;; *) echo "FAIL: variant must be release or debug, got: $VARIANT"; exit 1 ;; esac

JAVA_HOME="${JAVA_HOME_KRINIK:-C:/Program Files/Microsoft/jdk-21.0.11.10-hotspot}"
JAVA="$JAVA_HOME/bin/java"
BT="${ANDROID_BUILD_TOOLS:-C:/Android/Sdk/build-tools/36.0.0}"
APKEDITOR="tools/APKEditor-1.4.9.jar"   # REAndroid/APKEditor V1.4.9, sha256 a9cd40df…6e67 (checked against GitHub's digest)
KEYSTORE="keys/krinik-tribit-$VARIANT.keystore"
KS_PASS="${KRINIK_KS_PASS:-krinik-tribit}"   # personal fork keys, not secrets of value; override via env
OUT="out/KrinikTribit-$VARIANT.apk"

[ -f original-apk/base.apk ] || { echo "FAIL: original-apk/base.apk missing"; exit 1; }
[ -f "$APKEDITOR" ] || { echo "FAIL: $APKEDITOR missing - download V1.4.9 from github.com/REAndroid/APKEditor/releases"; exit 1; }

mkdir -p work out keys
if [ ! -f work/merged.apk ] || [ -n "$(find original-apk -name '*.apk' -newer work/merged.apk)" ]; then
  "$JAVA" -jar "$APKEDITOR" m -f -i original-apk -o work/merged.apk >/dev/null
fi

rm -rf work/base "$OUT" out/aligned.apk
if [ -d native/smali ]; then
  # The native tree (native/ = the private repository KrinikTribitNative: Tribit's decoded code with our fixes written in
  # it) is copied without its .git and apktool's build/; only the variant step is applied on top. krinik-app/ (the speaker
  # photos of OUR app, kept private there) is not part of Tribit's APK and stays out too.
  mkdir -p work/base
  tar -C native --exclude=./.git --exclude=./.gitignore --exclude=./build --exclude=./krinik-app -cf - . | tar -C work/base -xf -
  if [ "$VARIANT" = debug ]; then python -I patches/apply.py work/base --variant --debug; else python -I patches/apply.py work/base --variant; fi
else
  # No native tree on this machine: decode the merged APK and apply every patch (the way the native tree was made).
  "$JAVA" -jar tools/apktool.jar d -f -o work/base work/merged.apk >/dev/null
  if [ "$VARIANT" = debug ]; then python -I patches/apply.py work/base --debug; else python -I patches/apply.py work/base; fi
fi
"$JAVA" -jar tools/apktool.jar b work/base -o out/unsigned.apk >/dev/null

# Our own code (patches/java, e.g. krinik.ScrollFix of patch 16) and Tribit's classes rewritten as Java source
# (native/src, plans/03_EPIC_java_source.md) -> one extra classesN.dex inside the APK.
SDK="${ANDROID_SDK_KRINIK:-C:/Android/Sdk}"
ANDROID_JAR="$SDK/platforms/android-36/android.jar"
DEX2JAR="tools/dex2jar/dex-tools-2.4.38/d2j-dex2jar.bat"   # ThexXTURBOXx/dex2jar 2.4.38, sha256 5d88e269…54e5c (GitHub's digest)
rm -rf work/java && mkdir -p work/java/classes work/java/dex work/java/r work/java/rclasses
SOURCES=$(find patches/java -name '*.java')
CLASSPATH="$ANDROID_JAR"
D8_CP=()
if [ -d native/src ] && [ -n "$(find native/src -name '*.kt')" ]; then
  # The guard and the counter accept .kt, but kotlinc is not in the build yet (plans/03, phase 4): a .kt file would count
  # as migrated while its class is missing from the APK.
  echo "FAIL: Kotlin sources in native/src but no kotlinc step yet: $(find native/src -name '*.kt' | head -3)"; exit 1
fi
if [ -d native/src ] && [ -n "$(find native/src -name '*.java')" ]; then
  # A class written as source must not keep its smali: Android would run the first copy (tools/native_src_guard.py).
  python -I tools/native_src_guard.py native
  # Their classes as a jar - what the sources compile against; R from apktool's public.xml - compile time only.
  [ -f "$DEX2JAR" ] || { echo "FAIL: $DEX2JAR missing - gh release download 2.4.38 -R ThexXTURBOXx/dex2jar"; exit 1; }
  cmd //c "${DEX2JAR//\//\\} -f -o work\\java\\app.jar out\\unsigned.apk" > work/java/dex2jar.log 2>&1 || true
  if [ ! -f work/java/app.jar ] || ls work/java/*-error.zip >/dev/null 2>&1 || ls ./*-error.zip >/dev/null 2>&1; then
    echo "FAIL: dex2jar of out/unsigned.apk failed (no app.jar or an *-error.zip):"; cat work/java/dex2jar.log; exit 1
  fi
  python -I tools/gen_r.py native/res/values/public.xml work/java/r com.thousandshores.tribit com.thousandshores.tool \
    com.thousandshores.commondialog com.thousandshores.widget com.thousandshores.bluetoothlib
  "$JAVA_HOME/bin/javac" --release 11 -nowarn -d work/java/rclasses $(find work/java/r -name '*.java')
  CLASSPATH="$ANDROID_JAR;work/java/app.jar;work/java/rclasses"
  D8_CP=(--classpath work/java/app.jar)
  SOURCES="$SOURCES $(find native/src -name '*.java')"
fi
"$JAVA_HOME/bin/javac" --release 11 -nowarn -encoding UTF-8 -classpath "$CLASSPATH" -d work/java/classes $SOURCES
JAVA_HOME="$JAVA_HOME" "$BT/d8.bat" --min-api 26 --lib "$ANDROID_JAR" "${D8_CP[@]}" --output work/java/dex $(find work/java/classes -name '*.class')
python -I patches/add_dex.py out/unsigned.apk work/java/dex/classes.dex

if [ ! -f "$KEYSTORE" ]; then
  "$JAVA_HOME/bin/keytool" -genkeypair -keystore "$KEYSTORE" -alias krinik -keyalg RSA -keysize 3072 \
    -validity 10000 -storepass "$KS_PASS" -keypass "$KS_PASS" -dname "CN=Krinik Tribit $VARIANT, O=Krinik" >/dev/null
fi

"$BT/zipalign.exe" -f -p 4 out/unsigned.apk out/aligned.apk
"$BT/apksigner.bat" sign --ks "$KEYSTORE" --ks-pass "pass:$KS_PASS" --out "$OUT" out/aligned.apk
rm -f out/unsigned.apk out/aligned.apk "$OUT.idsig"
"$BT/apksigner.bat" verify "$OUT" && echo "built: $OUT"
