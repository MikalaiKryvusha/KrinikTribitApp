# read-only: which request models (http/model/*) are instantiated anywhere in own code
import os, re, sys
root = sys.argv[1]
own = os.path.join(root, 'com', 'thousandshores')
mdir = os.path.join(own, 'tribit', 'http', 'model')
models = sorted(f[:-5] for f in os.listdir(mdir) if f.endswith('.java') and 'IRequestApi' in open(os.path.join(mdir, f), encoding='utf-8', errors='replace').read() and f != 'RequestHandler.java')
src = {}
for dp, dn, fn in os.walk(own):
    for f in fn:
        if f.endswith('.java'):
            p = os.path.join(dp, f)
            src[os.path.relpath(p, own).replace(os.sep, '/')] = open(p, encoding='utf-8', errors='replace').read()
used, dead = [], []
for m in models:
    pat = re.compile(r'new ' + m + r'\(')
    hits = [f for f, t in src.items() if pat.search(t) and not f.endswith('/' + m + '.java')]
    (used if hits else dead).append((m, hits))
print('request models:', len(models), 'used:', len(used), 'dead:', len(dead))
for m, h in used: print('USED', m, '<-', ', '.join(sorted(set(h)))[:160])
for m, h in dead: print('DEAD', m)
