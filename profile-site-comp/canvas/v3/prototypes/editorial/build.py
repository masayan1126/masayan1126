"""Build a local-only design study without changing the public export.

Run from any directory. The generated pages use the existing asset files and
pricing modules through serve.py, keeping the original URL paths intact.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
import shutil
import subprocess
from monochrome import neutralize_css, neutralize_paint
from interactions import motion_only_css
from content import page_content, header, footer
import content as editorial_content
from site_copy import PAGE_INFO, refine_ui_copy, centralize_quote_controls, centralize_contact_page, relocate_pr_links

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
PUBLIC = PROJECT / 'canvas/v3/site'
OUT = PROJECT / 'output/editorial-concept/site'
PAGES = ['', 'profile', 'works', 'talks', 'membership', 'pricing', 'contact']
SOURCE_PAGE = {}


def build(*, source_root=None, output_root=None, production=False):
    global PUBLIC, OUT
    base = PROJECT / 'output/editorial-base/site'
    PUBLIC = Path(source_root) if source_root else (base if base.exists() else PROJECT / 'canvas/v3/site')
    OUT = Path(output_root) if output_root else PROJECT / 'output/editorial-concept/site'
    editorial_content.SOURCE_ROOT = PUBLIC
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ('editorial.css', 'editorial.mjs', 'compact.css', 'pricing-local.css', 'reading-progress.mjs'):
        if name.endswith('.css'):
            (OUT / name).write_text(motion_only_css((HERE / name).read_text()))
        else:
            shutil.copyfile(HERE / name, OUT / name)
    if production:
        runtime = (OUT / 'editorial.mjs').read_text()
        start = runtime.index("document.addEventListener('submit', event => {")
        end = runtime.index('const preference =', start)
        (OUT / 'editorial.mjs').write_text(runtime[:start] + runtime[end:])
    # The review and the local site use the same selected scale and selectors.
    scale_module = (HERE.parent / 'typography/scales.mjs').as_uri()
    scale_script = (
        'import {adoptedPreset,presets,typographyCss} from ' + json.dumps(scale_module) + ';'
        'const values=presets[adoptedPreset].values;'
        'process.stdout.write(JSON.stringify({preset:adoptedPreset,values,css:typographyCss({values})}));'
    )
    typography = json.loads(subprocess.run(
        ['node', '--input-type=module', '-e', scale_script],
        check=True, capture_output=True, text=True,
    ).stdout)
    (OUT / 'typography.css').write_text(typography['css'] + '\n')
    asset_dir = OUT / 'editorial-assets'
    asset_dir.mkdir(exist_ok=True)
    note_icon = HERE / 'icons/note/icon.svg'
    note_source = json.loads((HERE / 'icons/note/sources.json').read_text())
    assert hashlib.sha256(note_icon.read_bytes()).hexdigest() == note_source['sha256']
    shutil.copyfile(note_icon, asset_dir / 'note-icon.svg')
    font_dir = HERE / 'assets/fonts/ibm-plex-sans-jp'
    font_manifest = json.loads((font_dir / 'manifest.json').read_text())
    for face in font_manifest['faces']:
        assert hashlib.sha256((font_dir / face['file']).read_bytes()).hexdigest() == face['sha256']
    shutil.copytree(font_dir, asset_dir / 'fonts/ibm-plex-sans-jp', dirs_exist_ok=True)
    shutil.copyfile(HERE / 'assets/avatar-mono-pixel.png', asset_dir / 'avatar-mono-pixel.png')
    extension_dir = asset_dir / 'extensions'
    extension_dir.mkdir(exist_ok=True)
    for record in editorial_content.extension_records():
        icon = HERE / 'assets/extensions' / record['image']
        assert hashlib.sha256(icon.read_bytes()).hexdigest() == record['sha256'], icon
        shutil.copyfile(icon, extension_dir / icon.name)
    for record in json.loads((HERE / 'assets/talk-cards.json').read_text()).values():
        cover = HERE / 'assets' / record['image']
        shutil.copyfile(cover, asset_dir / cover.name)
    # Rewrite interface text in private copies; shared rate/PDF/model modules
    # continue to load unchanged from the existing public asset fallback.
    # Reuse the existing handoff format without installing a second receiver.
    handoff_source = (PROJECT / 'canvas/v3/quote-contact.mjs').read_text()
    auto_install = "if (typeof document !== 'undefined' && typeof window !== 'undefined') installQuoteContact(document, window);"
    assert auto_install in handoff_source
    (OUT / 'editorial-quote-contact.mjs').write_text(refine_ui_copy(handoff_source.replace(auto_install, '')))
    copy_modules = ['editorial-quote-contact.mjs']
    sources = [*PUBLIC.glob('pricing-wizard*.mjs'),
               *PUBLIC.glob('pricing-legacy*.mjs'),
               *(PUBLIC / 'site-assets').glob('quote-contact*.mjs')]
    for source in sources:
        original_module = source.read_text()
        revised = refine_ui_copy(original_module)
        if source.name.startswith(('pricing-wizard', 'pricing-legacy')):
            revised = centralize_quote_controls(revised)
        if revised != original_module:
            relative = source.relative_to(PUBLIC)
            target = OUT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(revised)
            copy_modules.append(str(relative))
    checks = []
    for page in PAGES:
        path = Path(page) / 'index.html'
        original = (PUBLIC / SOURCE_PAGE.get(page, page) / 'index.html').read_text()
        soup = BeautifulSoup(original, 'html.parser')
        soup.body['class'] = list(dict.fromkeys(soup.body.get('class', []) + ['editorial', 'compact-local']))
        if page in SOURCE_PAGE:
            soup.body['data-page'] = page
            preview_url = 'http://127.0.0.1:8776/' + page + '/'
            for canonical in soup.select('link[rel="canonical"]'):
                canonical['href'] = preview_url
            for meta in soup.select('meta[property="og:url"]'):
                meta['content'] = preview_url
        page_title, description = PAGE_INFO[page]
        title = page_title + ' | Miyabiya Studio'
        soup.title.string = title
        for meta in soup.select('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]'):
            meta['content'] = description
        for meta in soup.select('meta[property="og:title"],meta[name="twitter:title"]'):
            meta['content'] = title
        soup.select_one('.v3-head').replace_with(BeautifulSoup(header(page), 'html.parser'))
        soup.select_one('.v3-footer').replace_with(BeautifulSoup(footer(), 'html.parser'))
        for art in list(soup.select('.detail-page-art')):
            art.decompose()
        for intro in soup.select('.detail-page-intro'):
            intro['class'] = [name for name in intro.get('class', []) if name != 'detail-page-intro']
        # Analytics and the immersive hero belong to the existing public site.
        for script in list(soup.select('script')):
            if not production and ('googletagmanager' in script.get('src', '') or 'gtag(' in script.get_text()):
                script.decompose()
            elif not page and '/home-assets/' in script.get('src', ''):
                script.decompose()
        content = page_content(page, soup)
        if content is not None:
            soup.select_one('main').replace_with(BeautifulSoup(content, 'html.parser'))
        centralize_contact_page(soup, page)
        relocate_pr_links(soup)
        if not page:
            soup.body['data-reading-progress'] = ''
            soup.body.append(BeautifulSoup('<div class="site-reading-progress" aria-hidden="true"><span class="reading-progress-track"><span></span></span><span class="reading-progress-percent">0%</span></div>', 'html.parser'))
            soup.head.append(soup.new_tag('script', attrs={'type': 'module', 'src': '/reading-progress.mjs'}))
            for link in list(soup.head.select('link[href^="/home-assets/"]')):
                link.decompose()
        # Keep form validation and quote handoff, but the local study never sends.
        for form in ([] if production else soup.select('form#inquiry-form')):
            form['action'] = '/__preview/contact'
            form['data-editorial-preview'] = 'true'
        if not production:
            public_sitekey = json.loads((PROJECT / 'canvas/v3/contact-security.json').read_text())['sitekey']
            for script in soup.select('script:not([src])'):
                if 'onContactTurnstileReady' in script.get_text():
                    script.string = script.get_text().replace(public_sitekey, '1x00000000000000000000AA')
        # Local neutral copies cover every interaction state without changing
        # the public palette, pricing data or calculation/PDF modules.
        for link in soup.select('link[rel="stylesheet"]'):
            href = link.get('href', '')
            source = (PUBLIC / href.lstrip('/')).resolve()
            if not source.is_relative_to(PUBLIC.resolve()) or not source.is_file():
                raise ValueError(f'Unexpected stylesheet: {href}')
            css = motion_only_css(neutralize_css(source.read_text()))
            name = f'neutral-{hashlib.sha256(css.encode()).hexdigest()[:12]}.css'
            (asset_dir / name).write_text(css)
            link['href'] = '/editorial-assets/' + name
        for style in soup.select('style'):
            style.string = motion_only_css(neutralize_css(style.get_text()))
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
        if not production:
            soup.head.append(soup.new_tag('meta', attrs={'name': 'robots', 'content': 'noindex,nofollow'}))
        soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/editorial-assets/fonts/ibm-plex-sans-jp/font-faces.css'}))
        soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/editorial.css'}))
        soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/compact.css'}))
        soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/typography.css'}))
        if page == 'pricing':
            soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/pricing-local.css'}))
        soup.head.append(soup.new_tag('script', attrs={'type': 'module', 'src': '/editorial.mjs'}))
        result = refine_ui_copy(str(soup))
        if not production:
            result = result.replace('https://studio.msyn.me/api/contact', '/__preview/contact')
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result)
        before = BeautifulSoup(original, 'html.parser').select_one('#pricing-data')
        after = BeautifulSoup(result, 'html.parser').select_one('#pricing-data')
        if before:
            assert before.get_text() == after.get_text(), 'Pricing data changed in preview'
        checks.append({'path': '/' + (page + '/' if page else ''), 'source_sha256': hashlib.sha256(original.encode()).hexdigest(), 'pricing_data_unchanged': before is None or before.get_text() == after.get_text()})
    # A redirect shadows the public fallback on both local servers, so the
    # removed media page cannot reappear through an old URL.
    removed_media = OUT / 'media/index.html'
    removed_media.parent.mkdir(exist_ok=True)
    removed_media.write_text('''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url=/#product-pr"><link rel="canonical" href="/#product-pr"><title>製品PRの制作動画へ移動</title></head><body><a href="/#product-pr">製品PRの制作動画を見る</a></body></html>''')
    removed_activities = OUT / 'activities/index.html'
    removed_activities.parent.mkdir(exist_ok=True)
    removed_activities.write_text('''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><script>const anchors=new Set(['activities','youtube','tools','membership','personal-development']);const id=location.hash.slice(1);location.replace('/#'+(anchors.has(id)?id:'activities'));</script><meta http-equiv="refresh" content="0;url=/#activities"><link rel="canonical" href="/#activities"><title>技術発信・個人開発へ移動</title></head><body><a href="/#activities">技術発信・個人開発を見る</a></body></html>''')
    removed_services = OUT / 'services/index.html'
    removed_services.parent.mkdir(exist_ok=True)
    removed_services.write_text('''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><script>const anchors=new Set(['ai-adoption','ai-results','other-services','web-development','video-editing','product-pr']);const id=location.hash.slice(1);location.replace('/#'+(anchors.has(id)?id:'ai-adoption'));</script><meta http-equiv="refresh" content="0;url=/#ai-adoption"><link rel="canonical" href="/#ai-adoption"><title>AI活用支援へ移動</title></head><body><a href="/#ai-adoption">AI活用支援を見る</a></body></html>''')
    manifest = {'preview_url': 'http://127.0.0.1:8776/', 'compatibility_url': 'http://127.0.0.1:8777/', 'design': 'Approved A, without standalone link underlines', 'typography': {key: value for key, value in typography.items() if key != 'css'}, 'copy_modules': copy_modules, 'pages': checks, 'redirects': {'/media/': '/#product-pr', '/activities/': '/#activities', '/services/': '/#ai-adoption'}, 'public_export_modified': False, 'forms_send': False}
    record = OUT / 'build.json' if production else OUT.parent / 'build.json'
    record.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(checks)} local preview pages: {OUT}')


if __name__ == '__main__':
    build()
