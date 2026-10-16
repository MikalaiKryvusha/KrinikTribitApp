package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Byte-exact tests of the packet codec (`researches/11` §3.2) and of the stream framer - the guard against their app's
 * defect «one read() = one packet» (§3.1). Expected bytes are computed by hand from the rule: len = payload + 4,
 * sum = low byte of the sum of the bytes before it.
 */
class PacketTest {
    private fun bytes(vararg v: Int) = ByteArray(v.size) { v[it].toByte() }

    @Test fun `empty command carries one zero byte`() {
        // EA+05+01+00 = 0xF0
        assertEquals("EA 05 01 00 F0", Packet.encode(1).hex())
    }

    @Test fun `volume set 10`() {
        // one payload byte -> len 5; EA+05+0D+0A = 0x106 -> 06
        assertEquals("EA 05 0D 0A 06", Packet.encode(13, bytes(10)).hex())
    }

    @Test fun `framer cuts two packets out of one read`() {
        val f = Framer()
        val frames = f.feed(Packet.encode(6, bytes(1)) + Packet.encode(18))
        assertEquals(listOf(6, 18), frames.map { it.cmd })
        assertTrue(frames.all { it.sumOk })
    }

    @Test fun `framer joins a packet split across reads`() {
        val f = Framer()
        val p = Packet.encode(6, bytes(87))
        assertTrue(f.feed(p.copyOfRange(0, 3)).isEmpty())
        val frames = f.feed(p.copyOfRange(3, p.size))
        assertEquals(1, frames.size)
        assertEquals(87, frames[0].u8(0))
    }

    @Test fun `framer skips garbage before the head`() {
        val f = Framer()
        val frames = f.feed(bytes(0, 0, 0x13) + Packet.encode(18, bytes(20)))
        assertEquals(listOf(18), frames.map { it.cmd })
        assertEquals(20, frames[0].u8(0))
        assertEquals(3, f.skipped)
    }

    @Test fun `framer skips a false head with a too short len`() {
        val f = Framer()
        val frames = f.feed(bytes(0xEA, 0x02) + Packet.encode(6, bytes(50)))
        assertEquals(listOf(6), frames.map { it.cmd })
        assertEquals(50, frames[0].u8(0))
    }

    @Test fun `framer flags a wrong checksum and still delivers`() {
        val p = Packet.encode(6, bytes(50))
        p[p.size - 1] = (p[p.size - 1] + 1).toByte()
        val frames = Framer().feed(p)
        assertEquals(1, frames.size)
        assertFalse(frames[0].sumOk)
    }

    @Test fun `ten zero bytes are not a packet`() {
        // Their ReadThread injects 10 zeros as a fake «disconnected» packet (§3.1); for us it is noise.
        val f = Framer()
        assertTrue(f.feed(ByteArray(10)).isEmpty())
        assertEquals(10, f.skipped)
    }
}
