package com.kriniks.tribit.link

import android.Manifest
import android.annotation.SuppressLint
import android.app.Application
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.kriniks.tribit.protocol.Blast2
import com.kriniks.tribit.protocol.SpeakerState
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** Where the way to the speaker stands - each value is one face of the home card. */
sealed interface Link {
    /** «Устройства поблизости» (BLUETOOTH_CONNECT) not granted yet. */
    data object NoPermission : Link
    data object BluetoothOff : Link
    /** No bonded Blast 2: the user pairs it in Android's Bluetooth settings (needed for the sound anyway). */
    data object NotPaired : Link
    data class Connecting(val name: String) : Link
    data class Connected(val name: String) : Link
    /** The socket did not open or broke: speaker off, out of range, or its channel held by another app. */
    data class Failed(val name: String) : Link
}

/**
 * The one owner of the speaker connection for the UI (KARTUN's model: state in one ViewModel, `researches/11` §4a).
 * Finds the bonded Blast 2 (no scan, so no location on any Android - GOAL.md success line 2), opens [SpeakerLink],
 * sends the startup queries with their gaps (§3.4), and folds every reply into [speaker]. The socket closes when the
 * ViewModel is cleared (the activity finishes). [NOT-TESTED]
 */
@SuppressLint("MissingPermission")
class SpeakerViewModel(app: Application) : AndroidViewModel(app) {
    private val _link = MutableStateFlow<Link>(Link.NoPermission)
    val link: StateFlow<Link> = _link

    private val _speaker = MutableStateFlow(SpeakerState())
    val speaker: StateFlow<SpeakerState> = _speaker

    private var conn: SpeakerLink? = null
    private var job: Job? = null

    private fun hasPermission() = ContextCompat.checkSelfPermission(
        getApplication(), Manifest.permission.BLUETOOTH_CONNECT,
    ) == PackageManager.PERMISSION_GRANTED

    /** The adapter and the bonded Blast 2 the link opens to. */
    private class Found(val adapter: BluetoothAdapter, val device: BluetoothDevice)

    /**
     * Finds the bonded Blast 2, or sets the [Link] state that stops the way to it and returns null. Runs on
     * Dispatchers.IO: the first `getSystemService(BluetoothManager)` of a process reads the disk - StrictMode on the A51
     * 2026-10-16 16:27 measured 114 and 117 ms on the main thread - and `bondedDevices` is a binder call.
     */
    private fun lookUp(): Found? {
        if (!hasPermission()) { _link.value = Link.NoPermission; return null }
        val adapter = getApplication<Application>().getSystemService(BluetoothManager::class.java)?.adapter
        if (adapter == null || !adapter.isEnabled) { _link.value = Link.BluetoothOff; return null }
        val device = adapter.bondedDevices.orEmpty().firstOrNull { Blast2.isBlast2(it.name) }
        if (device == null) { _link.value = Link.NotPaired; return null }
        return Found(adapter, device)
    }

    /** (Re)starts the way to the speaker; does nothing while a connection is up or being made. */
    fun start() {
        if (job?.isActive == true) return
        job = viewModelScope.launch {
            val found = withContext(Dispatchers.IO) { lookUp() } ?: return@launch
            val adapter = found.adapter
            val device = found.device
            val name = device.name ?: Blast2.NAME
            _link.value = Link.Connecting(name)
            _speaker.value = SpeakerState()
            val c = SpeakerLink(adapter, device)
            conn = c
            try {
                c.open()
                _link.value = Link.Connected(name)
                launch {
                    for (q in Blast2.startup()) { c.send(q); delay(Blast2.STARTUP_GAP_MS) }
                }
                c.readLoop { f -> _speaker.update { it.apply(f) } }
                _link.value = Link.Failed(name)
            } catch (e: CancellationException) {
                throw e
            } catch (_: Exception) {
                _link.value = Link.Failed(name)
            } finally {
                c.close()
                if (conn === c) conn = null
            }
        }
    }

    /** Sets the volume 0..31; the speaker's own answer to a re-query is what the slider then shows. */
    fun setVolume(v: Int) = sendThen(Blast2.setVolume(v), Blast2.queryVolume())

    /**
     * Play/pause by the last state the SPEAKER reported (unknown → play); the screen is not flipped ahead of its answer
     * (EXP-0009). The state query after it is logged - its reply values are the inventory's open row.
     */
    fun togglePlay() {
        val playing = _speaker.value.playing ?: false
        sendThen(Blast2.play(if (playing) Blast2.PAUSE else Blast2.PLAY), Blast2.queryPlayState())
    }

    private fun sendThen(p: ByteArray, query: ByteArray) {
        val c = conn ?: return
        viewModelScope.launch {
            try { c.send(p); delay(Blast2.STARTUP_GAP_MS); c.send(query) } catch (_: Exception) {}
        }
    }

    /**
     * Closes the link when the app leaves the screen. Since Android 12 «Back» on the root screen only moves the app to
     * the background (the A51 run 2026-10-16 16:18: no «closed» line after Back), so waiting for onCleared kept the
     * speaker's channel busy for every other app. Closing the socket wakes the blocked read; [start] opens a new link.
     * [NOT-TESTED]
     */
    fun stop() {
        job?.cancel()
        job = null
        conn?.close()
    }

    override fun onCleared() = stop()
}
