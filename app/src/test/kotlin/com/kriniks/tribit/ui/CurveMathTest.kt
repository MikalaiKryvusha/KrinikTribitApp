package com.kriniks.tribit.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Guards the EQ chart: the curve never shows a gain the speaker does not have - between two bands it stays inside their
 * range. The broken version this was proven against: Catmull-Rom (the first mock-up sheet), which goes under 0 dB beside a
 * single +6 band - `catmullRomOvershoots` keeps that failure in view.
 */
class CurveMathTest {
    private val xs = List(10) { it * 10f }

    /** Samples the cubic Bezier segment from [p0] at t in 0..1. */
    private fun sample(p0x: Float, p0y: Float, s: CurveMath.Segment, t: Float): Pair<Float, Float> {
        val u = 1 - t
        val x = u * u * u * p0x + 3 * u * u * t * s.c1x + 3 * u * t * t * s.c2x + t * t * t * s.x
        val y = u * u * u * p0y + 3 * u * u * t * s.c1y + 3 * u * t * t * s.c2y + t * t * t * s.y
        return x to y
    }

    /** True when every sampled point of every segment lies between its two band values. */
    private fun staysInside(ys: List<Float>, segs: List<CurveMath.Segment>): Boolean {
        var px = xs[0]
        var py = ys[0]
        segs.forEachIndexed { i, s ->
            val lo = minOf(ys[i], ys[i + 1]) - EPS
            val hi = maxOf(ys[i], ys[i + 1]) + EPS
            for (k in 0..SAMPLES) if (sample(px, py, s, k / SAMPLES.toFloat()).second !in lo..hi) return false
            px = s.x; py = s.y
        }
        return true
    }

    @Test fun singleBandBoostDoesNotDipUnderZero() {
        val ys = listOf(0f, 0f, 0f, 0f, 0f, 6f, 0f, 0f, 0f, 0f)
        assertTrue(staysInside(ys, CurveMath.segments(xs, ys)))
    }

    @Test fun rockDoesNotPassTwelve() {
        val ys = listOf(10f, 6f, -4f, -8f, -6f, 6f, 12f, 8f, 2f, 0f) // the Rock table of Eq.kt, dB
        assertTrue(staysInside(ys, CurveMath.segments(xs, ys)))
    }

    @Test fun curvePassesThroughEveryBand() {
        val ys = listOf(-8f, -4f, 0f, 6f, 0f, 10f, 2f, -8f, -4f, -12f)
        val segs = CurveMath.segments(xs, ys)
        segs.forEachIndexed { i, s -> assertEquals(xs[i + 1], s.x, 0f); assertEquals(ys[i + 1], s.y, 0f) }
    }

    @Test fun catmullRomOvershoots() {
        // The control case: the old smoothing on the same single +6 band DOES leave the range - so the check can fail.
        val ys = listOf(0f, 0f, 0f, 0f, 0f, 6f, 0f, 0f, 0f, 0f)
        val segs = List(9) { i ->
            val p0 = if (i > 0) i - 1 else i
            val p3 = if (i + 2 < 10) i + 2 else i + 1
            CurveMath.Segment(
                xs[i] + (xs[i + 1] - xs[p0]) / 6, ys[i] + (ys[i + 1] - ys[p0]) / 6,
                xs[i + 1] - (xs[p3] - xs[i]) / 6, ys[i + 1] - (ys[p3] - ys[i]) / 6, xs[i + 1], ys[i + 1],
            )
        }
        assertTrue(!staysInside(ys, segs))
    }

    private companion object {
        const val SAMPLES = 40
        const val EPS = 1e-3f
    }
}
