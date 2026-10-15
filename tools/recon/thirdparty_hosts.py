# read-only: hard-coded hosts in third-party packages (not com/thousandshores), grouped by package root
import os, re, sys, collections
root = sys.argv[1]
url = re.compile(r'"((?:https?|wss?)://([A-Za-z0-9.-]+)[^"]*)"')
skip = re.compile(r'schemas\.android|w3\.org|apache\.org|xmlpull|ns\.adobe|purl\.org|xml\.org|example\.|localhost|127\.0\.0\.1|schema\.org|json-schema')
by = collections.defaultdict(set)
for dp, dn, fn in os.walk(root):
    rel = os.path.relpath(dp, root).replace(os.sep, '/')
    if rel.startswith('com/thousandshores'): continue
    for f in fn:
        if not f.endswith('.java'): continue
        t = open(os.path.join(dp, f), encoding='utf-8', errors='replace').read()
        for m in url.finditer(t):
            if skip.search(m.group(2)): continue
            key = '/'.join(rel.split('/')[:3])
            by[key].add(m.group(2))
for k in sorted(by): print(k, '->', ' '.join(sorted(by[k]))[:300])
