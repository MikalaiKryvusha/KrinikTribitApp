# Krinik Tribit — Internal architecture map

> **The INTERNAL map: the project's logical architecture** — the abstractions and how they interact. Where
> `PROJECT_STRUCTURE_EXTERNAL_MAP.md` says *where things live*, this says *how the system thinks*.
> **Living reference — never DONE-tagged.**

---

## Two products

1. **Our app** (`app/`, `com.kriniks.tribit`, debug `com.kriniks.tribit.debug`) — written from scratch, the owner's
   decision «Делаем по плану C» (2026-10-16 15:24). The main line.
2. **The fallback** (`native/`, «Old Krinik Tribit», `com.kriniks.tribit.old`) — Tribit 5.0.0 with our fixes, for models and
   firmware our app does not handle yet; only blocking fixes.

## Our app — the layers

| Layer | Abstraction | Responsibility |
|---|---|---|
| `protocol/` (pure Kotlin, JVM tests) | `Packet` + `Framer` | the packet `EA <len> <cmd> <payload> <sum>`; a byte stream cut into packets by `len`, checksum flagged |
| | `Blast2`, `Eq`, `Settings`, `SpeakerState`, `SpeakerSettings` | command builders and reply parsing of the Blast 2 (`researches/11` §3); the state = only what the speaker answered |
| | `Profile` | the settings file (`ideas/01`): EQ + light as JSON |
| `link/` | `SpeakerLink` | one SPP socket: open, send, read loop on `Dispatchers.IO`, close once; debug log `KT.Link` |
| | `SpeakerViewModel` | the one owner of the connection: follows the speaker's link while the app is on screen, startup queries, one command in flight (each waits for the speaker's echo), state flows for the UI |
| `ui/` | `Page`, `Card`, `SettingsRow`, `Choices`, `PinkButton`, theme | KARTUN's design scheme: one set of components everywhere (GOAL.md 11:18) |
| | `HomeScreen` + `SpeakerCard`, `EqScreen`, `SpeakerSettingsScreen`, About, Debug | screens; a screen shows the speaker's answer, never a default |
| `src/debug` | `DebugTools`, `EarActivity` | debug-only: device facts; the A51 microphone as the stand's ear |

## How they interact

```
Speaker ──SPP bytes──▶ SpeakerLink.readLoop ──Framer──▶ Frame ──▶ SpeakerState / SpeakerSettings ──StateFlow──▶ Compose
   ▲                                                                                                          │
   └──────── SpeakerLink.send ◀── exchange (lock, echo, retry) ◀── SpeakerViewModel actions ◀── user taps ◀───┘
Android Bluetooth broadcasts (ACL, A2DP, adapter) ──▶ SpeakerViewModel.receiver (only while on screen)
```

## Invariants & rules of the model

- The screen shows only what the speaker answered; an unanswered value is «—» (EXP-0009).
- One command in flight; a set waits for its echo (500 ms × attempt, 3 attempts).
- No location permission, no scan: the bonded Blast 2 and `BLUETOOTH_CONNECT` only.
- The link lives only while the app is on screen (`onStart`/`onStop`); a cancelled link sets no state.
- No component of ours talks to Tribit's servers (`HOUSE_RULES.md` R2).
- App texts are the owner's text — written by `AUTHOR_STYLOMETRY.md` (`HOUSE_RULES.md` R10).

## The fallback — how it is built

`native/` (Tribit's apktool tree + our fixes) ──`build.sh`──▶ variant step ──apktool──▶ signed APK. A patch edits by an exact
anchor only; protocol facts for our app are read from its code (`decompiled/`), never linked.
