"""Build a local-only design study without changing the public export.

Run from any directory. The generated pages use the existing asset files and
pricing modules through serve.py, keeping the original URL paths intact.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
import shutil
from monochrome import neutralize_css, neutralize_paint
from content import page_content, header, footer

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
PUBLIC = PROJECT / 'canvas/v3/site'
OUT = PROJECT / 'output/editorial-concept/site'
PAGES = ['', 'profile', 'works', 'services', 'media', 'talks', 'membership', 'pricing', 'contact']


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ('editorial.css', 'editorial.mjs'):
        shutil.copyfile(HERE / name, OUT / name)
    asset_dir = OUT / 'editorial-assets'
    asset_dir.mkdir(exist_ok=True)
    checks = []
    for page in PAGES:
        path = Path(page) / 'index.html'
        original = (PUBLIC / path).read_text()
        soup = BeautifulSoup(original, 'html.parser')
        soup.body['class'] = list(dict.fromkeys(soup.body.get('class', []) + ['editorial']))
        soup.select_one('.v3-head').replace_with(BeautifulSoup(header(page), 'html.parser'))
        soup.select_one('.v3-footer').replace_with(BeautifulSoup(footer(), 'html.parser'))
        for art in list(soup.select('.detail-page-art')):
            art.decompose()
        for intro in soup.select('.detail-page-intro'):
            intro['class'] = [name for name in intro.get('class', []) if name != 'detail-page-intro']
        # Analytics and the immersive hero belong to the existing public site.
        for script in list(soup.select('script')):
            if 'googletagmanager' in script.get('src', '') or 'gtag(' in script.get_text():
                script.decompose()
            elif not page and '/home-assets/' in script.get('src', ''):
                script.decompose()
        content = page_content(page, soup)
        if content is not None:
            soup.select_one('main').replace_with(BeautifulSoup(content, 'html.parser'))
        if not page:
            for link in list(soup.head.select('link[href^="/home-assets/"]')):
                link.decompose()
        # Keep form validation and quote handoff, but the local study never sends.
        for form in soup.select('form#inquiry-form'):
            form['action'] = '/__preview/contact'
            form['data-editorial-preview'] = 'true'
        # Local neutral copies cover every interaction state without changing
        # the public palette, pricing data or calculation/PDF modules.
        for link in soup.select('link[rel="stylesheet"]'):
            href = link.get('href', '')
            source = (PUBLIC / href.lstrip('/')).resolve()
            if not source.is_relative_to(PUBLIC.resolve()) or not source.is_file():
                raise ValueError(f'Unexpected stylesheet: {href}')
            css = neutralize_css(source.read_text())
            name = f'neutral-{hashlib.sha256(css.encode()).hexdigest()[:12]}.css'
            (asset_dir / name).write_text(css)
            link['href'] = '/editorial-assets/' + name
        for style in soup.select('style'):
            style.string = neutralize_css(style.get_text())
        for element in soup.select('[style]'):
            element['style'] = neutralize_css(element['style'])
        for element in soup.select('svg, svg *'):
            for attribute in ('fill', 'stroke', 'stop-color', 'flood-color', 'lighting-color'):
                if element.has_attr(attribute):
                    element[attribute] = neutralize_paint(element[attribute])
        for meta in soup.select('meta[name="theme-color"]'):
            meta['content'] = '#ffffff'
        for meta in list(soup.head.select('meta[name="robots"]')):
            meta.decompose()
        soup.head.append(soup.new_tag('meta', attrs={'name': 'robots', 'content': 'noindex,nofollow'}))
        soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/editorial.css'}))
        soup.head.append(soup.new_tag('script', attrs={'type': 'module', 'src': '/editorial.mjs'}))
        result = str(soup).replace('https://studio.msyn.me/api/contact', '/__preview/contact')
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result)
        before = BeautifulSoup(original, 'html.parser').select_one('#pricing-data')
        after = soup.select_one('#pricing-data')
        if before:
            assert before.get_text() == after.get_text(), 'Pricing data changed in preview'
        checks.append({'path': '/' + (page + '/' if page else ''), 'source_sha256': hashlib.sha256(original.encode()).hexdigest(), 'pricing_data_unchanged': before is None or before.get_text() == after.get_text()})
    manifest = {'preview_url': 'http://127.0.0.1:8777/', 'pages': checks, 'public_export_modified': False, 'forms_send': False}
    (OUT.parent / 'build.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(checks)} local preview pages: {OUT}')


if __name__ == '__main__':
    build()
