package com.kriniks.tribit.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.kriniks.tribit.R
import com.kriniks.tribit.link.Link
import com.kriniks.tribit.protocol.Blast2
import com.kriniks.tribit.protocol.Eq
import com.kriniks.tribit.protocol.SpeakerState
import kotlin.math.roundToInt

/** Smallest height of a card button: the text may wrap to two lines on a narrow screen and is never cut (run 2026-10-16, Found 2). */
private val BUTTON_MIN_HEIGHT = 52.dp

/** What the home screen can ask the outside world for: the permission, Android's Bluetooth settings, the speaker's commands. */
class SpeakerActions(
    val askPermission: () -> Unit,
    val openBluetoothSettings: () -> Unit,
    val retry: () -> Unit,
    val setVolume: (Int) -> Unit,
    val togglePlay: () -> Unit,
    val previous: () -> Unit,
    val next: () -> Unit,
    val openEq: () -> Unit,
    val setLight: (Int) -> Unit,
    val openSettings: () -> Unit,
)

/**
 * The speaker part of the home screen, mock-up A-home (`design/mockups-v1.html`, `interviews/interview_003` Q1 = A): the
 * drawn speaker on its pink glow, then - connected - the name with the «Подключена» and battery pills, the player card and
 * the section strips; otherwise the card of the [Link] state that stops the way (`plans/05` step 5). Values come only from
 * the speaker's answers ([SpeakerState]); an unanswered value shows «—», never a default (EXP-0009). [NOT-TESTED]
 */
@Composable
fun SpeakerHome(link: Link, speaker: SpeakerState, act: SpeakerActions) {
    val connected = link is Link.Connected
    Stage(lit = connected && speaker.light.let { it != null && it != Blast2.LIGHT_OFF })
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
        is Link.Failed -> Face(Dot.Off, link.name, stringResource(R.string.link_failed_hint), stringResource(R.string.link_retry), act.retry)
        is Link.Connected -> Connected(link.name, speaker, act)
    }
}

/**
 * The speaker's photo on its pink glow (.a-hero). The photo is Tribit's own picture of the Blast 2 from their model catalog
 * (`productLogo`), fetched once by `tools/fetch_speaker_images.py` and built into the app - the owner, 2026-10-16 ≈ 20:0x
 * +03:00: «мы сейчас забираем у него картинки из запросов и зашиваем в наш апп» · «наш апп не будет делать запросы на
 * сервер» (`HOUSE_RULES.md` R2, exception 2). The glow is brighter while the speaker's light is on. [NOT-TESTED]
 */
@Composable
private fun Stage(lit: Boolean) {
    val glow = Brush.radialGradient(
        if (lit) listOf(Color(0x66FF1A8C), Color(0x1AFF1A8C), Color.Transparent)
        else listOf(Color(0x40FF1A8C), Color(0x10FF1A8C), Color.Transparent),
    )
    Box(Modifier.fillMaxWidth().height(STAGE_HEIGHT).background(glow), contentAlignment = Alignment.Center) {
        Image(painterResource(R.drawable.speaker_blast2), Blast2.NAME, Modifier.width(SPEAKER_WIDTH))
    }
}

private enum class Dot { Off, Wait, On }

@Composable
private fun dotColor(dot: Dot) = when (dot) {
    Dot.Off -> MaterialTheme.colorScheme.outlineVariant
    Dot.Wait -> MaterialTheme.colorScheme.error
    Dot.On -> MaterialTheme.colorScheme.tertiary
}

/** One not-connected state: a card with a title and its dot, an explanation, and at most one action. */
@Composable
private fun Face(dot: Dot, title: String, hint: String, button: String? = null, onClick: () -> Unit = {}) {
    Card {
        Row(verticalAlignment = Alignment.CenterVertically) {
            StatusDot(dotColor(dot))
            Spacer(Modifier.size(10.dp))
            Text(title, style = MaterialTheme.typography.titleMedium)
        }
        Text(hint, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        if (button != null) PinkButton(button, onClick)
    }
}

/**
 * The pink action button of a card face: white bold text, larger than the body (the owner's choice for pink buttons,
 * interview_002 Q2 = B: contrast 3.63:1 needs large bold text to pass WCAG 3:1).
 */
@Composable
fun PinkButton(text: String, onClick: () -> Unit) {
    Button(onClick = onClick, modifier = Modifier.fillMaxWidth().heightIn(min = BUTTON_MIN_HEIGHT)) {
        Text(text, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = Color.White)
    }
}

@Composable
private fun Connected(name: String, s: SpeakerState, act: SpeakerActions) {
    val dash = stringResource(R.string.value_unknown)
    // Name and the two pills (.a-name).
    Column(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(name.removePrefix(TRIBIT_PREFIX), style = MaterialTheme.typography.titleLarge, textAlign = TextAlign.Center)
        Spacer(Modifier.height(10.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Pill { StatusDot(dotColor(Dot.On)); Text(stringResource(R.string.home_connected), style = MaterialTheme.typography.labelMedium) }
            Pill {
                BatteryIcon(s.battery)
                Text(s.battery?.let { stringResource(R.string.battery_percent, it) } ?: dash, style = MaterialTheme.typography.labelMedium)
            }
        }
    }
    Player(s, act)
    // The section strips (the owner ≈ 19:26: strips, not tiles; the EQ strip shows the preset's response).
    val eqDb = s.eq?.db
    Strip(R.drawable.ic_eq, stringResource(R.string.eq_title), eqName(s), onClick = act.openEq) {
        if (eqDb != null) {
            EqResponse(eqDb, Eq.offset(s.newFirmware ?: true), Modifier.fillMaxWidth().height(RESPONSE_HEIGHT))
            BandLabels(small = true)
        }
    }
    val lightName = when (val m = s.light) {
        null -> dash
        Blast2.LIGHT_OFF -> stringResource(R.string.light_off)
        else -> stringResource(R.string.light_mode, m)
    }
    Strip(R.drawable.ic_light, stringResource(R.string.light_title), lightName, onClick = null) {
        val options = listOf(Blast2.LIGHT_OFF to stringResource(R.string.light_off)) + Blast2.LIGHT_MODES.map { it to it.toString() }
        Choices(options, selected = s.light, enabled = s.light != null, onPick = act.setLight)
    }
    Strip(R.drawable.ic_sliders, stringResource(R.string.speaker_settings), stringResource(R.string.speaker_settings_sub), onClick = act.openSettings)
}

/**
 * The player card (.a-player): the volume slider 0..31 with its number; previous · the big pink «Пауза/Играть» (taken
 * from mock-up C - the owner ≈ 19:26: «кнопккккккку Пауза берём из C большую») · next.
 */
@Composable
private fun Player(s: SpeakerState, act: SpeakerActions) {
    Column(
        Modifier.fillMaxWidth().background(MaterialTheme.colorScheme.surfaceContainer, RoundedCornerShape(28.dp))
            .padding(horizontal = 18.dp, vertical = 16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        // While the finger drags, the slider shows the finger; after release - the speaker's answer to the re-query.
        var dragging by remember { mutableStateOf<Float?>(null) }
        val shown = dragging ?: (s.volume ?: 0).toFloat()
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Icon(painterResource(R.drawable.ic_volume), stringResource(R.string.speaker_volume, s.volume?.toString() ?: "—", Blast2.VOLUME_MAX),
                Modifier.size(22.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
            Slider(
                value = shown,
                onValueChange = { dragging = it },
                onValueChangeFinished = { dragging?.let { act.setVolume(it.roundToInt()) }; dragging = null },
                valueRange = 0f..Blast2.VOLUME_MAX.toFloat(),
                steps = Blast2.VOLUME_MAX - 1,
                enabled = s.volume != null,
                modifier = Modifier.weight(1f),
                colors = SliderDefaults.colors(
                    thumbColor = Color.White, activeTrackColor = MaterialTheme.colorScheme.primary,
                    inactiveTrackColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                    activeTickColor = Color.Transparent, inactiveTickColor = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f),
                ),
            )
            Text(
                if (dragging != null) shown.roundToInt().toString() else s.volume?.toString() ?: stringResource(R.string.value_unknown),
                Modifier.width(32.dp), style = MaterialTheme.typography.titleMedium, textAlign = TextAlign.End,
            )
        }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            val card2 = MaterialTheme.colorScheme.surfaceContainerHigh
            RoundIconButton(R.drawable.ic_prev, stringResource(R.string.track_previous), act.previous, size = 56.dp, container = card2)
            val playing = s.playing == true
            PrimaryButton(
                stringResource(if (playing) R.string.speaker_pause else R.string.speaker_play),
                if (playing) R.drawable.ic_pause else R.drawable.ic_play, act.togglePlay, Modifier.weight(1f),
                enabled = s.playing != null,
            )
            RoundIconButton(R.drawable.ic_next, stringResource(R.string.track_next), act.next, size = 56.dp, container = card2)
        }
    }
}

/** «Tribit StormBox Blast 2» → «StormBox Blast 2» under the drawing: the brand stands in the app's own name above. */
private const val TRIBIT_PREFIX = "Tribit "
private val STAGE_HEIGHT = 190.dp
private val SPEAKER_WIDTH = 280.dp
private val RESPONSE_HEIGHT = 62.dp
