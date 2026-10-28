"""Validate the approved public edition, including deployment-only boundaries."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import hashlib
import json
import re
import struct
from PIL import Image, ImageChops
from site_metadata import metadata, SITE_NAME, OWNER, ROLE, SOCIAL_PROFILES, ASSETS

ROOT = Path(__file__).resolve().parent
PAGES = ['', 'profile', 'works', 'talks', 'membership', 'pricing', 'contact']
BASE = 'https://studio.msyn.me'


def validate(site=ROOT / 'site'):
    site = Path(site)
    social_assets = json.loads((ASSETS / 'manifest.json').read_text())
    page_images = {record['page']: BASE + record['public_path'] for record in social_assets['files'] if 'page' in record}
    assert set(page_images) == set(PAGES)
    docs = {page: BeautifulSoup((site / page / 'index.html').read_text(), 'html.parser') for page in PAGES}
    for page, doc in docs.items():
        text = str(doc)
        assert len(doc.select('main')) == len(doc.select('h1')) == 1, page
        ids = [node['id'] for node in doc.select('[id]')]
        assert len(ids) == len(set(ids)), page
        route = '/' + (page + '/' if page else '')
        assert doc.select_one('link[rel="canonical"]')['href'] == BASE + route
        assert doc.select_one('meta[property="og:url"]')['content'] == BASE + route
        info = metadata(page)
        assert doc.title.get_text() == info['title'], page
        assert len(doc.select('link[rel="canonical"]')) == 1, page
        expected = {
            'description': info['description'], 'application-name': SITE_NAME,
            'twitter:title': info['title'], 'twitter:description': info['description'],
            'twitter:card': 'summary_large_image', 'theme-color': '#ffffff',
        }
        for name, value in expected.items():
            matches = doc.select(f'meta[name="{name}"]')
            assert len(matches) == 1 and matches[0]['content'] == value, (page, name)
        for name, value in {'og:title': info['title'], 'og:description': info['description'],
                            'og:site_name': SITE_NAME, 'og:image:alt': info['image_alt'],
                            'og:image:type': 'image/png', 'og:image:width': '1200', 'og:image:height': '630'}.items():
            matches = doc.select(f'meta[property="{name}"]')
            assert len(matches) == 1 and matches[0]['content'] == value, (page, name)
        image = doc.select('meta[property="og:image"]')
        assert len(image) == 1 and image[0]['content'].startswith(BASE + '/social/og-'), page
        assert image[0]['content'] == page_images[page], page
        image_path = site / urlsplit(image[0]['content']).path.lstrip('/')
        image_bytes = image_path.read_bytes()
        assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', image_bytes[16:24]) == (1200, 630), page
        assert hashlib.sha256(image_bytes).hexdigest()[:12] in image_path.name, image_path
        assert doc.select_one('meta[name="twitter:image"]')['content'] == image[0]['content'], page
        schema = doc.select('script[type="application/ld+json"]')
        assert len(schema) == 1, page
        graph = json.loads(schema[0].string)['@graph']
        assert len(graph) == len({node['@id'] for node in graph}) == 3, page
        website, person, webpage = graph
        assert website['@type'] == 'WebSite' and website['name'] == SITE_NAME and website['url'] == BASE + '/', page
        assert person['@type'] == 'Person' and person['name'] == OWNER and person['jobTitle'] == ROLE, page
        assert person['sameAs'] == SOCIAL_PROFILES and 'https://note.com/msyn1126' in person['sameAs'], page
        assert webpage['url'] == info['url'] and webpage['name'] == info['title'] and webpage['description'] == info['description'], page
        assert webpage['primaryImageOfPage']['url'] == image[0]['content'], page
        assert webpage['isPartOf']['@id'] == website['@id'] and webpage['about']['@id'] == person['@id'], page
        assert len(doc.select('link[rel~="icon"]')) == 3, page
        assert doc.select_one('link[rel="icon"][type="image/svg+xml"]')['href'] == '/favicon.svg', page
        assert doc.select_one('link[rel="icon"][type="image/png"]')['href'] == '/icons/favicon-96.png', page
        assert doc.select_one('link[rel="apple-touch-icon"]')['href'] == '/icons/apple-touch-icon.png', page
        assert doc.select_one('link[rel="manifest"]')['href'] == '/site.webmanifest', page
        assert not doc.select('meta[name="robots"][content*="noindex"]'), page
        assert len(doc.select('script[src*="googletagmanager.com"]')) == 1, page
        assert 'page_location:location.origin+location.pathname' in text
        assert not any(value in text for value in ('/__preview/', 'data-editorial-preview', '127.0.0.1', '/__review/')), page
        for element in doc.select('a[href],script[src],img[src],link[rel="stylesheet"]'):
            ref = element.get('href') or element.get('src')
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            if not url.path:
                if url.fragment:
                    assert doc.find(id=unquote(url.fragment)), ref
                continue
            path = site / url.path.lstrip('/')
            target = path / 'index.html' if path.is_dir() else path
            assert target.is_file(), ref
            if url.fragment and target.suffix == '.html':
                assert BeautifulSoup(target.read_text(), 'html.parser').find(id=unquote(url.fragment)), ref
        for link in doc.select('a[href^="/contact"]'):
            if page != 'contact':
                assert link.find_parent('header'), str(link)
    assert docs[''].select_one('.pr-video-plain')
    assert len(docs[''].select('.talk-preview')) == 2
    assert [node['data-category'] for node in docs[''].select('.a-entry')] == ['activity', 'pr', 'development', 'video', 'talk', 'ai']
    assert 'https://studio.msyn.me/api/contact' in str(docs['contact'])
    assert 'data-editorial-preview' not in str(docs['contact'])
    for archive in (ROOT / 'pricing-rates').glob('*.json'):
        assert archive.read_bytes() == (site / 'pricing-rates' / archive.name).read_bytes(), archive.name
    raw_rates = json.loads(docs['pricing'].select_one('#pricing-data').string)
    assert raw_rates['rateVersion'] == '4d2a90817527', 'Unapproved rate change'
    # Every module import and every content-addressed dependency must resolve.
    for script in site.rglob('*.mjs'):
        source = script.read_text()
        for ref in re.findall(r'''["']([^"'\s]+\.mjs)["']''', source):
            if ref.startswith(('./', '../')):
                assert (script.parent / ref).is_file(), (script, ref)
        if 'editorial.' in script.name:
            assert "document.addEventListener('submit'" not in source
        match = re.search(r'\.([a-f0-9]{12})\.mjs$', script.name)
        if match:
            assert match[1] == hashlib.sha256(script.read_bytes()).hexdigest()[:12], script
    sitemap = BeautifulSoup((site / 'sitemap.xml').read_text(), 'xml')
    assert {node.text for node in sitemap.select('loc')} == {BASE + '/' + (p + '/' if p else '') for p in PAGES}
    assert not list(site.rglob('__review'))
    for record in social_assets['files']:
        delivered = site / record['public_path'].lstrip('/')
        assert hashlib.sha256(delivered.read_bytes()).hexdigest() == record['sha256'], delivered
        if record['file'].endswith('.png'):
            assert struct.unpack('>II', delivered.read_bytes()[16:24]) == (record['width'], record['height']), delivered
        if 'page' in record:
            # Check actual raster pixels, not only the generator's text boxes.
            with Image.open(delivered) as source:
                image = source.convert('RGB')
            ink = ImageChops.difference(image, Image.new('RGB', image.size, 'white')).getbbox()
            left, top, right, bottom = social_assets['safe_bounds']
            assert ink and left <= ink[0] < ink[2] <= right and top <= ink[1] < ink[3] <= bottom, (delivered, ink)
            assert 285 <= left < right <= 915, social_assets['safe_bounds']
    bookmark = json.loads((site / 'site.webmanifest').read_text())
    assert (site / 'apple-touch-icon.png').read_bytes() == (ASSETS / 'apple-touch-icon.png').read_bytes()
    assert bookmark['name'] == SITE_NAME and bookmark['start_url'] == '/' and bookmark['display'] == 'browser'
    for icon in bookmark['icons']:
        width, height = struct.unpack('>II', (site / icon['src'].lstrip('/')).read_bytes()[16:24])
        assert icon['sizes'] == f'{width}x{height}' and width == height
    ico = (site / 'favicon.ico').read_bytes()
    assert struct.unpack('<HHH', ico[:6]) == (0, 1, 3)
    assert {(ico[6+i*16] or 256, ico[7+i*16] or 256) for i in range(3)} == {(16,16),(32,32),(48,48)}
    result = {'pages': len(PAGES), 'links_assets_and_modules': 'passed', 'metadata_and_bookmark_assets': 'passed', 'contact_production': True, 'analytics_clean_urls': True, 'indexable': True, 'rate_version': raw_rates['rateVersion'], 'historical_rates_unchanged': True}
    output = ROOT.parents[1] / 'output/public-release/validation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    validate()
