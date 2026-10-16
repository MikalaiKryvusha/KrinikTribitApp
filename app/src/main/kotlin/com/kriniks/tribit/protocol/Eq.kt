package com.kriniks.tribit.protocol

/**
 * The equalizer of Tribit StormBox Blast 2, read from their code (`researches/11_own_app.md` §3.6): ten bands, a preset is
 * sent as cmd 4 [id, 10 gains], the custom EQ as cmd 11 [10 gains], the state comes back as 21 (asked) or 82 (unasked)
 * [id, 10 gains]. A gain on the wire is dB + 12 on «new» firmware (our speaker: DSP 98 → 10098 > 10074) and dB + 8 on
 * old. Pure Kotlin, tested on the JVM (`EqTest`). [NOT-TESTED] on the speaker.
 */
object Eq {
    const val CMD_PRESET = 4
    const val CMD_CUSTOM = 11
    const val CMD_STATE = 21
    const val CMD_STATE_NOTICE = 82

    /** Unsolicited DSP version: payload[0] + 10000 (`Bts56ControlActivity.java:520–524`). */
    const val CMD_DSP_VERSION = 88
    const val DSP_BASE = 10000

    /** DSP above this → «new» firmware: ±12 dB bands, wire = dB + 12 (`Bts56ControlActivity.java:527`). */
    const val DSP_NEW = 10074

    const val BANDS = 10

    /** Band labels, low to high (`Bts56Constant.java:45`). */
    val BAND_LABELS = listOf("40", "62", "125", "250", "500", "1K", "2K", "4K", "8K", "16K")

    /** The preset id of the custom EQ in the state reply (`ViewModelDeviceBts.java:1112`). */
    const val CUSTOM_ID = 7

    /**
     * Presets of «new» firmware: id sent, name, gains on the wire (`Bts56Constant.java` :56–77, `EqUtil.java:995–1176`).
     * Blast traditional is sent as 8 and read back as 9 by their `PageUtil.bts56Eq` - the speaker's reply decides
     * (plans/06, risk (а)); both ids map to it.
     */
    enum class Preset(val id: Int, val label: String, val wire: List<Int>) {
        SIGNATURE(1, "TRIBIT Signature", List(BANDS) { 12 }),
        XBASS(2, "XBass", listOf(18, 24, 16, 12, 12, 12, 12, 12, 12, 12)),
        AUDIOBOOK(3, "Audiobook", listOf(4, 8, 12, 18, 12, 22, 14, 4, 8, 0)),
        CLASSICAL(4, "Classical", List(BANDS) { 12 }),
        ROCK(5, "Rock", listOf(22, 18, 8, 4, 6, 18, 24, 20, 14, 12)),
        JAZZ(6, "Jazz", listOf(8, 18, 20, 12, 14, 16, 12, 20, 22, 18)),
        BLAST(8, "Blast traditional", listOf(6, 8, 18, 12, 8, 20, 22, 18, 20, 16)),
        LIVE(10, "Live", List(BANDS) { 12 }),
        PODCAST(11, "Podcast", List(BANDS) { 12 });

        companion object {
            /** The preset the speaker reports by [id]; 9 is Blast traditional on the read side (`PageUtil.java:280–329`). */
            fun byId(id: Int): Preset? = if (id == 9) BLAST else entries.firstOrNull { it.id == id }
        }
    }

    /** Wire offset of a gain: 12 on «new» firmware, 8 on old (`EqUtil.java:3240–3243`). */
    fun offset(newFirmware: Boolean) = if (newFirmware) 12 else 8

    fun setPreset(p: Preset): ByteArray =
        Packet.encode(CMD_PRESET, (listOf(p.id) + p.wire).map { it.toByte() }.toByteArray())

    /** The custom EQ: exactly 10 gain bytes, no id (`Bts52Util.customEqSet1`, B:138–141); [db] clamped to ±offset. */
    fun setCustom(db: List<Int>, newFirmware: Boolean): ByteArray {
        require(db.size == BANDS) { "need $BANDS bands, got ${db.size}" }
        val off = offset(newFirmware)
        return Packet.encode(CMD_CUSTOM, db.map { (it.coerceIn(-off, off) + off).toByte() }.toByteArray())
    }

    fun queryState() = Packet.encode(CMD_STATE)

    /** The EQ the speaker reports: preset id and the ten band gains in dB. */
    data class State(val id: Int, val db: List<Int>) {
        val preset: Preset? get() = Preset.byId(id)
        val custom: Boolean get() = id == CUSTOM_ID
    }

    /**
     * Parses 21 / 82 [id, 10 gains]; null for another command or a short payload. The speaker reports band gains only
     * for the custom EQ: for a preset it sends zeros (A51 2026-10-16 16:48:43, after Rock: `EA 0F 15 05 00×10 13`), so a
     * preset's bands come from the preset table - as in their app, which decodes gains for id 7 only
     * (`ViewModelDeviceBts.java:1112`).
     */
    fun state(f: Frame, newFirmware: Boolean): State? {
        if ((f.cmd != CMD_STATE && f.cmd != CMD_STATE_NOTICE) || f.payload.size < 1 + BANDS) return null
        val off = offset(newFirmware)
        val id = f.u8(0)
        val preset = if (id == CUSTOM_ID) null else Preset.byId(id)
        val wire = preset?.wire ?: List(BANDS) { f.u8(1 + it) }
        return State(id, wire.map { it - off })
    }

    /** The DSP version from 88, or null. */
    fun dspVersion(f: Frame): Int? = if (f.cmd == CMD_DSP_VERSION && f.payload.isNotEmpty()) DSP_BASE + f.u8(0) else null
}
