package krinik;

import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;

/**
 * Patch 8 (patches/apply.py): the anonymous guest that Krinik Tribit shows to Tribit's server instead of the person.
 *
 * Owner 2026-10-16 10:45 +03:00 (interviews/interview_001 Q1 = C): «работаем с сервером трибит анонимным аккаунтом без
 * передачи им данных о пользователе, девайс ид и прочее»; accepted 11:00 +03:00 («ДА, принято»): the guest ID is random
 * 16 hex characters per install; the phone model and Android version are a random real pair from the device base, picked
 * ONCE per install (MASTER_PLAN decision journal); 11:07: Android 15 or 16 only. No reset button (interviews/interview_002
 * Q3 = A, 13:38 «А, без кнопки»): a new guest = reinstall, or Android's «Clear data» of the app (wipes these preferences
 * and their guest_token) - the user guide in the app's settings says so.
 *
 * Their app builds the guest login (VistitorLogin) from the MAC or ANDROID_ID, Build.MODEL and the real Android version;
 * patch 8 makes the VistitorLogin constructor take these three values from here instead, so the URL and the JSON body
 * (both built by EasyHttp from the fields) carry no value of the real device. Nothing here is derived from the device.
 * [TESTED: 2026-10-16 · A51: guest login sent emailAccount 595d7715c57e567e, logMobModel Infinix X6836, operSystem
 * Android 16; anon_check.py 0 real values · testcases/reports/2026-10-16_patch8_anon.md] - persistence across two guest logins not observed yet
 */
public final class Anon {
    private static final String PREFS = "krinik_anon";
    private static final String KEY_ID = "guest_id";
    private static final String KEY_MODEL = "model";
    private static final String KEY_OS = "os";
    private static final String DEVICE_BASE = "krinik/devices.txt";  // patch 22, one `Brand|Model` per line
    private static final String[] ANDROID_VERSIONS = {"15", "16"};   // owner 11:07: «андроит 15 и выше»
    private static final String FALLBACK_MODEL = "Android";          // owner 10:58: «Android - суппер» (base unreadable)
    private static final int ID_BYTES = 8;                           // 16 hex characters, the length of ANDROID_ID
    private static final SecureRandom RANDOM = new SecureRandom();

    private Anon() {}

    /** The guest ID sent as emailAccount: random per install, kept until the app's data is cleared or it is reinstalled. */
    public static synchronized String id() {
        SharedPreferences p = prefs();
        String id = p.getString(KEY_ID, null);
        if (id == null) {
            byte[] b = new byte[ID_BYTES];
            RANDOM.nextBytes(b);
            StringBuilder s = new StringBuilder();
            for (byte x : b) s.append(String.format("%02x", x & 0xff));
            id = s.toString();
            p.edit().putString(KEY_ID, id).apply();
        }
        return id;
    }

    /** The phone model sent as logMobModel: a random line of the device base, picked once per install. */
    public static synchronized String model() {
        SharedPreferences p = prefs();
        String model = p.getString(KEY_MODEL, null);
        if (model == null) {
            List<String> models = readModels();
            model = models.isEmpty() ? FALLBACK_MODEL : models.get(RANDOM.nextInt(models.size()));
            p.edit().putString(KEY_MODEL, model).apply();
        }
        return model;
    }

    /** The system sent as operSystem, in their format «Android <version>»: 15 or 16, picked once per install. */
    public static synchronized String os() {
        SharedPreferences p = prefs();
        String os = p.getString(KEY_OS, null);
        if (os == null) {
            os = "Android " + ANDROID_VERSIONS[RANDOM.nextInt(ANDROID_VERSIONS.length)];
            p.edit().putString(KEY_OS, os).apply();
        }
        return os;
    }

    private static List<String> readModels() {
        List<String> models = new ArrayList<>();
        try (BufferedReader r = new BufferedReader(new InputStreamReader(
                app().getAssets().open(DEVICE_BASE), StandardCharsets.UTF_8))) {
            String line;
            while ((line = r.readLine()) != null) {
                int bar = line.indexOf('|');
                if (bar > 0 && bar < line.length() - 1) models.add(line.substring(bar + 1));
            }
        } catch (Exception e) {
            android.util.Log.w("KrinikAnon", "device base unreadable: " + e);
        }
        return models;
    }

    private static SharedPreferences prefs() {
        return app().getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    /** The running Application: the request constructors that call us get no Context. */
    private static Application app() {
        try {
            return (Application) Class.forName("android.app.ActivityThread")
                    .getMethod("currentApplication").invoke(null);
        } catch (Exception e) {
            throw new IllegalStateException("Krinik Tribit: no Application", e);
        }
    }
}
