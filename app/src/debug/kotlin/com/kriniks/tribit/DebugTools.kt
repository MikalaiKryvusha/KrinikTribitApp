package com.kriniks.tribit

import android.os.Build
import android.util.DisplayMetrics
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import com.kriniks.tribit.ui.Card
import com.kriniks.tribit.ui.Page

/**
 * «Debug Krinik Tribit» only: the «Отладка» section opened from Settings (owner's rule R6, HOUSE_RULES.md). Shows the
 * facts a device report needs: the build, the Android version, the screen in dp and its density - the numbers that
 * explained the cut-off screens of the official app on the Titan (density 480 over a 320 panel). The release twin is
 * src/nodebug/.../DebugTools.kt. [NOT-TESTED]
 */
object DebugTools {
    const val ENABLED = true

    @Composable
    fun Screen(onBack: () -> Unit) {
        val config = LocalConfiguration.current
        val metrics = LocalContext.current.resources.displayMetrics
        val rows = listOf(
            "Build" to "${BuildConfig.APPLICATION_ID} · ${BuildConfig.VERSION_NAME} · ${BuildConfig.BUILD_TYPE}",
            "Android" to "${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})",
            "Device" to "${Build.MANUFACTURER} ${Build.MODEL}",
            "ABI" to Build.SUPPORTED_ABIS.joinToString(),
            "Screen" to "${config.screenWidthDp} × ${config.screenHeightDp} dp · ${metrics.widthPixels} × ${metrics.heightPixels} px",
            "Density" to "${metrics.densityDpi} dpi now · ${DisplayMetrics.DENSITY_DEVICE_STABLE} dpi panel",
            "Font scale" to "${config.fontScale}",
            "Locale" to config.locales.toLanguageTags(),
        )
        Page(stringResource(R.string.debug), onBack = onBack) {
            Card {
                for ((name, value) in rows) {
                    Text(name, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                    Text(value, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}
