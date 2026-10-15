import fs from 'node:fs';
const raw=JSON.parse(fs.readFileSync('raw.json','utf8'));
const R=raw.reviews.filter(r=>r.score<=3).sort((a,b)=>b.date.localeCompare(a.date));
const lines=R.map((r,i)=>`#${i} ${r.score}* ${r.date.slice(0,10)} v${r.version||'-'} ${r._lang} | ${(r.text||'').replace(/\s+/g,' ')}`);
fs.writeFileSync('neg.txt',lines.join('\n'));
const P=raw.reviews.filter(r=>r.score>=4).sort((a,b)=>b.date.localeCompare(a.date));
fs.writeFileSync('pos.txt',P.map((r,i)=>`#${i} ${r.score}* ${r.date.slice(0,10)} v${r.version||'-'} ${r._lang} | ${(r.text||'').replace(/\s+/g,' ')}`).join('\n'));
console.log(R.length,P.length);
