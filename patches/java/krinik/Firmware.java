package krinik;

import android.app.Activity;
import android.app.Application;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewTreeObserver;

import java.util.Map;

/**
 * Patch 25 (patches/apply.py): the firmware check runs only when the person asks for it.
 *
 * Owner 2026-10-16 10:45 +03:00 (interviews/interview_001 Q2 = A): «По кнопке «Проверить прошивку» в настройках колонки»;
 * its check: «в журнале при открытии страницы колонки нет checkFirmwareUpgrade; после нажатия — ровно один».
 *
 * Their app asks Tribit by itself whenever a speaker page gets the battery and version from the speaker (A51 2026-10-16
 * 11:43: two requests on the first open). Their settings screens already have the manual path: a tap on the version value
 * (tv_version) runs onClick -> phoneBattery() -> queryFireVersion. So:
 *  - both sinks, ViewModelDeviceBts.queryFireVersion and ViewModelDeviceInfo.queryFireVersion, ask allowBts()/allowInfo()
 *    first: a request passes only when a tap armed it in the last ARM_MS (one request per tap) or, for speakers, when their
 *    own cache already holds the answer (no network then);
 *  - install() watches every activity: in a screen with tv_version a touch on it arms; the whole row ll_fire_version
 *    (label «Версия прошивки» + value) becomes a button that arms and clicks tv_version. 14 layouts have the row
 *    (activity_bts_info*, activity_earphone_info*), so one place serves every speaker and earphone family.
 *  - the answer is theirs: «В настоящее время последняя версия прошивки!» or their update dialog (A51 12:25).
 * [TESTED: 2026-10-16 · A51 Blast 2: auto checks dropped, a row tap sent main + DSP checks, their answer shown ·
 * testcases/reports/2026-10-16_patch8_anon.md] - allowInfo (earphones) not run on a device
 */
public final class Firmware {
    private static final long ARM_MS = 20_000;  // the speaker answers the battery query first, then the app asks Tribit
    private static final long BURST_MS = 3_000; // one tap checks every firmware of the speaker (Blast 2: main + DSP)
    private static long armedAt = -1;
    private static long firstPassAt = -1;

    private Firmware() {}

    /** A tap asked for one firmware check. */
    public static synchronized void arm() {
        armedAt = SystemClock.elapsedRealtime();
        firstPassAt = -1;
    }

    /** true while a tap's window is open: ARM_MS for the first request, then BURST_MS for the other firmwares. */
    private static synchronized boolean takeArm() {
        long now = SystemClock.elapsedRealtime();
        boolean ok = armedAt >= 0 && now - armedAt <= ARM_MS && (firstPassAt < 0 || now - firstPassAt <= BURST_MS);
        if (ok) {
            if (firstPassAt < 0) firstPassAt = now;
        } else {
            armedAt = -1;
        }
        return ok;
    }

    /** Gate of ViewModelDeviceBts.queryFireVersion: true = let it run. */
    public static boolean allowBts(Object vm, Object owner, String deviceName, String packageName, int version, boolean isDsp) {
        boolean ok = takeArm();  // first, so a tap answered from their cache still closes the tap's window
        if (cached(version + "|" + deviceName + "|" + isDsp)) return true;  // their cache: answered, no request
        android.util.Log.i("KrinikFirmware", (ok ? "check on tap: " : "auto check dropped: ") + deviceName);
        return ok;
    }

    /** Gate of ViewModelDeviceInfo.queryFireVersion (earphones; no cache there): true = let it run. */
    public static boolean allowInfo(Object vm, Object owner, String deviceName, String packageName, int version) {
        boolean ok = takeArm();
        android.util.Log.i("KrinikFirmware", (ok ? "check on tap: " : "auto check dropped: ") + deviceName);
        return ok;
    }

    /** PageUtil.INSTANCE.getFireVersionCache().containsKey(key) - their in-memory cache of answers. */
    private static boolean cached(String key) {
        try {
            Class<?> c = Class.forName("com.thousandshores.tribit.utils.PageUtil");
            Object page = c.getField("INSTANCE").get(null);
            Object cache = c.getMethod("getFireVersionCache").invoke(page);
            return cache instanceof Map && ((Map<?, ?>) cache).containsKey(key);
        } catch (Exception e) {
            return false;
        }
    }

    /** Called from TribitApp.onCreate: wires the firmware row of every settings screen. */
    public static void install(Application app) {
        app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
            @Override public void onActivityResumed(Activity a) { wire(a); }
            @Override public void onActivityCreated(Activity a, Bundle b) {}
            @Override public void onActivityStarted(Activity a) {}
            @Override public void onActivityPaused(Activity a) {}
            @Override public void onActivityStopped(Activity a) {}
            @Override public void onActivitySaveInstanceState(Activity a, Bundle b) {}
            @Override public void onActivityDestroyed(Activity a) {}
        });
    }

    private static void wire(Activity a) {
        int versionId = a.getResources().getIdentifier("tv_version", "id", Res.ORIGINAL_PACKAGE);
        int rowId = a.getResources().getIdentifier("ll_fire_version", "id", Res.ORIGINAL_PACKAGE);
        if (versionId == 0 || rowId == 0) return;
        View root = a.getWindow().getDecorView();
        // Fragments add their views after resume: wire on every layout pass until both views are found once.
        root.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
            @Override public void onGlobalLayout() {
                View version = root.findViewById(versionId);
                View row = root.findViewById(rowId);
                if (version == null || row == null) return;
                root.getViewTreeObserver().removeOnGlobalLayoutListener(this);
                version.setOnTouchListener((v, e) -> {
                    if (e.getAction() == MotionEvent.ACTION_UP) arm();
                    return false;  // their own click handler still runs
                });
                row.setOnClickListener(v -> {
                    arm();
                    version.performClick();
                });
            }
        });
    }
}
