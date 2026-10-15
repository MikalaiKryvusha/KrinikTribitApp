"""Translation volume of keys the app actually uses. python -I this.py <jadx> <apktool>"""
import pathlib,re,sys
import xml.etree.ElementTree as ET
SRC,ROOT=pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2])
names={e.get("name"):"".join(e.itertext()) for e in ET.parse(ROOT/"res/values/strings.xml").getroot() if e.tag=="string"}
code="\n".join(f.read_text(encoding="utf-8",errors="replace") for f in (SRC/"com/thousandshores").rglob("*.java"))
used=set(re.findall(r"R\.string\.(\w+)",code))
lay=set()
for f in (ROOT/"res").glob("layout*/*.xml"): lay|=set(re.findall(r'"@string/(\w+)"',f.read_text(encoding="utf-8")))
keys=(used|lay)&names.keys()
w=sum(len(re.findall(r"\w+",names[k])) for k in keys)
print("keys used by own code (any R.string) or layouts:",len(keys),"words:",w,"; via ResourceUtils only set is the server-overridable one")
# CJK literal attrs whose value is pure numbers/symbols are skipped by the rewriter
CJK=re.compile(r"[\u4e00-\u9fff]")
vals=[]
for f in (ROOT/"res").glob("layout*/*.xml"):
    vals+=re.findall(r'android:(?:text|hint|contentDescription)="([^@?"][^"]*)"',f.read_text(encoding="utf-8"))
words=[v for v in vals if re.search(r"[A-Za-z\u4e00-\u9fff]{2}",v)]
print("layout literals total",len(vals),"with words (to externalize)",len(words),"unique",len(set(words)),"numeric/symbol-only kept",len(vals)-len(words))
