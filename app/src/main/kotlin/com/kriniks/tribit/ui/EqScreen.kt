package com.kriniks.tribit.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.LocalContentColor
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.kriniks.tribit.R
import com.kriniks.tribit.protocol.Eq
import com.kriniks.tribit.protocol.SpeakerState
import com.kriniks.tribit.protocol.UserPreset

/** A gain as the reader expects it: «+6», «0», «−4» - a typographic minus, no sign at zero (A51 16:50 showed «+0 дБ»). */
fun signed(v: Int): String = when {
    v > 0 -> "+$v"
    v < 0 -> "−${-v}"
    else -> "0"
}

/**
 * The preset's name on screen. For the Blast 2 Tribit's app shows its own names, the same in every language: id 4
 * «Classical» is «X-3D», id 10 «Live» is «XBass Off (V8.6/V7.4)», id 11 «Podcast» is «XBass (V8.6/V7.4)»
 * (`EqButton56Activity.java:347–375`, `Bts56ControlActivity.java:1825`) - found after the owner's «x-3d где???»
 * (2026-10-16 ≈ 19:55 +03:00); the full inventory is `researches/12`. The rest are translated.
 */
@Composable
fun presetName(p: Eq.Preset): String = when (p) {
    Eq.Preset.SIGNATURE -> "TRIBIT Signature"
    Eq.Preset.XBASS -> "XBass"
    Eq.Preset.AUDIOBOOK -> stringResource(R.string.eq_audiobook)
    Eq.Preset.CLASSICAL -> "X-3D"
    Eq.Preset.ROCK -> stringResource(R.string.eq_rock)
    Eq.Preset.JAZZ -> stringResource(R.string.eq_jazz)
    Eq.Preset.BLAST -> stringResource(R.string.eq_blast)
    Eq.Preset.LIVE -> "XBass Off (V8.6/V7.4)"
    Eq.Preset.PODCAST -> "XBass (V8.6/V7.4)"
}

/** What the home strip says about the EQ: the speaker's preset, «Пользовательский», or «—» before the speaker answered. */
@Composable
fun eqName(s: SpeakerState): String {
    val eq = s.eq ?: return stringResource(R.string.value_unknown)
    if (eq.custom) return stringResource(R.string.eq_custom_name)
    return eq.preset?.let { presetName(it) } ?: stringResource(R.string.value_unknown)
}

/** Everything the EQ screens can ask for. */
class EqActions(
    val onPreset: (Eq.Preset) -> Unit,
    val onCustomSlot: () -> Unit,
    val onUserPreset: (UserPreset) -> Unit,
    val onEdit: (List<Int>) -> Unit,
    val onCreate: (String) -> Unit,
    val onRename: (String, String) -> Unit,
    val onFullScreen: () -> Unit,
    val onImport: () -> Unit,
    val onSaveFile: () -> Unit,
    val onShareFile: () -> Unit,
)

/** What is on the speaker, as the EQ screens show it: the name, the bands, and whether the graph edits. */
private class OnSpeaker(val name: String, val db: List<Int>?, val custom: Boolean, val named: UserPreset?)

@Composable
private fun onSpeaker(s: SpeakerState, presets: List<UserPreset>, active: String?): OnSpeaker? {
    val eq = s.eq ?: return null
    if (eq.custom) {
        val named = presets.firstOrNull { it.id == active }
        return OnSpeaker(named?.name ?: stringResource(R.string.eq_custom_name), eq.db, true, named)
    }
    return OnSpeaker(eq.preset?.let { presetName(it) } ?: stringResource(R.string.value_unknown), eq.db, false, null)
}

/**
 * The EQ screen, mock-up A-eq with the owner's corrections (`interviews/interview_003`): the graph of what is on the speaker
 * - it only shows for Tribit's presets and is the editor for a custom one (the owner ≈ 19:5x); the presets as cards two per
 * row, «Пользовательский» first, in colour, with «+» (≈ 19:30); the user's presets after it; «Импорт» / «Экспорт» pinned at
 * the bottom. Every mark is the SPEAKER's answer: the pink border stands on the preset the speaker reported. [NOT-TESTED]
 */
@Composable
fun EqScreen(s: SpeakerState, presets: List<UserPreset>, active: String?, onBack: () -> Unit, act: EqActions) {
    val range = Eq.offset(s.newFirmware ?: true)
    val now = onSpeaker(s, presets, active)
    var dialog by rememberSaveable { mutableStateOf(EqDialog.NONE) }
    Page(
        stringResource(R.string.eq_title), onBack = onBack,
        bottom = {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                SoftButton(stringResource(R.string.eq_import), R.drawable.ic_import, act.onImport, Modifier.weight(1f), height = 56.dp)
                SoftButton(stringResource(R.string.eq_export), R.drawable.ic_export, { dialog = EqDialog.EXPORT }, Modifier.weight(1f), height = 56.dp)
            }
        },
    ) {
        GraphCard(now, range, act, onRename = { dialog = EqDialog.RENAME }, editorHeight = EDITOR_HEIGHT)
        // A named preset on the speaker keeps every move in its file (`editCustom`) - the hint says so (§7B pass 2026-10-16 ≈ 20:0x).
        if (now?.custom == true) Hint(R.drawable.ic_eq, now.named?.let { stringResource(R.string.eq_edit_hint_named, it.name) }
            ?: stringResource(R.string.eq_edit_hint))
        val eq = s.eq
        val cards = buildList<@Composable (Modifier) -> Unit> {
            add { m -> SlotCard(eq?.custom == true && now?.named == null, if (eq?.custom == true && now?.named == null) eq.db else null, range,
                act.onCustomSlot, { dialog = EqDialog.NEW }, m) }
            for (p in presets) add { m ->
                PresetCard(p.name, p.db, range, eq?.custom == true && active == p.id, { act.onUserPreset(p) }, m, Color(USER_TINT))
            }
            for (p in Eq.Preset.entries) add { m ->
                // The preset table is new-firmware wire (dB + 12, `Eq.kt`), whatever the speaker's range.
                PresetCard(presetName(p), p.wire.map { it - Eq.offset(true) }, range, eq != null && !eq.custom && eq.preset == p, { act.onPreset(p) }, m)
            }
        }
        for (row in cards.chunked(2)) Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            for (card in row) card(Modifier.weight(1f))
            if (row.size == 1) Spacer(Modifier.weight(1f))
        }
    }
    EqDialogs(dialog, now, act) { dialog = EqDialog.NONE }
}

/** Which centred dialog of the EQ screens is open. */
enum class EqDialog { NONE, NEW, RENAME, EXPORT }

/** The dialogs shared by the EQ screen and the full-screen editor. */
@Composable
private fun EqDialogs(dialog: EqDialog, now: OnSpeaker?, act: EqActions, close: () -> Unit) {
    when (dialog) {
        EqDialog.NONE -> {}
        EqDialog.NEW -> NameDialog(stringResource(R.string.eq_new), stringResource(R.string.eq_new_hint), "",
            stringResource(R.string.eq_create), { act.onCreate(it); close() }, close)
        EqDialog.RENAME -> {
            val p = now?.named
            // The named preset left the speaker while the dialog was open: nothing to rename, the dialog closes.
            if (p == null) SideEffect(close)
            else NameDialog(stringResource(R.string.eq_rename_title), null, p.name, stringResource(R.string.save),
                { act.onRename(p.id, it); close() }, close)
        }
        EqDialog.EXPORT -> CenterDialog(stringResource(R.string.eq_export_title), stringResource(R.string.eq_export_hint), close) {
            SoftButton(stringResource(R.string.file_save), R.drawable.ic_save, { close(); act.onSaveFile() }, Modifier.fillMaxWidth(), start = true)
            SoftButton(stringResource(R.string.file_share), R.drawable.ic_share, { close(); act.onShareFile() }, Modifier.fillMaxWidth(), start = true)
            SoftButton(stringResource(R.string.cancel), null, close, Modifier.fillMaxWidth(), outlined = true)
        }
    }
}

/** The graph card (.graph): name, «Сейчас на колонке», the expand and pencil buttons of a custom EQ, the graph or editor. */
@Composable
private fun GraphCard(now: OnSpeaker?, range: Int, act: EqActions, onRename: () -> Unit, editorHeight: androidx.compose.ui.unit.Dp) {
    Column(
        Modifier.fillMaxWidth().background(MaterialTheme.colorScheme.surfaceContainer, RoundedCornerShape(28.dp))
            .padding(start = 16.dp, end = 14.dp, top = 16.dp, bottom = 10.dp),
    ) {
        Row(verticalAlignment = Alignment.Top) {
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    // A long name gets the smaller title (the mock-up: «Рок» 26 px, «Пользовательский» 19 px) - on the A51
                    // 19:50 «Пользовательский» in the big title was cut to «Пользовательск…».
                    val name = now?.name ?: stringResource(R.string.value_unknown)
                    Text(name, Modifier.weight(1f, fill = false),
                        style = if (name.length > LONG_NAME) MaterialTheme.typography.titleLarge else MaterialTheme.typography.displaySmall,
                        maxLines = 1, overflow = TextOverflow.Ellipsis)
                    if (now?.named != null) {
                        Spacer(Modifier.width(8.dp))
                        Icon(painterResource(R.drawable.ic_pencil), stringResource(R.string.eq_rename), Modifier.size(32.dp)
                            .clip(CircleShape).clickable(onClick = onRename).padding(6.dp), tint = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                Text(stringResource(R.string.eq_now), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            if (now?.custom == true) RoundIconButton(R.drawable.ic_expand, stringResource(R.string.eq_full_screen), act.onFullScreen,
                size = 40.dp, container = MaterialTheme.colorScheme.surfaceContainerHigh)
        }
        Spacer(Modifier.height(8.dp))
        val db = now?.db
        when {
            db == null -> Spacer(Modifier.height(GRAPH_HEIGHT))
            now.custom -> EqEditor(db, range, enabled = true, onRelease = act.onEdit, modifier = Modifier.fillMaxWidth().height(editorHeight))
            else -> {
                EqGraph(db, range, Modifier.fillMaxWidth().height(GRAPH_HEIGHT))
                BandLabels(Modifier.padding(horizontal = 6.dp, vertical = 4.dp))
            }
        }
    }
}

/** A line of help with its pink icon (.hint). */
@Composable
private fun Hint(icon: Int, text: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Icon(painterResource(icon), null, Modifier.size(20.dp), tint = MaterialTheme.colorScheme.primary)
        Text(text, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

/** A preset card (.a-preset): the name, the preset's own curve as a ribbon, the pink border and tick on the speaker's preset. */
@Composable
private fun PresetCard(name: String, db: List<Int>, range: Int, on: Boolean, onClick: () -> Unit, modifier: Modifier, tint: Color = Color(PINK)) {
    val shape = RoundedCornerShape(22.dp)
    val pink = MaterialTheme.colorScheme.primary
    var m = modifier.height(CARD_HEIGHT).clip(shape)
    m = if (on) m.background(Brush.linearGradient(listOf(pink.copy(alpha = 0.18f), MaterialTheme.colorScheme.surfaceContainer)))
        .border(BorderStroke(1.5.dp, pink), shape)
    else m.background(MaterialTheme.colorScheme.surfaceContainer)
    Box(m.clickable(onClick = onClick)) {
        EqRibbon(db, range, Modifier.fillMaxWidth().height(RIBBON_HEIGHT).align(Alignment.BottomCenter), tint)
        Text(name, Modifier.padding(start = 14.dp, top = 14.dp, end = if (on) 44.dp else 14.dp), style = MaterialTheme.typography.labelLarge.copy(fontSize = CARD_NAME),
            maxLines = 2, overflow = TextOverflow.Ellipsis, color = MaterialTheme.colorScheme.onSurface)
        if (on) Tick(Modifier.align(Alignment.TopEnd).padding(12.dp))
    }
}

/**
 * «Пользовательский» - the speaker's own custom slot, first in the list, in pink-violet, with the «+» that makes a new
 * preset (the owner ≈ 19:30: «Пользовательский нужно выделить цветом, добавить кнопку +, так как это создание пресета»).
 */
@Composable
private fun SlotCard(on: Boolean, db: List<Int>?, range: Int, onClick: () -> Unit, onPlus: () -> Unit, modifier: Modifier) {
    val shape = RoundedCornerShape(22.dp)
    var m = modifier.height(CARD_HEIGHT).clip(shape).background(Brush.linearGradient(listOf(Color(PINK), Color(VIOLET))))
    if (on) m = m.border(BorderStroke(1.5.dp, Color.White), shape)
    Box(m.clickable(onClick = onClick)) {
        EqRibbon(db ?: List(Eq.BANDS) { 0 }, range, Modifier.fillMaxWidth().height(RIBBON_HEIGHT).align(Alignment.BottomCenter),
            Color.White.copy(alpha = 0.85f))
        Text(stringResource(R.string.eq_custom_name), Modifier.padding(start = 14.dp, top = 14.dp, end = 14.dp),
            style = MaterialTheme.typography.labelLarge.copy(fontSize = CARD_NAME), color = Color.White, maxLines = 1,
            overflow = TextOverflow.Ellipsis)
        Box(
            Modifier.align(Alignment.BottomEnd).padding(10.dp).size(34.dp).clip(CircleShape).background(Color.White)
                .clickable(onClick = onPlus),
            contentAlignment = Alignment.Center,
        ) { Icon(painterResource(R.drawable.ic_plus), stringResource(R.string.eq_new), Modifier.size(20.dp), tint = Color(PINK)) }
    }
}

/** The pink tick on the selected card (.tick). */
@Composable
private fun Tick(modifier: Modifier) {
    Box(modifier.size(24.dp).background(MaterialTheme.colorScheme.primary, CircleShape), contentAlignment = Alignment.Center) {
        Icon(painterResource(R.drawable.ic_check), null, Modifier.size(15.dp), tint = Color.White)
    }
}

/**
 * The name dialog: «+» (new preset) and the pencil (rename). A name of up to [UserPreset.NAME_MAX] characters
 * (`interviews/interview_002` Q4), the counter under the field, the confirm button off for an empty name.
 */
@Composable
private fun NameDialog(title: String, text: String?, initial: String, confirm: String, onConfirm: (String) -> Unit, onDismiss: () -> Unit) {
    var name by rememberSaveable { mutableStateOf(initial) }
    CenterDialog(title, text, onDismiss) {
        val c = MaterialTheme.colorScheme
        Box(
            Modifier.fillMaxWidth().height(54.dp).background(c.background, RoundedCornerShape(16.dp))
                .border(1.5.dp, c.primary, RoundedCornerShape(16.dp)).padding(horizontal = 16.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            if (name.isEmpty()) Text(stringResource(R.string.eq_name_field), style = MaterialTheme.typography.bodyLarge, color = c.outlineVariant)
            BasicTextField(
                name, { name = it.take(UserPreset.NAME_MAX) }, Modifier.fillMaxWidth(), singleLine = true,
                textStyle = MaterialTheme.typography.bodyLarge.copy(color = c.onSurface), cursorBrush = SolidColor(c.primary),
            )
        }
        Text(stringResource(R.string.eq_name_counter, name.length, UserPreset.NAME_MAX), Modifier.fillMaxWidth(),
            style = MaterialTheme.typography.labelMedium, color = c.onSurfaceVariant, textAlign = TextAlign.End)
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SoftButton(stringResource(R.string.cancel), null, onDismiss, Modifier.weight(1f), outlined = true)
            PrimaryButton(confirm, null, { onConfirm(name) }, Modifier.weight(1f), height = 52.dp, enabled = UserPreset.validName(name))
        }
    }
}

/**
 * The custom EQ on the full screen (mock-ups A-full-port / A-full-land): the whole screen is the editor; turned to
 * landscape the name and buttons move left and the graph takes the rest (the owner ≈ 19:30: «открыть на полный экран,
 * можно повернуть в лендскейм для удобства»). The activity handles rotation itself (`configChanges`), so the speaker's
 * link stays open. [NOT-TESTED]
 */
@Composable
fun EqFullScreen(s: SpeakerState, presets: List<UserPreset>, active: String?, onBack: () -> Unit, act: EqActions) {
    val now = onSpeaker(s, presets, active)
    val db = now?.db
    val range = Eq.offset(s.newFirmware ?: true)
    var dialog by rememberSaveable { mutableStateOf(EqDialog.NONE) }
    val c = MaterialTheme.colorScheme
    // The content colour is set here: outside Page and Card a Text without a colour is black - on the A51 19:54 the title
    // of this screen was black on black (the same class as `Card`, `testcases/reports/2026-10-16_two_packages.md`).
    CompositionLocalProvider(LocalContentColor provides c.onBackground) {
    BoxWithConstraints(Modifier.fillMaxSize().background(c.background).systemBarsPadding()) {
        val shrink = @Composable { RoundIconButton(R.drawable.ic_shrink, stringResource(R.string.eq_exit_full_screen), onBack) }
        val editor = @Composable { m: Modifier ->
            Box(m.background(c.surfaceContainer, RoundedCornerShape(26.dp)).padding(start = 8.dp, end = 10.dp, top = 10.dp, bottom = 6.dp)) {
                if (db != null) EqEditor(db, range, enabled = true, onRelease = act.onEdit, modifier = Modifier.fillMaxSize())
            }
        }
        if (maxWidth > maxHeight) Row(Modifier.fillMaxSize().padding(18.dp), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
            Column(Modifier.width(SIDE_WIDTH).fillMaxHeight(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                shrink()
                Text(now?.name ?: "", style = MaterialTheme.typography.titleMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
                Text(stringResource(R.string.eq_now), style = MaterialTheme.typography.bodySmall, color = c.onSurfaceVariant)
                Spacer(Modifier.weight(1f))
                if (now?.named != null) SoftButton(stringResource(R.string.eq_rename), R.drawable.ic_pencil, { dialog = EqDialog.RENAME },
                    Modifier.fillMaxWidth(), height = 48.dp)
                SoftButton(stringResource(R.string.eq_export), R.drawable.ic_export, { dialog = EqDialog.EXPORT }, Modifier.fillMaxWidth(), height = 48.dp)
            }
            editor(Modifier.weight(1f).fillMaxHeight())
        } else Column(Modifier.fillMaxSize().padding(horizontal = 20.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // The name and its pencil take all the room up to the button (two weights halved it: «Пользова…», A51 19:56).
                Row(Modifier.weight(1f), verticalAlignment = Alignment.CenterVertically) {
                    val name = now?.name ?: ""
                    Text(name, Modifier.weight(1f, fill = false), maxLines = 1, overflow = TextOverflow.Ellipsis,
                        style = if (name.length > LONG_NAME) MaterialTheme.typography.titleLarge else MaterialTheme.typography.displaySmall)
                    if (now?.named != null) Icon(painterResource(R.drawable.ic_pencil), stringResource(R.string.eq_rename),
                        Modifier.padding(start = 6.dp).size(32.dp).clip(CircleShape).clickable { dialog = EqDialog.RENAME }.padding(6.dp),
                        tint = c.onSurfaceVariant)
                }
                shrink()
            }
            editor(Modifier.weight(1f).fillMaxWidth())
            Hint(R.drawable.ic_rotate, stringResource(R.string.eq_rotate_hint))
        }
    }
    }
    EqDialogs(dialog, now, act) { dialog = EqDialog.NONE }
}

private const val PINK = 0xFFFF1A8C
private const val VIOLET = 0xFF9B2CFF
/** The ribbon colour of the user's own presets - violet, so they stand apart from Tribit's pink presets. */
private const val USER_TINT = 0xFFC77DFF
/** Longer names take the smaller title on the graph card. */
private const val LONG_NAME = 10
/** Card names at 14 sp, as on the mock-up: at 16 sp «Пользовательский» did not fit a phone card (A51 19:50). */
private val CARD_NAME = 14.sp
private val CARD_HEIGHT = 92.dp
private val RIBBON_HEIGHT = 44.dp
private val GRAPH_HEIGHT = 190.dp
private val EDITOR_HEIGHT = 250.dp
private val SIDE_WIDTH = 220.dp
