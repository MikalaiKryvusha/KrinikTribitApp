package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Frames captured from the real StormBox Blast 2 on the A51 (debug log `KT.Link`, 2026-10-16 16:17–16:18 +03:00,
 * `testcases/reports/2026-10-16_own_app_connection.md`). Each `read()` is fed as it arrived, so these tests pin the
 * framing and parsing against what the speaker actually sends.
 */
class SpeakerFramesTest {
    private fun hex(s: String) = s.split(" ").map { it.toInt(16).toByte() }.toByteArray()

    @Test fun `startup answers`() {
        val f = Framer()
        var s = SpeakerState()
        for (read in listOf(
            "EA 08 01 72 1A 07 18 9E", // version
            "EA 05 58 62 A9",          // unsolicited 88: DSP version 98
            "EA 05 06 1E 13",          // battery 30 %
            "EA 05 12 09 0A",          // volume 9
            "EA 05 13 02 04",          // play state 2
        )) for (fr in f.feed(hex(read))) { assertTrue(fr.toString(), fr.sumOk); s = s.apply(fr) }
        assertEquals(SpeakerState(version = "26/7/24_11.4", battery = 30, volume = 9), s)
        assertEquals(0, f.skipped)
    }

    @Test fun `echo of volume set and the volume notice arrive in one read`() {
        // Their app parsed this read as ONE packet (researches/11 §3.1); here it is two.
        val frames = Framer().feed(hex("EA 05 0D 0A 06 EA 05 54 0A 4D"))
        assertEquals(listOf(13, 84), frames.map { it.cmd })
        assertEquals(listOf(10, 10), frames.map { it.u8(0) })
        assertTrue(frames.all { it.sumOk })
        // The notice alone moves the volume - the speaker's own buttons send it too (researches/11 §3.6).
        assertEquals(10, SpeakerState(volume = 9).apply(frames[1]).volume)
    }

    @Test fun `echo of play and pause`() {
        val f = Framer()
        val play = f.feed(hex("EA 05 02 04 F5")).single()
        assertEquals(true, SpeakerState().apply(play).playing)
        val pause = f.feed(hex("EA 05 02 03 F4")).single()
        assertEquals(false, SpeakerState().apply(pause).playing)
    }
}
