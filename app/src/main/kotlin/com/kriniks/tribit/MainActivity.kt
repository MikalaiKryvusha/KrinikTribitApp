package com.kriniks.tribit

import android.Manifest
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.StrictMode
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import com.kriniks.tribit.link.SpeakerViewModel
import com.kriniks.tribit.ui.AboutScreen
import com.kriniks.tribit.ui.HomeScreen
import com.kriniks.tribit.ui.SettingsScreen
import com.kriniks.tribit.ui.SpeakerActions
import com.kriniks.tribit.ui.theme.KrinikTheme

/** The screens of the app; the back stack is this enum's parent chain (Home ← Settings ← About / Debug). */
enum class Screen(val parent: Screen?) { HOME(null), SETTINGS(HOME), ABOUT(SETTINGS), DEBUG(SETTINGS) }

/**
 * The single activity: one Compose tree, navigation by a saved enum (survives rotation). The «Отладка» screen comes
 * from DebugTools - src/debug in «Debug Krinik Tribit», an empty stub in release (owner's rule R6). The speaker
 * connection lives in [SpeakerViewModel]; every return to the app (onResume) restarts it if it is down - after the
 * user granted the permission, turned Bluetooth on or paired the speaker in Android's settings. [NOT-TESTED]
 */
class MainActivity : ComponentActivity() {
    private val speakerVm: SpeakerViewModel by viewModels()

    /** Set after the first refusal: Android then stops showing its dialog, so the next tap opens the app's settings. */
    private var permissionRefused = false

    private val askConnect = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        permissionRefused = !granted
        speakerVm.start()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Debug only: every disk or network call on the main thread goes to logcat (tag StrictMode) - the check of
        // plans/05 criterion 4 «no main-thread I/O». [NOT-TESTED]
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder().detectAll().penaltyLog().build())
        }
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val actions = SpeakerActions(
            askPermission = {
                if (permissionRefused) openAppSettings() else askConnect.launch(Manifest.permission.BLUETOOTH_CONNECT)
            },
            openBluetoothSettings = { startActivity(Intent(Settings.ACTION_BLUETOOTH_SETTINGS)) },
            retry = speakerVm::start,
            setVolume = speakerVm::setVolume,
            togglePlay = speakerVm::togglePlay,
        )
        setContent {
            KrinikTheme {
                var screen by rememberSaveable { mutableStateOf(Screen.HOME) }
                val back = { screen = screen.parent ?: screen }
                val link by speakerVm.link.collectAsState()
                val speaker by speakerVm.speaker.collectAsState()
                BackHandler(enabled = screen.parent != null) { back() }
                when (screen) {
                    Screen.HOME -> HomeScreen(link, speaker, actions, onSettings = { screen = Screen.SETTINGS })
                    Screen.SETTINGS -> SettingsScreen(
                        onBack = back,
                        onAbout = { screen = Screen.ABOUT },
                        onDebug = if (DebugTools.ENABLED) ({ screen = Screen.DEBUG }) else null,
                    )
                    Screen.ABOUT -> AboutScreen(onBack = back)
                    Screen.DEBUG -> DebugTools.Screen(onBack = back)
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        speakerVm.start()
    }

    /** The speaker's channel is ours only while the app is on screen (`SpeakerViewModel.stop`). */
    override fun onStop() {
        super.onStop()
        speakerVm.stop()
    }

    private fun openAppSettings() =
        startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.fromParts("package", packageName, null)))
}
