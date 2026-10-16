package com.kriniks.tribit

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.pm.PackageManager
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.os.Bundle
import android.util.Log
import java.util.Locale
import kotlin.concurrent.thread
import kotlin.math.PI
import kotlin.math.log10
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * The ear of the stand - debug build only (`plans/06` step 7a). The owner, 2026-10-16 ≈ 16:49–16:50 +03:00: the A51
 * stands in one room with the speaker; «микрофон в А51 плохой, ты не сможешь оценить качество работы жквалайзера» ·
 * «качества такого, чтобы услышать вообще, есть звук, или нет, меняется громкость, или нет». So it answers exactly
 * two questions: is there sound, and did the loudness change - never the EQ's quality.
 *
 * Run: `adb shell am start -W -n com.kriniks.tribit.debug/com.kriniks.tribit.EarActivity [--ez tone false]`.
 * It measures the microphone for [WINDOW_MS] in silence, then plays a [TONE_HZ] sine through the media stream (to the
 * connected speaker) and measures again; one line goes to logcat under [TAG]:
 * `noise=-58.3 dBFS tone=-41.0 dBFS delta=17.3 dB`. With `--ez tone false` it only listens (is music playing?).
 * Play sound only at speaker volume 1–2 (`HOUSE_RULES.md` §3 - the owner's word). [NOT-TESTED]
 */
class EarActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tone = intent.getBooleanExtra("tone", true)
        thread(name = "ear") {
            try { listen(tone) } catch (e: Exception) { Log.e(TAG, "failed: $e") }
            runOnUiThread { finish() }
        }
    }

    @SuppressLint("MissingPermission")
    private fun listen(tone: Boolean) {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "no RECORD_AUDIO - adb shell pm grant $packageName android.permission.RECORD_AUDIO")
            return
        }
        val minBuf = AudioRecord.getMinBufferSize(RATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
        val rec = AudioRecord(MediaRecorder.AudioSource.MIC, RATE, AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT, maxOf(minBuf, RATE))
        rec.startRecording()
        try {
            rec.read(ShortArray(RATE / 4), 0, RATE / 4) // the first quarter second of a mic start is a ramp - dropped
            val noise = levelDb(rec, WINDOW_MS)
            if (!tone) { Log.i(TAG, "level=%.1f dBFS".format(Locale.ROOT, noise)); return }
            val track = sineTrack()
            track.play()
            Thread.sleep(SETTLE_MS) // the Bluetooth path delays the sound by a few hundred ms
            val loud = levelDb(rec, WINDOW_MS)
            track.stop()
            track.release()
            Log.i(TAG, "noise=%.1f dBFS tone=%.1f dBFS delta=%.1f dB".format(Locale.ROOT, noise, loud, loud - noise))
        } finally {
            rec.stop()
            rec.release()
        }
    }

    /** RMS level of the microphone over [ms], in dB relative to full scale. */
    private fun levelDb(rec: AudioRecord, ms: Long): Double {
        val n = (RATE * ms / 1000).toInt()
        val buf = ShortArray(n)
        var got = 0
        while (got < n) { val r = rec.read(buf, got, n - got); if (r <= 0) break; got += r }
        var sum = 0.0
        for (i in 0 until got) { val v = buf[i] / FULL_SCALE; sum += v * v }
        val rms = sqrt(sum / maxOf(got, 1))
        return 20 * log10(maxOf(rms, MIN_RMS))
    }

    /** A static AudioTrack holding [TONE_MS] of the sine at half scale on the media stream. */
    private fun sineTrack(): AudioTrack {
        val n = (RATE * TONE_MS / 1000).toInt()
        val pcm = ShortArray(n) { (TONE_AMPLITUDE * FULL_SCALE * sin(2 * PI * TONE_HZ * it / RATE)).toInt().toShort() }
        val track = AudioTrack.Builder()
            .setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
            .setAudioFormat(AudioFormat.Builder().setSampleRate(RATE).setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                .setChannelMask(AudioFormat.CHANNEL_OUT_MONO).build())
            .setTransferMode(AudioTrack.MODE_STATIC).setBufferSizeInBytes(n * 2).build()
        track.write(pcm, 0, n)
        return track
    }

    private companion object {
        const val TAG = "KT.Ear"
        const val RATE = 44_100
        const val FULL_SCALE = 32_768.0
        const val MIN_RMS = 1e-6
        const val WINDOW_MS = 1_000L
        const val SETTLE_MS = 700L
        const val TONE_MS = 2_500L
        const val TONE_HZ = 1_000.0
        const val TONE_AMPLITUDE = 0.5
    }
}
