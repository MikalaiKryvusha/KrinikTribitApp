package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/** Byte-exact settings sends and reply parsing (`researches/11` §3.6); sums computed in the test by the rule. */
class SettingsTest {
    private fun expected(vararg b: Int) = (b.toList() + (b.sum() and 0xFF)).joinToString(" ") { "%02X".format(it) }
    private fun reply(cmd: Int, vararg p: Int) =
        Framer().feed(Packet.encode(cmd, ByteArray(p.size) { p[it].toByte() })).single()

    @Test fun `sends`() {
        assertEquals(expected(0xEA, 5, 3, 1), Settings.setAutoOff(true).hex())
        assertEquals(expected(0xEA, 5, 3, 2), Settings.setAutoOff(false).hex())
        assertEquals(expected(0xEA, 6, 14, 1, 30), Settings.setSleep(90).hex())
        assertEquals(expected(0xEA, 6, 14, 255, 255), Settings.setSleep(0).hex())
        assertEquals(expected(0xEA, 9, 48, 1, 0, 1, 1, 0), Settings.setVoice(listOf(true, false, true, true, false)).hex())
        assertEquals(expected(0xEA, 5, 52, 1), Settings.setIndicator(true).hex())
        assertEquals(expected(0xEA, 5, 97, 0), Settings.setMic(false).hex())
        assertEquals(expected(0xEA, 5, 99, 1), Settings.setHowl(true).hex())
        assertEquals(expected(0xEA, 5, 16, 0), Settings.query(Settings.CMD_AUTO_OFF_GET).hex())
    }

    @Test fun `auto shutdown reply 0 means on`() {
        assertEquals(true, SpeakerSettings().apply(reply(16, 0)).autoOff)
        assertEquals(false, SpeakerSettings().apply(reply(16, 1)).autoOff)
    }

    @Test fun `sleep timer`() {
        assertEquals(90, SpeakerSettings().apply(reply(15, 1, 30)).sleepMinutes)
        assertEquals(0, SpeakerSettings().apply(reply(15, 255, 255)).sleepMinutes)
    }

    @Test fun `voice flags and switches`() {
        val s = SpeakerSettings().apply(reply(49, 1, 0, 1, 1, 0)).apply(reply(51, 1)).apply(reply(98, 0)).apply(reply(100, 1))
        assertEquals(listOf(true, false, true, true, false), s.voice)
        assertEquals(true, s.indicator)
        assertEquals(false, s.mic)
        assertEquals(true, s.howl)
        assertNull(SpeakerSettings().apply(reply(49, 1)).voice)
    }
}
