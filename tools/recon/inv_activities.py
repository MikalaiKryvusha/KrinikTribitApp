"""Own activities: how many inherit com.thousandshores.tribit.base.BaseActivity. python -I this.py <apktool> <jadx>"""
import pathlib,re,sys
ROOT,SRC=pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2])
man=(ROOT/"AndroidManifest.xml").read_text(encoding="utf-8")
acts=[a for a in re.findall(r'<activity[^>]*android:name="([^"]+)"',man) if a.startswith("com.thousandshores")]
def sup(c):
    f=SRC/(c.replace(".","/")+".java")
    if not f.exists(): return None
    t=f.read_text(encoding="utf-8",errors="replace")
    m=re.search(r"class\s+\w+(?:<[^>]*>)?\s+extends\s+([\w.]+)",t)
    if not m: return None
    s=m.group(1)
    if "." in s: return s
    im=re.search(r"import\s+([\w.]+\."+s+");",t)
    return im.group(1) if im else c.rsplit(".",1)[0]+"."+s
base=0; other={}
for a in acts:
    c=a; chain=[]
    while c and c!="com.thousandshores.tribit.base.BaseActivity" and len(chain)<8:
        chain.append(c); c=sup(c)
    if c=="com.thousandshores.tribit.base.BaseActivity": base+=1
    else: other[a]=chain[-1] if chain else a
print("own activities",len(acts),"inherit BaseActivity",base,"other",len(other))
for k,v in list(other.items())[:15]: print("  ",k,"<- top:",v, sup(v))
