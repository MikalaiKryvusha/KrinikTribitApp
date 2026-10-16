package com.kriniks.tribit.protocol

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

/**
 * A settings file of the speaker - the owner's idea `ideas/01` (2026-10-16 ≈ 09:20 +03:00: «файлы настроек эквалайзера и
 * подсветки колонки учимся Импортировать json файлом и экспортировать - чтобы сохранить в память телефона и поделиться с
 * другом файлом»). One JSON object:
 *
 *     { "format": "krinik-tribit-profile", "version": 1, "model": "Tribit StormBox Blast 2",
 *       "eq": { "preset": "ROCK" }  or  { "custom_db": [10 numbers, dB] },
 *       "light": { "mode": 1 }   (1..3, or 4 = off) }
 *
 * `[AI]` the field names are the agent's choice (a format nobody reads but this app). The file never carries anything about
 * the user or the phone - only the speaker model and its sound and light. [NOT-TESTED] on the device.
 */
data class Profile(val model: String, val preset: Eq.Preset?, val customDb: List<Int>?, val light: Int?) {

    fun toJson(): String = JSONObject().apply {
        put("format", FORMAT)
        put("version", VERSION)
        put("model", model)
        put("eq", JSONObject().apply {
            if (preset != null) put("preset", preset.name) else put("custom_db", JSONArray(customDb ?: List(Eq.BANDS) { 0 }))
        })
        if (light != null) put("light", JSONObject().put("mode", light))
    }.toString(2)

    /** Why a file is refused - each case has its own text for the user. */
    enum class Problem { NOT_A_PROFILE, OTHER_MODEL, BROKEN }

    companion object {
        const val FORMAT = "krinik-tribit-profile"
        const val VERSION = 1

        /** The current state as a profile; null while the speaker has not reported its EQ. */
        fun of(s: SpeakerState): Profile? {
            val eq = s.eq ?: return null
            return Profile(Blast2.NAME, if (eq.custom) null else eq.preset, if (eq.custom) eq.db else null, s.light)
        }

        /** Reads a file; the problem tells the user what is wrong instead of crashing (`ideas/01`, criterion 5). */
        fun parse(text: String): Result = try {
            val o = JSONObject(text)
            if (o.optString("format") != FORMAT) Result.Refused(Problem.NOT_A_PROFILE)
            else if (!Blast2.isBlast2(o.optString("model"))) Result.Refused(Problem.OTHER_MODEL)
            else {
                val eq = o.getJSONObject("eq")
                val preset = if (eq.has("preset")) Eq.Preset.valueOf(eq.getString("preset")) else null
                val db = if (preset == null) eq.getJSONArray("custom_db").let { a -> List(a.length()) { a.getInt(it) } } else null
                val light = o.optJSONObject("light")?.getInt("mode")
                when {
                    db != null && (db.size != Eq.BANDS || db.any { it !in -Eq.offset(true)..Eq.offset(true) }) ->
                        Result.Refused(Problem.BROKEN)
                    light != null && light !in Blast2.LIGHT_MODES && light != Blast2.LIGHT_OFF -> Result.Refused(Problem.BROKEN)
                    else -> Result.Ok(Profile(Blast2.NAME, preset, db, light))
                }
            }
        } catch (_: JSONException) {
            Result.Refused(Problem.NOT_A_PROFILE)
        } catch (_: IllegalArgumentException) {
            Result.Refused(Problem.BROKEN) // an unknown preset name
        }
    }

    sealed interface Result {
        data class Ok(val profile: Profile) : Result
        data class Refused(val problem: Problem) : Result
    }
}
