package com.kriniks.tribit.link

import android.Manifest
import android.annotation.SuppressLint
import android.app.Application
import android.bluetooth.BluetoothA2dp
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.util.Log
import androidx.core.content.ContextCompat
import androidx.core.content.IntentCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.kriniks.tribit.BuildConfig
import com.kriniks.tribit.protocol.Blast2
import com.kriniks.tribit.protocol.SpeakerState
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlin.coroutines.resume

/** Where the way to the speaker stands - each value is one face of the home card. */
sealed interface Link {
    /** «Устройства поблизости» (BLUETOOTH_CONNECT) not granted yet. */
    data object NoPermission : Link
    data object BluetoothOff : Link
    /** No bonded Blast 2: the user pairs it in Android's Bluetooth settings (needed for the sound anyway). */
    data object NotPaired : Link
    /** The Blast 2 is bonded but not connected to the phone (off, asleep, away): the app waits for it, no SPP attempt. */
    data class Waiting(val name: String) : Link
    data class Connecting(val name: String) : Link
    data class Connected(val name: String) : Link
    /** The speaker is connected to the phone, but the control channel did not open or broke - e.g. held by another app. */
    data class Failed(val name: String) : Link
}

/**
 * The one owner of the speaker connection for the UI (KARTUN's model: state in one ViewModel, `researches/11` §4a).
 *
 * It follows the speaker's own link to the phone while the app is visible ([watch] / [unwatch], `researches/11` §4b.1):
 * the A2DP connection of the bonded Blast 2 opens the SPP control channel by itself, its ACL disconnect closes the
 * channel at once and the card goes back to «Включите колонку» - no blind reconnect loop (§4b.2). Bluetooth on/off and a
 * new bond restart the lookup. No scan, so no location on any Android (GOAL.md success line 2). [NOT-TESTED]
 */
@SuppressLint("MissingPermission")
class SpeakerViewModel(app: Application) : AndroidViewModel(app) {
    private val _link = MutableStateFlow<Link>(Link.NoPermission)
    val link: StateFlow<Link> = _link

    private val _speaker = MutableStateFlow(SpeakerState())
    val speaker: StateFlow<SpeakerState> = _speaker

    private var conn: SpeakerLink? = null
    private var job: Job? = null

    /** The A2DP profile proxy - asked which devices carry sound right now; obtained once, closed in [onCleared]. */
    private var a2dp: BluetoothA2dp? = null

    private val app get() = getApplication<Application>()
    private val adapter: BluetoothAdapter? get() = app.getSystemService(BluetoothManager::class.java)?.adapter

    private fun hasPermission() =
        ContextCompat.checkSelfPermission(app, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED

    /** The adapter and the bonded Blast 2 the link opens to. */
    private class Found(val adapter: BluetoothAdapter, val device: BluetoothDevice)

    /** The A2DP proxy; the system hands it over asynchronously (developer.android.com, bluetooth profiles). */
    private suspend fun a2dpProxy(adapter: BluetoothAdapter): BluetoothA2dp? = a2dp ?: suspendCancellableCoroutine { k ->
        val asked = adapter.getProfileProxy(app, object : BluetoothProfile.ServiceListener {
            override fun onServiceConnected(profile: Int, proxy: BluetoothProfile) {
                a2dp = proxy as BluetoothA2dp
                if (k.isActive) k.resume(proxy)
            }
            override fun onServiceDisconnected(profile: Int) { a2dp = null }
        }, BluetoothProfile.A2DP)
        if (!asked && k.isActive) k.resume(null)
    }

    /** True when the speaker carries the phone's sound right now - then its SPP channel can be opened. */
    private suspend fun soundConnected(adapter: BluetoothAdapter, device: BluetoothDevice): Boolean =
        a2dpProxy(adapter)?.getConnectionState(device) == BluetoothProfile.STATE_CONNECTED

    /**
     * Finds the bonded Blast 2, or sets the [Link] state that stops the way to it and returns null. Runs on
     * Dispatchers.IO: the first `getSystemService(BluetoothManager)` of a process reads the disk - StrictMode on the A51
     * 2026-10-16 16:27 measured 114 and 117 ms on the main thread - and `bondedDevices` is a binder call.
     */
    private fun lookUp(): Found? {
        if (!hasPermission()) { _link.value = Link.NoPermission; return null }
        val adapter = adapter
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
            if (!soundConnected(adapter, device)) { _link.value = Link.Waiting(name); return@launch }
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
            } catch (e: CancellationException) {
                throw e
            } catch (_: Exception) {
                // falls through to the verdict below
            } finally {
                c.close()
                if (conn === c) conn = null
            }
            // The channel ended: the speaker left the phone (off, asleep, away) → wait for it; it is still there → the
            // channel itself failed (held by another app).
            _link.value = if (soundConnected(adapter, device)) Link.Failed(name) else Link.Waiting(name)
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
     * The speaker's link to the phone, seen through system broadcasts (exempt implicit broadcasts, `researches/11`
     * §4b.1). Only the Blast 2 matters; other devices are ignored.
     */
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val device = IntentCompat.getParcelableExtra(intent, BluetoothDevice.EXTRA_DEVICE, BluetoothDevice::class.java)
            val ours = device != null && hasPermission() && Blast2.isBlast2(device.name)
            when (intent.action) {
                BluetoothAdapter.ACTION_STATE_CHANGED -> {
                    val on = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, -1) == BluetoothAdapter.STATE_ON
                    if (on) start() else { closeLink(); _link.value = Link.BluetoothOff }
                }
                BluetoothDevice.ACTION_BOND_STATE_CHANGED -> if (ours) start()
                BluetoothA2dp.ACTION_CONNECTION_STATE_CHANGED -> if (ours &&
                    intent.getIntExtra(BluetoothProfile.EXTRA_STATE, -1) == BluetoothProfile.STATE_CONNECTED
                ) start()
                // ACL down: close the socket now instead of waiting for the read to fail; the connect job then sets
                // «Включите колонку» (BluetoothSocket.close() is thread-safe and aborts a blocked read - AOSP).
                BluetoothDevice.ACTION_ACL_DISCONNECTED -> if (ours) conn?.close()
            }
            if (BuildConfig.DEBUG) Log.d(SpeakerLink.TAG, "event ${intent.action?.substringAfterLast('.')} ours=$ours")
        }
    }
    private var watching = false

    /** The app came on screen: follow the speaker's link and look it up now. */
    fun watch() {
        if (!watching) {
            val filter = IntentFilter().apply {
                addAction(BluetoothAdapter.ACTION_STATE_CHANGED)
                addAction(BluetoothDevice.ACTION_BOND_STATE_CHANGED)
                addAction(BluetoothA2dp.ACTION_CONNECTION_STATE_CHANGED)
                addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED)
            }
            // System broadcasts reach a NOT_EXPORTED receiver; other apps cannot send to it.
            ContextCompat.registerReceiver(app, receiver, filter, ContextCompat.RECEIVER_NOT_EXPORTED)
            watching = true
        }
        start()
    }

    /**
     * The app left the screen: stop following and close the link. Since Android 12 «Back» on the root screen only moves
     * the app to the background (the A51 run 2026-10-16 16:18: no «closed» line after Back), so waiting for onCleared
     * kept the speaker's channel busy for every other app. Background control is deferred (`researches/11` §4b.6).
     */
    fun unwatch() {
        if (watching) { app.unregisterReceiver(receiver); watching = false }
        closeLink()
    }

    private fun closeLink() {
        job?.cancel()
        job = null
        conn?.close()
    }

    override fun onCleared() {
        unwatch()
        a2dp?.let { proxy -> adapter?.closeProfileProxy(BluetoothProfile.A2DP, proxy) }
    }
}
