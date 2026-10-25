#!/usr/bin/env python3
"""Export the approved V3 design as ordinary, independently addressable pages."""
import html
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
design = runpy.run_path(str(HERE / 'build_v3.py'))
OUT = HERE / 'site'
OUT.mkdir(exist_ok=True)
BASE = 'https://studio.msyn.me'
paths = {'home':'/', 'profile':'/profile/', 'works':'/works/', 'services':'/services/',
         'media':'/media/', 'talks':'/talks/', 'membership':'/membership/', 'contact':'/contact/'}
titles = design['titles']
descriptions = {'home':'WebエンジニアのMasaya Nishigakiです。現在はテックリードとしてMCPサーバーやAPI開発に携わり、個人のYouTubeチャンネルで発信しています。', **design['intros']}
home_builder = runpy.run_path(str(HERE / 'build_home.py'))
home_page = home_builder['build'](design, OUT)
site_builder = runpy.run_path(str(HERE / 'build_site_design.py'))
site_design = site_builder['build'](OUT)

for asset in (HERE / 'preview').glob('*.webp'):
    shutil.copyfile(asset, OUT / asset.name)
for name in ('favicon.svg', 'apple-touch-icon.png', 'og-pricing.png', 'og-profile.png'):
    shutil.copyfile(HERE.parent.parent / 'site' / name, OUT / name)
# Link previews cache the image by its URL, so a redrawn og-profile.png (build_og.py) gets a new address.
# og-profile.png itself stays published for previews that already point at it.
for stale in OUT.glob('og-profile.*.png'):
    stale.unlink()
og_bytes = (OUT / 'og-profile.png').read_bytes()
OG_IMAGE = 'og-profile.' + hashlib.sha256(og_bytes).hexdigest()[:12] + '.png'
(OUT / OG_IMAGE).write_bytes(og_bytes)

def public_body(payload):
    for key, filename in design['files'].items():
        target = paths['home' if key == 'mobile' else key]
        payload = payload.replace('href="'+filename, 'href="'+target)
    payload = payload.replace('href="https://studio.msyn.me/pricing/"', 'href="/pricing/"')
    payload = payload.replace('</nav><div class="v3-footer-bottom">', '<a href="/pricing/">PR動画制作の見積もり</a></nav><div class="v3-footer-bottom">')
    payload = re.sub(r'src="([^"/]+\.webp)"', r'src="/\1"', payload)
    payload = re.sub(r'<a\b(?![^>]*\btarget=)([^>]*href="https?://[^>]+)>',
        lambda m: '<a'+m.group(1)+' target="_blank" rel="noopener noreferrer">', payload)
    return payload

# Google Analytics 4 (property "Miyabiya Studio (studio.msyn.me)", approved 2026-09-25).
# Enhanced measurement covers page views, scrolls and outbound links; the events below add
# the purpose-based entry buttons, the contact form and email links.
GA4_ID = 'G-0HHRPGZRZB'
GA4 = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
       f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');"
       "const inquiryKinds={'開発・AI導入のご依頼':'development','PR・タイアップのご依頼':'pr','登壇のご依頼':'talk','動画編集のご依頼':'video','採用・業務委託のご相談':'recruit','その他':'other'};"
       "const inquiryKind=value=>Object.prototype.hasOwnProperty.call(inquiryKinds,value)?inquiryKinds[value]:'unselected';"
       "const track=(name,detail={})=>gtag('event',name,{page:location.pathname,...detail});"
       "document.addEventListener('click',e=>{const a=e.target.closest('a,button');if(!a)return;"
       "if(a.id==='wizard-open')track('pricing_start',{mode:'wizard'});"
       "const cta=a.matches('[data-site-action],[data-quote-inquiry],[data-quote-copy],.business-cta,.v3-primary,.v3-secondary,.btn,.estimate-button,.estimate-copy-button,#pricing-wizard .button,#inquiry-form button[type=submit]');"
       "if(cta){let action='other';if(a.hasAttribute('data-quote-inquiry'))action='quote_inquiry';else if(a.hasAttribute('data-quote-copy'))action='quote_copy';else if(a.id==='wizard-open')action='pricing_start';else if(a.id==='save-pdf'||a.id==='estimate-pdf')action='quote_pdf';else if(a.id==='wizard-copy-url'||a.id==='estimate-share')action='quote_share';else if(a.id==='show-alternatives')action='quote_compare';else if(a.closest('#inquiry-form'))action='inquiry_submit';else if(a.href){const u=new URL(a.href,location.href);action=u.protocol==='mailto:'?'email':u.pathname.startsWith('/contact')?'contact':u.pathname.startsWith('/pricing')?'pricing':u.pathname.endsWith('/join')?'membership':'details';}"
       "const position=a.closest('#pricing-wizard,#legacy-estimate')?'estimate':a.closest('.hero-priority-actions')?'hero':a.closest('.page-actions')?'page_header':a.closest('header')?'header':'content';track('cta_click',{action,position});}"
       "if(a.href?.startsWith('mailto:'))track('email_click');"
       "else if(['x.com','www.instagram.com','instagram.com'].includes(a.hostname)&&location.pathname.startsWith('/contact'))track('dm_click',{service:a.hostname});},true);"
       "const startedForms=new WeakSet();document.addEventListener('input',e=>{const f=e.target.closest('#inquiry-form');if(!f||startedForms.has(f)||e.target.name==='website')return;startedForms.add(f);track('inquiry_start',{kind:inquiryKind(f.elements.kind.value)});},true);"
       "document.addEventListener('site:pricing-start',e=>{if(e.detail?.mode==='legacy')track('pricing_start',{mode:'legacy'});});"
       "document.addEventListener('site:pricing-complete',e=>{if(['wizard','legacy'].includes(e.detail?.mode))track('pricing_complete',{mode:e.detail.mode});});"
       "document.addEventListener('site:inquiry-sent',e=>{const kind=inquiryKind(e.detail?.kind);if(kind!=='unselected')track('generate_lead',{kind});});</script>")

def document(key, body):
    # 見出しの装飾 (decorate) で文字が分割される前に、文言の置き換えを済ませる。
    import copy_updates
    body = copy_updates.apply(body)
    body, legacy_styles = site_builder['decorate'](key, body, paths, titles)
    route = paths[key]
    title = 'Masaya Nishigaki | Miyabiya Studio' if key == 'home' else titles[key]+' | Miyabiya Studio'
    desc = descriptions[key]
    person = {'@context':'https://schema.org', '@type':'Person', 'name':'Masaya Nishigaki',
        'url':BASE+'/', 'jobTitle':'Webエンジニア・テックリード', 'image':BASE+'/hero-photo.webp',
        'sameAs':['https://www.youtube.com/@masayan-ai-hack','https://x.com/masayan_ai_hack','https://github.com/masayan1126',
                  'https://www.instagram.com/miyabiya1126/','https://zenn.dev/masayan1126','https://substack.com/@masayan1126',
                  'https://speakerdeck.com/masayan1126'],
        # Approved 2026-09-25: nickname, expertise and the trade name for search and AI answers.
        'alternateName':'まさやん', 'brand':{'@type':'Brand','name':'Miyabiya Studio'},
        'knowsAbout':['Claude Code','Model Context Protocol (MCP)','AI駆動開発','AIエージェント','Python','TypeScript','Django','FastAPI','Vue.js','Google Cloud','動画編集']}
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{BASE}{route}"><meta property="og:type" content="website">
<meta property="og:site_name" content="Miyabiya Studio"><meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{BASE}{route}"><meta property="og:image" content="{BASE}/{OG_IMAGE}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Masaya Nishigaki Webエンジニア・テックリード">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#133F8F">
<link rel="icon" href="/avatar.webp" type="image/webp"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(person,ensure_ascii=False)}</script>{GA4}{legacy_styles}{site_design['head']}{home_page['head'] if key == 'home' else ''}
<style>html{{scroll-behavior:smooth}}[id]{{scroll-margin-top:104px}}@media(max-width:820px){{[id]{{scroll-margin-top:88px}}}}:focus-visible{{outline:3px solid #4164A5;outline-offset:4px}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}</style>
</head><body class="site-renewal" data-page="{key}">{body}
<script>(()=>{{const panel=document.getElementById('ratecard');if(!panel)return;const reveal=()=>{{if(location.hash==='#ratecard'){{panel.open=true;panel.scrollIntoView();}}}};window.addEventListener('hashchange',reveal);reveal();}})();</script>
</body></html>'''

for key, path in paths.items():
    body = public_body(home_page['body'] if key == 'home' else design['public_payloads'][key])
    target = OUT / path.strip('/') / 'index.html'
    target.parent.mkdir(exist_ok=True)
    target.write_text(document(key, body))

# The simulator replaces the previous static rate page at its existing URL.
media = public_body(design['public_payloads']['media'])
style = re.search(r'<style>.*?</style>', media, re.S).group()
header = re.search(r'<header.*?</header>', media, re.S).group()
footer = re.search(r'<footer.*?</footer>', media, re.S).group()
paths['pricing'] = '/pricing/'
titles['pricing'] = 'PR動画制作の見積もり'
descriptions['pricing'] = 'YouTube本編・ショート・X投稿を組み合わせて、制作範囲と概算料金を確認できます。選択内容をURLで共有し、PDFに保存できます。未確定の料金は要相談です。'
pricing_builder = runpy.run_path(str(HERE / 'build_pricing.py'))
# Shared links keep their original rates, even after the main price list changes.
rate_data = pricing_builder['public_rates']()
rate_version = hashlib.sha256(json.dumps(rate_data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]
rate_data['rateVersion'] = rate_version
archive = HERE / 'pricing-rates'
archive.mkdir(exist_ok=True)
snapshot = archive / (rate_version + '.json')
if not snapshot.exists():
    snapshot.write_text(json.dumps(rate_data, ensure_ascii=False, indent=2) + '\n')
# Export the managed archive exactly; discarded local prototypes are not releases.
exported_archive = OUT / 'pricing-rates'
if exported_archive.exists():
    for stale in exported_archive.glob('*.json'):
        if not (archive / stale.name).exists():
            stale.unlink()
shutil.copytree(archive, OUT / 'pricing-rates', dirs_exist_ok=True)
# Content-addressed assets prevent an older cached stylesheet or model from mixing
# with the updated estimate form.
for stale in OUT.iterdir():
    if re.fullmatch(r'pricing(?:-model|-ui|-pdf|-wizard|-legacy)?\.[a-f0-9]{12}\.(?:css|mjs)', stale.name):
        stale.unlink()
def pricing_asset(stem, suffix, content):
    digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    filename = f'{stem}.{digest}.{suffix}'
    (OUT / filename).write_text(content)
    return filename
model_name = pricing_asset('pricing-model', 'mjs', (HERE / 'pricing-model.mjs').read_text())
pdf_source = (HERE / 'pricing-pdf.mjs').read_text().replace("'./pricing-model.mjs'", "'./"+model_name+"'")
pdf_name = pricing_asset('pricing-pdf', 'mjs', pdf_source)
wizard_source = (HERE / 'pricing-wizard.mjs').read_text().replace("'./pricing-model.mjs'", "'./"+model_name+"'").replace("'./pricing-pdf.mjs'", "'./"+pdf_name+"'")
wizard_name = pricing_asset('pricing-wizard', 'mjs', wizard_source)
legacy_source = (HERE / 'pricing-legacy.mjs').read_text().replace("'./pricing-model.mjs'", "'./"+model_name+"'").replace("'./pricing-pdf.mjs'", "'./"+pdf_name+"'")
legacy_name = pricing_asset('pricing-legacy', 'mjs', legacy_source)
ui_source = (HERE / 'pricing-ui.mjs').read_text().replace("'./pricing-model.mjs'", "'./"+model_name+"'").replace("'./pricing-wizard.mjs'", "'./"+wizard_name+"'").replace("'./pricing-legacy.mjs'", "'./"+legacy_name+"'")
ui_name = pricing_asset('pricing-ui', 'mjs', ui_source)
shutil.copytree(HERE / 'pdf-assets', OUT / 'pdf-assets', dirs_exist_ok=True)
vendor = OUT / 'pdf-vendor'
vendor.mkdir(exist_ok=True)
modules = HERE.parent.parent / 'node_modules'
for source, filename in (
    ('pdf-lib/dist/pdf-lib.esm.min.js', 'pdf-lib-1.17.1.mjs'),
    ('pdf-lib/LICENSE.md', 'pdf-lib-LICENSE.md'),
):
    shutil.copyfile(modules / source, vendor / filename)
subprocess.run([
    str(modules / 'esbuild/bin/esbuild'), str(modules / '@pdf-lib/fontkit/dist/fontkit.es.js'),
    '--bundle', '--format=esm', '--platform=browser', '--minify',
    '--outfile='+str(vendor / 'fontkit-1.1.1.mjs'), '--log-level=warning',
], check=True)
css_name = pricing_asset('pricing', 'css', (HERE / 'pricing.css').read_text())
wizard_css = (HERE / 'pricing-wizard.css').read_text()
compiled_css = subprocess.run([str(modules / 'esbuild/bin/esbuild'), '--loader=css', '--target=safari15', '--log-level=warning'],input=wizard_css,text=True,capture_output=True,check=True).stdout
wizard_css_name = pricing_asset('pricing-wizard', 'css', compiled_css)
(OUT / 'pricing-wizard.css').write_text(compiled_css)
pricing_body = pricing_builder['content'](rate_data).replace('/pricing.css', '/'+css_name).replace('/pricing-wizard.css', '/'+wizard_css_name).replace('/pricing-ui.mjs', '/'+ui_name)
pricing = '<div class="v3 v3-detail">'+style+header+pricing_body+footer+'</div>'
(OUT / 'pricing').mkdir(exist_ok=True)
(OUT / 'pricing/index.html').write_text(document('pricing',pricing))
# Keep the existing asset URLs available for previously opened pages.
for asset in ('pricing.css', 'pricing-model.mjs', 'pricing-ui.mjs', 'pricing-pdf.mjs', 'pricing-wizard.mjs', 'pricing-legacy.mjs'):
    shutil.copyfile(HERE / asset, OUT / asset)
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+p+'</loc></url>' for p in paths.values())+'</urlset>')
(OUT / '_redirects').write_text('/ratecard /pricing/ 301\n/price /pricing/ 301\n')
(OUT / '_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/*.webp\n  Cache-Control: public, max-age=604800\n/*.png\n  Cache-Control: public, max-age=604800\n')
(OUT / '_headers').write_text((OUT / '_headers').read_text() + '/home-assets/*\n  Cache-Control: public, max-age=31536000, immutable\n')
(OUT / '_headers').write_text((OUT / '_headers').read_text() + '/site-assets/*\n  Cache-Control: public, max-age=31536000, immutable\n')
# Overlay the latest YouTube figures on the approved snapshot values (set YOUTUBE_STATS_OFFLINE=1 to reuse the cache).
import os
import youtube_stats
import copy_updates
youtube = youtube_stats.load(fetch=os.environ.get('YOUTUBE_STATS_OFFLINE') != '1')
for page_path in paths.values():
    target = OUT / page_path.strip('/') / 'index.html'
    target.write_text(copy_updates.apply(youtube_stats.apply(target.read_text(), youtube)))
print('YouTube:', f"{youtube['subs']:,}", 'subscribers as of', youtube['date'])
latest = youtube_stats.load_latest(fetch=os.environ.get('YOUTUBE_STATS_OFFLINE') != '1')
for video in latest:
    shutil.copyfile(HERE / 'latest-thumbs' / (video['id'] + '.webp'), OUT / ('latest-thumb-' + video['id'] + '.webp'))
home_path = OUT / 'index.html'
home_anchor = '<section class="career-chapters" data-depth="excerpt" id="career-history">'
home_html = home_path.read_text()
assert home_anchor in home_html
home_path.write_text(home_html.replace(home_anchor, youtube_stats.render_latest(latest) + home_anchor, 1))
# The top page is an excerpt of the detail pages, so the latest videos also appear on the YouTube page (2026-09-30).
media_path = OUT / 'media/index.html'
media_html = media_path.read_text()
media_anchor = '<section class="works-story detail-feature" id="channel-story">'
assert media_anchor in media_html
media_path.write_text(media_html.replace(media_anchor, youtube_stats.render_latest(latest) + media_anchor, 1))
# Sharing the design comparison is on hold; publish only the profile website.
# Every link to another site opens in a new tab, including sections added after public_body (approved 2026-09-25).
def external_new_tab(page):
    return re.sub(r'<a\b(?![^>]*\btarget=)([^>]*\bhref="https?://[^"]+"[^>]*)>', r'<a\1 target="_blank" rel="noopener noreferrer">', page)
for page_path in paths.values():
    target = OUT / page_path.strip('/') / 'index.html'
    # Break the long service heading between its two phrases instead of mid-word (2026-09-25).
    page = external_new_tab(target.read_text()).replace('<span>AIエージェントの設計・ハーネス構築</span>',
        '<span><span class="type-phrase">AIエージェントの</span><wbr><span class="type-phrase">設計・ハーネス構築</span></span>')
    target.write_text(page)

# Page text now changes at build time (video titles, figures), so extend the Japanese font subset
# with any new characters and rebuild once. Needs the full Noto Sans JP variable font locally.
import sys
from fontTools.ttLib import TTFont
FULL_FONT = HERE.parents[1] / 'docs/pricing/private/pdf-qa/NotoSansJP-variable.ttf'
SUBSET = HERE / 'site-assets/studio-jp.woff2'
covered = TTFont(SUBSET).getBestCmap()
page_text = ''
# Include labels rendered by the simulator after the initial HTML is loaded.
page_text += (HERE / 'pricing-wizard.mjs').read_text() + (HERE / 'pricing-model.mjs').read_text()
for page_path in paths.values():
    source = (OUT / page_path.strip('/') / 'index.html').read_text()
    source = re.sub(r'<(script|style)[\s\S]*?</\1>', '', source)
    page_text += html.unescape(re.sub(r'<[^>]+>', '', source))
missing = sorted({c for c in page_text if ord(c) > 0x2000 and ord(c) not in covered})
if missing and os.environ.get('FONT_SUBSET_PASS') != '2' and FULL_FONT.exists():
    unicodes = ','.join('U+%04X' % c for c in sorted(set(covered) | {ord(c) for c in missing}))
    subprocess.run([sys.executable, '-m', 'fontTools.subset', str(FULL_FONT), '--unicodes=' + unicodes,
                    '--layout-features=ccmp,liga,locl,vert,vrt2,halt,kern,palt,vhal,vkrn,vpal', '--flavor=woff2',
                    '--output-file=' + str(SUBSET)], check=True)
    print('Font subset extended with', ''.join(missing), '- rebuilding once')
    subprocess.run([sys.executable, __file__], check=True, env={**os.environ, 'FONT_SUBSET_PASS': '2', 'YOUTUBE_STATS_OFFLINE': '1'})
    sys.exit(0)
if missing:
    print('警告: 日本語フォントに無い文字があります:', ''.join(missing))
print('Public pages:',len(paths),'in',OUT)
