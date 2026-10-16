package com.kriniks.tribit

import android.Manifest
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.StrictMode
import android.provider.Settings
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.File
import androidx.lifecycle.lifecycleScope
import com.kriniks.tribit.protocol.Profile
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
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
import com.kriniks.tribit.link.Link
import com.kriniks.tribit.link.SpeakerViewModel
import com.kriniks.tribit.ui.AboutScreen
import com.kriniks.tribit.ui.EqScreen
import com.kriniks.tribit.ui.HomeScreen
import com.kriniks.tribit.ui.SettingsActions
import com.kriniks.tribit.ui.SettingsScreen
import com.kriniks.tribit.ui.SpeakerSettingsScreen
import com.kriniks.tribit.ui.SpeakerActions
import com.kriniks.tribit.ui.theme.KrinikTheme

/** The screens of the app; the back stack is this enum's parent chain (Home ← Settings ← About / Debug). */
enum class Screen(val parent: Screen?) {
    HOME(null), EQ(HOME), SPEAKER_SETTINGS(HOME), SETTINGS(HOME), ABOUT(SETTINGS), DEBUG(SETTINGS);

    /** Screens that talk to the speaker - left for home when the speaker's link ends. */
    val needsSpeaker get() = this == EQ || this == SPEAKER_SETTINGS
}

/**
 * The single activity: one Compose tree, navigation by a saved enum (survives rotation). The «Отладка» screen comes
 * from DebugTools - src/debug in «Debug Krinik Tribit», an empty stub in release (owner's rule R6). The speaker
 * connection lives in [SpeakerViewModel], which follows the speaker's link while the app is on screen. [NOT-TESTED]
 */
class MainActivity : ComponentActivity() {
    private val speakerVm: SpeakerViewModel by viewModels()

    /** Set after the first refusal: Android then stops showing its dialog, so the next tap opens the app's settings. */
    private var permissionRefused = false

    private val askConnect = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        permissionRefused = !granted
        speakerVm.start()
    }

    /** «Сохранить в файл»: Android's own save dialog; the user picks the folder (`ideas/01`). */
    private val saveFile = registerForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        // The profile is taken when the button is pressed: on return from the dialog the link restarts and the state is
        // empty (the §7B pass 2026-10-16 17:18).
        val profile = profileToSave
        profileToSave = null
        if (uri != null && profile != null) lifecycleScope.launch {
            val ok = withContext(Dispatchers.IO) {
                runCatching {
                    val out = contentResolver.openOutputStream(uri) ?: error("no stream")
                    out.use { it.write(profile.toJson().toByteArray()) }
                }.isSuccess
            }
            toast(if (ok) R.string.file_saved else R.string.file_not_saved)
        }
    }

    /** The speaker's EQ and light at the moment «Сохранить в файл» was pressed. */
    private var profileToSave: Profile? = null

    /** «Открыть файл»: Android's own file picker; a refused file says why and changes nothing (`ideas/01`, criterion 5). */
    private val openFile = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) lifecycleScope.launch {
            val text = withContext(Dispatchers.IO) {
                runCatching { contentResolver.openInputStream(uri)?.use { it.readBytes().decodeToString() } }.getOrNull()
            }
            when (val r = text?.let { Profile.parse(it) }) {
                is Profile.Result.Ok -> { speakerVm.apply(r.profile); toast(R.string.file_applied) }
                is Profile.Result.Refused -> toast(
                    when (r.problem) {
                        Profile.Problem.OTHER_MODEL -> R.string.file_other_model
                        Profile.Problem.BROKEN -> R.string.file_broken
                        Profile.Problem.NOT_A_PROFILE -> R.string.file_not_profile
                    },
                )
                null -> toast(R.string.file_unreadable)
            }
        }
    }

    private fun toast(text: Int) = Toast.makeText(this, text, Toast.LENGTH_LONG).show()

    /**
     * «Поделиться файлом» (`ideas/01`, criterion 4): writes the speaker's EQ and light to cache/shared/ and hands the file
     * to Android's share menu (messenger, mail). [NOT-TESTED]
     */
    private fun shareProfile() {
        val profile = Profile.of(speakerVm.speaker.value) ?: return toast(R.string.file_not_saved)
        lifecycleScope.launch {
            val file = withContext(Dispatchers.IO) {
                runCatching {
                    File(cacheDir, SHARED_DIR).apply { mkdirs() }.resolve(PROFILE_FILE_NAME)
                        .also { it.writeText(profile.toJson()) }
                }.getOrNull()
            } ?: return@launch toast(R.string.file_not_saved)
            val uri = FileProvider.getUriForFile(this@MainActivity, "$packageName.files", file)
            val send = Intent(Intent.ACTION_SEND).setType("application/json").putExtra(Intent.EXTRA_STREAM, uri)
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            startActivity(Intent.createChooser(send, getString(R.string.file_share)))
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Debug only: every disk or network call on the main thread goes to logcat (tag StrictMode) - the check of
        // plans/05 criterion 4 «no main-thread I/O». [NOT-TESTED]
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder().detectAll().penaltyLog().build())
        }
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        var openEq: () -> Unit = {}
        var openSpeakerSettings: () -> Unit = {}
        val actions = SpeakerActions(
            askPermission = {
                if (permissionRefused) openAppSettings() else askConnect.launch(Manifest.permission.BLUETOOTH_CONNECT)
            },
            openBluetoothSettings = { startActivity(Intent(Settings.ACTION_BLUETOOTH_SETTINGS)) },
            retry = speakerVm::start,
            setVolume = speakerVm::setVolume,
            togglePlay = speakerVm::togglePlay,
            openEq = { openEq() },
            setLight = speakerVm::setLight,
            openSettings = { openSpeakerSettings() },
        )
        val settingsActions = SettingsActions(
            autoOff = speakerVm::setAutoOff, sleep = speakerVm::setSleep, voice = speakerVm::setVoice,
            indicator = speakerVm::setIndicator, mic = speakerVm::setMic, howl = speakerVm::setHowl,
        )
        setContent {
            KrinikTheme {
                var screen by rememberSaveable { mutableStateOf(Screen.HOME) }
                val back = { screen = screen.parent ?: screen }
                val link by speakerVm.link.collectAsState()
                val speaker by speakerVm.speaker.collectAsState()
                val speakerSettings by speakerVm.settings.collectAsState()
                openEq = { screen = Screen.EQ }
                openSpeakerSettings = { screen = Screen.SPEAKER_SETTINGS }
                BackHandler(enabled = screen.parent != null) { back() }
                // Speaker screens need a live link; when the speaker leaves, the app returns home to its card. A reconnect
                // (Connecting) keeps the screen: Android's save dialog stops the app and the link reopens on return - on the
                // A51 2026-10-16 17:11 the EQ screen jumped home there.
                if (screen.needsSpeaker && link !is Link.Connected && link !is Link.Connecting) screen = Screen.HOME
                when (screen) {
                    Screen.HOME -> HomeScreen(link, speaker, actions, onSettings = { screen = Screen.SETTINGS })
                    Screen.EQ -> EqScreen(
                        speaker, onBack = back, onPreset = speakerVm::selectPreset, onCustom = speakerVm::setCustom,
                        onSaveFile = {
                            profileToSave = Profile.of(speakerVm.speaker.value)
                            if (profileToSave != null) saveFile.launch(PROFILE_FILE_NAME) else toast(R.string.file_not_saved)
                        },
                        onOpenFile = { openFile.launch(arrayOf("application/json", "text/plain", "application/octet-stream")) },
                        onShareFile = ::shareProfile,
                    )
                    Screen.SPEAKER_SETTINGS ->
                        SpeakerSettingsScreen(speakerSettings, speaker.newFirmware, onBack = back, act = settingsActions)
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

    /** On screen: follow the speaker's link to the phone (`SpeakerViewModel.watch`). */
    override fun onStart() {
        super.onStart()
        speakerVm.watch()
    }

    /** Off screen: the speaker's channel is free for other apps (`SpeakerViewModel.unwatch`). */
    override fun onStop() {
        super.onStop()
        speakerVm.unwatch()
    }

    private companion object {
        /** The name the save dialog proposes; the user may change it. */
        const val PROFILE_FILE_NAME = "Krinik Tribit - StormBox Blast 2.json"

        /** The cache folder FileProvider shares (`res/xml/shared_files.xml`). */
        const val SHARED_DIR = "shared"
    }

    private fun openAppSettings() =
        startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.fromParts("package", packageName, null)))
}
