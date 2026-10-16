package com.kriniks.tribit.protocol

import org.junit.Assert.assertEquals
import org.junit.Test

/** The settings file of `ideas/01`: round trip, and every refusal the user can meet (criterion 5). */
class ProfileTest {
    private fun ok(text: String) = (Profile.parse(text) as Profile.Result.Ok).profile
    private fun refused(text: String) = (Profile.parse(text) as Profile.Result.Refused).problem

    @Test fun `preset and light round trip`() {
        val p = Profile(Blast2.NAME, Eq.Preset.ROCK, null, 2)
        assertEquals(p, ok(p.toJson()))
    }

    @Test fun `custom bands round trip`() {
        val p = Profile(Blast2.NAME, null, listOf(-12, -6, 0, 3, 6, 6, 0, 0, 12, 12), Blast2.LIGHT_OFF)
        assertEquals(p, ok(p.toJson()))
    }

    @Test fun `profile of the speaker state`() {
        // the custom flat EQ and the light off, as the speaker reported them on the A51 2026-10-16
        val f = Framer().feed(Packet.encode(Eq.CMD_STATE, byteArrayOf(7) + ByteArray(10) { 12 })).single()
        val s = SpeakerState(dsp = 10098, eqFrame = f, light = Blast2.LIGHT_OFF)
        assertEquals(Profile(Blast2.NAME, null, List(10) { 0 }, 4), Profile.of(s))
    }

    @Test fun `refusals`() {
        assertEquals(Profile.Problem.NOT_A_PROFILE, refused("hello"))
        assertEquals(Profile.Problem.NOT_A_PROFILE, refused("""{"format":"other"}"""))
        assertEquals(Profile.Problem.OTHER_MODEL,
            refused("""{"format":"krinik-tribit-profile","version":1,"model":"Tribit XSound Go","eq":{"preset":"ROCK"}}"""))
        assertEquals(Profile.Problem.BROKEN,
            refused("""{"format":"krinik-tribit-profile","version":1,"model":"Tribit StormBox Blast 2","eq":{"custom_db":[1,2]}}"""))
        assertEquals(Profile.Problem.BROKEN,
            refused("""{"format":"krinik-tribit-profile","version":1,"model":"Tribit StormBox Blast 2","eq":{"preset":"LOUD"}}"""))
        assertEquals(Profile.Problem.BROKEN, refused(
            """{"format":"krinik-tribit-profile","version":1,"model":"Tribit StormBox Blast 2","eq":{"preset":"ROCK"},"light":{"mode":9}}"""))
        // our format without "eq" is our damaged file, not «another file» (§7B pass 2026-10-16 17:18)
        assertEquals(Profile.Problem.BROKEN,
            refused("""{"format":"krinik-tribit-profile","version":1,"model":"Tribit StormBox Blast 2"}"""))
    }
}
