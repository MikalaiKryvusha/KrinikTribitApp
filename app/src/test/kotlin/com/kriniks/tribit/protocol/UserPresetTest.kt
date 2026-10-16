package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** Guards the preset file: what is written reads back; a broken or foreign file is skipped; the name limit is 15. */
class UserPresetTest {
    @Test fun roundTrip() {
        val p = UserPreset("1729100000000", "Вечер", listOf(10, 6, -4, -8, -6, 6, 12, 8, 2, 0))
        assertEquals(p, UserPreset.parse(p.id, p.toJson()))
    }

    @Test fun newPresetStartsAtZero() {
        val p = UserPreset.new("1", "  Вечер  ")
        assertEquals(List(Eq.BANDS) { 0 }, p.db)
        assertEquals("Вечер", p.name)
    }

    @Test fun nameLimitIsFifteen() {
        assertTrue(UserPreset.validName("123456789012345"))
        assertFalse(UserPreset.validName("1234567890123456"))
        assertFalse(UserPreset.validName("   "))
    }

    @Test fun brokenFilesAreSkipped() {
        assertNull(UserPreset.parse("x", "not json"))
        assertNull(UserPreset.parse("x", """{"format":"krinik-tribit-profile","name":"a","db":[0,0,0,0,0,0,0,0,0,0]}"""))
        assertNull(UserPreset.parse("x", """{"format":"krinik-tribit-eq","name":"a","db":[0,0,0]}"""))
        assertNull(UserPreset.parse("x", """{"format":"krinik-tribit-eq","name":"a","db":[13,0,0,0,0,0,0,0,0,0]}"""))
        assertNull(UserPreset.parse("x", """{"format":"krinik-tribit-eq","name":"","db":[0,0,0,0,0,0,0,0,0,0]}"""))
    }
}
