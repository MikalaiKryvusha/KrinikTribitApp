# Krinik Tribit — Internal architecture map

> **The INTERNAL map: the project's logical architecture** — the abstractions and how they interact. Where
> `PROJECT_STRUCTURE_EXTERNAL_MAP.md` says *where things live*, this says *how the system thinks*.
> **Living reference — never DONE-tagged.**

---

## The core abstractions

| Abstraction | What it *is* (essence) | Responsibility |
|-------------|------------------------|----------------|
| Their app (reference) | Tribit 5.0.0 `com.thousandshores.tribit`, decompiled | the reference behaviour and the source of the speaker protocol |
| Patch | an anchored text edit of smali or resources | fixes one defect of their app; fails loudly when the anchor moved |
| Fork build | their split APK set, patched base + untouched splits, one signing key | what goes on the Titan today |
| Speaker | a Tribit speaker (StormBox Blast 2 on the stand) | the device both apps control |
| Speaker protocol | packets `EA <len> <cmd> <data> <checksum>` over RFCOMM (UUID `0CF12D31-…`) or BLE (`0000ffa0`/`ffa1`) | EQ (cmds 4, 11), volume (13), light (12/52), battery (6); EQ gain shifted +12 |
| Krinik Tribit | their app + our patches, signed by our key | the product: the owner chose to fix their app — «чиним ИХ приложение» (chat 2026-10-16) |

All protocol facts above are read from decompiled code (`researches/03_tribit_app_pains.md`), `[NOT-TESTED]` on a speaker.

## How they interact

```
original-apk ──decode──▶ work/base ──patches──▶ fork build ──adb──▶ Titan ──BT──▶ Speaker
```

## Invariants & rules of the model

- A patch never edits by line number — only by an exact anchor that must occur exactly once.
- The fork's split set is signed by ONE key; a mixed set does not install.
- No component of ours talks to Tribit's servers (`HOUSE_RULES.md` R2).

## Key decisions embedded in the architecture

- Their app is fixed by patches, not rewritten (the owner, 2026-10-16: «чиним ИХ приложение»). Texts that come from
  their server are intercepted and replaced by ours; layouts are reworked as resources (researches 04–06).
