package com.kriniks.tribit

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import com.kriniks.tribit.ui.AboutScreen
import com.kriniks.tribit.ui.HomeScreen
import com.kriniks.tribit.ui.SettingsScreen
import com.kriniks.tribit.ui.theme.KrinikTheme

/** The screens of the app; the back stack is this enum's parent chain (Home ← Settings ← About / Debug). */
enum class Screen(val parent: Screen?) { HOME(null), SETTINGS(HOME), ABOUT(SETTINGS), DEBUG(SETTINGS) }

/**
 * The single activity: one Compose tree, navigation by a saved enum (survives rotation). The «Отладка» screen comes
 * from DebugTools - src/debug in «Debug Krinik Tribit», an empty stub in release (owner's rule R6). [NOT-TESTED]
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            KrinikTheme {
                var screen by rememberSaveable { mutableStateOf(Screen.HOME) }
                val back = { screen = screen.parent ?: screen }
                BackHandler(enabled = screen.parent != null) { back() }
                when (screen) {
                    Screen.HOME -> HomeScreen(onSettings = { screen = Screen.SETTINGS })
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
}
