"""Build the compact device base that Krinik Tribit picks a random phone from (owner, 2026-10-16: «скачай БД из ГУГЛ
телефонов, кладём внутрь АПК» · «не больше 1 мб» · «давай возьмём популярные девайсы» · «можно меньше» 10 000).

Usage:
    curl -sSL -o tools/devices/raw/supported_devices.csv https://storage.googleapis.com/play_public/supported_devices.csv
    python tools/devices/make_device_base.py tools/devices/raw/supported_devices.csv patches/assets/krinik_devices.txt
Input: Google Play's public supported-devices list (UTF-16 CSV: Retail Branding, Marketing Name, Device, Model).
Output: one `Brand|Model` per line, sorted, deduplicated, ASCII only - the Model column is what Build.MODEL reports.
The list has no sales data: «popular» is approximated by the main smartphone brands below ([AI] choice of the agent,
not a market-share source) and a cap on the line count. The file must stay under MAX_BYTES (the owner's 1 MB).
[TESTED: 2026-10-16 · 1134 devices, 18978 bytes, 15 brands; A51 (2019) excluded; a 25-name random sample all 2022+]
"""
import csv
import io
import pathlib
import re
import sys

BRANDS = {  # [AI] main smartphone brands; Retail Branding values as Google writes them, compared lowercase
    "samsung", "xiaomi", "redmi", "poco", "google", "oneplus", "oppo", "vivo", "realme", "motorola", "honor",
    "nokia", "sony", "tecno", "infinix", "asus", "nothing",  # no huawei (no Google services), no zte/lenovo (old A-names)
}
# Owner 2026-10-16 ≈ 11:05 +03:00: «давай только новые модели, от 2022 года и новее» · «андроит 15 и выше» · «только
# популярные девайсы». The Google list carries neither a release year nor sales: [AI] the series below are the mass-market
# lines of the main brands released in 2022 or later, chosen by the agent from public knowledge of the line-ups, not from
# sales data. The Android version (15 or 16) is picked at run time - the list has no versions.
SERIES = re.compile(
    r"^(Galaxy (S2[2-5]( ?\+| Ultra| FE)?|A(1[3-7]|2[3-6]|3[3-6]|5[3-6]|73)( 5G)?|M(1[4-5]|3[4-5]|5[4-5])( 5G)?|"
    r"Z (Flip|Fold) ?[4-7])|"
    r"Redmi Note 1[1-4]( Pro| Pro\+| 5G| S|S)*|Redmi 1[2-5]C?( 5G)?|Redmi A[1-3]|POCO (X[5-7]|F[4-7]|M[5-7])( Pro| GT| 5G)*|"
    r"Xiaomi 1[2-5]( Pro| Ultra| T| T Pro|T|T Pro|X)*|"
    r"Pixel ([7-9]|10)( Pro| Pro XL| Pro Fold|a)?|Pixel Fold|"
    r"OnePlus (1[0-3]( Pro|R|T)?|Nord( 2T| 3| 4| CE ?[2-4]( Lite)?( 5G)?| N[2-3]0))|"
    r"(OPPO )?(Reno ?([89]|1[0-3])( Pro| F| Z| 5G)*|A(1[78]|38|5[78]|60|7[789]|80)( 5G)?)|"
    r"vivo (Y(1[6-9]|2[2-9]|3[5-9]|0[3-4])s?( 5G)?|V(2[5-9]|3[0-9]|40)( Pro| e| Lite)?|X(80|90|100|200)( Pro)?)|"
    r"realme (1[0-4]( Pro| Pro\+| 5G)*|C(3[3-5]|5[1-5]|6[1-7]|7[1-5])|GT ?[2-7]( Pro)?)|"
    r"moto g(2[2-9]|[3-9][0-9]|0[4-6])( 5G)?|moto g( 5G| power| stylus)? - 202[2-5]|motorola edge (20(22|23|24)|[3-6]0)( pro| neo| fusion| ultra)?|"
    r"HONOR (X[5-9][abc]?( Plus)?|X[5-9]b|(70|80|90|200|400)( Lite| Pro)?|Magic ?[4-7]( Pro| Lite)?)|"
    r"Nothing Phone ?\(([1-3])a?\)|TECNO (SPARK (1[0-9]|20|30)|CAMON (19|2[0-9]|30))|Infinix (HOT (2[0-9]|[3-5]0)|NOTE (1[2-9]|[2-4]0)))",
    re.IGNORECASE)
ANDROID_VERSIONS = (15, 16)  # owner: «андроит 15 и выше»; used by the run-time picker, printed here for the record
MAX_LINES = 5000
MAX_BYTES = 1_000_000
CLEAN = re.compile(r"^[A-Za-z0-9 ._+()/-]{2,40}$")

src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
rows = csv.DictReader(io.StringIO(src.read_bytes().decode("utf-16")))
seen = {}
for r in rows:
    brand = (r.get("Retail Branding") or "").strip()
    model = (r.get("Model") or "").strip()
    name = (r.get("Marketing Name") or "").strip()
    if brand.lower() not in BRANDS or not CLEAN.match(model) or "|" in model or not SERIES.match(name):
        continue
    seen.setdefault(model.lower(), (brand, model))
items = sorted(seen.values(), key=lambda x: (x[0].lower(), x[1].lower()))
if len(items) > MAX_LINES:  # an even spread over brands and models, deterministic: every k-th line
    step = len(items) / MAX_LINES
    items = [items[int(i * step)] for i in range(MAX_LINES)]
text = "".join(f"{b}|{m}\n" for b, m in items)
size = len(text.encode("ascii"))
if size > MAX_BYTES:
    sys.exit(f"FAIL: {size} bytes > {MAX_BYTES}")
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(text, encoding="ascii", newline="\n")
brands = sorted({b for b, _ in items})
print(f"{len(items)} devices, {size} bytes, {len(brands)} brands: {', '.join(brands)}")
