package krinik;

import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;

/**
 * Patch 18 - the speaker is found and connected without location (the owner, 2026-10-15/16). Tribit's own code asks
 * ContextCompat.checkSelfPermission(ctx, ACCESS_FINE_LOCATION) on the permission screens, the search-condition screen
 * and in PairHelper, and refuses to go on without it. Their manifest already declares BLUETOOTH_SCAN with
 * usesPermissionFlags="neverForLocation", so on Android 12+ (API 31) the system scans without location: the demand is
 * Tribit's own, not the platform's. Every own call of ContextCompat.checkSelfPermission is routed here: location reads
 * as granted on API 31+, everything else (and location on Android 8-11, where the system does need it for a Bluetooth
 * scan) is the real check.
 * [TESTED: 2026-10-16 · Titan run testcases/reports/2026-10-16_fork_run2.md - from clean data the permission screen goes on to the main screen without a location permission]
 */
public final class Perm {
    private Perm() {}

    public static int check(Context context, String permission) {
        if (Build.VERSION.SDK_INT >= 31
                && ("android.permission.ACCESS_FINE_LOCATION".equals(permission)
                    || "android.permission.ACCESS_COARSE_LOCATION".equals(permission))) {
            return PackageManager.PERMISSION_GRANTED;
        }
        return context.checkPermission(permission, android.os.Process.myPid(), android.os.Process.myUid());
    }
}
