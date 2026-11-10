#!/usr/bin/env python3
"""Check translated pages, RBM branding and the selected deployment origin."""
import json
import struct
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://financeself.jp'
ROUTES = [('ja', '/'), ('en', '/en/'), ('pt', '/pt/')]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.ids = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])

for lang, route in ROUTES:
    file = ROOT / (route.strip('/') + '/' if route != '/' else '') / 'index.html'
    text = file.read_text()
    page = Page(text)
    assert 'RBM' in text and 'Byte TSC' not in text and 'BYTE TSC' not in text
    assert dict(page.tags)['html']['lang'].split('-')[0] == lang
    assert len(page.ids) == len(set(page.ids)), f'Duplicate IDs: {file}'
    assert {'main', 'project', 'development', 'participate', 'faq'} <= set(page.ids)
    canonical = [a['href'] for t, a in page.tags if t == 'link' and a.get('rel') == 'canonical']
    assert canonical == [ORIGIN + route]
    alternates = [(a['hreflang'], a['href']) for t, a in page.tags if t == 'link' and a.get('rel') == 'alternate']
    assert sorted(alternates) == sorted([(l, ORIGIN + p) for l, p in ROUTES] + [('x-default', ORIGIN + '/')])
    for prop, expected in [('og:site_name', 'RBM'), ('og:url', ORIGIN + route), ('og:image', ORIGIN + '/assets/img/og-share.png')]:
        assert [a.get('content') for t, a in page.tags if t == 'meta' and a.get('property') == prop] == [expected]
    for _, attrs in page.tags:
        for key in ['src', 'href']:
            value = attrs.get(key)
            if not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            if not url.path:
                if url.fragment:
                    assert url.fragment in page.ids, f'Broken anchor: {value}'
                continue
            target = ROOT / url.path.lstrip('/') if url.path.startswith('/') else file.parent / url.path
            assert target.exists(), f'Missing local target: {value}'
            if target.is_dir():
                target = target / 'index.html'
            if url.fragment:
                assert url.fragment in Page(target.read_text()).ids
    print(f'ok {route}: RBM, metadata, anchors and local assets')

manifest = json.loads((ROOT / 'site.webmanifest').read_text())
assert manifest['name'] == manifest['short_name'] == 'RBM'
for file in (ROOT / 'assets').rglob('*.svg'):
    ET.parse(file)
    assert 'Byte TSC' not in file.read_text() and 'BYTE TSC' not in file.read_text()
for name, size in [('assets/favicon-16.png', (16, 16)), ('assets/favicon-32.png', (32, 32)), ('assets/apple-touch-icon.png', (180, 180)), ('assets/img/og-share.png', (1200, 630)), ('docs/homepage-preview.png', (1440, 1000))]:
    data = (ROOT / name).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', data[16:24]) == size
sitemap = ET.parse(ROOT / 'sitemap.xml')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert [e.text for e in sitemap.findall('s:url/s:loc', ns)] == [ORIGIN + p for _, p in ROUTES]
assert f'Sitemap: {ORIGIN}/sitemap.xml' in (ROOT / 'robots.txt').read_text()
print('ok manifest, SVG/XML, raster dimensions, sitemap and robots')
