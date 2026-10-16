package com.kriniks.tribit.protocol

/**
 * Commands of Tribit StormBox Blast 2 (their family «bts56») for phase 1 of the own app: version, battery, volume,
 * play/pause. Ids and payloads are read from their code - `researches/11_own_app.md` §3.3, send side
 * `Bts52Util.java`, reply side `ViewModelDeviceBts.bts56Read` + `Bts52Util.payloadToState/payloadToString`.
 * Every reply value below is `payload[0]` unless said otherwise. [NOT-TESTED] on the speaker - the inventory in
 * `plans/05_epic04_phase1_connection.md` flips row by row from the debug log.
 */
object Blast2 {
    /** The Bluetooth names their app matches (`MainNewActivity.java:1074`, `DeviceConstant.java:62`), compared ignoring case. */
    const val NAME = "Tribit StormBox Blast 2"

    /** Classic SPP - the control channel of Blast 2 (`BtClient.java:590`), not the 0CF12D31 UUID of older notes. */
    const val SPP_UUID = "00001101-0000-1000-8000-00805f9b34fb"

    const val CMD_VERSION = 1
    const val CMD_PLAY = 2
    const val CMD_BATTERY = 6
    const val CMD_VOLUME_SET = 13
    const val CMD_VOLUME_GET = 18
    const val CMD_PLAY_STATE = 19

    /**
     * Sent by the speaker unasked when its volume changes - by our command or by its own buttons; payload[0] = 0..31.
     * Their app handles it as command 18 (smali `ViewModelDeviceBts.smali:1922` packed-switch 0x52, `researches/11` §3.6);
     * observed on the A51 2026-10-16 16:17:51: `EA 05 54 0A` after a volume set to 10.
     */
    const val CMD_VOLUME_NOTICE = 84

    /** Volume steps of the speaker: their slider `setMax(31)` (`Bts56ControlActivity.java:1269`). */
    const val VOLUME_MAX = 31

    /** Payload of CMD_PLAY: 4 = play, 3 = pause (INFERRED from their buttons, §3.3), 1 = previous, 2 = next. */
    const val PLAY = 4
    const val PAUSE = 3
    const val PREVIOUS = 1
    const val NEXT = 2

    /** Gaps between the startup queries, as their app sends them (§3.4: 100/100/50 ms). */
    const val STARTUP_GAP_MS = 100L

    fun isBlast2(name: String?) = name != null && name.equals(NAME, ignoreCase = true)

    fun queryVersion() = Packet.encode(CMD_VERSION)
    fun queryBattery() = Packet.encode(CMD_BATTERY, byteArrayOf(1))
    fun queryVolume() = Packet.encode(CMD_VOLUME_GET)
    fun queryPlayState() = Packet.encode(CMD_PLAY_STATE)
    fun setVolume(v: Int) = Packet.encode(CMD_VOLUME_SET, byteArrayOf(v.coerceIn(0, VOLUME_MAX).toByte()))
    fun play(action: Int) = Packet.encode(CMD_PLAY, byteArrayOf(action.toByte()))

    /** Startup queries in their order (§3.4): version, then battery, then volume and play state for our card. */
    fun startup() = listOf(queryVersion(), queryBattery(), queryVolume(), queryPlayState())

    /**
     * Firmware version text as their app shows it: «p1/p2/p3_p0÷10» (`Bts52Util.payloadToString`, command 1). The
     * division is a DOUBLE one in smali (`Bts52Util.smali:2191`), jadx prints an integer one - we follow smali.
     */
    fun version(f: Frame): String? =
        if (f.cmd != CMD_VERSION || f.payload.size < 4) null
        else "${f.u8(1)}/${f.u8(2)}/${f.u8(3)}_${f.u8(0) / 10.0}"
}

/** What the speaker told us so far; null = not answered yet (a screen never shows a default as the speaker's state, EXP-0009). */
data class SpeakerState(
    val version: String? = null,
    val battery: Int? = null,
    val volume: Int? = null,
    val playing: Boolean? = null,
) {
    /** Applies one reply frame; unknown commands leave the state as it was. */
    fun apply(f: Frame): SpeakerState = when (f.cmd) {
        Blast2.CMD_VERSION -> Blast2.version(f)?.let { copy(version = it) } ?: this
        Blast2.CMD_BATTERY -> f.u8(0).takeIf { it in 0..100 }?.let { copy(battery = it) } ?: this
        Blast2.CMD_VOLUME_GET, Blast2.CMD_VOLUME_NOTICE -> f.u8(0).takeIf { it in 0..Blast2.VOLUME_MAX }?.let { copy(volume = it) } ?: this
        // Their reading of command 2: payload 3 = paused, anything else = playing (`ViewModelDeviceBts.bts56Read`).
        Blast2.CMD_PLAY -> if (f.u8(0) < 0) this else copy(playing = f.u8(0) != Blast2.PAUSE)
        // Command 19 carries the raw state; their mapping of its values is not in the code we read - logged, not shown.
        else -> this
    }
}
