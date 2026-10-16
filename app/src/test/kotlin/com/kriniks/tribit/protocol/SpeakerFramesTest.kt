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
        // play state 2 at rest = paused (mapped since the play/pause run 16:18); 88 → DSP 10098, «new» firmware
        assertEquals(SpeakerState(version = "26/7/24_11.4", battery = 30, volume = 9, playing = false, dsp = 10098), s)
        assertEquals(true, s.newFirmware)
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

    @Test fun `eq state of the custom flat and of rock`() {
        // At connect 16:47:15: custom (7), all bands wire 12 = 0 dB.
        val custom = Eq.state(Framer().feed(hex("EA 0F 15 07 0C 0C 0C 0C 0C 0C 0C 0C 0C 0C 8D")).single(), true)!!
        assertTrue(custom.custom)
        assertEquals(List(10) { 0 }, custom.db)
        // After Rock 16:48:43: the speaker sends id 5 with zero gains - the bands come from the Rock table, never -12 dB.
        val rock = Eq.state(Framer().feed(hex("EA 0F 15 05 00 00 00 00 00 00 00 00 00 00 13")).single(), true)!!
        assertEquals(Eq.Preset.ROCK, rock.preset)
        assertEquals(listOf(10, 6, -4, -8, -6, 6, 12, 8, 2, 0), rock.db)
    }

    @Test fun `light on - echo, notice and state in one read`() {
        // A51 16:53:18 after «1»: three packets in one read.
        val frames = Framer().feed(hex("EA 05 0C 01 FC EA 05 55 01 45 EA 05 14 01 04"))
        assertEquals(listOf(12, 85, 20), frames.map { it.cmd })
        assertEquals(1, frames.fold(SpeakerState()) { s, f -> s.apply(f) }.light)
    }

    @Test fun `settings read at connect`() {
        // A51 16:57:33-34, one read per answer.
        var s = SpeakerSettings()
        for (read in listOf("EA 05 10 01 00", "EA 06 0F FF FF FD", "EA 09 31 01 01 01 01 01 29", "EA 05 33 01 23",
            "EA 05 62 00 51", "EA 05 64 00 53")) for (f in Framer().feed(hex(read))) { assertTrue(f.sumOk); s = s.apply(f) }
        // auto shutdown 1 = OFF (0 means on); sleep FF FF = off; all voice prompts on; indicator on; mic, anti-howl off
        assertEquals(SpeakerSettings(false, 0, List(5) { true }, true, false, false), s)
    }

    @Test fun `echo of play and pause`() {
        val f = Framer()
        val play = f.feed(hex("EA 05 02 04 F5")).single()
        assertEquals(true, SpeakerState().apply(play).playing)
        val pause = f.feed(hex("EA 05 02 03 F4")).single()
        assertEquals(false, SpeakerState().apply(pause).playing)
    }
}
