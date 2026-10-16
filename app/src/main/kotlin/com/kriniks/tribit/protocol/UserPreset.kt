package com.kriniks.tribit.protocol

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

/**
 * A custom EQ preset the user made with «+» - one file in the app's folder (the owner, 2026-10-16 ≈ 19:4x +03:00:
 * «пресеты хранить в директории приложения файлами»; `interviews/interview_003`). The speaker has ONE custom slot
 * (cmd 11, `Eq.kt`): choosing a preset sends its ten bands there. A new preset starts at 0 dB on every band (the owner
 * ≈ 19:4x: «новый эквалайзер начинается с нулей»); a name holds up to [NAME_MAX] characters, as in Tribit's app
 * (`interviews/interview_002` Q4). One JSON object:
 *
 *     { "format": "krinik-tribit-eq", "version": 1, "name": "…", "db": [10 numbers, dB] }
 *
 * `[AI]` the field names are the agent's choice. [id] is the file name without `.json` - the moment of creation, so the
 * list keeps the order the presets were made in. Pure Kotlin, tested on the JVM (`UserPresetTest`). [NOT-TESTED] on the device.
 */
data class UserPreset(val id: String, val name: String, val db: List<Int>) {

    fun toJson(): String = JSONObject().apply {
        put("format", FORMAT)
        put("version", VERSION)
        put("name", name)
        put("db", JSONArray(db))
    }.toString(2)

    companion object {
        const val FORMAT = "krinik-tribit-eq"
        const val VERSION = 1
        const val NAME_MAX = 15

        /** The widest band gain any Blast 2 firmware takes («new» firmware: ±12 dB, `Eq.offset`). */
        private val GAIN = -Eq.offset(true)..Eq.offset(true)

        /** A fresh preset: [name] trimmed to [NAME_MAX], every band at 0 dB. */
        fun new(id: String, name: String) = UserPreset(id, name.trim().take(NAME_MAX), List(Eq.BANDS) { 0 })

        /** True when [name] can name a preset: not blank, at most [NAME_MAX] characters. */
        fun validName(name: String) = name.isNotBlank() && name.trim().length <= NAME_MAX

        /** Reads a preset file; null for anything that is not a whole, valid preset (a broken file is skipped, never shown). */
        fun parse(id: String, text: String): UserPreset? = try {
            val o = JSONObject(text)
            val a = o.getJSONArray("db")
            val db = List(a.length()) { a.getInt(it) }
            val name = o.getString("name")
            if (o.optString("format") != FORMAT || db.size != Eq.BANDS || db.any { it !in GAIN } || !validName(name)) null
            else UserPreset(id, name.trim(), db)
        } catch (_: JSONException) { null }
    }
}
