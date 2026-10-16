package com.kriniks.tribit

import androidx.compose.runtime.Composable

/**
 * Release build: no «Отладка» section (owner's rule R6). Same API as src/debug/.../DebugTools.kt; Settings hides the
 * button because ENABLED is false, and Screen is never reached. [NOT-TESTED]
 */
object DebugTools {
    const val ENABLED = false

    @Composable
    fun Screen(onBack: () -> Unit) = Unit
}
