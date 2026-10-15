import gplay from 'google-play-scraper';
import fs from 'node:fs';
const APP='com.thousandshores.tribit';
const raw=JSON.parse(fs.readFileSync('raw.json','utf8'));
const byId=Object.fromEntries(raw.reviews.map(r=>[r.id,r]));
const L=[['hu','hu'],['ro','ro'],['el','gr'],['th','th'],['vi','vn'],['id','id'],['hi','in'],['iw','il'],['fi','fi'],['da','dk'],['no','no'],['zh','cn'],['zh-HK','hk'],['ms','my'],['bg','bg'],['sk','sk'],['hr','hr'],['sr','rs'],['lt','lt'],['lv','lv'],['et','ee'],['sl','si'],['fil','ph'],['fa','ir'],['pt','pt'],['es','ar'],['es','co'],['es','cl']];
for (const [lang,country] of L){const key=`${lang}/${country}`;let token=null,got=0,neu=0,err=null;
try{do{const res=await gplay.reviews({appId:APP,lang,country,sort:gplay.sort.NEWEST,num:200,paginate:true,nextPaginationToken:token});
for(const r of res.data){got++;if(byId[r.id]){if(!byId[r.id]._locales.includes(key))byId[r.id]._locales.push(key);}else{neu++;byId[r.id]={...r,_locales:[key],_lang:lang};}}
token=res.nextPaginationToken;await new Promise(r=>setTimeout(r,400));}while(token&&got<5000);}catch(e){err=String(e)}
raw.perLocale[key]={fetched:got,newUnique:neu,error:err};console.log(key,got,neu,err||'');}
raw.reviews=Object.values(byId);raw.totalUnique=raw.reviews.length;fs.writeFileSync('raw.json',JSON.stringify(raw,null,1));console.log('unique',raw.totalUnique);
