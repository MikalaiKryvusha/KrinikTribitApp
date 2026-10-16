package com.kriniks.tribit.protocol

/**
 * The Tribit speaker packet, read from their code (`researches/11_own_app.md` §3.2):
 *
 *     EA <len> <cmd> <payload…> <sum>
 *
 * `len` counts the WHOLE packet (payload + 4), `sum` is the low byte of the sum of every byte before it. A command
 * without payload still carries one 0x00 byte (len = 5). Pure Kotlin, no Android: tested byte-exact on the JVM
 * (`PacketTest`). [NOT-TESTED]
 */
object Packet {
    const val HEAD = 0xEA

    /** Bytes around the payload: head, len, cmd, sum. */
    const val OVERHEAD = 4

    /** The shortest packet: overhead + the one 0x00 byte an empty command carries. */
    const val MIN_LEN = OVERHEAD + 1

    /** Builds the packet for [cmd]; an empty [payload] becomes the single 0x00 byte their app sends. */
    fun encode(cmd: Int, payload: ByteArray = ByteArray(0)): ByteArray {
        val body = if (payload.isEmpty()) byteArrayOf(0) else payload
        val out = ByteArray(body.size + OVERHEAD)
        out[0] = HEAD.toByte()
        out[1] = out.size.toByte()
        out[2] = cmd.toByte()
        body.copyInto(out, 3)
        out[out.size - 1] = sum(out, out.size - 1).toByte()
        return out
    }

    /** Low byte of the sum of the first [count] bytes. */
    fun sum(bytes: ByteArray, count: Int): Int {
        var s = 0
        for (i in 0 until count) s += bytes[i].toInt() and 0xFF
        return s and 0xFF
    }
}

/** One packet the speaker sent: the command, its payload, and whether its checksum matched the rule above. */
class Frame(val cmd: Int, val payload: ByteArray, val sumOk: Boolean) {
    /** The payload byte at [i] as 0..255, or -1 when the payload is shorter. */
    fun u8(i: Int): Int = if (i < payload.size) payload[i].toInt() and 0xFF else -1

    override fun toString() = "cmd=$cmd payload=${payload.hex()}" + if (sumOk) "" else " SUM-MISMATCH"
}

/**
 * Cuts the byte stream of the SPP socket into packets by their `len` byte. Their app took one `read()` as one packet,
 * so two replies in one read were parsed as one (`researches/11` §3.1); here a read may hold several packets or a part
 * of one. Bytes before a 0xEA are skipped (resync). The checksum is checked and FLAGGED, not enforced: their app never
 * checked it, and the rule is confirmed only by frames from the real speaker (plans/05, risk (а)). [NOT-TESTED]
 */
class Framer {
    private var buf = ByteArray(0)

    /** Number of bytes skipped while looking for a packet head - shown in the debug log. */
    var skipped = 0
        private set

    /** Feeds [count] bytes of [data]; returns every packet completed by them, in order. */
    fun feed(data: ByteArray, count: Int = data.size): List<Frame> {
        buf += data.copyOf(count)
        val frames = mutableListOf<Frame>()
        while (true) {
            val head = buf.indexOfFirst { (it.toInt() and 0xFF) == Packet.HEAD }
            if (head < 0) {
                skipped += buf.size; buf = ByteArray(0); break
            }
            if (head > 0) {
                skipped += head; buf = buf.copyOfRange(head, buf.size)
            }
            if (buf.size < 2) break
            val len = buf[1].toInt() and 0xFF
            if (len < Packet.MIN_LEN) {
                // Not a real head: an 0xEA inside garbage. Drop it and look further.
                skipped += 1; buf = buf.copyOfRange(1, buf.size); continue
            }
            if (buf.size < len) break
            val sumOk = Packet.sum(buf, len - 1) == (buf[len - 1].toInt() and 0xFF)
            frames += Frame(buf[2].toInt() and 0xFF, buf.copyOfRange(3, len - 1), sumOk)
            buf = buf.copyOfRange(len, buf.size)
        }
        return frames
    }
}

/** «EA 05 01 00 F0» - how packets read in the debug log and in the tests. */
fun ByteArray.hex(): String = joinToString(" ") { "%02X".format(it.toInt() and 0xFF) }
