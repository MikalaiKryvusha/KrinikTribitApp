import gplay from 'google-play-scraper';
import fs from 'node:fs';

const APP = 'com.thousandshores.tribit';
const OUT = process.argv[2] || 'raw.json';
const LOCALES = [
  ['en', 'us'], ['en', 'gb'], ['en', 'ca'], ['en', 'au'], ['en', 'in'],
  ['ru', 'ru'], ['de', 'de'], ['fr', 'fr'], ['es', 'es'], ['es', 'mx'], ['it', 'it'],
  ['ja', 'jp'], ['zh', 'tw'], ['pt', 'br'], ['pl', 'pl'], ['nl', 'nl'], ['ko', 'kr'],
  ['uk', 'ua'], ['tr', 'tr'], ['ar', 'sa'], ['cs', 'cz'], ['sv', 'se'],
];
const MAX = 5000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const result = { fetchedAt: new Date().toISOString(), app: null, perLocale: {}, reviews: {} };
try {
  result.app = await gplay.app({ appId: APP, lang: 'en', country: 'us' });
} catch (e) { result.appError = String(e); }

for (const [lang, country] of LOCALES) {
  const key = `${lang}/${country}`;
  let token = null, got = 0, pages = 0, err = null;
  try {
    do {
      const res = await gplay.reviews({
        appId: APP, lang, country, sort: gplay.sort.NEWEST, num: 200,
        paginate: true, nextPaginationToken: token,
      });
      const data = res.data || [];
      for (const r of data) {
        got++;
        const prev = result.reviews[r.id];
        if (prev) { if (!prev._locales.includes(key)) prev._locales.push(key); }
        else result.reviews[r.id] = { ...r, _locales: [key], _lang: lang };
      }
      token = res.nextPaginationToken;
      pages++;
      await sleep(400);
    } while (token && got < MAX);
  } catch (e) { err = String(e); }
  result.perLocale[key] = { fetched: got, pages, error: err };
  console.log(key, got, pages, err || '');
}
const arr = Object.values(result.reviews);
result.totalUnique = arr.length;
fs.writeFileSync(OUT, JSON.stringify({ ...result, reviews: arr }, null, 1));
console.log('unique', arr.length);
