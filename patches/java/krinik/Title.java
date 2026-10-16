package krinik;

/**
 * Patch 27 (patches/apply.py): the title of a speaker settings screen is «Настройки», the speaker name on its own line.
 *
 * Owner 2026-10-16 12:41 +03:00: «Заголовок экрана просто Настройки» · «Отдельной строкой ниже название колонки». Their 13
 * settings screens (and the rename dialog of each) build the title as getString(R.string.settings) + name, which gave
 * «НастройкиTribit StormBox Blast 2» (A51 11:51, shot 15_settings). The 26 calls of ResourceUtils.getString(
 * R.string.settings) in those classes call settings(id) instead: their own text (their ResourceUtils returns the language
 * dictionary's value) plus a line break, so the name they append lands on the second line. Other uses stay.
 * [TESTED: 2026-10-16 · A51 Blast 2 settings title in two lines · testcases/reports/2026-10-16_patch8_anon.md]
 */
public final class Title {
    private Title() {}

    public static String settings(int id) {
        String text;
        try {
            text = (String) Class.forName("com.thousandshores.tool.utils.ResourceUtils")
                    .getMethod("getString", int.class).invoke(null, id);
        } catch (Exception e) {
            return "";
        }
        return text == null ? "" : text + "\n";
    }
}
