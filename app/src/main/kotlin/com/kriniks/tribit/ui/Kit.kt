package com.kriniks.tribit.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.kriniks.tribit.R

/*
 * The shared building blocks of the accepted mock-ups A + A (`design/mockups-v1.html`, `interviews/interview_003`), each one
 * named after its CSS class on the sheet, after KARTUN's `ui/Common.kt` (`researches/11` §4a.1): one set of components for
 * the whole app (the owner, GOAL.md 11:18). Every colour comes from the theme. [NOT-TESTED]
 */

/** Size of a line icon inside a button (.ic). */
private val ICON = 22.dp

/** Round dark button with a line icon (.icon-btn); [size] 44 dp, 56 dp for the track buttons (.icon-btn.big). */
@Composable
fun RoundIconButton(icon: Int, name: String?, onClick: () -> Unit, modifier: Modifier = Modifier, size: Dp = 44.dp,
                    container: Color = MaterialTheme.colorScheme.surfaceContainer, enabled: Boolean = true) {
    Box(
        modifier.size(size).clip(CircleShape).background(container).alpha(if (enabled) 1f else DISABLED)
            .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) { Icon(painterResource(icon), name, Modifier.size(ICON), tint = MaterialTheme.colorScheme.onBackground) }
}

/** The pink pill button with the main action of a screen (.btn.primary): white bold text, a pink glow under it. */
@Composable
fun PrimaryButton(text: String, icon: Int?, onClick: () -> Unit, modifier: Modifier = Modifier, height: Dp = 56.dp, enabled: Boolean = true) {
    val pink = MaterialTheme.colorScheme.primary
    Row(
        modifier.height(height)
            .shadow(if (enabled) 18.dp else 0.dp, CircleShape, ambientColor = pink, spotColor = pink)
            .clip(CircleShape).background(if (enabled) pink else MaterialTheme.colorScheme.surfaceContainerHigh)
            .clickable(enabled = enabled, onClick = onClick).padding(horizontal = 18.dp),
        horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically,
    ) {
        val fg = if (enabled) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
        if (icon != null) { Icon(painterResource(icon), null, Modifier.size(ICON), tint = fg); Spacer(Modifier.width(10.dp)) }
        Text(text, style = MaterialTheme.typography.labelLarge, color = fg, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

/** The dark pill button (.btn.soft) - a pink icon, light text; [outlined] gives the bordered «Отмена» (.btn.ghost). */
@Composable
fun SoftButton(text: String, icon: Int?, onClick: () -> Unit, modifier: Modifier = Modifier, height: Dp = 52.dp,
               outlined: Boolean = false, start: Boolean = false) {
    val c = MaterialTheme.colorScheme
    var m = modifier.height(height).clip(CircleShape)
    m = if (outlined) m.border(1.5.dp, c.outline, CircleShape) else m.background(c.surfaceContainerHigh)
    Row(
        m.clickable(onClick = onClick).padding(horizontal = 18.dp),
        horizontalArrangement = if (start) Arrangement.Start else Arrangement.Center, verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icon != null) { Icon(painterResource(icon), null, Modifier.size(ICON), tint = c.primary); Spacer(Modifier.width(12.dp)) }
        Text(text, style = MaterialTheme.typography.labelLarge, color = c.onSurface, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

/** The pink-soft square behind a section icon (.ico-box). */
@Composable
fun IconBox(icon: Int) {
    Box(
        Modifier.size(40.dp).background(MaterialTheme.colorScheme.primaryContainer, RoundedCornerShape(13.dp)),
        contentAlignment = Alignment.Center,
    ) { Icon(painterResource(icon), null, Modifier.size(ICON), tint = MaterialTheme.colorScheme.primary) }
}

/** A small rounded chip (.pill): the connection dot and the battery on the home screen. */
@Composable
fun Pill(modifier: Modifier = Modifier, content: @Composable RowScope.() -> Unit) {
    Row(
        modifier.clip(CircleShape).background(MaterialTheme.colorScheme.surfaceContainer).padding(horizontal = 13.dp, vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(7.dp), content = content,
    )
}

/**
 * A section as a full-width strip (.a-strip): the owner, 2026-10-16 ≈ 19:26 +03:00: «Виджет эквалайзера, подсветки, настройки
 * колонки делаем не тайлами, а полосками во всю ширину, чтобы можно было уместить больше информации». The head row is the
 * icon, the title, the line under it and a chevron when the strip opens a screen; [content] goes under the head.
 */
@Composable
fun Strip(icon: Int, title: String, subtitle: String?, onClick: (() -> Unit)?, modifier: Modifier = Modifier,
          content: (@Composable ColumnScope.() -> Unit)? = null) {
    var m = modifier.fillMaxWidth().clip(RoundedCornerShape(22.dp)).background(MaterialTheme.colorScheme.surfaceContainer)
    if (onClick != null) m = m.clickable(onClick = onClick)
    Column(m.padding(start = 12.dp, end = 14.dp, top = 12.dp, bottom = 12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            IconBox(icon)
            Column(Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurface)
                if (subtitle != null) Text(subtitle, style = MaterialTheme.typography.bodySmall,
                    // Three lines: the speaker settings list did not fit two at the A51's font scale 1.1 (20:04).
                    color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 3, overflow = TextOverflow.Ellipsis)
            }
            if (onClick != null) Icon(painterResource(R.drawable.ic_chevron), null, Modifier.size(20.dp),
                tint = MaterialTheme.colorScheme.outlineVariant)
        }
        content?.invoke(this)
    }
}

/**
 * A dialog in the centre of the screen (.dim + .dialog): KARTUN's rule - dialogs stand in the centre, never bottom sheets
 * (`researches/11` §4a.1). Title, the line under it, then the dialog's own content.
 */
@Composable
fun CenterDialog(title: String, text: String?, onDismiss: () -> Unit, content: @Composable ColumnScope.() -> Unit) {
    Dialog(onDismissRequest = onDismiss) {
        Column(
            Modifier.fillMaxWidth().background(MaterialTheme.colorScheme.surfaceContainer, RoundedCornerShape(28.dp))
                .padding(start = 20.dp, end = 20.dp, top = 22.dp, bottom = 18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Text(title, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onSurface)
            if (text != null) Text(text, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            content()
        }
    }
}

/** A green connection dot with its glow (.dot). */
@Composable
fun StatusDot(color: Color) {
    Box(Modifier.size(8.dp).background(color, CircleShape))
}

/** A battery icon filled to [percent] (.batt): outlined body, a nub, the fill. */
@Composable
fun BatteryIcon(percent: Int?) {
    val c = MaterialTheme.colorScheme.onSurface
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(width = 24.dp, height = 12.dp).border(1.6.dp, c, RoundedCornerShape(3.dp)).padding(2.dp)) {
            val fill = (percent ?: 0).coerceIn(0, 100) / 100f
            if (fill > 0f) Box(Modifier.fillMaxWidth(fill).height(8.dp).background(c, RoundedCornerShape(1.5.dp)))
        }
        Box(Modifier.padding(start = 1.dp).size(width = 2.dp, height = 5.dp).background(c, RoundedCornerShape(1.dp)))
    }
}

/** Alpha of a control that cannot be used yet (no answer from the speaker). */
private const val DISABLED = 0.4f
