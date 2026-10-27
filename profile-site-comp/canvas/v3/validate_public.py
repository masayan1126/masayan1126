"""Validate the approved public edition, including deployment-only boundaries."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
PAGES = ['', 'profile', 'works', 'talks', 'membership', 'pricing', 'contact']
BASE = 'https://studio.msyn.me'


def validate(site=ROOT / 'site'):
    site = Path(site)
    docs = {page: BeautifulSoup((site / page / 'index.html').read_text(), 'html.parser') for page in PAGES}
    for page, doc in docs.items():
        text = str(doc)
        assert len(doc.select('main')) == len(doc.select('h1')) == 1, page
        ids = [node['id'] for node in doc.select('[id]')]
        assert len(ids) == len(set(ids)), page
        route = '/' + (page + '/' if page else '')
        assert doc.select_one('link[rel="canonical"]')['href'] == BASE + route
        assert doc.select_one('meta[property="og:url"]')['content'] == BASE + route
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
    result = {'pages': len(PAGES), 'links_assets_and_modules': 'passed', 'contact_production': True, 'analytics_clean_urls': True, 'indexable': True, 'rate_version': raw_rates['rateVersion'], 'historical_rates_unchanged': True}
    output = ROOT.parents[1] / 'output/public-release/validation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    validate()
