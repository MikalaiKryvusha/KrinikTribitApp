package com.kriniks.tribit.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.kriniks.tribit.protocol.Eq
import kotlin.math.roundToInt

/*
 * The EQ curves of the accepted mock-ups (`design/mockups-v1.html`): the graph of a preset (it only SHOWS - the owner,
 * 2026-10-16 ≈ 19:5x: «график … служит редактором, - да, но только для пользовательских пресетов, не для дефолтных»), the
 * response strip of the home screen, the ribbon on a preset card, and the editor of a custom preset. One curve function
 * for all: monotone cubic through the bands (`CurveMath`). [NOT-TESTED]
 */

private val PINK = Color(0xFFFF1A8C)
private val PINK_LIGHT = Color(0xFFFF7CBF)
private val GRID = Color(0xFF2A2A2E)
private val ZERO = Color(0xFF45454B)
private val DASH = PathEffect.dashPathEffect(floatArrayOf(6f, 8f))

/** The curve through [pts] as a Compose path. */
private fun curve(pts: List<Offset>): Path = Path().apply {
    moveTo(pts[0].x, pts[0].y)
    for (s in CurveMath.segments(pts.map { it.x }, pts.map { it.y })) cubicTo(s.c1x, s.c1y, s.c2x, s.c2y, s.x, s.y)
}

/** Band points: x evenly from [left] to width − [right], y from the gain over ±[range] between [top] and [bottom]. */
private fun DrawScope.points(db: List<Int>, range: Int, left: Float, right: Float, top: Float, bottom: Float): List<Offset> {
    val mid = (top + bottom) / 2f
    val half = (bottom - top) / 2f
    return db.mapIndexed { i, v ->
        Offset(left + i * (size.width - left - right) / (db.size - 1), mid - v.coerceIn(-range, range) / range.toFloat() * half)
    }
}

/** The pink line with its glow, and the fill under it down to [floor]. */
private fun DrawScope.drawCurve(pts: List<Offset>, floor: Float, width: Float) {
    val line = curve(pts)
    val fill = Path().apply { addPath(line); lineTo(pts.last().x, floor); lineTo(pts.first().x, floor); close() }
    drawPath(fill, Brush.verticalGradient(listOf(PINK.copy(alpha = 0.45f), PINK.copy(alpha = 0f)), pts.minOf { it.y }, floor))
    drawPath(line, PINK.copy(alpha = 0.3f), style = Stroke(width * 3f, cap = StrokeCap.Round))
    drawPath(line, PINK, style = Stroke(width, cap = StrokeCap.Round))
}

/** Lines at +range, 0 and −range: 0 solid, the edges dashed. */
private fun DrawScope.drawLevels(top: Float, bottom: Float) {
    val mid = (top + bottom) / 2f
    drawLine(GRID, Offset(0f, top), Offset(size.width, top), 1.dp.toPx(), pathEffect = DASH)
    drawLine(GRID, Offset(0f, bottom), Offset(size.width, bottom), 1.dp.toPx(), pathEffect = DASH)
    drawLine(ZERO, Offset(0f, mid), Offset(size.width, mid), 1.dp.toPx())
}

/** The ten band names under a chart, spread as the band points are. */
@Composable
fun BandLabels(modifier: Modifier = Modifier, small: Boolean = false) {
    Row(modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        for (l in Eq.BAND_LABELS) Text(l, style = MaterialTheme.typography.labelSmall.copy(fontSize = if (small) 10.sp else 11.sp),
            color = MaterialTheme.colorScheme.outlineVariant)
    }
}

/**
 * The graph of an EQ that only shows (.graph svg.big): levels, a faint line per band, the filled curve, a small dot on
 * every band - no knobs, nothing to drag. [range] is ±12 on new firmware, ±8 on old (`Eq.offset`).
 */
@Composable
fun EqGraph(db: List<Int>, range: Int, modifier: Modifier = Modifier) {
    Canvas(modifier) {
        val pad = 12.dp.toPx()
        val pts = points(db, range, pad, pad, pad, size.height - pad)
        drawLevels(pad, size.height - pad)
        for (p in pts) drawLine(Color(0xFF232326), Offset(p.x, pad), Offset(p.x, size.height - pad), 1.dp.toPx())
        drawCurve(pts, size.height - pad, 3.dp.toPx())
        for (p in pts) drawCircle(PINK_LIGHT, 2.6.dp.toPx(), p)
    }
}

/** The response strip of the home screen (.a-strip svg.resp): levels and the filled curve. */
@Composable
fun EqResponse(db: List<Int>, range: Int, modifier: Modifier = Modifier) {
    Canvas(modifier) {
        val pad = 6.dp.toPx()
        val pts = points(db, range, pad, pad, pad, size.height - pad)
        drawLevels(pad, size.height - pad)
        drawCurve(pts, size.height, 2.5.dp.toPx())
    }
}

/** The ribbon at the bottom of a preset card (.a-preset svg.art). */
@Composable
fun EqRibbon(db: List<Int>, range: Int, modifier: Modifier = Modifier, color: Color = PINK) {
    Canvas(modifier) {
        val pad = 10.dp.toPx()
        val pts = points(db, range, -pad, -pad, pad, size.height - pad)
        val line = curve(pts)
        val fill = Path().apply { addPath(line); lineTo(size.width + pad, size.height); lineTo(-pad, size.height); close() }
        drawPath(fill, Brush.verticalGradient(listOf(color.copy(alpha = 0.32f), color.copy(alpha = 0f))))
        drawPath(line, color.copy(alpha = 0.35f), style = Stroke(6.dp.toPx()))
        drawPath(line, color, style = Stroke(2.dp.toPx()))
    }
}

/**
 * The editor of a custom preset (.editor): levels every 6 dB with their numbers, a knob on every band, the gain over each
 * band; the band under the finger turns pink. A drag moves the nearest band in whole dB; on release [onRelease] gets all
 * ten bands - the moment the speaker is told (their app sends on release, `researches/11` §3.6). [enabled] false while the
 * speaker has not reported its bands: unknown bands are never drawn as a curve (judge pass D1). [NOT-TESTED]
 */
@Composable
fun EqEditor(db: List<Int>, range: Int, enabled: Boolean, onRelease: (List<Int>) -> Unit, modifier: Modifier = Modifier,
             bandLabels: Boolean = true) {
    var drag by remember { mutableStateOf<List<Int>?>(null) }
    var active by remember { mutableStateOf(-1) }
    val shown = drag ?: db
    val latest by rememberUpdatedState(db)
    val release by rememberUpdatedState(onRelease)
    val measurer = rememberTextMeasurer()
    val labelStyle = MaterialTheme.typography.labelSmall.copy(fontSize = 11.sp, color = MaterialTheme.colorScheme.outlineVariant)
    val valueStyle = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
    val text = MaterialTheme.colorScheme.onSurface
    val sub = MaterialTheme.colorScheme.onSurfaceVariant
    Column(modifier) {
        Canvas(
            Modifier.weight(1f).fillMaxWidth().pointerInput(enabled, range) {
                if (!enabled) return@pointerInput
                val left = AXIS.toPx()
                val right = EDGE.toPx()
                val top = TOP.toPx()
                fun band(x: Float) = ((x - left) / (size.width - left - right) * (Eq.BANDS - 1)).roundToInt().coerceIn(0, Eq.BANDS - 1)
                fun gain(y: Float): Int {
                    val bottom = size.height - EDGE.toPx()
                    val mid = (top + bottom) / 2f
                    return ((mid - y) / ((bottom - top) / 2f) * range).roundToInt().coerceIn(-range, range)
                }
                fun move(o: Offset) {
                    val b = if (active >= 0) active else band(o.x)
                    active = b
                    drag = (drag ?: latest).toMutableList().also { it[b] = gain(o.y) }
                }
                fun done() { drag?.let { if (it != latest) release(it) }; drag = null; active = -1 }
                // The editor takes the touch at once (consumes the down and every move): it stands inside a scrolling page,
                // and on the A51 2026-10-16 19:50 a vertical drag on the graph scrolled the page and moved no band. A touch
                // picks the nearest band, the finger sets its gain, lifting the finger sends all ten bands.
                awaitEachGesture {
                    val down = awaitFirstDown()
                    down.consume()
                    move(down.position)
                    while (true) {
                        val change = awaitPointerEvent().changes.firstOrNull { it.id == down.id } ?: break
                        if (!change.pressed) break
                        move(change.position)
                        change.consume()
                    }
                    done()
                }
            },
        ) {
            val left = AXIS.toPx()
            val top = TOP.toPx()
            val bottom = size.height - EDGE.toPx()
            val mid = (top + bottom) / 2f
            for (v in listOf(range, range / 2, 0, -range / 2, -range)) {
                val y = mid - v / range.toFloat() * (bottom - top) / 2f
                drawLine(if (v == 0) ZERO else GRID, Offset(left - 6.dp.toPx(), y), Offset(size.width, y), 1.dp.toPx(),
                    pathEffect = if (v == 0) null else DASH)
                val t = measurer.measure(signed(v), labelStyle)
                drawText(t, topLeft = Offset(0f, y - t.size.height / 2f))
            }
            val pts = points(shown, range, left, EDGE.toPx(), top, bottom)
            pts.forEachIndexed { i, p ->
                drawLine(if (i == active) PINK.copy(alpha = 0.35f) else Color(0xFF232326), Offset(p.x, top), Offset(p.x, bottom),
                    (if (i == active) 2 else 1).dp.toPx())
            }
            drawCurve(pts, bottom, 3.dp.toPx())
            pts.forEachIndexed { i, p ->
                val on = i == active
                if (on) drawCircle(PINK.copy(alpha = 0.22f), 20.dp.toPx(), p)
                drawCircle(if (on) PINK else Color(0xFF0D0D0D), (if (on) 11 else 8).dp.toPx(), p)
                drawCircle(Color.White, (if (on) 11 else 8).dp.toPx(), p, style = Stroke((if (on) 3f else 2.2f).dp.toPx()))
                val t = measurer.measure(signed(shown[i]),
                    valueStyle.copy(color = if (on) PINK else if (shown[i] != 0) text else sub, fontSize = if (on) 14.sp else 12.sp))
                drawText(t, topLeft = Offset(p.x - t.size.width / 2f, top - TOP.toPx() + 2.dp.toPx()))
            }
        }
        if (bandLabels) BandLabels(Modifier.padding(start = AXIS - 8.dp, end = 0.dp, top = 4.dp))
    }
}

/** Space for the dB numbers left of the editor. */
private val AXIS = 34.dp
/** Space above the top level for the gain numbers. */
private val TOP = 30.dp
/** Margin right and under the bottom level. */
private val EDGE = 14.dp
