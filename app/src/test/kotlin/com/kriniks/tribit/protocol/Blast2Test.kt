package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Byte-exact sends and reply parsing of the Blast 2 commands of phase 1 (`researches/11` §3.3). Expected bytes are
 * computed by hand: len = payload + 4, sum = low byte of EA + len + cmd + payload.
 */
class Blast2Test {
    private fun reply(cmd: Int, vararg payload: Int) =
        Framer().feed(Packet.encode(cmd, ByteArray(payload.size) { payload[it].toByte() })).single()

    @Test fun `sends`() {
        assertEquals("EA 05 01 00 F0", Blast2.queryVersion().hex())   // EA+05+01+00 = F0
        assertEquals("EA 05 06 01 F6", Blast2.queryBattery().hex())   // EA+05+06+01 = F6
        assertEquals("EA 05 12 00 01", Blast2.queryVolume().hex())    // EA+05+12+00 = 101 -> 01 (researches/11 §3.2)
        assertEquals("EA 05 13 00 02", Blast2.queryPlayState().hex()) // EA+05+13+00 = 102 -> 02
        assertEquals("EA 05 02 04 F5", Blast2.play(Blast2.PLAY).hex()) // EA+05+02+04 = F5
    }

    @Test fun `volume is clamped to the speaker range`() {
        assertEquals("EA 05 0D 1F 1B", Blast2.setVolume(99).hex())    // 31 = 1F; 234+5+13+31 = 283 = 11B -> 1B
        assertEquals("EA 05 0D 00 FC", Blast2.setVolume(-3).hex())    // 234+5+13+0 = 252 = FC
    }

    @Test fun `name matches both spellings`() {
        assertTrue(Blast2.isBlast2("Tribit StormBox Blast 2"))
        assertTrue(Blast2.isBlast2("TRIBIT StormBox Blast 2"))
        assertFalse(Blast2.isBlast2("Tribit StormBox Blast"))
        assertFalse(Blast2.isBlast2(null))
    }

    @Test fun `state from replies`() {
        var s = SpeakerState()
        s = s.apply(reply(Blast2.CMD_BATTERY, 87))
        s = s.apply(reply(Blast2.CMD_VOLUME_GET, 12))
        s = s.apply(reply(Blast2.CMD_VERSION, 25, 1, 2, 3))
        s = s.apply(reply(Blast2.CMD_PLAY, Blast2.PAUSE))
        assertEquals(SpeakerState(version = "1/2/3_2.5", battery = 87, volume = 12, playing = false), s)
    }

    @Test fun `out of range values are not taken as state`() {
        val s = SpeakerState().apply(reply(Blast2.CMD_BATTERY, 200)).apply(reply(Blast2.CMD_VOLUME_GET, 40))
        assertNull(s.battery)
        assertNull(s.volume)
    }
}
