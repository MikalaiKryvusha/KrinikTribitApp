# read-only inventory of server endpoints in the Tribit app's own code
import os, re, sys
root = sys.argv[1]  # decompiled/jadx-base/sources
own = os.path.join(root, 'com', 'thousandshores')
api_re = re.compile(r'"(api-[a-z]+/[^"]*)"')
retro_re = re.compile(r'@(GET|POST|PUT|DELETE|PATCH|Multipart|Streaming|Url)\b(?:\("([^"]*)"\))?')
url_re = re.compile(r'"((?:https?|wss?)://[^"\s]+)"')
apis, retro, urls = [], [], {}
for dp, dn, fn in os.walk(own):
    for f in fn:
        if not f.endswith('.java'): continue
        p = os.path.join(dp, f)
        t = open(p, encoding='utf-8', errors='replace').read()
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        if 'implements IRequestApi' in t or 'IRequestApi' in t:
            for m in api_re.finditer(t):
                ln = t.count('\n', 0, m.start()) + 1
                apis.append((m.group(1), rel, ln))
        for m in retro_re.finditer(t):
            if 'retrofit2' in t:
                retro.append((m.group(1), m.group(2), rel, t.count('\n', 0, m.start()) + 1))
        for m in url_re.finditer(t):
            urls.setdefault(m.group(1), []).append('%s:%d' % (rel, t.count('\n', 0, m.start()) + 1))
print('== EasyHttp IRequestApi.getApi():', len(apis), 'classes;', len({a[0] for a in apis}), 'unique paths')
for a in sorted(apis): print('%-70s %s:%d' % a)
print('== Retrofit annotations in own code:', len(retro))
for r in retro: print(r)
print('== hard-coded URLs in own code:', len(urls))
for u, w in sorted(urls.items()): print(u, ' <- ', ', '.join(w[:4]), ('(+%d)' % (len(w)-4) if len(w) > 4 else ''))
