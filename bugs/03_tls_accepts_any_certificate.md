# Bug 03 — их HTTP-клиент принимает любой сертификат и любое имя сервера (TLS без проверки)

**Status:** 🔧 fix pending verification (2026-10-16 13:03 +03:00: патч 30 включён, путь проходит; отказ поддельному сертификату не наблюдался) · **Severity:** S1 (безопасность людей: подмена ответов сервера, в том числе о прошивке) · **Fixing:**
эта сессия — патч 30 (вернуть OkHttp стандартную проверку), проверка на A51
**Version/build:** Tribit 5.0.0 и Krinik Tribit до патча 30 · **When/context:** найдено 2026-10-16 12:57 +03:00 при
составлении `researches/09` (вопрос владельца о том, что нравится и не нравится в коде)

## Symptom

По коду (не по сети — HOUSE_RULES R2): единственный клиент приложения (`TribitApp`, EasyHttp) не проверяет сертификат
сервера и имя хоста. Человек в той же Wi-Fi сети может выдать себя за `gateway.tribit.com`.

## Forensics

- `decompiled/jadx-base/sources/com/thousandshores/tribit/TribitApp.java:216–225`: `HttpSslFactory.generateSslConfig()`
  → `builder.sslSocketFactory(…, trustManager)` → `.hostnameVerifier(HttpSslFactory.generateUnSafeHostnameVerifier())`.
- `com/hjq/http/ssl/HttpSslFactory.java:42–51`: без сертификатов `prepareTrustManager` не даёт менеджера →
  `x509TrustManager = new UnSafeTrustManager()`; `UnSafeTrustManager.checkServerTrusted` — пустой (принимает всё);
  `UnSafeHostnameVerifier.verify` — `return true`.

## Root cause

Библиотека EasyHttp даёт «небезопасные» фабрики для отладки; приложение включило их в выпускной сборке.

## Fix plan

Патч 30: убрать из сборки клиента в `TribitApp.initNetWork` вызовы `sslSocketFactory(…)` и `hostnameVerifier(…)` —
OkHttp проверяет сертификат и имя системным хранилищем. Проверка: на A51 гость, каталог, страница колонки и проверка
прошивки работают (их сертификат настоящий — тогда запросы проходят); контроль — тот же путь без патча.

## Decisions made without the owner

- Исправлено сразу, без вопроса владельцу: правило безопасности людей и его же принцип «мы уважаем приватность»
  (2026-10-16 10:50 +03:00); откат — одна строка в `patches/apply.py`.

## Fix (2026-10-16 13:02 +03:00)

Hygiene: сборка зелёная, `ok 30`. Functional run: A51 — весь путь до проверки прошивки, ответы «success», ошибок TLS нет
(`testcases/reports/2026-10-16_patch8_anon.md`). Не наблюдалось: отказ при подмене сертификата.

## Links

`researches/09_likes_dislikes_code_ui.md` (код — не нравится, п. 0); `plans/02` → «Баги проекта».
