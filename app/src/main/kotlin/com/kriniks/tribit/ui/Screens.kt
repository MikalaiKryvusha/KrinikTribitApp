package com.kriniks.tribit.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.kriniks.tribit.BuildConfig
import com.kriniks.tribit.R
import com.kriniks.tribit.link.Link
import com.kriniks.tribit.protocol.SpeakerState

/** GitHub of the project and of the author - the «О приложении» links (owner's rule R5, HOUSE_RULES.md). */
const val REPO_URL = "https://github.com/MikalaiKryvusha/KrinikTribitApp"
const val AUTHOR_URL = "https://github.com/MikalaiKryvusha"

/** Widest a content column grows: on a tablet or in landscape the column stays readable and centred. */
private val MAX_CONTENT_WIDTH = 640.dp

/**
 * The page frame of every screen: a scrolling column, centred, never wider than MAX_CONTENT_WIDTH, clear of the system
 * bars - so a screen fits a phone, a tablet, landscape and an enlarged display size (GOAL.md, success line 3).
 * [NOT-TESTED]
 */
@Composable
fun Page(title: String, onBack: (() -> Unit)? = null, content: @Composable ColumnScope.() -> Unit) {
    Box(
        Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).systemBarsPadding(),
        contentAlignment = Alignment.TopCenter,
    ) { CompositionLocalProvider(LocalContentColor provides MaterialTheme.colorScheme.onBackground) {
        Column(
            Modifier.widthIn(max = MAX_CONTENT_WIDTH).fillMaxWidth().verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (onBack != null) {
                    TextButton(onClick = onBack) { Text(stringResource(R.string.back), color = MaterialTheme.colorScheme.primary) }
                }
                Text(title, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onBackground)
            }
            content()
        }
    } }
}

/**
 * A flat dark card, KARTUN's shape. It sets the content colour itself: a Text without a colour outside a Surface is
 * black, and the A51 run of 2026-10-16 showed «Колонка не подключена» black on the dark card
 * (`testcases/reports/2026-10-16_two_packages.md`, Found 1) - fixed here once for every card. [NOT-TESTED]
 */
@Composable
fun Card(modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    CompositionLocalProvider(LocalContentColor provides MaterialTheme.colorScheme.onSurface) {
        Column(
            modifier.fillMaxWidth().background(MaterialTheme.colorScheme.surfaceContainer, MaterialTheme.shapes.large)
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
            content = content,
        )
    }
}

/**
 * One tappable row of a settings list. Inside a [Card] pass `inCard = true`: the row takes the lighter container colour,
 * so it reads as a button on the card (on the A51 16:47 a row in the card's own colour was invisible).
 */
@Composable
fun SettingsRow(title: String, subtitle: String? = null, inCard: Boolean = false, onClick: () -> Unit) {
    val container = if (inCard) MaterialTheme.colorScheme.surfaceContainerHigh else MaterialTheme.colorScheme.surfaceContainer
    Column(
        Modifier.fillMaxWidth().background(container, MaterialTheme.shapes.medium)
            .clickable(onClick = onClick).padding(horizontal = 20.dp, vertical = 16.dp),
    ) {
        Text(title, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurface)
        if (subtitle != null) Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

/**
 * Home: the speaker card (`SpeakerCard.kt`) and Settings. The promise card «Без геолокации, без аккаунта…» is gone - the
 * owner, 2026-10-16 ≈ 16:12 +03:00, on «Геолокация не нужна.»: «НАХУЙ ТАКОЕ ПИСАТЬ?»; app texts follow his portrait
 * (HOUSE_RULES.md R10). [NOT-TESTED]
 */
@Composable
fun HomeScreen(link: Link, speaker: SpeakerState, act: SpeakerActions, onSettings: () -> Unit) {
    Page(stringResource(R.string.app_title)) {
        SpeakerCard(link, speaker, act)
        SettingsRow(stringResource(R.string.settings), onClick = onSettings)
    }
}

/** Settings: «О приложении» for everyone, «Отладка» in the debug build only (owner's rule R6). [NOT-TESTED] */
@Composable
fun SettingsScreen(onBack: () -> Unit, onAbout: () -> Unit, onDebug: (() -> Unit)?) {
    Page(stringResource(R.string.settings), onBack = onBack) {
        SettingsRow(stringResource(R.string.about), stringResource(R.string.about_sub), onClick = onAbout)
        if (onDebug != null) SettingsRow(stringResource(R.string.debug), stringResource(R.string.debug_sub), onClick = onDebug)
    }
}

/** «О приложении»: name, version, author, the GitHub links (owner's rule R5). [NOT-TESTED] */
@Composable
fun AboutScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    fun open(url: String) = context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    Page(stringResource(R.string.about), onBack = onBack) {
        Card {
            Text(stringResource(R.string.app_name), style = MaterialTheme.typography.titleMedium)
            Text(stringResource(R.string.about_version, BuildConfig.VERSION_NAME), style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(stringResource(R.string.about_text), style = MaterialTheme.typography.bodyMedium)
            Text(stringResource(R.string.about_author), style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        SettingsRow(stringResource(R.string.about_repo), REPO_URL) { open(REPO_URL) }
        SettingsRow(stringResource(R.string.about_author_github), AUTHOR_URL) { open(AUTHOR_URL) }
        Text(stringResource(R.string.about_legal), style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.outlineVariant)
    }
}
