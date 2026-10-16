package com.kriniks.tribit.link

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.util.Log
import com.kriniks.tribit.BuildConfig
import com.kriniks.tribit.protocol.Blast2
import com.kriniks.tribit.protocol.Frame
import com.kriniks.tribit.protocol.Framer
import com.kriniks.tribit.protocol.hex
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.Closeable
import java.util.UUID

/**
 * The control channel to one speaker: a Classic SPP socket (`researches/11` §3.1). All socket I/O runs on
 * Dispatchers.IO - `connect()` blocks up to ≈ 12 s (developer.android.com, connect-bluetooth-devices). The reader
 * cuts the stream into packets with [Framer] (their app took one read() as one packet). In the debug build every
 * packet both ways goes to logcat under the tag [TAG]: the frames from the real speaker are the source of the protocol
 * tests (`plans/05`, inventory). Callers hold BLUETOOTH_CONNECT before creating a link. [NOT-TESTED]
 */
@SuppressLint("MissingPermission")
class SpeakerLink(private val adapter: BluetoothAdapter, private val device: BluetoothDevice) : Closeable {
    private var socket: BluetoothSocket? = null
    private val writeLock = Mutex()

    /** Opens the socket. Throws IOException when the speaker is off, out of range, or its SPP is held by another app. */
    suspend fun open() = withContext(Dispatchers.IO) {
        // Discovery slows a connect down; but cancelling it needs BLUETOOTH_SCAN, which we do not ask for (we never
        // start discovery ourselves) - so the call is best-effort.
        try { adapter.cancelDiscovery() } catch (_: SecurityException) {}
        val s = device.createRfcommSocketToServiceRecord(UUID.fromString(Blast2.SPP_UUID))
        socket = s
        log("connecting ${device.address}")
        s.connect()
        log("connected")
    }

    /** Sends one packet; writes from several coroutines never interleave. */
    suspend fun send(packet: ByteArray) = withContext(Dispatchers.IO) {
        writeLock.withLock {
            val out = socket?.outputStream ?: throw java.io.IOException("not open")
            out.write(packet)
            out.flush()
            log("TX ${packet.hex()}")
        }
    }

    /** Reads until the socket closes; every complete packet goes to [onFrame]. Returns normally on a closed stream. */
    suspend fun readLoop(onFrame: (Frame) -> Unit) = withContext(Dispatchers.IO) {
        val input = socket?.inputStream ?: return@withContext
        val framer = Framer()
        val buf = ByteArray(READ_BUFFER)
        while (true) {
            val n = input.read(buf)
            if (n < 0) break
            log("RX ${buf.copyOf(n).hex()}")
            for (f in framer.feed(buf, n)) {
                if (!f.sumOk) log("RX checksum mismatch: $f")
                onFrame(f)
            }
        }
    }

    /** Closes the socket once; a second call (stop() and the connect coroutine's finally) does nothing. */
    override fun close() {
        val s = socket ?: return
        try { s.close() } catch (_: java.io.IOException) {}
        socket = null
        log("closed")
    }

    private fun log(msg: String) {
        if (BuildConfig.DEBUG) Log.d(TAG, msg)
    }

    companion object {
        const val TAG = "KT.Link"

        /** One read takes up to this many bytes - their ReadThread used the same 1 024 (`ReadThread.java:36`). */
        private const val READ_BUFFER = 1024
    }
}
