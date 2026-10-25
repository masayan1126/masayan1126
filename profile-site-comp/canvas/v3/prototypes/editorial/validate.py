"""Check preview links, preserved quote contracts and the inquiry boundary."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import copy
import json

PROJECT = Path(__file__).resolve().parents[4]
PUBLIC = PROJECT / 'canvas/v3/site'
PREVIEW = PROJECT / 'output/editorial-concept/site'
PAGES = ['', 'profile', 'works', 'services', 'media', 'talks', 'membership', 'pricing', 'contact']


def document(root, page):
    return BeautifulSoup((root / page / 'index.html').read_text(), 'html.parser')


def content_size(soup):
    main = copy.copy(soup.select_one('main'))
    for hidden in main.select('script, style, #legacy-estimate, dialog'):
        hidden.decompose()
    return len(''.join(main.get_text().split()))


def validate():
    docs = {page: document(PREVIEW, page) for page in PAGES}
    pages = []
    for page, soup in docs.items():
        assert len(soup.select('main')) == len(soup.select('h1')) == 1, page
        ids = [el['id'] for el in soup.select('[id]')]
        assert len(ids) == len(set(ids)), f'Duplicate ID: {page}'
        for anchor in soup.select('a[href]'):
            url = urlsplit(anchor['href'])
            if url.scheme or url.netloc:
                continue
            target = docs[page] if not url.path else docs[url.path.strip('/')]
            if url.fragment:
                assert target.find(id=unquote(url.fragment)), anchor['href']
        for asset in soup.select('img[src], script[src], link[rel="stylesheet"]'):
            url = urlsplit(asset.get('src') or asset['href'])
            if url.scheme or url.netloc:
                continue
            asset_path = url.path.lstrip('/')
            assert (PREVIEW / asset_path).is_file() or (PUBLIC / asset_path).is_file(), asset_path
        before = content_size(document(PUBLIC, page))
        after = content_size(soup)
        pages.append({'path': '/' + (page + '/' if page else ''), 'source_chars': before, 'preview_chars': after})

    for selector in ('#pricing-data', '#pricing-wizard', '#legacy-estimate'):
        assert str(document(PUBLIC, 'pricing').select_one(selector)) == str(docs['pricing'].select_one(selector)), selector
    original_form = document(PUBLIC, 'contact').select_one('#inquiry-form')
    preview_form = copy.copy(docs['contact'].select_one('#inquiry-form'))
    assert preview_form['action'] == '/__preview/contact'
    assert preview_form['data-editorial-preview'] == 'true'
    del preview_form['action'], preview_form['data-editorial-preview']
    assert str(original_form) == str(preview_form), 'Inquiry fields changed'
    assert docs['contact'].get_text().count('通常2営業日以内') == 1
    assert 'https://studio.msyn.me/api/contact' not in str(docs['contact'])
    assert not docs['talks'].select('iframe'), 'Slides should open only on request'
    assert len(docs[''].select('.focus-highlight')) == 3
    result = {'pages': pages, 'links_and_assets': 'passed', 'quote_dom_unchanged': True, 'form_fields_unchanged': True, 'forms_send': False}
    output = PREVIEW.parent / 'selection'
    output.mkdir(exist_ok=True)
    (output / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    validate()
