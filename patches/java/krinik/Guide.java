package krinik;

import java.util.Locale;

/**
 * Patch 32 (patches/apply.py): no way out of Krinik Tribit to Tribit - their help center becomes our user guide.
 *
 * Owner 2026-10-16 13:32 +03:00: «ни на какую поддерку Трибита и на их сайт, форумы - мы не ведем из Krinik Tribit.
 * Убираем это. В О приложении будет ссылка на GH Криника»; 13:38 +03:00 (interviews/interview_002 Q3): «в руководстве
 * пользователя, которое ты сделаешь в настройках приложения по аналогии с KARTUN и Krinik Cam, укажем про возможность в
 * андроид очистить данные приложения - это можно использовать для сбросса аккаунта.»
 *
 * Their «help center» row of the profile and the «?» of every speaker and earphone page opened Tribit's web pages
 * (gtwt.1000shores.cn/tribit_help_*, the speaker's FAQ URL from their server) in their WebViewActivity. Every one of those
 * entry points (MineActivity/MineFragment/DeviceHelpNewActivity.goHelpCenter, UpdateUtils.goDeviceHelp) calls open()
 * instead: the same WebViewActivity shows our guide from the APK's assets (assets/krinik/guide_ru.html, guide_en.html) -
 * no request leaves the phone. Their WebViewActivity is reached by reflection: our dex is compiled against android.jar only.
 * [TESTED: 2026-10-16 · A51: profile row and Blast 2 «?» open guide_ru.html, 0 requests; About shows GITHUB as a link ·
 * testcases/reports/2026-10-16_patch31_32.md] - the English page not opened
 */
public final class Guide {
    /** The user guide inside the APK (patches/assets/krinik/, copied by patch 32). */
    private static final String URL_RU = "file:///android_asset/krinik/guide_ru.html";
    private static final String URL_EN = "file:///android_asset/krinik/guide_en.html";
    /** Our repository - the canon of AGENT_GUIDE.md → Project identity. */
    public static final String GITHUB = "https://github.com/MikalaiKryvusha/KrinikTribitApp";
    private static final String WEB_VIEW = "com.thousandshores.tribit.modulecommon.webview.WebViewActivity";

    private Guide() {}

    /** Russian for a Russian-speaking phone, English for everyone else (the two languages the guide is written in). */
    private static boolean ru() {
        String lang = Locale.getDefault().getLanguage();
        return "ru".equals(lang) || "be".equals(lang) || "uk".equals(lang);
    }

    /** The title of the guide - the label of the profile row and of the guide screen. The id (their help_center) is unused. */
    public static String title(int ignored) {
        return ru() ? "Руководство пользователя" : "User guide";
    }

    /** About screen: our GitHub instead of their support e-mail. The id (their contact_email) is unused. */
    public static String github(int ignored) {
        return GITHUB;
    }

    /** Opens the guide in their web view screen. */
    public static void open() {
        try {
            Class.forName(WEB_VIEW).getMethod("startWithUrl", String.class, String.class)
                    .invoke(null, title(0), ru() ? URL_RU : URL_EN);
        } catch (Exception e) {
            android.util.Log.e("KrinikGuide", "guide not opened", e);
        }
    }
}
