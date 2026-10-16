package com.kriniks.tribit.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.kriniks.tribit.R
import com.kriniks.tribit.link.Link
import com.kriniks.tribit.protocol.Blast2
import com.kriniks.tribit.protocol.SpeakerState
import kotlin.math.roundToInt

/** Smallest height of a card button: the text may wrap to two lines on a narrow screen and is never cut (run 2026-10-16, Found 2). */
private val BUTTON_MIN_HEIGHT = 52.dp

/** What the home card can ask the outside world for: the permission, Android's Bluetooth settings, a retry. */
class SpeakerActions(
    val askPermission: () -> Unit,
    val openBluetoothSettings: () -> Unit,
    val retry: () -> Unit,
    val setVolume: (Int) -> Unit,
    val togglePlay: () -> Unit,
)

/**
 * The speaker card of the home screen - one face per [Link] state (`plans/05` step 5). Values come only from the
 * speaker's answers ([SpeakerState]); an unanswered value shows «—», never a default (EXP-0009). [NOT-TESTED]
 */
@Composable
fun SpeakerCard(link: Link, speaker: SpeakerState, act: SpeakerActions) {
    Card {
        when (link) {
            Link.NoPermission -> Face(
                Dot.Off, stringResource(R.string.link_permission), stringResource(R.string.link_permission_hint),
                stringResource(R.string.link_permission_button), act.askPermission,
            )
            Link.BluetoothOff -> Face(
                Dot.Off, stringResource(R.string.link_bt_off), stringResource(R.string.link_bt_off_hint),
                stringResource(R.string.link_bt_settings), act.openBluetoothSettings,
            )
            Link.NotPaired -> Face(
                Dot.Off, stringResource(R.string.link_not_paired), stringResource(R.string.link_not_paired_hint, Blast2.NAME),
                stringResource(R.string.link_bt_settings), act.openBluetoothSettings,
            )
            is Link.Waiting -> Face(
                Dot.Off, stringResource(R.string.link_waiting), stringResource(R.string.link_waiting_hint, link.name),
                stringResource(R.string.link_bt_settings), act.openBluetoothSettings,
            )
            is Link.Connecting -> Face(Dot.Wait, link.name, stringResource(R.string.link_connecting))
            is Link.Failed -> Face(
                Dot.Off, link.name, stringResource(R.string.link_failed_hint),
                stringResource(R.string.link_retry), act.retry,
            )
            is Link.Connected -> Connected(link.name, speaker, act)
        }
    }
}

private enum class Dot { Off, Wait, On }

@Composable
private fun Title(dot: Dot, text: String) {
    val color = when (dot) {
        Dot.Off -> MaterialTheme.colorScheme.outlineVariant
        Dot.Wait -> MaterialTheme.colorScheme.error
        Dot.On -> MaterialTheme.colorScheme.tertiary
    }
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(10.dp).background(color, CircleShape))
        Spacer(Modifier.size(10.dp))
        Text(text, style = MaterialTheme.typography.titleMedium)
    }
}

/** One state of the card: a title with a dot, an explanation, and at most one action. */
@Composable
private fun Face(dot: Dot, title: String, hint: String, button: String? = null, onClick: () -> Unit = {}) {
    Title(dot, title)
    Text(hint, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    if (button != null) PinkButton(button, onClick)
}

/**
 * The pink action button: white bold text, larger than the body (the owner's choice for pink buttons, interview_002
 * Q2 = B: contrast 3.63:1 needs large bold text to pass WCAG 3:1).
 */
@Composable
fun PinkButton(text: String, onClick: () -> Unit) {
    Button(onClick = onClick, modifier = Modifier.fillMaxWidth().heightIn(min = BUTTON_MIN_HEIGHT)) {
        Text(text, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = Color.White)
    }
}

@Composable
private fun Connected(name: String, s: SpeakerState, act: SpeakerActions) {
    Title(Dot.On, name)
    val dash = stringResource(R.string.value_unknown)
    Text(
        stringResource(R.string.speaker_battery, s.battery?.let { "$it %" } ?: dash),
        style = MaterialTheme.typography.bodyLarge,
    )

    // While the finger drags, the slider shows the finger; after release - the speaker's answer to the re-query.
    var dragging by remember { mutableStateOf<Float?>(null) }
    val shown = dragging ?: (s.volume ?: 0).toFloat()
    Text(
        stringResource(R.string.speaker_volume, s.volume?.toString() ?: dash, Blast2.VOLUME_MAX),
        style = MaterialTheme.typography.bodyLarge,
    )
    Slider(
        value = shown,
        onValueChange = { dragging = it },
        onValueChangeFinished = { dragging?.let { act.setVolume(it.roundToInt()) }; dragging = null },
        valueRange = 0f..Blast2.VOLUME_MAX.toFloat(),
        steps = Blast2.VOLUME_MAX - 1,
        enabled = s.volume != null,
        colors = SliderDefaults.colors(
            thumbColor = MaterialTheme.colorScheme.primary, activeTrackColor = MaterialTheme.colorScheme.primary,
            activeTickColor = Color.Transparent, inactiveTickColor = Color.Transparent,
        ),
    )
    OutlinedButton(onClick = act.togglePlay, modifier = Modifier.fillMaxWidth().heightIn(min = BUTTON_MIN_HEIGHT)) {
        Text(
            stringResource(if (s.playing == true) R.string.speaker_pause else R.string.speaker_play),
            style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurface,
        )
    }
}
