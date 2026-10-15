# Krinik Tribit App

Personal fixes for the official Tribit Android app (`com.thousandshores.tribit` 5.0.0) so it is usable on a
large tablet with system display zoom and Russian locale. Only **patches and build scripts** live here — no
Tribit APK or decompiled code is published. You bring the APK from your own device.

## Known defects being fixed

1. **Crash on "create custom EQ"** — `EqUtil.getUnnameEq` splits preset names by `-` and reads `[1]`
   without a bounds check → `IndexOutOfBoundsException: Index: 1, Size: 1` (StormBox Blast 2 / bts56 EQ screen).
2. **UI cut off under display zoom** — screens are not scrollable; with an enlarged system display size the
   bottom of cards (incl. the equalizer) is clipped.
3. **Broken Russian localisation** — mixed English/Russian, strings missing.

## How it works

`adb pull` the installed split APKs → apktool decode → apply patches from `patches/` → rebuild → sign with
your own key → `adb install-multiple`. The original app must be uninstalled first (signature differs).

Not affiliated with Tribit / Thousandshores.
