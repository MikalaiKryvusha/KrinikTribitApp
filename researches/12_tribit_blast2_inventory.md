# Research 12 — parity inventory of Tribit's app screens for StormBox Blast 2
> **Created:** 2026-10-16 · **Parent:** plans/07_epic04_phase3_screens.md · **Status:** recon done 20:03 +03:00 · **Outbound:** —

Read-only recon of Tribit's official app 5.0.0 (jadx). No network contact. Every claim cites a line that was read;
**(I)** marks an inference. Bonded name in all Blast 2 branches: `"Tribit StormBox Blast 2"` (a second spelling
`"TRIBIT StormBox Blast 2"` appears in a few branches, noted where it matters).

**Path keys.** `J/` = `decompiled/jadx-base/sources/com/thousandshores/` · `L/` = `decompiled/jadx-base/resources/res/layout/`
· `EN:n` = line n of `decompiled/jadx-base/resources/res/values/strings.xml` · `S/` = `work/base/smali_classes5/com/thousandshores/tribit/moduledevice/bts56/`.
Screen files (all under `J/tribit/moduledevice/bts56/`): **C** = `Bts56ControlActivity.java`, **ES** = `Eq56SettingActivity.java`,
**ED** = `Eq56DetailActivity.java`, **EB** = `EqButton56Activity.java`, **LC** = `LightControl56Activity.java`,
**LX** = `LightCustom56Activity.java`, **INFO** = `Bts56InfoActivity.java`. Helpers: **B** = `J/bluetoothlib/spaker/Bts52Util.java`,
**K** = `J/tribit/constant/Bts56Constant.java`, **EU** = `J/tribit/utils/EqUtil.java`, **EL** = `J/tribit/utils/audio/EqListUtil.java`,
**PU** = `J/tribit/utils/PageUtil.java`, **NA** = `J/tribit/moduledevice/adapter/EqNewAdapter.java`,
**CA** = `J/tribit/moduledevice/adapter/EqCustomAdapter.java`, **DD** = `J/tribit/utils/DialogDefault.java`,
**DC** = `J/bluetoothlib/utils/DeviceConstant.java`.

## 0. Russian (and Chinese) display names — how they work

- Tribit's APK has **no Russian for its own strings.** `decompiled/jadx-ru/resources/res/values-ru/strings.xml` (173 lines)
  holds only library strings (`abc_*` etc.); every app key looked up below (`sound_effect`, `blast_trad`, `xbass`, …) returns
  nothing there (helper lookup, this recon; agrees with `researches/02_languages.md` item 4).
- At runtime every `ResourceUtils.getString(id)` first asks a server-downloaded map keyed by the **resource name**, and falls
  back to the APK (English) only if empty: `J/tool/utils/ResourceUtils.java:34-46`. So a Russian user sees Tribit's server
  Russian when it was downloaded, else **English**. The server texts are not in the repo, so **RU for resource-based names is
  "server-provided, not verifiable offline; offline fallback = EN"** throughout this document.
- **Hard-coded literals are identical in Russian.** The code special-cases only `app_language == "zh"`; every other language,
  Russian included, gets the literal: "TRIBIT Signature", "X-3D", "XBass Off (V8.6/V7.4)", "XBass (V8.6/V7.4)",
  "XBass 2.0", "Ex‑XBass" (C:1811-1814, EB:340-343, NA:73-77).

## 0a. Firmware flags (four different definitions — parity trap)

| Where | `isNewVersion56` | `isNewEqVersion56` |
|---|---|---|
| Main screen | fw > 10093 or BTS56C | fw > 10110 or BTS56C (`J/tribit/MainNewActivity.java:1939-1940`) |
| Control screen (on DSP reply 88) | dsp > 10074 or BTS56C (C:527) | dsp > 10095 (C:528) |
| EQ detail screen | fw > 10093 or BTS56C (ED:272) | fw > 10110 (ED:273) |
| Settings screen (on DSP reply) | fw > 10093 **and** dsp > 10074 (INFO:1304) | fw > 10110 **and** dsp > 10095 (INFO:1305) |

DSP version = reply payload + 10000, value 47 ignored (C:519-524). fw = `versionView(versionName)`; the version string is
`"v" + fwVersion.split("_")[1]`, with "9.4" rewritten to "1.1" (C:600-610). The flag in force is whichever screen wrote it last (I).

---

## 1. The device control screen (`L/activity_device_control_56.xml` + C)

Top to bottom. "Shown" = default visibility in the layout; conditions from code.

1. **Back** `iv_back` (layout :15-20) → `finish()` (C:904-909).
2. **Title** `tv_title` (:21-28) = `device_setting` "Device Settings" (C:221; EN:514).
3. **Settings gear** `iv_setting` (:29-34, `ic_setting_new`) → opens **INFO** (C:915-920). Turns **red** (`ic_setting_red`)
   when the server reports a newer firmware (`getUpdateResult`, C:493-502) — server only.
4. **Device name** `tv_name` (:55-62) = user's stored name `getDevice().getName()` (C:1221), not the Bluetooth name.
5. **Battery pill** `ll_battery_left` (:63-103): ring `pb_battery` + icon `iv_battery` + `tv_battery` "NN%"
   (C:1561-1580; empty/out of range → "0%", C:1544-1559). Charging state from `getBatteryState`: 1 → ring shown, icon
   `ic_charge`, text `charging` "Charging"; 2 → `full` "Full"; else ring hidden (C:652-718; EN:239, EN:705).
   `tv_battery_state` receives the text but stays `gone` in the layout (:104-112) (I: never visible).
   Battery is re-queried 1 s after resume while the ring reads 0 (`Bts56ControlActivity$queryBattery$1.java:85-105`).
6. **Light animation** `lottieView` (:113-122, `lottie/light_mode.json`) — `gone`, never referenced in C (grep) (I: dead).
7. **Product picture** `iv_icon` (:124-129) via `UpdateUtils.deviceImage` (C:249-251): server product logo cached under
   `blueName+"info"`, else placeholder `ic_deviceloading` (`J/tribit/utils/UpdateUtils.java:214-227`).
8. **Partner (TWS) battery strip** `rl_battery` (:131-173, `gone`): shown when reply **96** has payload > 0, text is a
   **Chinese literal** `"从机电量 " + N + "%"` ("slave battery") (C:2037-2059); hidden otherwise (C:2060-2078). Query 96
   is sent 800 ms after resume (C:1291-1296, 1328-1337; B:48-49).
9. **Debug log button** `btn_log` (:174-180, text "蓝牙数据日志") — only in a pre-release build (C:279-293).
10. **Play card** `rl_contorl` (:181-242):
    - **Previous** `iv_last` → cmd 2 [1], icon switches to pause, `isPlay=true` (C:1073-1092; B:64-66).
    - **Play/Pause** `iv_play` (debounced 100 ms) → cmd 2 [3] if playing else [4]; local toggle (C:1041-1071).
      Icons `ic_play_stop` (playing) / `ic_play_new` (C:1384-1407).
    - **Next** `iv_next` → cmd 2 [2] (C:1094-1113).
    - **Volume** `sb_sound` max **31** (:233, C:1269); sends cmd 13 [v] **on release only** and only for the Blast 2 name
      (C:938-969; B:56-57). First time above 70 % → toast `high_volume_note` (C:952-955; EN:750).
11. **EQ strip** `rl_eq` (:243-283): label `tv_eq` = `sound_effect` "Sound Effects" (C:1252; EN:1438); right pill
    `tv_eq_name` = current preset display name (C:1768-1876, §2); background picture per preset (§2 table); tap →
    **ES** (C:1033-1038). The name comes from reply 21 / unsolicited 82 → `PU.bts56Eq` (C:575-588; PU:280-329).
12. **Light strip** `rl_light` (:284-351): shown only if the name is in `speakerLight` (both Blast 2 spellings are,
    DC:11; C:1525-1541). Label `light` "Light" (C:1245; EN:833). Pill `tv_light_mode` = "Mode 1/2/3" (`mode_one/two/three`,
    EN:976/978/977) with backgrounds `ic_light_bg` / `ic_light_two` / `ic_light_three`; off → empty text, `bg_paly`
    (C:1582-1653). Mode from reply 20/85: for fw > 10037, 4 = off (C:620-637).
    - **On/off switch** `ln_light_switch` (knob `iv_left`/`iv_right`, :305-326) → toggles; on = cmd 12 [saved mode,
      default 1], off = cmd 12 [4] (C:1115-1118, 2289-2308; B:76-81).
    - **Tap the strip** → **LC**, only while the light is on (C:1021-1026, 1200-1212).
13. **No-Bluetooth overlay** `ll_no_bluetooth` (:358-361, `layout_no_bluetooth`): text `bluetooth_disconnected`
    "Bluetooth disconnected." (EN:169), button `connect_to` "Connect to" (EN:406) (C:1227, 1239); shown and content hidden
    when the classic link is down (C:1729-1765). No click handler for its button is set in C (I: handled elsewhere or none).
14. **No-network overlay** `ll_no_net` (:354-357): text `network_connection_failed` (C:1233; EN:1055); `netDisconnect`
    actually hides it (C:1906-1933) (I: effectively never shown here).
15. **Behaviour not on screen but user-visible:** on resume the app queries play state (550 ms), device info (700 ms),
    partner battery (800 ms) (C:1279-1296) and volume / EQ / light / play state with 100 ms gaps
    (`Bts56ControlActivity$queryState$1.java:40-117`); speaker disconnect → toast `bluetooth_disconnected` and close
    (C:2253-2265); Bluetooth switched off → screen closes (C:1888-1904); auto-reconnect with 3 retries and a
    `reconnecting` "Reconnecting..." dialog (C:2157-2198; EN:1295); bond lost → system Bluetooth dialog (C:1465-1482).

**Not on the Blast 2 control screen at all:** no X-Bass / 3D / party / TWS-pairing toggle, no battery-saving, no power
button, no firmware row, no rename (the layout has only the items above, `L/activity_device_control_56.xml:1-362`).

---

## 2. EQ presets for Blast 2

### 2.1 Lists built by `EqUtil.getEqPre` (EU:993-1241)

`types` is the internal id; the Bluetooth preset id sent is **types − 2** (`eqSetNew(types − 2, …)`, ES:2525/2538), except
Default (types 1 → `eqDefault`, ES:2508-2510, 2574-2607). Customized (types 3) is a placeholder and is filtered out of the
preset list (ES:770-772; EB:467, 488).

| Firmware | Order shown (EU lines) |
|---|---|
| **OLD** (`!isNewVersion56`, not 56C) | Default · XBass · Blast traditional · Classical · **Ex‑XBass** · Audiobook · Rock · Jazz (EU:1003-1067) |
| **MID** (new, not newEq) | Default (MusicGainsO) · XBass (XBassGainsO) · Blast traditional · Classical · Audiobook · Rock · Jazz · Live · Podcast (EU:1098-1175) |
| **NEW_EQ** (new and newEq) — the owner's speaker | Default (MusicGainsN) · XBass (XBassGainsN) · Blast traditional · Classical · Audiobook · Rock · Jazz · Live · Podcast (EU:1071-1095, 1125-1175) |
| **BTS56C** | Default · XBass · Blast traditional · Classical · Audiobook · Rock · Jazz — no Live/Podcast (EU:1179-1238) |

Visibility filters applied when the list is shown (smali-confirmed, `S/Eq56SettingActivity.smali` `initObserver$lambda$15`,
constants :4966ff, branch `.line 489-495` at :5867-5938; same logic in C:854-865 and EB:537-571):
- **Blast traditional (types 10)** shown only if fw > 10083 **or** BTS56C.
- **Ex‑XBass (types 11)** shown only if fw > 10085 **and** dsp > 10072; entries already in the database are also dropped when
  fw ≥ 10093 (C:811-813; ES:729-731).
Order after the first run comes from the database `order("sort asc")` (`J/tribit/moduledevice/viewmodel/ViewModelEqlist.java:129`);
all presets have sort 0 (EU:1012ff) (I: insertion order = the table above).

### 2.2 The owner's list (NEW_EQ), with display names

Display-name sources: preset list NA:67-120, EQ-button screen EB:329-383, control strip C:1768-1876. Backgrounds: list
card NA:196-505 + NA:520-563 (normal/checked), control strip EL:263-395 via C:1776-1859.

| # | Preset (types → id sent) | Gains sent (K line) | EN shown | RU shown | zh shown | List card bg (normal / checked) | Control-strip bg |
|---|---|---|---|---|---|---|---|
| 1 | Default (1 → cmd 4 [1, gains]) | MusicGainsN 12×10 (K:65); MID MusicGainsO (K:64); OLD `eqSet(1)` (ES:2597-2605) | **TRIBIT Signature** (NA:74, EB:341, C:1812) | TRIBIT Signature (literal) | 默认 | `ic_default_normal` / `ic_default_checked` (NA:538-545) | `ic_default_checked` (EL:266-267) |
| 2 | XBass (4 → 2) | XBassGainsN (K:56); MID XBassGainsO (K:55) | **XBass** (`xbass`, EN:1663); **"XBass 2.0" on BTS56C** (NA:117-118, EB:374-375, C:1861-1862) | server / EN fallback | server | `ic_xbass_normal` / `ic_xbass_checked` (NA:467-474) | `ic_xbass_checked` (EL:374-375) |
| 3 | Blast traditional (10 → 8) | BlastGainsN (K:60) | **Blast traditional** (`blast_trad`, EN:166; NA:106) | server / EN fallback | 户外 (NA:104, EB:366, C:1831) | `ic_out_normal` / `ic_out_checked` (NA:296-303) | `ic_out_checked` via `outdoor` (C:1845-1847; EL:302-303) |
| 4 | Classical (6 → 4) | ClassicGainsN 12×10 (K:74) | **X-3D** (NA:81-82, EB:347-355, C:1816-1826) | X-3D (literal) | X-3D | `ic_x3d_normal` / `ic_x3d_checked` (NA:556-563) | `ic_x3d_checked` (EL:362-363) |
| 5 | Audiobook (5 → 3) | AudioBookGainsN (K:68) | **Audiobook** (EN:144) | server / EN fallback | server | `ic_audiobook_normal` / `_checked` (NA:476-483) | `ic_audiobook_checked` (EL:378-379) |
| 6 | Rock (7 → 5) | RockGainsN (K:71) | **Rock** (EN:1320) | server / EN fallback | server | `ic_rock_normal` / `ic_eq_rock` (NA:323-330) | `ic_eq_rock` (EL:314-315) |
| 7 | Jazz (8 → 6) | JazzGainsN (K:77) | **Jazz** (EN:803) | server / EN fallback | server | `ic_jazz_normal` / `_checked` (NA:233-240) | `ic_jazz_checked` (EL:274-275) |
| 8 | Live (12 → 10) | always flat 12×10 — types ≥ 12 skip the gains branch (ES:2516-2538) | **XBass Off (V8.6/V7.4)** (NA:108-110, EB:370-371, C:1848-1860) | literal | literal | `ic_music_normal` / `ic_music_checked` (NA:529-535) | `ic_music_checked` (C:1857-1859; EL:326-327) |
| 9 | Podcast (13 → 11) | flat 12×10 (ES:2536-2538) | **XBass (V8.6/V7.4)** (NA:111-113, EB:372-373, C:1774, 1788-1797, 1863) | literal | literal | `ic_xbass_86` / `ic_xbass_86_checked` (NA:547-553) | `ic_xbass_86_checked` (EL:392-393) |
| — | OLD only: Ex‑XBass (11 → 9) | flat 12×10 (ES:2536-2538) | **Ex-XBass** (EU:1046; name is a literal) | literal | literal | `ic_basstrea_normal` / `_checked` (NA:251-258) | `ic_basstrea_checked` (EL:282-283) |
| — | Custom (any user name) | cmd 11 [10 gains] (ES:2561-2571) | its own name (CA:59) | same | same | custom card bg (CA:86-105) (I) | `ic_eq_custom_new` (EL:395) |

- **Cards carry no description text** — `L/item_eq_list_n.xml` has only `tv_name` (:16), the check animation
  `lottie/eq_checked_new.json` (:25-32), `iv_normal` (:35-40), and the `iv_edit` / `iv_add` buttons (:49-68).
- **Reading the current preset back** (reply 21/82 → PU:280-329): 1 Default · 2 XBass · 3 Audiobook · 4 Classical · 5 Rock ·
  6 Jazz · 7 custom (name from storage, default "Customized") · **8 → "" (no name)** · **9 → Blast traditional** ·
  10 → Live (new) / "Ex-XBass" (old) · 11 → Podcast. The send side uses 8 for Blast traditional and 9 for Ex‑XBass —
  **their send and read tables disagree for Blast traditional** (ES bts56EqView 1950-2014 repeats the same read table).
- **Curves shown for presets are decorative tables** (`EL.getData56(types)`, ES:1013) drawn on a −6…+6 axis for
  types ≤ 11 (ES:1048-1049); Live/Podcast (12/13) use the device range ±12/±8 (ES:1078-1079; PU:717-727) (I: inconsistent axis).

---

## 3. The EQ screens

### 3.1 Sound Effects list — ES + `L/activity_eqlist_56.xml`
- Title `set_eq` "Sound Effects" (ES:199; EN:1360). Back (ES:1498-1503).
- **Two tabs**: `tv_pre` "Preset EQ" (`title_preset_eq`, EN:1538) and `tv_custom` "Customized" (`customized`, EN:478)
  with underline views (layout :48-89; ES:223-229, 1385-1480). The screen opens on the tab of the active preset (ES:2609-2652).
- **Band labels** `tv_freq1…10` (layout :91-176): preset tab new → 40, 62, 125, 250, 500, 1K, 2K, 4K, 8K, 16K; old →
  50, 80, 150, 300, 600, 1.2K, 2.5K, 5K, 9K, 13K (PU:409-410; K:41, K:45). Custom tab new → same 40…16K; old → 50…13K
  (PU:562-563; K:44-45).
- **Graph** `aa_chart_view` (AAChart areaspline, touch disabled; ES:1034-1098); axis labels `tv_max/tv_mid/tv_min`
  (layout :202-226) set to `+max / min` = ±12 new, ±8 old (ES:382-395; PU:717-727). Line colour per preset name
  (`EqUtil.getEqBackground`, ES:1033).
- **Preset row tap** (debounced 100 ms) → select + send (ES:1221-1227, 2815-2886, 2505-2559). Selected preset row shows
  **"+"** `iv_add` (NA:164-173) → "copy preset as a new custom": `CustomEqEvent(type 0)` (ES:1163-1184) →
  smali `eqEdit` sets editType 1 → `showCreateDialog` (`S/Eq56SettingActivity.smali` method `eqEdit`, `.line 1394-1399`)
  → new custom named **"Unnamed EQ-N"** (`title_unnamed_eq`, EN:1542; EU:6788-6816) with the preset's stored gains (I: these
  are wire values, offset +12) → opens ED.
- **Custom tab**: list of customs newest first (sort desc, ES:803-810). Selected custom row shows a **pencil** `iv_edit`
  (CA:64-67) → ED (ES:1312-1339). Empty state: `no_custom_effect` / `no_custom_to_add` (ES:890-914; EN:1066-1067).
- **New Custom** button `btn_edit` = `create_new_custom` "New Custom" (EN:466) → flat new custom (all 0 dB) → ED
  (ES:241, 260-295, 1599-1618, 2301-2305). Shown on the Customized tab only (ES:1455-1462).
- **Edit (delete mode)** `tv_edit` "Edit" (EN:571), shown on the Customized tab when customs exist (ES:1463-1479) → rows get
  check boxes `iv_delete` (`ic_edit_no` / `ic_edit_checked`), bottom **Cancel** / **Delete** (`ln_delete`, ES:1620-1650,
  1341-1373) → dialog `sure_delete_eq` "Are you sure to delete it?" Yes/No (ES:3000-3021; EN:1494). Deleting the active custom
  falls back to Default (types 4 on OLD Blast 2) (ES:3034-3038, 2127-2143); a custom bound to the EQ button is re-sent to the
  speaker (ES:3051-3063, 2683-2725).
- **Preset edit menu** (`DD.showEditListDialog`, DD:679-695): "Copy Preset" (`button_customize_on_this_basis`, EN:199) /
  "Edit Preset" (`button_only_modify_the_current_eq`, EN:206) / "Delete" (EN:489). Reached from `iv_edit` on the preset
  adapter (ES:1186-1210), but that button is visible only on custom rows (NA:167-169) (I: unreachable for Blast 2 presets).
- **Limits:** no maximum number of customs found (no size check in bts56 code; only analytics read `eq_custom_num`,
  `J/tribit/utils/ui/dialog/EvaluateDialog.java:66`).
- Disconnected → `ll_no_bluetooth` with "Connect to" (opens Bluetooth settings or enables the adapter, ES:1584-1597, 1816-1850).

### 3.2 Custom Sound Effect editor — ED + `L/activity_eq_detail_56.xml`
- Title `custom_effect` "Custom Sound Effect" (ED:281; EN:475); right action **Reset** (`title_reset_the_eq`, ED:437) →
  `EqResetDialog` → restores the gains the EQ had on entry (not zero), saves, re-sends (ED:1133-1184).
- **Name**: label `custom_name` "Custom Name" (ED:425); field `et_name` **maxLength 15** (layout :36). Rename on focus loss;
  duplicates and the reserved names list (Music, TRIBIT Signature, X-3D, XBass 2.0, XBass Off (V8.6/V7.4), …, EL:40)
  rejected with `name_already_exist` "This name already exists" (ED:926-962; EL:785-792; EN:1052); Back is blocked while the
  name clashes (ED:918-924, 1200-1205).
- Label `sound_config` "Sound Configuration" (ED:431). Band labels from `getFreqList1` (ED:353-419).
- **Graph** spline, refreshed live (ED:449-452, 855-863). Axis and dB labels ±12 new / ±8 old (ED:650-741).
- **10 vertical band sliders** `rv_eq_seekbar` (layout :337-345) + horizontal scroll bar `seekbar` (:346). Every change sends
  cmd 11 [10 gains] and saves (ED:744-805, 839-849). Wire = dB + 12 new / + 8 old (`researches/11_own_app.md` §3.6).
  Slider range ±12/±8 (jadx shows them swapped at ED:171-177; smali disagrees per research 11 §3.6) (I).
- Saving a new custom: toast `saved_successfully` (ED:597-604; EN:1331); edits to a custom bound to the EQ button re-send
  the button table (ED:1071-1100).

### 3.3 EQ Button screen — EB + `L/activity_eq_button_56.xml` (from INFO's "Eq Button" row)
- Title `eq_button_setting` "Eq Button" (EB:883; EN:624). **Reset** `tv_reset` (EN:1540) → dialog "Confirm reset" with text
  `eq_button_reset_info_30` with "XBass Off" replaced by "TRIBIT Signature" (DD:721-740; EN:623) → sends cmd 71 for two slots:
  slot 0 = Default, slot 1 = XBass (gains O on old, N on new) (EB:670-739).
- **Two slots for Blast 2**: the third (`ll_blue`) is hidden for the Blast 2 name (EB:133-140). Slot labels reuse light
  strings: `ll_white` "Light on" (`light_on`, EN:839) is listed first (layout :50), `ll_off` "Light Off" (EN:838) second
  (layout :86) (EB:907-913). Each slot card shows the EQ name (EB:288-327, via `eqName` EB:329-383) on that preset's
  background; tap → `EqSelectNewActivity` to pick any preset or custom (EB:845-874, 923-943).
- **Apply** `btn_yes` "Apply" → "Applied" (`apply_mode` / `apply_moded`, EN:118-119): one cmd 71 per slot
  [count, slot, type, 10 gains]; type 0 Default, 0xFE (`Format.DEFAULT_PAYLOAD_MAX_LENGTH`, I) custom, Live 10 (unchanged),
  others types − 3 (EB:741-843). Confirmation toasts `successfully_updated` / `factory_reset_successed` (EB:1004-1011).
- Reads current slots with cmd 72, one 17-byte reply per slot (EB:1100-1212; B:258-259).

---

## 4. Light screens

### 4.1 Lighting control — LC + `L/activity_light_control_56.xml` (from the control screen's light strip)
- Title `lighting_control` "Lighting control" (LC:412; EN:842); note `display_switch_light_mode` (LC:425; EN:559).
- **Three modes** `rb_1/rb_2/rb_3` = "Mode 1 / Mode 2 / Mode 3" (LC:431-443); Mode 4 and the "custom" button are hidden
  (LC:103-121). Tap → cmd 12 [1/2/3] (LC:466-503, 272-282). Active backgrounds `ic_light_bg` / `ic_light_two` /
  `ic_light_three`, inactive `*_no` (LC:284-409). The content is hidden when the light is off (mode 4) (LC:132-151, 226-228).
- **Gear** `iv_setting1/2/3` next to the **active** mode only (others invisible, `hasCustom()` = false, LC:49-51, 547-590)
  → LX for that mode (LC:482-497). `ln_volume` "Volume Indicator" row is `gone` here (layout :146-151).
- Re-queries cmd 20 on resume (LC:532-545).
- RU names: `mode_one/two/three`, `lighting_control` → server / EN fallback.

### 4.2 Light customisation — LX + `L/activity_light_custom_56.xml`
- Mode taken from storage (`light_mode`, LX:126-128). Title bar action **Reset** → dialog `restore_factory_settings`
  "Are you sure to restore factory settings?" → cmd 73 [mode] (LX:155-186, 2471-2483, 945-960; B:262-263).
- Picture `iv_light_current`: `ic_light_bar6` / `ic_light_mid` / `ic_light_side` / `ic_light_all` per zone (LX:208, 1160-1422).
- **Zone tabs** (`tab_light2`): `light_bar` "light bar", `mid_horn` "middle horn", `side_horn` "side horn"; **mode 2 adds
  "All"** (`all`) (LX:161-167, 371-415; EN:834, 970, 1421, 95).
- **Colour** (`tv_bar` "color", EN:279):
  - light bar: **rotate** / **rainbow** / **customize** → cmd 62 [mode, 1 / 2 / 0] (LX:599-628, 1026-1036); customize
    opens the colour picker (LX:627).
  - horn colour taps: LX:630-730.
  - mid / side horn: **rotate** / **customize** → cmd 68 / 69 [mode, 1 / 0] (LX:922-944, 1038-1060).
  - Picker `ChooseColorNewDialog`: colour wheel, R/G/B fields (default 255,255,255), 7 swatches
    (`J/tribit/utils/ui/dialog/ChooseColorNewDialog.java:91-172`) → cmd 54 / 55 / 56 [mode, R, G, B] (LX:2424-2466).
- **Brightness** `sb_light` 0…100 (layout :221-227), "luminance" (EN:917), sent on release → cmd 57 / 58 / 59 [mode, value]
  (LX:965-1012).
- **Rhythm**:
  - modes 1 and 3, every zone: `ll_move1` = **low frequency / high frequency / high and low / Stillness** → cmd 53
    [mode, zone 1/2/3, 1/2/3/4] (LX:210-236, 1160-1267; moveListener1; B:194-195; EN:914, 748, 749, 1302).
  - mode 2: no rhythm per zone (LX:1268-1290: `ll_move1` hidden on tabs 0-2). The **All** tab hides colour and brightness and
    shows `ll_move1` (rhythm, sent for zone 1) plus `ll_move3` "form" = **diverge / compact / random** → cmd 53 [mode, 2, 1/2/3]
    (LX:1268-1422; moveListener3; EN:700, 561, 397, 1283).
- Reads with 150 ms gaps: cmd 67 (rhythm), 61 (bar colour), 70 (horn colour mode), 60 (colours), 63 (bar colour mode)
  (`LightCustom56Activity$queryLight$1.java:40-134`).

---

## 5. Speaker settings screen — INFO + `L/activity_bts_info_56.xml` (the gear)

Header: Back; title `settings` + device name "Settings<Name>" (INFO:1486; EN:1364); help icon `iv_setting` (`ic_help_new`)
→ web help / FAQ page, needs network (INFO:1838-1843; `J/tribit/utils/UpdateUtils.java:405-434`).

| Row (id) | EN (RU = server / EN fallback) | Shown for Blast 2 | Action / command |
|---|---|---|---|
| Firmware version `ll_fire_version` | `firmware_version` "Firmware Version" (INFO:1498; EN:693) + `tv_version` "vX.Y" + `tv_dsp` "/vNN" (INFO:1302) | always; `iv_help_fire` appears when DSP is known (INFO:1295); **"New"** badge `btn_ota` when the server has an update (INFO:359-366) | tap version / "New" → network check, phone battery > 10 % (INFO:2211-2229), speaker battery ≥ 21 % (INFO:712-718) → OTA dialog (INFO:1700-1718) — server |
| Device name `ll_name` | `device_name` "Device Name" (INFO:1492; EN:508) | always | rename dialog, max 25 chars, counter "n/25", empty and duplicate names refused (`J/tribit/utils/ui/dialog/NameEditDialog.java:73-121`; `L/dialog_edit_name_new.xml:69`; INFO:2642-2718); stored in the local DB and synced to the server, **no Bluetooth command** (INFO:2749-2761) |
| Eq Button `ll_eq` | `eq_button_setting` "Eq Button" (INFO:1603; EN:624) — Micro 3 gets "XBass Button" instead (INFO:1582-1595) | fw ≥ 10000, i.e. always (INFO:548, 3531-3561) | → EB (INFO:1885-1890); help `showEqDialog2` (INFO:1771-1776) |
| Voice Prompt `ll_voice` | `voice_prompt` "Voice Prompt" (INFO:1540; EN:1638) | always (fw ≥ 10000 → five-switch form, INFO:611-656) | → `VoiceSetNewActivity`: Power On/Off Beep, Bluetooth Pairing Beep, Low Battery Beep, Maximum Volume Beep, TWS Pairing Beep (`J/tribit/moduledevice/activity/VoiceSetNewActivity.java:682-707`; EN:1570, 175, 916, 965, 1577) → cmd 48 [5 × 1/0] (same file :432, :512; B:146-148) |
| Auto Shutdown `ll_shutdown` | `auto_shutdown` "Auto Shutdown" (INFO:1534; EN:147) | always (layout :235-262) | switch → cmd 3 [on/off] (INFO:1844-1857, 2170-2180; B:155-162); help popup (INFO:1764-1770) |
| Volume Indicator `ll_volume` | `light_volume` "Volume Indicator" (INFO:1552; EN:840) | always (INFO:559-563) | switch → cmd 52 [1/0] (INFO:1873-1884; B:91-92); help (INFO:1807-1811) |
| Movie Mode `ll_game` | `video_mod` "Movie Mode" (INFO:1558; EN:1629) | **hidden** (layout :306-312, no code shows it) | — |
| Microphone Boost `ll_mac` | `microphone_boost` (INFO:1564; EN:968) | only if `isNewVersion56` (INFO:395, 420) | switch → cmd 97 [1/0] (INFO:1825-1837; B:290-291); help (INFO:1797-1801) |
| Howling Boost `ll_howling` | `howling_boost` (INFO:1570; EN:760) | only if `isNewVersion56` (INFO:407, 432) | switch → cmd 99 [1/0] (INFO:1812-1824; B:298-299); help (INFO:1792-1796) |
| Auto Sleep `ll_sleep_new` | `auto_sleep` "Auto Sleep" (INFO:1528; EN:150); state "Turn on" / "#h #min later" / "Turn off" (INFO:1613-1680) | always (INFO:518-549) | → `SleepSetNewActivity`: on/off + hour:minute picker, note `auto_sleep_shut_down` (`.../activity/SleepSetNewActivity.java:297-345, 350-357`) → cmd 14 [h, m], off = [255, 255] (`J/bluetoothlib/BtClient.java:3270-3285`; B:147-148; Blast 2 branch decompiled empty at BtClient:3374-3379 — route (I), consistent with research 11 §3.6) |
| **Shutdown** `btn_shutdown` | `shutdown` "Shutdown" (INFO:1522; EN:1420) | fw ≥ 10000 → shown (INFO:691-711) | confirm `sure_shutdown_device` → cmd 50 → screen closes (INFO:1725-1730, 2521-2535; B:190-191) |
| **Factory Reset** `btn_factory_reset` | `factory_reset` (INFO:1510; EN:648) | always | confirm with tip `clear_connection_reconnect` → cmd 7 [1] + loading dialog (INFO:1691-1696, 2536-2549, 2763-2783; B:169-170; EN:258) |
| **Delete the device** `btn_delete` | `delete_the_device` (INFO:1516; EN:493) | always | confirm `sure_delete_device` → marks the DB row deleted, leaves the screen, posts DeviceDelete (INFO:1684-1690, 2507-2520, 2785-2800, 1383-1395) |
| Upgrade the Firmware `btn_upgrade` | `upgrade_the_firmware` | hidden (INFO:337) | — |
| Upgrade the Dsp Firmware `btn_upgrade_dsp` | `upgrade_the_dsp_firmware` | hidden (INFO:555) | (DSP OTA runs inside the firmware flow, I) |
| Clock `btn_time`, Reboot `btn_reboot`, EQ-button button `btn_eq_button` | — | hidden (layout :445-463, :521-530) | — |
| Debug log `btn_log` | "蓝牙数据日志" | pre-release builds only | → BlueLogsActivity (INFO:1697-1699) |

---

## 6. Anything else reachable for Blast 2

- **TWS / Party:** no pairing UI anywhere in the bts56 screens (grep for "tws/party" in `J/tribit/moduledevice/bts56/` finds
  nothing). The only TWS traces: the partner-battery strip (§1 item 8) and the "TWS Pairing Beep" voice prompt (§5).
- **Firmware update (OTA + DSP):** server check `queryFireVersion` with names `<name>`, `<name>_n`/`_nc` (56C) and DSP
  `<name>_d` / `_nd` / `_ndc` (C:1120-1197); red gear and "New" badge; the flow is in INFO (OTA listeners INFO:2836-3245).
  Server only.
- **User manual / FAQ:** help icon in settings → `WebViewHelpActivity` with the product FAQ URL from the server, or
  `https://gtwt.1000shores.cn/tribit_help_en/` (`_zh/` for Chinese) when none is known (`J/tribit/utils/UpdateUtils.java:405-434`).
  Network required (INFO:1838-1841). (Not contacted in this recon.)
- **Rename speaker:** settings only; local + server, no Bluetooth (§5).
- **Find device / locate:** none found for Blast 2.
- **Delete device / unpair:** "Delete the device" (§5); an `unpair()` helper exists (INFO:2802-2825) (I: not wired to a
  Blast 2 button).
- **Product picture and catalog:** from the server cache (§1 item 7).

---

## 7. Checklist

| # | Element | Where (file:line) | In Tribit for Blast 2 | Notes |
|---|---|---|---|---|
| 1 | Back button (control) | C:904-909 | yes | finish |
| 2 | Title "Device Settings" | C:221; EN:514 | yes | not the device name |
| 3 | Settings gear → INFO | C:915-920 | yes | |
| 4 | Gear turns red on update | C:493-502 | yes | server |
| 5 | Device name (user's) | C:1221 | yes | |
| 6 | Battery % + ring | C:1561-1580 | yes | |
| 7 | Charging / Full state | C:652-718 | yes | icon `ic_charge`; text view stays gone (I) |
| 8 | Battery re-query loop | `Bts56ControlActivity$queryBattery$1.java:85-105` | yes | 1 s while 0 |
| 9 | Product picture | C:249-251; UpdateUtils:214-227 | yes | server cache, placeholder |
| 10 | Partner battery strip | C:2037-2078 | yes, if TWS partner | Chinese literal text |
| 11 | Previous | C:1073-1092 | yes | cmd 2 [1] |
| 12 | Play/Pause | C:1041-1071 | yes | cmd 2 [3]/[4], debounce 100 ms |
| 13 | Next | C:1094-1113 | yes | cmd 2 [2] |
| 14 | Volume slider 0-31 | layout :223-241; C:938-969 | yes | send on release |
| 15 | High-volume toast > 70 % | C:952-955; EN:750 | yes | once per screen |
| 16 | EQ strip "Sound Effects" + name | C:1252, 1768-1876 | yes | |
| 17 | EQ strip background per preset | C:1776-1859; EL:263-395 | yes | |
| 18 | EQ strip → Sound Effects list | C:1033-1038 | yes | |
| 19 | Light strip (speakerLight) | DC:11; C:1525-1541 | yes | |
| 20 | Light mode label Mode 1/2/3 + bg | C:1582-1653 | yes | |
| 21 | Light on/off switch | C:1115-1118, 2289-2308 | yes | cmd 12 [mode]/[4] |
| 22 | Light strip → Lighting control (only if on) | C:1200-1212 | yes | |
| 23 | No-Bluetooth overlay + "Connect to" | C:1227-1239, 1729-1765 | yes | button handler not in C (I) |
| 24 | No-network overlay | C:1233, 1906-1933 | no (I) | hidden by its own code |
| 25 | Debug log button | C:279-293 | pre-release only | |
| 26 | Resume query burst | C:1279-1296; queryState$1:40-117 | yes | 100 ms gaps |
| 27 | Disconnect toast + close | C:2253-2265 | yes | |
| 28 | Auto-reconnect ×3 + dialog | C:2157-2198 | yes | |
| 29 | Lottie light animation | layout :113-122 | no | never referenced |
| 30 | X-Bass / 3D / party / power on control screen | layout :1-362 | no | |
| 31 | Firmware flags (4 definitions) | MainNewActivity:1939-1940; C:527-528; ED:272-273; INFO:1304-1305 | yes | parity trap |
| 32 | Preset Default "TRIBIT Signature" | NA:72-77; EB:339-343; C:1810-1815 | yes | zh "默认" |
| 33 | Preset XBass ("XBass 2.0" on 56C) | NA:117-118; EB:374-375; C:1861-1862 | yes | id 2 |
| 34 | Preset Blast traditional | NA:102-107; EB:364-369; C:1829-1847 | fw > 10083 or 56C | zh "户外"; id 8 sent, 9 read |
| 35 | Preset Classical shown "X-3D" | NA:81-84; EB:347-355; C:1816-1826 | yes | id 4 |
| 36 | Preset Audiobook | EU:1141-1147 | yes | id 3 |
| 37 | Preset Rock | EU:1148-1154 | yes | id 5 |
| 38 | Preset Jazz | EU:1155-1161 | yes | id 6 |
| 39 | Preset Live "XBass Off (V8.6/V7.4)" | NA:108-110; EB:370-371; C:1848-1860 | MID/NEW_EQ | id 10, flat |
| 40 | Preset Podcast "XBass (V8.6/V7.4)" | NA:111-113; EB:372-373; C:1774-1797 | MID/NEW_EQ | id 11, flat |
| 41 | Preset Ex‑XBass | EU:1046; smali :5938 | OLD, fw > 10085 and dsp > 10072 | id 9 |
| 42 | Preset order per firmware | EU:1003-1238 | yes | §2.1 |
| 43 | Preset card backgrounds | NA:196-563 | yes | §2.2 |
| 44 | Read-back id → name | PU:280-329 | yes | 8 → "" |
| 45 | Default send per firmware | ES:2574-2607 | yes | |
| 46 | Preset send cmd 4 [id, gains] | ES:2505-2559; B:104-119 | yes | id = types − 2 |
| 47 | RU names = server / EN fallback | ResourceUtils:34-46 | yes | literals identical |
| 48 | Sound Effects title | ES:199 | yes | |
| 49 | Tabs Preset EQ / Customized | ES:223-229, 1385-1480 | yes | |
| 50 | Band labels 40…16K / 50…13K | PU:409-410, 562-563; K:41-45 | yes | per firmware |
| 51 | Graph on list (read-only) | ES:933-1100 | yes | presets decorative |
| 52 | Axis ±12 / ±8 | ES:382-395; PU:717-727 | yes | presets drawn ±6 |
| 53 | Preset row tap = select + send | ES:2815-2886 | yes | |
| 54 | "+" on selected preset = copy as custom | NA:164-173; ES:1163-1184; smali eqEdit .line 1394-1399 | yes | "Unnamed EQ-N" |
| 55 | Custom list newest first | ES:803-810 | yes | |
| 56 | Pencil on selected custom → editor | CA:64-67; ES:1312-1339 | yes | |
| 57 | New Custom button | ES:241, 1599-1618, 2301-2305 | yes | flat 0 dB |
| 58 | Empty custom state texts | ES:890-914 | yes | |
| 59 | Edit → multi-select delete | ES:1620-1650, 1341-1373 | yes | |
| 60 | Delete confirm Yes/No | ES:3000-3021 | yes | |
| 61 | Delete active custom → Default | ES:3034-3038, 2127-2143 | yes | |
| 62 | Deleted custom on EQ button re-sent | ES:3051-3063, 2683-2725 | yes | |
| 63 | Copy/Edit/Delete preset menu | DD:679-695 | no (I) | button not visible on presets |
| 64 | No custom count limit | (absence; EvaluateDialog:66) | yes | |
| 65 | Editor title + Reset (restore entry state) | ED:281, 437, 1133-1184 | yes | |
| 66 | Custom name, max 15 chars | layout eq_detail :36 | yes | |
| 67 | Duplicate / reserved names refused | ED:926-962; EL:40, 785-792 | yes | |
| 68 | Back blocked on clashing name | ED:918-924, 1200-1205 | yes | |
| 69 | 10 band sliders, live send cmd 11 | ED:744-805, 839-849 | yes | ±12 / ±8 |
| 70 | Editor graph live | ED:449-452, 855-863 | yes | |
| 71 | Saved toast | ED:597-604 | yes | |
| 72 | EQ button table refreshed after edit | ED:1071-1100 | yes | |
| 73 | Lighting control: 3 modes | LC:431-443, 466-503 | yes | cmd 12 |
| 74 | Mode 4 / custom button hidden | LC:103-121 | no | |
| 75 | Gear on active mode → customise | LC:547-590, 482-497 | yes | |
| 76 | Light content hidden when off | LC:132-151, 226-228 | yes | |
| 77 | Light customise Reset (cmd 73) | LX:155-186, 945-960, 2471-2483 | yes | |
| 78 | Zone tabs bar / mid horn / side horn | LX:371-378 | yes | |
| 79 | "All" tab in mode 2 | LX:161-167, 376-378 | mode 2 only | |
| 80 | Bar colour rotate/rainbow/customize | LX:1026-1036 | yes | cmd 62 |
| 81 | Horn colour rotate/customize | LX:922-944, 1038-1060 | yes | cmd 68/69 |
| 82 | Colour picker wheel + RGB + 7 swatches | ChooseColorNewDialog:91-172 | yes | cmd 54/55/56 |
| 83 | Brightness 0-100 per zone | LX:965-1012 | yes | cmd 57/58/59 |
| 84 | Rhythm low/high/both/still (modes 1, 3) | LX:210-236, 1160-1267 | yes | cmd 53 |
| 85 | Mode 2 "All": rhythm + form diverge/compact/random | LX:1268-1422 | mode 2 | cmd 53 zone 1 / 2 |
| 86 | Light reads 67/61/70/60/63 | queryLight$1:40-134 | yes | 150 ms gaps |
| 87 | Settings title + name | INFO:1486 | yes | |
| 88 | Help / FAQ (web) | INFO:1838-1843; UpdateUtils:405-434 | yes | network |
| 89 | Firmware version + DSP | INFO:1295-1302 | yes | |
| 90 | "New" firmware badge + OTA flow | INFO:1700-1718, 2836-3245 | yes | server; battery guards |
| 91 | Rename (25 chars, no BT) | NameEditDialog:73-121; INFO:2642-2761 | yes | server sync |
| 92 | Eq Button row → EB | INFO:1603, 1885-1890, 3531-3561 | yes | |
| 93 | Voice Prompt → 5 beeps | INFO:611-656; VoiceSetNewActivity:432, 682-707 | yes | cmd 48 |
| 94 | Auto Shutdown switch | INFO:1844-1857, 2170-2180 | yes | cmd 3 |
| 95 | Volume Indicator switch | INFO:559-563, 1873-1884 | yes | cmd 52 |
| 96 | Movie Mode | layout bts_info :306-312 | no | hidden |
| 97 | Microphone Boost | INFO:1825-1837 | new firmware only | cmd 97 |
| 98 | Howling Boost | INFO:1812-1824 | new firmware only | cmd 99 |
| 99 | Auto Sleep → timer screen | INFO:1613-1680, 1910-1916; SleepSetNewActivity:297-345 | yes | cmd 14 [h,m] / [255,255] |
| 100 | Shutdown button | INFO:691-711, 1725-1730, 2521-2535 | yes | cmd 50 |
| 101 | Factory Reset | INFO:1691-1696, 2536-2549, 2763-2783 | yes | cmd 7 [1] |
| 102 | Delete the device | INFO:1684-1690, 2785-2800 | yes | local + server |
| 103 | Upgrade FW / DSP / Clock / Reboot buttons | INFO:337, 555; layout :445-530 | no | hidden |
| 104 | EQ Button: 2 slots ("Light on", "Light Off") | EB:133-140, 907-913 | yes | 3rd slot hidden |
| 105 | EQ Button: pick EQ per slot | EB:845-874, 923-943 | yes | EqSelectNewActivity |
| 106 | EQ Button: Apply | EB:741-843 | yes | cmd 71 per slot |
| 107 | EQ Button: Reset to Signature + XBass | EB:670-739; DD:721-740 | yes | |
| 108 | EQ Button: read slots | EB:1100-1212 | yes | cmd 72 |
| 109 | TWS / party pairing UI | (absence in bts56) | no | |
| 110 | Find device | (absence) | no | |
