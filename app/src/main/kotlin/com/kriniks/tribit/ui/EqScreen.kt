package com.kriniks.tribit.ui

import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.kriniks.tribit.R
import com.kriniks.tribit.protocol.Eq
import com.kriniks.tribit.protocol.SpeakerState
import kotlin.math.roundToInt

/** Width of the band label column («16K») - the sliders line up. */
private val BAND_LABEL_WIDTH = 44.dp

/** Width of the value column («+12 дБ»). */
private val BAND_VALUE_WIDTH = 64.dp

/** A gain as the reader expects it: «+6», «0», «−4» - a typographic minus, no sign at zero (A51 16:50 showed «+0 дБ»). */
fun signed(v: Int): String = when {
    v > 0 -> "+$v"
    v < 0 -> "−${-v}"
    else -> "0"
}

/** The preset's name on screen; the brand names stay as Tribit writes them, the rest are translated. */
@Composable
fun presetName(p: Eq.Preset): String = when (p) {
    Eq.Preset.SIGNATURE -> "TRIBIT Signature"
    Eq.Preset.XBASS -> "XBass"
    Eq.Preset.AUDIOBOOK -> stringResource(R.string.eq_audiobook)
    Eq.Preset.CLASSICAL -> stringResource(R.string.eq_classical)
    Eq.Preset.ROCK -> stringResource(R.string.eq_rock)
    Eq.Preset.JAZZ -> stringResource(R.string.eq_jazz)
    Eq.Preset.BLAST -> stringResource(R.string.eq_blast)
    Eq.Preset.LIVE -> stringResource(R.string.eq_live)
    Eq.Preset.PODCAST -> stringResource(R.string.eq_podcast)
}

/** What the home card says about the EQ: the speaker's preset, «Пользовательский», or «—» before the speaker answered. */
@Composable
fun eqName(s: SpeakerState): String {
    val eq = s.eq ?: return stringResource(R.string.value_unknown)
    if (eq.custom) return stringResource(R.string.eq_custom_name)
    return eq.preset?.let { presetName(it) } ?: stringResource(R.string.value_unknown)
}

/**
 * The EQ screen (`plans/06` step 3): presets, the one the speaker reports marked pink; ten bands showing the speaker's
 * current curve. A band is sent on release, as the custom EQ with all ten bands (cmd 11). [NOT-TESTED]
 */
@Composable
fun EqScreen(
    s: SpeakerState, onBack: () -> Unit, onPreset: (Eq.Preset) -> Unit, onCustom: (List<Int>) -> Unit,
    onSaveFile: () -> Unit, onOpenFile: () -> Unit,
) {
    val eq = s.eq
    val range = Eq.offset(s.newFirmware ?: true)
    // Finger positions while dragging, by band; released bands fall back to the speaker's value.
    val dragging = remember { mutableStateMapOf<Int, Float>() }
    Page(stringResource(R.string.eq_title), onBack = onBack) {
        Card {
            Text(stringResource(R.string.eq_presets), style = MaterialTheme.typography.titleMedium)
            for (p in Eq.Preset.entries) {
                val selected = eq != null && !eq.custom && eq.preset == p
                val border = if (selected) MaterialTheme.colorScheme.primary else Color.Transparent
                Row(
                    Modifier.fillMaxWidth().border(2.dp, border, MaterialTheme.shapes.small)
                        .clickable { onPreset(p) }.padding(horizontal = 14.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        presetName(p), style = MaterialTheme.typography.labelLarge,
                        fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                    )
                }
            }
        }
        Card {
            val title = stringResource(R.string.eq_custom)
            Text(if (eq?.custom == true) "$title ✓" else title, style = MaterialTheme.typography.titleMedium)
            Text(
                stringResource(R.string.eq_custom_hint), style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            val current = eq?.db ?: List(Eq.BANDS) { 0 }
            for (band in 0 until Eq.BANDS) {
                val value = dragging[band] ?: current[band].toFloat()
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(Eq.BAND_LABELS[band], Modifier.width(BAND_LABEL_WIDTH), style = MaterialTheme.typography.labelMedium)
                    Slider(
                        value = value,
                        onValueChange = { dragging[band] = it },
                        onValueChangeFinished = {
                            val db = List(Eq.BANDS) { i -> dragging[i]?.roundToInt() ?: current[i] }
                            dragging.clear()
                            onCustom(db)
                        },
                        valueRange = -range.toFloat()..range.toFloat(),
                        steps = 2 * range - 1,
                        enabled = eq != null,
                        modifier = Modifier.weight(1f),
                        colors = SliderDefaults.colors(
                            thumbColor = MaterialTheme.colorScheme.primary,
                            activeTrackColor = MaterialTheme.colorScheme.primary,
                            activeTickColor = Color.Transparent, inactiveTickColor = Color.Transparent,
                        ),
                    )
                    Text(
                        stringResource(R.string.eq_db, signed(value.roundToInt())), Modifier.width(BAND_VALUE_WIDTH),
                        style = MaterialTheme.typography.labelMedium,
                    )
                }
            }
        }
        // The settings file (`ideas/01`): the EQ and the light of the speaker in one JSON file.
        Card {
            Text(stringResource(R.string.file_title), style = MaterialTheme.typography.titleMedium)
            Text(
                stringResource(R.string.file_hint), style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            SettingsRow(stringResource(R.string.file_save), inCard = true, onClick = onSaveFile)
            SettingsRow(stringResource(R.string.file_open), inCard = true, onClick = onOpenFile)
        }
        Spacer(Modifier.padding(4.dp))
    }
}
