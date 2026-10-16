package com.kriniks.tribit.ui

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.kriniks.tribit.R
import com.kriniks.tribit.protocol.SpeakerSettings

/** Sleep timer choices in minutes; 0 = off. Their app takes any hour and minute - four steps cover the common use. */
private val SLEEP_CHOICES = listOf(0, 30, 60, 120)


/** What the speaker-settings screen can change; each call writes the setting and reads it back. */
class SettingsActions(
    val autoOff: (Boolean) -> Unit,
    val sleep: (Int) -> Unit,
    val voice: (List<Boolean>) -> Unit,
    val indicator: (Boolean) -> Unit,
    val mic: (Boolean) -> Unit,
    val howl: (Boolean) -> Unit,
)

/** A row with a switch; the switch is the speaker's answer and stays disabled until the speaker answered. */
@Composable
private fun SwitchRow(title: String, value: Boolean?, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text(title, Modifier.weight(1f), style = MaterialTheme.typography.bodyLarge)
        Spacer(Modifier.width(12.dp))
        Switch(
            checked = value == true, onCheckedChange = onChange, enabled = value != null,
            // The default «off» look was a dark thumb on a dark track - invisible on the A51 16:57; grey thumb + border.
            colors = SwitchDefaults.colors(
                checkedTrackColor = MaterialTheme.colorScheme.primary,
                uncheckedThumbColor = MaterialTheme.colorScheme.onSurfaceVariant,
                uncheckedTrackColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                uncheckedBorderColor = MaterialTheme.colorScheme.outlineVariant,
            ),
        )
    }
}

/**
 * «Настройки колонки» (`plans/06` step 6): auto shutdown, sleep timer, voice prompts, volume indicator; microphone
 * boost and anti-howl on «new» firmware only, as in their app (`Bts56InfoActivity.java:383–433`). [NOT-TESTED]
 */
@Composable
fun SpeakerSettingsScreen(s: SpeakerSettings, newFirmware: Boolean?, onBack: () -> Unit, act: SettingsActions) {
    Page(stringResource(R.string.speaker_settings), onBack = onBack) {
        Card {
            SwitchRow(stringResource(R.string.set_auto_off), s.autoOff, act.autoOff)
            SwitchRow(stringResource(R.string.set_indicator), s.indicator, act.indicator)
        }
        Card {
            Text(stringResource(R.string.set_sleep), style = MaterialTheme.typography.titleMedium)
            Text(
                stringResource(R.string.set_sleep_hint), style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            val options = SLEEP_CHOICES.map { m ->
                m to when {
                    m == 0 -> stringResource(R.string.sleep_off)
                    m < 60 -> stringResource(R.string.minutes, m)
                    else -> stringResource(R.string.hours, m / 60)
                }
            }
            Choices(options, selected = s.sleepMinutes, enabled = s.sleepMinutes != null, onPick = act.sleep)
            val other = s.sleepMinutes?.takeIf { it > 0 && it !in SLEEP_CHOICES }
            if (other != null) Text(stringResource(R.string.set_sleep_other, other), style = MaterialTheme.typography.bodyMedium)
        }
        Card {
            Text(stringResource(R.string.set_voice), style = MaterialTheme.typography.titleMedium)
            val names = listOf(
                R.string.voice_power, R.string.voice_pairing, R.string.voice_battery, R.string.voice_max_volume, R.string.voice_tws,
            )
            val flags = s.voice
            names.forEachIndexed { i, name ->
                SwitchRow(stringResource(name), flags?.get(i)) { on ->
                    flags?.let { act.voice(it.toMutableList().also { l -> l[i] = on }) }
                }
            }
        }
        if (newFirmware == true) {
            Card {
                Text(stringResource(R.string.set_mic_title), style = MaterialTheme.typography.titleMedium)
                SwitchRow(stringResource(R.string.set_mic), s.mic, act.mic)
                SwitchRow(stringResource(R.string.set_howl), s.howl, act.howl)
            }
        }
    }
}
