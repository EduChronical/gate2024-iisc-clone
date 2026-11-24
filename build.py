#!/usr/bin/env python3
"""Build the static GATE 2024 clone from the read-only wget mirror.
Usage: python3 build.py [mirror_dir]   -> writes ./site
"""
import os, re, sys, shutil, json, html, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIRROR = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'source-mirror')
SITE = ROOT / 'site'
DOMAIN_RE = r'(?:https?:)?//gate2024\.iisc\.ac\.in'
# Original links that are broken on production -> working equivalents
FIXUPS = {
    '/wp-content/uploads/2024/06/GATE2024StatisticalAndPerformanceReportWebVersion2.pdf':
        '/wp-content/uploads/2026/04/GATE2024StatisticalAndPerformanceReportWebVersion.pdf',
}

if SITE.exists():
    shutil.rmtree(SITE)
shutil.copytree(MIRROR, SITE, ignore=shutil.ignore_patterns('index.html@p=*', 'seeds.txt', 'wget.log', '*.orig', 'ext'))
# local copies of third-party CSS/fonts (Font Awesome, MIT/OFL)
shutil.copytree(MIRROR / 'ext', SITE / 'vendor' / 'fontawesome' / 'css', dirs_exist_ok=True)
fa = SITE / 'vendor' / 'fontawesome'
shutil.move(str(fa / 'css' / 'webfonts'), str(fa / 'webfonts'))
shutil.move(str(fa / 'css' / 'fa-all.min.css'), str(fa / 'css' / 'all.min.css'))
subprocess.run([sys.executable, str(ROOT / 'src' / 'tables.py')], check=True)
shutil.copytree(ROOT / 'src' / 'clone', SITE / 'clone')

# ---- map WordPress shortlinks (?p=NNN) to canonical pages
pmap = {}
for f in MIRROR.rglob('index.html'):
    h = f.read_text(errors='ignore')
    m = re.search(r"<link rel='shortlink' href='[^']*index\.html@p=(\d+)\.html'", h) or re.search(r'<body[^>]*class="[^"]*(?:page-id|postid)-(\d+)', h)
    if m:
        pmap[f'index.html@p={m.group(1)}.html'] = '/' + str(f.parent.relative_to(MIRROR)).replace(os.sep, '/').strip('.') + '/'
        pmap[f'index.html@p={m.group(1)}.html'] = pmap[f'index.html@p={m.group(1)}.html'].replace('//', '/')
print('shortlinks mapped:', len(pmap))

def local_target(path):
    """site-absolute path ('/x/y/') -> Path of a local file or None"""
    path = html.unescape(path).split('#')[0]
    path = FIXUPS.get(path, path)
    if '?' in path:
        return None
    p = SITE / path.lstrip('/')
    if path.endswith('/') or path == '':
        p = p / 'index.html'
    return p if p.exists() else None

def rel(from_file, target):
    r = os.path.relpath(target, from_file.parent)
    return r.replace(os.sep, '/')

pages = sorted(SITE.rglob('*.html'))
for f in pages:
    h = f.read_text(errors='ignore')
    # head clutter that points back at the live CMS
    h = re.sub(r'<link[^>]+(?:rel="(?:alternate|EditURI|https://api\.w\.org/|shortlink|pingback|dns-prefetch)")[^>]*>\s*', '', h)
    # third-party hit counter (counter.websiteout.com) is not loaded: it would count clone visits on production's
    # counter and currently injects ad text. Keep the "Page Views" box with a static label instead.
    h = re.sub(r'<script[^>]+counter\.websiteout\.com[^>]*></script>', '<span class="gc-counter" title="Third-party hit counter not loaded in the clone">Hit counter</span>', h)
    h = re.sub(r'<a[^>]+cutercounter\.com[^>]*>.*?</a>', '', h, flags=re.S)
    # shortlinks
    h = re.sub(r'((?:href|src)=")((?:\.\./)*index\.html@p=\d+\.html)(?=[#"])', lambda m: (m.group(1) + rel(f, local_target(pmap[os.path.basename(m.group(2))]))) if os.path.basename(m.group(2)) in pmap and local_target(pmap[os.path.basename(m.group(2))]) else m.group(0), h)
    # absolute links to the original domain -> local relative when we have the file
    def abs_sub(m):
        attr, path = m.group(1), m.group(2) or '/'
        t = local_target(path)
        return f'{attr}"{rel(f, t)}"' if t else m.group(0)
    h = re.sub(r'((?:href|src|action)=)"' + DOMAIN_RE + r'(/[^"]*)?"', abs_sub, h)
    h = re.sub(r'url\(([\'"]?)' + DOMAIN_RE + r'(/[^)\'"]+)\1\)', lambda m: f'url({m.group(1)}{rel(f, local_target(m.group(2)))}{m.group(1)})' if local_target(m.group(2)) else m.group(0), h)
    # srcset lists
    def srcset_sub(m):
        parts = []
        for item in m.group(2).split(','):
            bits = item.strip().split()
            if not bits: continue
            u = bits[0]
            mm = re.match(DOMAIN_RE + r'(/.*)', u)
            if mm:
                t = local_target(mm.group(1))
                if not t: continue
                u = rel(f, t)
            parts.append(' '.join([u] + bits[1:]))
        return f'{m.group(1)}="{", ".join(parts)}"'
    h = re.sub(r'((?:srcset|data-srcset))="([^"]*)"', srcset_sub, h)
    # JSON-escaped URLs used by Divi clickable rows / scripts
    def json_sub(m):
        p = m.group(1).replace('\\/', '/')
        t = local_target(p)
        return rel(f, t).replace('/', '\\/') if t else m.group(0)
    h = re.sub(r'https?:\\/\\/gate2024\.iisc\.ac\.in(\\/[^"]*)', json_sub, h)
    # duplicate jQuery 3.5.1 from Google CDN (download page) clobbers the WP jQuery plugins -> remove
    h = re.sub(r'<script[^>]+ajax\.googleapis\.com/ajax/libs/jquery/[^>]+></script>', '', h)
    # Ninja Tables rows: the live admin-ajax endpoint returns 403 even on production; serve recovered rows locally
    def nt_sub(m):
        tid = m.group(1)
        return '"data_request_url":"' + rel(f, SITE / 'clone' / 'tables' / f'table-{tid}.json').replace('/', '\\/') + '"'
    h = re.sub(r'"data_request_url":"[^"]*?table_id=(\d+)[^"]*"', nt_sub, h)
    # broken intranet link on production footer ("Home" -> http://10.0.94.4)
    h = h.replace('href="http://10.0.94.4"', f'href="{rel(f, SITE / "index.html")}"')
    # Font Awesome from cdnjs -> vendored copy
    h = re.sub(r'https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.4\.2/css/all\.min\.css', rel(f, fa / 'css' / 'all.min.css'), h)
    # search form -> client-side search page
    h = re.sub(r'(<form role="search"[^>]*action=")[^"]*(")', lambda m: m.group(1) + rel(f, SITE / 'search' / 'index.html') + m.group(2), h)
    root = rel(f, SITE / 'index.html')[:-len('index.html')] or './'
    inj_head = f'<link rel="stylesheet" href="{root}clone/clone.css">\n'
    inj_body = f'<script>window.CLONE_ROOT={json.dumps(root)};</script>\n<script src="{root}clone/search-index.js"></script>\n<script src="{root}clone/clone.js"></script>\n'
    h = h.replace('</head>', inj_head + '</head>', 1)
    h = h[::-1].replace('>ydob/<', (inj_body + '</body>')[::-1], 1)[::-1]
    f.write_text(h)

# ---- search index
def text_of(fragment):
    fragment = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>', ' ', fragment, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', fragment))
    return re.sub(r'\s+', ' ', t).strip()

index, downloads, notifications = [], {}, []
for f in sorted(SITE.rglob('*.html')):
    h = f.read_text(errors='ignore')
    url = '/' + str(f.relative_to(SITE)).replace(os.sep, '/')
    url = url[:-len('index.html')] if url.endswith('index.html') else url
    title = text_of(re.search(r'<title>(.*?)</title>', h, re.S).group(1)) if '<title>' in h else url
    title = re.sub(r'\s*[|\-–]\s*GATE 2024.*$', '', title) or 'Home'
    if url == '/': title = 'Home – GATE 2024'
    m = re.search(r'<div id="et-main-area">(.*?)<footer', h, re.S) or re.search(r'<body[^>]*>(.*)</body>', h, re.S)
    main = m.group(1) if m else h
    main = re.sub(r'<header.*?</header>', ' ', main, flags=re.S)
    main = re.split(r'class="et-l et-l--footer"', main)[0]
    body = text_of(main)
    # include restored Ninja Tables rows in the search index
    for tid in re.findall(r'clone\\/tables\\/table-(\d+)\.json', h):
        tf = SITE / 'clone' / 'tables' / f'table-{tid}.json'
        if tf.exists() and json.loads((SITE / 'clone' / 'tables' / 'meta.json').read_text()).get(tid) != 'unavailable':
            body += ' ' + ' '.join(text_of(v) for r in json.loads(tf.read_text()) for v in r['value'].values())
    if url.startswith('/author/') or url == '/search/':
        continue
    index.append({'t': title, 'u': url, 'b': body[:6000]})
    for a in re.finditer(r'<a[^>]+href="([^"]+\.(?:pdf|docx?|xlsx?|zip))"[^>]*>(.*?)</a>', main, re.S | re.I):
        href = a.group(1)
        absu = os.path.normpath(os.path.join(os.path.dirname(url) if not url.endswith('/') else url, href)) if not href.startswith('http') else href
        label = text_of(a.group(2)) or os.path.basename(href)
        downloads.setdefault(absu, {'t': label, 'u': absu, 'p': url, 'pt': title})

# notifications from the WordPress "Notifications" category listing pages (newest first)
for f in [SITE / 'category/notifications/index.html'] + sorted((SITE / 'category/notifications/page').glob('*/index.html')):
    h = f.read_text(errors='ignore')
    for art in re.finditer(r'<article.*?</article>', h, re.S):
        a = re.search(r'<h2[^>]*>\s*<a href="([^"]+)"[^>]*>(.*?)</a>', art.group(0), re.S)
        d = re.search(r'<span class="published">(.*?)</span>', art.group(0))
        if a:
            u = os.path.normpath(os.path.join('/' + str(f.parent.relative_to(SITE)) + '/', a.group(1)))
            u = re.sub(r'index\.html$', '', u)
            u = u if u.endswith('/') else u + '/'
            notifications.append({'t': text_of(a.group(2)), 'u': u, 'd': d.group(1) if d else ''})

out = {'pages': index, 'downloads': list(downloads.values()), 'notifications': notifications}
(SITE / 'clone' / 'search-index.js').write_text('window.CLONE_INDEX=' + json.dumps(out, ensure_ascii=False) + ';\n')
print(f"pages={len(index)} downloads={len(downloads)} notifications={len(notifications)}")
