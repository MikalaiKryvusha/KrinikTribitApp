package com.kriniks.tribit.protocol

/**
 * Speaker settings of Tribit StormBox Blast 2 (`researches/11_own_app.md` §3.6, their `Bts56InfoActivity`, builders in
 * `Bts52Util.java:87–303`). Every «get» is the command with one 0x00 byte; the reply carries the same command. Factory
 * reset (7) and power off (50) are left out on purpose: on the stand they would cost the owner a trip to the speaker.
 * [NOT-TESTED] on the speaker.
 */
object Settings {
    /** Auto shutdown: set 3 [1 on / 2 off]; get 16 - its reply 0 means ON (`Bts56InfoActivity.java:1189`). */
    const val CMD_AUTO_OFF_SET = 3
    const val CMD_AUTO_OFF_GET = 16

    /** Sleep timer, the «new» form Blast 2 always uses: set 14 [hour, minute], off = [255, 255]; get 15. */
    const val CMD_SLEEP_SET = 14
    const val CMD_SLEEP_GET = 15
    const val SLEEP_OFF = 255

    /** Voice prompts: set 48 [5 × 1/0], get 49 → 5 bytes (`VoiceSetNewActivity.java`). */
    const val CMD_VOICE_SET = 48
    const val CMD_VOICE_GET = 49
    const val VOICE_FLAGS = 5

    /** Volume indicator (the light that shows the volume): set 52 [1/0], get 51. */
    const val CMD_INDICATOR_SET = 52
    const val CMD_INDICATOR_GET = 51

    /** Microphone boost: set 97, get 98; anti-howl: set 99, get 100 - shown only on «new» firmware. */
    const val CMD_MIC_SET = 97
    const val CMD_MIC_GET = 98
    const val CMD_HOWL_SET = 99
    const val CMD_HOWL_GET = 100

    private const val ON = 1
    private const val OFF = 0

    fun setAutoOff(on: Boolean) = Packet.encode(CMD_AUTO_OFF_SET, byteArrayOf(if (on) 1 else 2))
    fun setSleep(minutes: Int): ByteArray {
        val bytes = if (minutes <= 0) byteArrayOf(SLEEP_OFF.toByte(), SLEEP_OFF.toByte())
        else byteArrayOf((minutes / 60).toByte(), (minutes % 60).toByte())
        return Packet.encode(CMD_SLEEP_SET, bytes)
    }
    fun setVoice(flags: List<Boolean>): ByteArray {
        require(flags.size == VOICE_FLAGS)
        return Packet.encode(CMD_VOICE_SET, flags.map { (if (it) ON else OFF).toByte() }.toByteArray())
    }
    fun setIndicator(on: Boolean) = Packet.encode(CMD_INDICATOR_SET, byteArrayOf((if (on) ON else OFF).toByte()))
    fun setMic(on: Boolean) = Packet.encode(CMD_MIC_SET, byteArrayOf((if (on) ON else OFF).toByte()))
    fun setHowl(on: Boolean) = Packet.encode(CMD_HOWL_SET, byteArrayOf((if (on) ON else OFF).toByte()))

    /** The «get» queries read at connect - each answered by the same command. */
    val QUERIES = listOf(CMD_AUTO_OFF_GET, CMD_SLEEP_GET, CMD_VOICE_GET, CMD_INDICATOR_GET, CMD_MIC_GET, CMD_HOWL_GET)
    fun query(cmd: Int) = Packet.encode(cmd)
}

/** The speaker's settings as it reported them; null = not answered yet. */
data class SpeakerSettings(
    val autoOff: Boolean? = null,
    /** Sleep timer in minutes, 0 = off. */
    val sleepMinutes: Int? = null,
    val voice: List<Boolean>? = null,
    val indicator: Boolean? = null,
    val mic: Boolean? = null,
    val howl: Boolean? = null,
) {
    fun apply(f: Frame): SpeakerSettings = when (f.cmd) {
        Settings.CMD_AUTO_OFF_GET -> if (f.u8(0) < 0) this else copy(autoOff = f.u8(0) == 0)
        Settings.CMD_SLEEP_GET -> {
            val h = f.u8(0)
            val m = f.u8(1)
            when {
                h < 0 -> this
                h == Settings.SLEEP_OFF || m < 0 || m == Settings.SLEEP_OFF -> copy(sleepMinutes = 0)
                else -> copy(sleepMinutes = h * 60 + m)
            }
        }
        Settings.CMD_VOICE_GET -> if (f.payload.size < Settings.VOICE_FLAGS) this
            else copy(voice = List(Settings.VOICE_FLAGS) { f.u8(it) == 1 })
        Settings.CMD_INDICATOR_GET -> if (f.u8(0) < 0) this else copy(indicator = f.u8(0) == 1)
        Settings.CMD_MIC_GET -> if (f.u8(0) < 0) this else copy(mic = f.u8(0) == 1)
        Settings.CMD_HOWL_GET -> if (f.u8(0) < 0) this else copy(howl = f.u8(0) == 1)
        else -> this
    }
}
