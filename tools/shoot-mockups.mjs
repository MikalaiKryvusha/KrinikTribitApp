#!/usr/bin/env node
// shoot-mockups.mjs - shoots every phone of a mock-up sheet (design/<sheet>.html) and the whole sheet into WebP
// (HOUSE_RULES.md R4), so the agent sees the render with its own eyes and the owner gets pictures. Playwright is
// borrowed read-only from KARTUN's node_modules (the same tool KARTUN shoots its sheets with); `magick` makes WebP.
// [NOT-TESTED]
//
// Usage: node tools/shoot-mockups.mjs [design/mockups-v1.html]  -> design/mockups-v1/<id>.webp + sheet.webp
import { createRequire } from 'node:module';
import { mkdirSync, rmSync } from 'node:fs';
import { resolve, join, basename } from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const KARTUN = 'D:/work/ai_sandbox/KARTUN/package.json';
const { chromium } = createRequire(KARTUN)('playwright');

const sheet = resolve(process.argv[2] || 'design/mockups-v1.html');
const out = join('design', basename(sheet, '.html'));
mkdirSync(out, { recursive: true });

// PNG from the browser, then WebP at quality 85; the PNG is removed.
function webp(png, file, width) {
  execFileSync('magick', [png, ...(width ? ['-resize', `${width}x`] : []), '-quality', '85', file]);
  rmSync(png);
  console.log(`shot ${file}`);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1340, height: 1000 }, deviceScaleFactor: 2 });
await page.goto(pathToFileURL(sheet).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
console.log(`fonts loaded: ${fonts.join(', ') || 'NONE'}`);

for (const wrap of await page.$$('.phone-wrap')) {
  const id = await wrap.getAttribute('data-id');
  const png = join(out, `${id}.png`);
  await (await wrap.$('.screen')).screenshot({ path: png });
  webp(png, join(out, `${id}.webp`), 780);
}
const png = join(out, 'sheet.png');
await page.screenshot({ path: png, fullPage: true });
webp(png, join(out, 'sheet.webp'), 1600);
await browser.close();
