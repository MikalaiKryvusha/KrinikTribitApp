package krinik;

import android.content.res.Resources;

/**
 * Debug variant only (patches/apply.py variant_debug): the package is renamed to com.kriniks.tribit.old, but the
 * resource table keeps the original package name, so Tribit's calls of
 * getResources().getIdentifier(name, type, getPackageName()) (about 26-35 of the 73 getIdentifier calls) found nothing - dialogs showed their designer placeholders
 * (seen on the Titan 2026-10-16 01:06: the notification dialog in Chinese). Every Resources.getIdentifier call of the
 * debug build is routed here: the given package first, then the original package name.
 * [TESTED: 2026-10-16 · Titan run testcases/reports/2026-10-16_fork_run2.md - the notification dialog shows its Russian texts]
 */
public final class Res {
    public static final String ORIGINAL_PACKAGE = "com.thousandshores.tribit";

    private Res() {}

    public static int getIdentifier(Resources resources, String name, String type, String pkg) {
        int id = resources.getIdentifier(name, type, pkg);
        if (id == 0 && pkg != null && !ORIGINAL_PACKAGE.equals(pkg)) {
            id = resources.getIdentifier(name, type, ORIGINAL_PACKAGE);
        }
        return id;
    }
}
