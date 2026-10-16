package krinik;

/**
 * Patch 20, widened by patch 8 (patches/apply.py): which requests of their app may reach Tribit's API server.
 *
 * Owner 2026-10-16 10:45 +03:00 (interviews/interview_001 Q1 = C): «только сообщаем, какая колонка просит прошивку и
 * настроек»; 10:52: «мы ПРОТИВ отслеживания метрик через Фаербейз и сервер Трибит». So the rule is an ALLOW list, not a
 * cut list: on their API hosts only the anonymous guest login, the speaker catalog, the firmware check and the text
 * dictionary pass; everything else - statistics points (synchPointStaticTribit; dead in 5.0.0 anyway: UpdateUtils.postPoint
 * is empty), the user profile, the cloud copy of
 * the device list and of EQ presets, the support form, error logs, messages - is cut on the phone by krinik/NoCloud
 * (an IOException, the onHttpFail path their app already handles). Pictures and FAQ pages live on other hosts
 * (resource.1000shores.com, saasadmin.tribit.com) and are not touched.
 * Every request allowed here carries only the speaker model, the language, their client name and app version - read
 * from their request classes (FireUpgrade, GetOtaHistory, DeviceDetail, GetAllDevices, GetDeviceSupport, EquipCategory,
 * EquipCategory2, ProductString) 2026-10-16; the guest login carries Anon's values (patch 8).
 * [TESTED: 2026-10-16 · A51: getUserOfSpNeerInfoTribit cut on the phone (KrinikNoCloud); catalog, guest login and
 * firmware check passed; speaker page opened · testcases/reports/2026-10-16_patch8_anon.md]
 */
public final class Gate {
    /** Their API servers: release (ReleaseServer.smali) and the test one found in the code. */
    private static final String[] API_HOSTS = {"://gateway.tribit.com/", "://testingtribit.1000shores.cn/"};

    private static final String[] ALLOWED = {
        "/api-user/thirdApi/tribit-users/visitorLoginOfTribit",    // the anonymous guest (Anon's values)
        "/api-equip/thirdApi/equip-anon/produCateByClient",        // the speaker catalog (also ...Pre)
        "/api-equip/thirdApi/equip-anon/queryAllThridProducts",    // products and «device support» of one model
        "/api-equip/thirdApi/equip-anon/categorys",                // product categories
        "/api-equip/thirdApi/equip-anon/secondCategorys",
        "/api-app/api/checkFirmwareUpgrade",                       // the firmware check - owner: kept, on a button
        "/api-app/api/otaHistoryUpRecords",                        // firmware history of a model
        "/api-app/api/lang/getLangInfoBySchemaOrLangKey",          // their text dictionary until our values-ru
    };

    private Gate() {}

    /** true = cut this request on the phone. */
    public static boolean cut(String url) {
        if (url == null) return false;
        int host = -1;
        for (String h : API_HOSTS) {
            int i = url.indexOf(h);
            if (i >= 0) { host = i + h.length() - 1; break; }
        }
        if (host < 0) return false;  // not their API server
        int end = url.indexOf('?', host);
        String path = end < 0 ? url.substring(host) : url.substring(host, end);
        for (String a : ALLOWED) {
            if (path.startsWith(a)) return false;
        }
        return true;
    }
}
