package com.kriniks.tribit.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.scale

/**
 * The StormBox Blast 2 drawn for Krinik Tribit - the symbol `spk` of the accepted mock-up sheet (`design/mockups-v1.html`,
 * viewBox 300×180): the handle, the barrel body, the mesh grille, the end caps with the light rings. No picture of Tribit's
 * app is used (whether a photo replaces it is `interviews/interview_004`). [lit] paints the rings pink - the light is on;
 * off they are grey. [NOT-TESTED]
 */
@Composable
fun SpeakerArt(modifier: Modifier = Modifier, lit: Boolean = true) {
    Canvas(modifier.aspectRatio(W / H)) {
        scale(size.width / W, size.height / H, pivot = Offset.Zero) { speaker(lit) }
    }
}

private const val W = 300f
private const val H = 180f
private val PINK = Color(0xFFFF1A8C)
private val PINK_LIGHT = Color(0xFFFF7CBF)
private val RING_OFF = Color(0xFF3A3A40)

private fun DrawScope.speaker(lit: Boolean) {
    // Shadow under the speaker.
    drawOval(Color.Black.copy(alpha = 0.6f), Offset(32f, 163f), Size(236f, 14f))
    // Handle: a dark arc with a thin highlight.
    val handle = Path().apply { moveTo(86f, 70f); cubicTo(92f, 20f, 208f, 20f, 214f, 70f) }
    drawPath(handle, Color(0xFF1C1C1F), style = Stroke(16f, cap = StrokeCap.Round))
    val shine = Path().apply { moveTo(90f, 66f); cubicTo(97f, 27f, 203f, 27f, 210f, 66f) }
    drawPath(shine, Color(0xFF3B3B40), style = Stroke(2f, cap = StrokeCap.Round))
    // Body.
    val body = Brush.verticalGradient(listOf(Color(0xFF3A3A3E), Color(0xFF1F1F22), Color(0xFF111113)), 62f, 164f)
    drawRoundRect(body, Offset(18f, 62f), Size(264f, 102f), CornerRadius(50f))
    // Grille: dots on a dark field.
    drawRoundRect(Color(0xFF19191B), Offset(72f, 74f), Size(156f, 78f), CornerRadius(26f))
    var y = 80f
    while (y < 148f) {
        var x = 78f
        while (x < 224f) { drawCircle(Color(0xFF34343A), 1.25f, Offset(x, y)); x += 6f }
        y += 6f
    }
    drawRoundRect(Color(0xFF4B4B52), Offset(136f, 108f), Size(28f, 7f), CornerRadius(3.5f))
    // End caps with the light rings.
    for (cx in listOf(46f, 254f)) {
        val cap = Brush.verticalGradient(listOf(Color(0xFF2C2C30), Color(0xFF0F0F11)), 66f, 160f)
        drawOval(cap, Offset(cx - 27f, 66f), Size(54f, 94f))
        drawOval(Color(0xFF2F2F34), Offset(cx - 27f, 66f), Size(54f, 94f), style = Stroke(2f))
        if (lit) drawOval(PINK.copy(alpha = 0.35f), Offset(cx - 20f, 77f), Size(40f, 72f), style = Stroke(10f))
        drawOval(if (lit) PINK_LIGHT else RING_OFF, Offset(cx - 17f, 80f), Size(34f, 66f), style = Stroke(if (lit) 3f else 2f))
        drawOval(Color(0xFF121214), Offset(cx - 9f, 93f), Size(18f, 40f))
    }
    // Glass highlight over the body.
    val glass = Brush.verticalGradient(listOf(Color.White.copy(alpha = 0.14f), Color.Transparent), 62f, 103f)
    drawRoundRect(glass, Offset(18f, 62f), Size(264f, 102f), CornerRadius(50f))
}
