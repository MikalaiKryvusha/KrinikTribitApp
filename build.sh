#!/usr/bin/env bash
# Krinik Tribit - build ONE patched universal APK from the official split APKs.
#   bash build.sh            -> release: «Krinik Tribit», package com.thousandshores.tribit (replaces the original)
#   bash build.sh debug      -> debug:   «Debug Krinik Tribit», package com.kriniks.tribit.debug (installs beside it)
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
"$JAVA" -jar tools/apktool.jar d -f -o work/base work/merged.apk >/dev/null
if [ "$VARIANT" = debug ]; then python -I patches/apply.py work/base --debug; else python -I patches/apply.py work/base; fi
"$JAVA" -jar tools/apktool.jar b work/base -o out/unsigned.apk >/dev/null

# Our own code (patches/java, e.g. krinik.ScrollFix of patch 16) -> one extra classesN.dex inside the APK.
SDK="${ANDROID_SDK_KRINIK:-C:/Android/Sdk}"
ANDROID_JAR="$SDK/platforms/android-36/android.jar"
rm -rf work/java && mkdir -p work/java/classes work/java/dex
"$JAVA_HOME/bin/javac" --release 11 -nowarn -classpath "$ANDROID_JAR" -d work/java/classes $(find patches/java -name '*.java')
JAVA_HOME="$JAVA_HOME" "$BT/d8.bat" --min-api 26 --lib "$ANDROID_JAR" --output work/java/dex $(find work/java/classes -name '*.class')
python -I patches/add_dex.py out/unsigned.apk work/java/dex/classes.dex

if [ ! -f "$KEYSTORE" ]; then
  "$JAVA_HOME/bin/keytool" -genkeypair -keystore "$KEYSTORE" -alias krinik -keyalg RSA -keysize 3072 \
    -validity 10000 -storepass "$KS_PASS" -keypass "$KS_PASS" -dname "CN=Krinik Tribit $VARIANT, O=Krinik" >/dev/null
fi

"$BT/zipalign.exe" -f -p 4 out/unsigned.apk out/aligned.apk
"$BT/apksigner.bat" sign --ks "$KEYSTORE" --ks-pass "pass:$KS_PASS" --out "$OUT" out/aligned.apk
rm -f out/unsigned.apk out/aligned.apk "$OUT.idsig"
"$BT/apksigner.bat" verify "$OUT" && echo "built: $OUT"
