# Research 07 — patch 8 without an account: what the speaker page needs from their catalog

> **Created:** 2026-10-16 · **Parent:** `plans/01_patch_plan.md` §4б item 1; owner 2026-10-16 «аккаунт не нужен» ·
> «выпиливаем НАХУЙ аккаунты» (`MASTER_PLAN.md` decision journal) · **Status:** recon done 2026-10-16 ≈ 10:00 +03:00;
> patch not written · **Outbound:** —

## The problem (observed)

Patch 8 (no account) opens the main screen, but on the A51 with a StormBox Blast 2 the connection dialog never closes:
without a token their gateway answers `{"datas": null, "resp_code": 1, "resp_msg": "Full authentication is required to
access this resource"}` even to the `equip-anon` endpoints (`testcases/reports/2026-10-16_wave1.md`, Found 0). With a guest
token the same path opens the speaker page (control, same report, run 9).

## What the app asks for on the way to the speaker page

Source: the app's own EasyHttp log of one guest run, `diagnostics/2026-10-16_a51_easyhttp_visitor.log` (local, ignored:
it holds a guest bearer token). No request of ours went to their server (HOUSE_RULES R2).

| Call site | Endpoint | Needed for the speaker page |
|---|---|---|
| `ViewModelMainNew.kt:722` | `equip-anon/queryAllThridProducts` | product list of the main screen |
| `ViewModelMainNew.kt:472`, `ViewModelDevice.kt:472` | `equip-anon/produCateByClient?clientId=Tribit` | catalog: `productId`, `productName`, `productLogo` (URL of a picture), `productModel` per product — the connection dialog waits for it |
| `ViewModelDeviceBts.kt:662` | `equip-anon/queryAllThridProducts?productName=<model>` | «device support» of one model |
| `ViewModelDeviceBts.kt:254` | `api-app/api/checkFirmwareUpgrade?clientId=Tribit&os=2&equipmentModel=<model>…` | firmware check — the owner keeps it, without an account |
| — | `equip-anon/synchSpnerUserEquipsTribit` | copy of the user's device list in their cloud — not needed |

## Plan for patch 8 (next session)

1. Extend the interceptor of patch 20 (`krinik/NoCloud`, the app's only OkHttp client): for `produCateByClient` and
   `queryAllThridProducts` it answers by itself with a local JSON from the APK assets (`okhttp3.Response.Builder`, code
   200, the same `datas` shape) — no token, no request to their server.
2. The local JSON carries the owner's models first (StormBox Blast 2), taken from the app's own logged answers; product
   pictures are already a placeholder in the APK (researches/06 B) or our own icon.
3. `synchSpnerUserEquipsTribit` joins the cut list of patch 20.
4. The firmware check: verify whether `checkFirmwareUpgrade` answers without a token; if it demands one, the owner's
   «проверка прошивки без аккаунта» needs a decision (ask, do not guess).
5. Then patch 8 is switched on again and checked on the A51 with the speaker: clean install → START → «Tap to Add Device»
   → «Go to Connect» → the speaker page opens; logcat shows no `visitorLoginOfTribit`.

## Raw material extracted (2026-10-16 ≈ 10:00 +03:00)

`python tools/recon/answers_from_log.py diagnostics/2026-10-16_a51_easyhttp_visitor.log diagnostics/2026-10-16_answers`
(both paths ignored by git) wrote 7 answers: `DeviceDetail__produCateByClient` (27 products, Blast 2 among them),
`GetAllDevices__queryAllThridProducts` (25), `GetDeviceSupport__queryAllThridProducts` (1 — Blast 2: logo, FAQ URLs,
firmware prompts in 10 languages, `isUpgrad`), `FireUpgrade__checkFirmwareUpgrade` (`datas` null — no update),
`ProductString__getLangInfoBySchemaOrLangKey` (**756 Russian strings** — `{"ru": {key: text}}`), plus the visitor login and
user info answers (not needed).

**Second use — wave 2 and patch 8a.** The Russian dictionary is what their server sends on every start; turned into our own
`values-ru` (plans/01 §3, the validator first), it lets patch 8a stop waiting for the server without the interface turning
English (`testcases/reports/2026-10-16_wave1.md`, Found 1).

## Open fork before step 1

FORK: options <A: a local catalog with the owner's models only (Blast 2) | B: the full catalog (27 + 25 products) shipped in
the APK - their data in our git | C: the interceptor passes the request on and substitutes the local answer ONLY when their
gateway answers «Full authentication» (fallback; local data needed only for that case)> · price of error <A: every user with
another Tribit model loses the speaker page; B: their catalog in a public repository; C: more smali, still needs the data of
A or B for the substitution> · consulted <recon of the app's own answers above; owner's word on accounts - the choice of
which models the fork supports is the owner's (asked in the next session's chat, not decided here)>
