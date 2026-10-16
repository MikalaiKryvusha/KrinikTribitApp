package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Byte-exact EQ sends and state parsing (`researches/11` §3.6). Sums are computed independently of the codec: by the
 * rule (low byte of the sum of the bytes before it), summing the expected bytes in the test itself.
 */
class EqTest {
    /** Builds the expected packet text from head bytes by the rule, without Packet.encode. */
    private fun expected(vararg b: Int): String {
        val sum = b.sum() and 0xFF
        return (b.toList() + sum).joinToString(" ") { "%02X".format(it) }
    }

    @Test fun `rock preset`() {
        // EA, len 15 (11 payload + 4), cmd 4, id 5, gains 22,18,8,4,6,18,24,20,14,12
        assertEquals(
            expected(0xEA, 0x0F, 0x04, 0x05, 22, 18, 8, 4, 6, 18, 24, 20, 14, 12),
            Eq.setPreset(Eq.Preset.ROCK).hex(),
        )
        assertTrue(Eq.setPreset(Eq.Preset.ROCK).hex().startsWith("EA 0F 04 05 16 12 08 04 06 12 18 14 0E 0C"))
    }

    @Test fun `every preset has ten bands within the wire range`() {
        for (p in Eq.Preset.entries) {
            assertEquals(p.name, Eq.BANDS, p.wire.size)
            assertTrue(p.name, p.wire.all { it in 0..24 })
        }
    }

    @Test fun `custom flat on new firmware`() {
        assertEquals(expected(0xEA, 0x0E, 0x0B, *IntArray(10) { 12 }), Eq.setCustom(List(10) { 0 }, true).hex())
    }

    @Test fun `custom gains are offset and clamped`() {
        val db = listOf(-12, -6, 0, 3, 6, 6, 0, 0, 12, 20)
        // new: dB + 12, 20 clamped to 12 -> 24
        assertEquals(expected(0xEA, 0x0E, 0x0B, 0, 6, 12, 15, 18, 18, 12, 12, 24, 24), Eq.setCustom(db, true).hex())
        // old: dB + 8, clamped to ±8
        assertEquals(expected(0xEA, 0x0E, 0x0B, 0, 2, 8, 11, 14, 14, 8, 8, 16, 16), Eq.setCustom(db, false).hex())
    }

    @Test fun `state reply round trip`() {
        val wire = listOf(7) + listOf(0, 6, 12, 15, 18, 18, 12, 12, 24, 24)
        val f = Framer().feed(Packet.encode(Eq.CMD_STATE, wire.map { it.toByte() }.toByteArray())).single()
        val s = Eq.state(f, newFirmware = true)!!
        assertTrue(s.custom)
        assertEquals(listOf(-12, -6, 0, 3, 6, 6, 0, 0, 12, 12), s.db)
    }

    @Test fun `an unknown preset id has unknown bands, never the zeros`() {
        // judge pass D1: id 12 is outside the table; the speaker sends zero gains for presets
        val f = Framer().feed(Packet.encode(Eq.CMD_STATE, byteArrayOf(12) + ByteArray(10))).single()
        val s = Eq.state(f, newFirmware = true)!!
        assertNull(s.db)
        assertNull(s.preset)
    }

    @Test fun `blast traditional is read as 9 and as 8`() {
        assertEquals(Eq.Preset.BLAST, Eq.Preset.byId(9))
        assertEquals(Eq.Preset.BLAST, Eq.Preset.byId(8))
        assertNull(Eq.Preset.byId(7))
    }

    @Test fun `dsp version of our speaker`() {
        // Captured on the A51 2026-10-16 16:17:30: EA 05 58 62 A9 -> 98 -> 10098, «new» firmware.
        val f = Framer().feed(byteArrayOf(0xEA.toByte(), 0x05, 0x58, 0x62, 0xA9.toByte())).single()
        assertEquals(10098, Eq.dspVersion(f))
        assertTrue(Eq.dspVersion(f)!! > Eq.DSP_NEW)
    }
}
