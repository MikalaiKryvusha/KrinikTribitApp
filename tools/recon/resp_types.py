# read-only: request model -> response type (from OnHttpListener<...> at the call site)
import os, re, sys, collections
root = sys.argv[1]
own = os.path.join(root, 'com', 'thousandshores')
pat = re.compile(r'\.api\([^;]*?new ([A-Z][A-Za-z0-9]+)\([^;]*?OnHttpListener<(.+?)>\(\)')
pat2 = re.compile(r'\.api\(([a-z][A-Za-z0-9]*)\)\)\.request\(new OnHttpListener<(.+?)>\(\)')
res = collections.defaultdict(set)
for dp, dn, fn in os.walk(own):
    for f in fn:
        if not f.endswith('.java'): continue
        for line in open(os.path.join(dp, f), encoding='utf-8', errors='replace'):
            for m in pat.finditer(line): res[m.group(1)].add(m.group(2).replace('? extends ', ''))
            for m in pat2.finditer(line): res['var:' + m.group(1)].add(m.group(2).replace('? extends ', ''))
for k in sorted(res): print(k, '->', ' | '.join(sorted(res[k])))
