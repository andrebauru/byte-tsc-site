"""Generate deployment metadata only with an explicitly confirmed HTTPS origin."""
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

if len(sys.argv) != 2:
    raise SystemExit('Usage: python3 scripts/configure_deployment.py https://CONFIRMED-DOMAIN')
origin = sys.argv[1].rstrip('/')
u = urlsplit(origin)
if u.scheme != 'https' or not u.hostname or u.path or u.query or u.fragment or u.username or u.password:
    raise SystemExit('Expected an HTTPS origin without path, credentials, query or fragment.')
origin = escape(origin, {'"': '&quot;'})
root = Path(__file__).resolve().parent.parent
paths = [('ja', '/'), ('en', '/en/'), ('pt', '/pt/')]
alternates = paths + [('x-default', '/')]
for lang, path in paths:
    file = root / ('index.html' if path == '/' else path.strip('/') + '/index.html')
    text = file.read_text()
    text = re.sub(r'  <!-- DEPLOY-METADATA:START -->.*?  <!-- DEPLOY-METADATA:END -->\n', '', text, flags=re.S)
    text = re.sub(r'  <link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', text)
    block = '  <!-- DEPLOY-METADATA:START -->\n'
    block += f'  <link rel="canonical" href="{origin}{path}">\n'
    for code, alt in alternates:
        block += f'  <link rel="alternate" hreflang="{code}" href="{origin}{alt}">\n'
    block += f'  <meta property="og:url" content="{origin}{path}">\n'
    block += f'  <meta property="og:image" content="{origin}/assets/img/og-share.png">\n'
    block += '  <!-- DEPLOY-METADATA:END -->\n'
    marker = '  <!-- DEPLOY-METADATA: generated only after confirmed deployment URL -->\n'
    text = text.replace(marker, marker + block)
    file.write_text(text)
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
for _, path in paths:
    xml += f'  <url><loc>{origin}{path}</loc>\n'
    for lang, alt in alternates:
        xml += f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{origin}{alt}"/>\n'
    xml += '  </url>\n'
xml += '</urlset>\n'
(root / 'sitemap.xml').write_text(xml)
(root / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {origin}/sitemap.xml\n')
print('Deployment metadata configured. Review the diff before publishing.')
