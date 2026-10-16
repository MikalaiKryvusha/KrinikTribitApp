package com.kriniks.tribit.ui

import kotlin.math.sqrt

/**
 * The EQ curve through the ten band points - monotone cubic interpolation (Fritsch-Carlson, 1980): between two bands the
 * curve never goes above or below both of them, so a chart never shows a gain the speaker does not have. The mock-up
 * sheet first drew Catmull-Rom and showed a dip under 0 dB beside a +6 band and a peak over +12 (`design/mockups-v1.html`,
 * the same function in its script). Pure Kotlin - tested on the JVM (`CurveMathTest`). [NOT-TESTED] on screen.
 */
object CurveMath {
    /** One cubic segment from the previous end point: two control points and the end point. */
    data class Segment(val c1x: Float, val c1y: Float, val c2x: Float, val c2y: Float, val x: Float, val y: Float)

    /** Segments through [xs]/[ys] (xs strictly increasing, same size ≥ 2); the path starts at (xs[0], ys[0]). */
    fun segments(xs: List<Float>, ys: List<Float>): List<Segment> {
        val n = xs.size
        require(n >= 2 && ys.size == n) { "need ≥ 2 points, got ${xs.size}/${ys.size}" }
        val dx = FloatArray(n - 1) { xs[it + 1] - xs[it] }
        val slope = FloatArray(n - 1) { (ys[it + 1] - ys[it]) / dx[it] }
        val m = FloatArray(n)
        m[0] = slope[0]
        m[n - 1] = slope[n - 2]
        // A local extremum (the slopes change sign) gets a flat tangent: the curve turns AT the band, not past it.
        for (i in 1 until n - 1) m[i] = if (slope[i - 1] * slope[i] <= 0f) 0f else (slope[i - 1] + slope[i]) / 2f
        for (i in 0 until n - 1) {
            if (slope[i] == 0f) { m[i] = 0f; m[i + 1] = 0f; continue }
            val a = m[i] / slope[i]
            val b = m[i + 1] / slope[i]
            val s = a * a + b * b
            if (s > MONOTONE_LIMIT) {
                val t = 3f / sqrt(s)
                m[i] = t * a * slope[i]
                m[i + 1] = t * b * slope[i]
            }
        }
        return List(n - 1) { i ->
            val h = dx[i] / 3f
            Segment(xs[i] + h, ys[i] + m[i] * h, xs[i + 1] - h, ys[i + 1] - m[i + 1] * h, xs[i + 1], ys[i + 1])
        }
    }

    /** Fritsch-Carlson: tangents inside the circle of radius 3 keep the segment monotone. */
    private const val MONOTONE_LIMIT = 9f
}
