# read-only: map EasyHttp call sites -> request model class
import os, re, sys
root = sys.argv[1]
own = os.path.join(root, 'com', 'thousandshores')
call = re.compile(r'EasyHttp\.(get|post|put|delete|download)\(')
api = re.compile(r'\.api\(([^;]{0,80})|\.api\((?:\(IRequestApi\) )?new ([A-Za-z0-9_]+)\(|\.api\("([^"]+)"\)|\.url\(([^)]*)\)')
for dp, dn, fn in os.walk(own):
    for f in fn:
        if not f.endswith('.java'): continue
        p = os.path.join(dp, f); rel = os.path.relpath(p, own).replace(os.sep, '/')
        lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
        for i, l in enumerate(lines):
            m = call.search(l)
            if not m: continue
            seg = ' '.join(lines[i:i+14])
            a = api.search(seg)
            print('%s:%d %s -> %s' % (rel, i+1, m.group(1), a.group(0) if a else '?'))
