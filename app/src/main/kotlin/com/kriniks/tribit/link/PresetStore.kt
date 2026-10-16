package com.kriniks.tribit.link

import com.kriniks.tribit.protocol.UserPreset
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/**
 * The user's custom presets as files in the app's own folder `files/presets/<id>.json` (the owner, 2026-10-16 ≈ 19:4x
 * +03:00: «пресеты хранить в директории приложения файлами»). Private storage: no permission, removed with the app.
 * Disk work runs on Dispatchers.IO (StrictMode in debug logs any main-thread disk access). [NOT-TESTED]
 */
class PresetStore(private val filesDir: () -> File) {
    /** Resolved on Dispatchers.IO only: the first `getFilesDir()` of a process may create the folder. */
    private val dir get() = File(filesDir(), DIR)

    /** Every readable preset in the order they were made; an unreadable file is skipped. */
    suspend fun list(): List<UserPreset> = withContext(Dispatchers.IO) {
        val dir = dir
        dir.listFiles { f -> f.isFile && f.name.endsWith(EXT) }.orEmpty().sortedBy { it.name }
            .mapNotNull { f -> runCatching { UserPreset.parse(f.name.removeSuffix(EXT), f.readText()) }.getOrNull() }
    }

    /** Writes [p] (new or changed) through a temporary file, so a crash mid-write never leaves half a preset. */
    suspend fun save(p: UserPreset): Boolean = withContext(Dispatchers.IO) {
        runCatching {
            val dir = dir
            dir.mkdirs()
            val tmp = File(dir, "${p.id}$EXT.tmp")
            tmp.writeText(p.toJson())
            check(tmp.renameTo(File(dir, "${p.id}$EXT")))
        }.isSuccess
    }

    private companion object {
        const val DIR = "presets"
        const val EXT = ".json"
    }
}
