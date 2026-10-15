// Build researches/01_play_reviews.md from the classified Play reviews. Non-ASCII goes through this file,
// never through shell args (project rule: text travels through files). [NOT-TESTED]
import fs from 'node:fs';
const d = JSON.parse(fs.readFileSync(new URL('./play-reviews-raw.json', import.meta.url), 'utf8'));
const R = d.results || [];
const meta = Object.fromEntries((d.themes || []).map(t => [t.id, t]));
const cnt = {}, low = {}, byLocale = {};
for (const r of R) {
  const arr = Array.isArray(r.themes) ? r.themes : [r.themes].filter(Boolean);
  const s = r.score || r.rating;
  const loc = r.locale || r.lang || '?';
  byLocale[loc] = (byLocale[loc] || 0) + 1;
  for (const t of arr) { cnt[t] = (cnt[t] || 0) + 1; if (s && s <= 2) low[t] = (low[t] || 0) + 1; }
}
const rows = Object.entries(cnt).sort((a, b) => b[1] - a[1]);
let md = '# Исследование 01 — жалобы пользователей Tribit из отзывов Google Play\n\n' +
  '> **Создан:** 2026-10-15 · **Родитель:** — (разведка перед развилкой «латать или писать своё») · ' +
  '**Статус:** срез собран 2026-10-15; файл пишет скрипт `01_play_reviews/make-reviews-md.mjs` · **Вовне:** —\n\n';
md += 'Дата: 2026-10-15. Классифицировано отзывов: ' + R.length + '. ';
md += 'Срез самых свежих отзывов по локалям. По локалям: ' +
  Object.entries(byLocale).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', ') + '.\n\n';
md += 'Колонка «Чиним в приложении»: да — правится в нашей сборке; частично — часть случаев ' +
  '(другие упираются в прошивку или сервер); нет — прошивка или железо.\n\n';
md += '| # | Тема | Отзывов | Из них 1–2★ | Чиним в приложении |\n|---|---|---:|---:|---|\n';
rows.forEach(([id, c], i) => {
  const m = meta[id] || {};
  md += `| ${i + 1} | ${m.title || id} | ${c} | ${low[id] || 0} | ${m.fixable || '?'} |\n`;
});
fs.writeFileSync(new URL('../01_play_reviews.md', import.meta.url), md);
console.log('written 01_play_reviews.md with', rows.length, 'themes,', R.length, 'reviews');
