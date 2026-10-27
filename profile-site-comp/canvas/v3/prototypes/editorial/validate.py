"""Check preview links, preserved quote contracts and the inquiry boundary."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import copy
import hashlib
import json
from content import extension_records
from site_copy import refine_ui_copy, centralize_contact_page

PROJECT = Path(__file__).resolve().parents[4]
PUBLIC = PROJECT / 'canvas/v3/site'
if (PROJECT / 'output/editorial-base/site').exists():
    PUBLIC = PROJECT / 'output/editorial-base/site'
PREVIEW = PROJECT / 'output/editorial-concept/site'
PAGES = ['', 'profile', 'works', 'talks', 'membership', 'pricing', 'contact']
SOURCE_PAGE = {}


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
        before = content_size(document(PUBLIC, SOURCE_PAGE.get(page, page)))
        after = content_size(soup)
        pages.append({'path': '/' + (page + '/' if page else ''), 'source_chars': before, 'preview_chars': after})

    expected_quote = document(PUBLIC, 'pricing')
    centralize_contact_page(expected_quote, 'pricing')
    expected_quote = BeautifulSoup(refine_ui_copy(str(expected_quote)), 'html.parser')
    for selector in ('#pricing-data', '#pricing-wizard', '#legacy-estimate'):
        before = str(expected_quote.select_one(selector))
        assert before == str(docs['pricing'].select_one(selector)), selector
    for page, soup in docs.items():
        if page == 'contact':
            continue
        for anchor in soup.select('a[href]'):
            if urlsplit(anchor['href']).path.rstrip('/') == '/contact':
                assert anchor.find_parent('header') and 'editorial-contact-link' in anchor.get('class', []), page
        assert not soup.select('main .focus-invitation, main .a-invitation'), page
    original_form = document(PUBLIC, 'contact').select_one('#inquiry-form')
    preview_form = copy.copy(docs['contact'].select_one('#inquiry-form'))
    assert preview_form['action'] == '/__preview/contact'
    assert preview_form['data-editorial-preview'] == 'true'
    preview_form['action'] = original_form['action']
    del preview_form['data-editorial-preview']
    assert str(original_form) == str(preview_form), 'Inquiry fields changed'
    assert docs['contact'].get_text().count('通常2営業日以内') == 1
    assert 'https://studio.msyn.me/api/contact' not in str(docs['contact'])
    assert not docs['talks'].select('iframe'), 'Slides should open only on request'
    assert docs[''].select_one('.a-bio'), 'Approved profile introduction is missing'
    assert [item['data-category'] for item in docs[''].select('.a-entry')] == ['activity', 'pr', 'development', 'video', 'talk', 'ai'], 'Activity order must follow the approved introduction'
    for page, soup in docs.items():
        assert not soup.select('.editorial-nav'), page
        social_urls = ['https://www.youtube.com/@masayan-ai-hack', 'https://x.com/masayan_ai_hack', 'https://www.instagram.com/miyabiya1126/', 'https://note.com/msyn1126', 'https://github.com/masayan1126']
        expected_header_links = ['/', *social_urls, '/' if page == 'contact' else '/contact/']
        assert [a['href'] for a in soup.select('.editorial-header a')] == expected_header_links, page
        assert [a['href'] for a in soup.select('.editorial-footer .site-social-links a')] == social_urls, page
        assert not soup.select('main .site-social-links, .profile-social-links'), page
        assert len({nav['aria-label'] for nav in soup.select('.site-social-links')}) == 2, page
        for anchor in soup.select('.site-social-links a'):
            assert anchor.get('aria-label') and anchor['target'] == '_blank' and 'noopener' in anchor['rel'], page
        if page == 'contact':
            home_link = soup.select_one('.editorial-header .editorial-home-link')
            assert home_link and home_link['href'] == '/'
            assert home_link['aria-label'] == 'トップページへ戻る'
            assert not soup.select('.editorial-contact-link')
    assert len(docs[''].select('#ai-adoption > .activity-group > .activity-highlights > li')) == 5
    assert not docs[''].select('#ai-adoption .plain-link')
    assert not docs[''].select('#other-services[open]')
    assert docs[''].select_one('#web-development') and docs[''].select_one('#video-editing')
    assert docs[''].get_text().count('約90%') == 1, 'YouTube automation result is duplicated'
    assert docs[''].select_one('#activities a[href="https://www.youtube.com/@masayan-ai-hack"]')
    assert docs[''].select_one('#personal-development a[href="https://github.com/masayan1126/chrome-extensions"]')
    assert not docs[''].select_one('#personal-development a[href="https://github.com/masayan1126"]')
    assert docs[''].select_one('#activities a[href="/membership/"]')
    assert len(docs[''].select('#activities .activity-highlights > li')) == 5
    assert len(docs[''].select('#personal-development .activity-highlights > li')) == 1
    extension_links = docs[''].select('#personal-development .project-extension-links a')
    records = extension_records()
    assert len(extension_links) == len(records) == 5
    for anchor, record in zip(extension_links, records):
        assert anchor['href'] == record['store_url']
        assert record['name'] in anchor['aria-label'] and anchor['title'] == record['name']
        assert anchor['target'] == '_blank' and 'noopener' in anchor['rel']
        image = anchor.select_one('img')
        assert image and image['alt'] == '' and image['width'] == image['height'] == '48'
        icon = PREVIEW / image['src'].lstrip('/')
        assert hashlib.sha256(icon.read_bytes()).hexdigest() == record['sha256'], icon
    assert len(docs[''].select('#video-editing .activity-highlights > li')) == 2
    assert '約90%' in docs[''].select_one('#video-editing').get_text()
    assert not docs[''].select_one('#video-editing').find_parent('details')
    assert docs[''].select_one('#activities h3').get_text(strip=True) == '技術発信'
    assert docs[''].select_one('#personal-development h3').get_text(strip=True) == '個人開発'
    assert '（Markdownプレビュー・タブのコピーなど）' not in docs[''].get_text()
    assert not docs[''].select('#activities a[href*="github.com"]')
    assert not docs[''].select('#activities .plain-link')
    assert docs[''].select_one('#product-pr a.pr-estimate-link[href="/pricing/"]')
    removed = document(PREVIEW, 'activities')
    assert not removed.select('main')
    assert removed.select_one('meta[http-equiv="refresh"]')['content'] == '0;url=/#activities'
    removed_services = document(PREVIEW, 'services')
    assert not removed_services.select('main')
    assert removed_services.select_one('meta[http-equiv="refresh"]')['content'] == '0;url=/#ai-adoption'
    assert not docs[''].select('[data-pattern]'), 'Comparison tabs do not belong to the site'
    result = {'pages': pages, 'links_and_assets': 'passed', 'quote_dom_matches_expected_copy': True, 'quote_data_unchanged': True, 'form_fields_unchanged': True, 'contact_entry_header_only': True, 'forms_send': False}
    output = PREVIEW.parent / 'selection'
    output.mkdir(exist_ok=True)
    (output / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    validate()
