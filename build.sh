#!/usr/bin/env bash
# Krinik Tribit - build the patched app from the official split APKs.
#   1. original-apk/ holds the split APKs pulled from a device (adb shell pm path com.thousandshores.tribit).
#   2. apktool decodes base.apk fresh, patches/apply.py patches it, apktool rebuilds it.
#   3. every APK of the set (patched base + untouched splits) is zipaligned and signed with ONE key -
#      Android refuses a split set with mixed signatures.
# Output: out/signed/*.apk  ->  adb install-multiple out/signed/*.apk
set -euo pipefail
cd "$(dirname "$0")"

JAVA_HOME="${JAVA_HOME_KRINIK:-C:/Program Files/Microsoft/jdk-21.0.11.10-hotspot}"
JAVA="$JAVA_HOME/bin/java"
BT="${ANDROID_BUILD_TOOLS:-C:/Android/Sdk/build-tools/36.0.0}"
KEYSTORE="keys/krinik-tribit.keystore"
KS_PASS="${KRINIK_KS_PASS:-krinik-tribit}"   # personal fork key, not a secret of value; override via env

[ -f original-apk/base.apk ] || { echo "FAIL: original-apk/base.apk missing"; exit 1; }

rm -rf work/base out
mkdir -p out/aligned out/signed keys
"$JAVA" -jar tools/apktool.jar d -f -o work/base original-apk/base.apk >/dev/null
python -I patches/apply.py work/base
"$JAVA" -jar tools/apktool.jar b work/base -o out/base-unsigned.apk >/dev/null

if [ ! -f "$KEYSTORE" ]; then
  "$JAVA_HOME/bin/keytool" -genkeypair -keystore "$KEYSTORE" -alias krinik -keyalg RSA -keysize 3072 \
    -validity 10000 -storepass "$KS_PASS" -keypass "$KS_PASS" -dname "CN=Krinik Tribit, O=Krinik" >/dev/null
fi

for src in out/base-unsigned.apk original-apk/split_*.apk; do
  name=$(basename "$src"); [ "$name" = base-unsigned.apk ] && name=base.apk
  "$BT/zipalign.exe" -f -p 4 "$src" "out/aligned/$name"
  "$BT/apksigner.bat" sign --ks "$KEYSTORE" --ks-pass "pass:$KS_PASS" --out "out/signed/$name" "out/aligned/$name"
done
rm -f out/signed/*.idsig
"$BT/apksigner.bat" verify out/signed/base.apk && echo "built: $(ls out/signed)"
