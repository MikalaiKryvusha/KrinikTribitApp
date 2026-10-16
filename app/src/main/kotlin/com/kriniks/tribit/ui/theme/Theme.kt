package com.kriniks.tribit.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontVariation
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.kriniks.tribit.R

/**
 * Krinik's style for Krinik Tribit - the ONE place colours, shapes and type live. The tokens are KARTUN's
 * (`KARTUN/app/.../ui/theme/Theme.kt`, accepted there by the owner): near-black background, flat dark cards, one pink
 * accent #FF1A8C (HOUSE_RULES.md R3). Dark theme only. [NOT-TESTED]
 */
private val Pink = Color(0xFFFF1A8C)
private val Bg = Color(0xFF0D0D0D)
private val Surface = Color(0xFF151516)
private val Card = Color(0xFF1C1C1E)
private val Card2 = Color(0xFF262628)
private val Line = Color(0xFF2E2E31)
private val Text = Color(0xFFF5F5F7)
private val Sub = Color(0xFFA1A1A6)
private val Mute = Color(0xFF6E6E73)
private val PinkSoft = Color(0x24FF1A8C)
private val Green = Color(0xFF3DDC84)
private val Amber = Color(0xFFFFB020)

private val Colors = darkColorScheme(
    primary = Pink, onPrimary = Color.White, primaryContainer = PinkSoft, onPrimaryContainer = Pink,
    background = Bg, onBackground = Text,
    surface = Bg, onSurface = Text,
    surfaceContainerLowest = Bg, surfaceContainerLow = Surface, surfaceContainer = Card,
    surfaceContainerHigh = Card2, surfaceContainerHighest = Card2,
    onSurfaceVariant = Sub, outline = Line, outlineVariant = Mute,
    tertiary = Green, error = Amber, onError = Color.Black,
    scrim = Color(0x8C000000),
)

// Unbounded for headings, Manrope for text - KARTUN's pair (OFL, licences in docs/licenses/).
private fun variable(res: Int, weight: Int) =
    Font(res, FontWeight(weight), variationSettings = FontVariation.Settings(FontVariation.weight(weight)))

private val Unbounded = FontFamily(variable(R.font.unbounded, 600), variable(R.font.unbounded, 700), variable(R.font.unbounded, 800))
private val Manrope = FontFamily(
    variable(R.font.manrope, 400), variable(R.font.manrope, 500), variable(R.font.manrope, 600),
    variable(R.font.manrope, 700), variable(R.font.manrope, 800),
)

private val Type = Typography(
    displaySmall = TextStyle(fontFamily = Unbounded, fontWeight = FontWeight(800), fontSize = 24.sp, letterSpacing = 0.5.sp),
    titleLarge = TextStyle(fontFamily = Unbounded, fontWeight = FontWeight(700), fontSize = 20.sp),
    titleMedium = TextStyle(fontFamily = Unbounded, fontWeight = FontWeight(700), fontSize = 16.sp),
    bodyLarge = TextStyle(fontFamily = Manrope, fontWeight = FontWeight(400), fontSize = 15.sp, lineHeight = 22.sp),
    bodyMedium = TextStyle(fontFamily = Manrope, fontWeight = FontWeight(400), fontSize = 14.sp, lineHeight = 20.sp),
    bodySmall = TextStyle(fontFamily = Manrope, fontWeight = FontWeight(400), fontSize = 13.sp, lineHeight = 18.sp),
    labelLarge = TextStyle(fontFamily = Manrope, fontWeight = FontWeight(700), fontSize = 16.sp, letterSpacing = 0.3.sp),
    labelMedium = TextStyle(fontFamily = Manrope, fontWeight = FontWeight(600), fontSize = 14.sp),
)

private val KShapes = Shapes(
    small = RoundedCornerShape(14.dp), medium = RoundedCornerShape(20.dp),
    large = RoundedCornerShape(24.dp), extraLarge = RoundedCornerShape(28.dp),
)

@Composable
fun KrinikTheme(content: @Composable () -> Unit) =
    MaterialTheme(colorScheme = Colors, typography = Type, shapes = KShapes, content = content)
