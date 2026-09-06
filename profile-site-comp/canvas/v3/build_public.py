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

for asset in (HERE / 'preview').glob('*.webp'):
    shutil.copyfile(asset, OUT / asset.name)
for name in ('favicon.svg', 'apple-touch-icon.png', 'og-pricing.png'):
    shutil.copyfile(HERE.parent.parent / 'site' / name, OUT / name)

def public_body(payload):
    for key, filename in design['files'].items():
        target = paths['home' if key == 'mobile' else key]
        payload = payload.replace('href="'+filename, 'href="'+target)
    payload = payload.replace('href="https://studio.msyn.me/pricing/"', 'href="/pricing/"')
    payload = payload.replace('</nav><div class="v3-footer-bottom">', '<a href="/pricing/">PR動画制作の見積もり</a></nav><div class="v3-footer-bottom">')
    payload = re.sub(r'src="([^"/]+\.webp)"', r'src="/\1"', payload)
    payload = re.sub(r'<a\b([^>]*href="https?://[^>]+)>',
        lambda m: '<a'+m.group(1)+' target="_blank" rel="noopener noreferrer">', payload)
    return payload

def document(key, body):
    route = paths[key]
    title = 'Masaya Nishigaki | Miyabiya Studio' if key == 'home' else titles[key]+' | Miyabiya Studio'
    desc = descriptions[key]
    person = {'@context':'https://schema.org', '@type':'Person', 'name':'Masaya Nishigaki',
        'url':BASE+'/', 'jobTitle':'Webエンジニア・テックリード', 'image':BASE+'/hero-photo.webp',
        'sameAs':['https://www.youtube.com/@masayan-ai-hack','https://x.com/masayan_ai_hack','https://github.com/masayan1126']}
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{BASE}{route}"><meta property="og:type" content="website">
<meta property="og:site_name" content="Miyabiya Studio"><meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{BASE}{route}"><meta property="og:image" content="{BASE}/hero-photo.webp">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#133F8F">
<link rel="icon" href="/avatar.webp" type="image/webp"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(person,ensure_ascii=False)}</script>
<style>html{{scroll-behavior:smooth}}[id]{{scroll-margin-top:104px}}@media(max-width:820px){{[id]{{scroll-margin-top:88px}}}}:focus-visible{{outline:3px solid #4164A5;outline-offset:4px}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}</style>
</head><body>{body}
<script>(()=>{{const panel=document.getElementById('ratecard');if(!panel)return;const reveal=()=>{{if(location.hash==='#ratecard'){{panel.open=true;panel.scrollIntoView();}}}};window.addEventListener('hashchange',reveal);reveal();}})();</script>
</body></html>'''

for key, path in paths.items():
    body = public_body(design['public_payloads'][key])
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
descriptions['pricing'] = '依頼したい作業を選んで、PR動画の制作・YouTube公開の概算料金を確認できます。選択内容と見積もりをURLで共有できます。'
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
shutil.copytree(archive, OUT / 'pricing-rates', dirs_exist_ok=True)
# Content-addressed assets prevent an older cached stylesheet or model from mixing
# with the updated estimate form.
for stale in OUT.iterdir():
    if re.fullmatch(r'pricing(?:-model|-ui|-pdf)?\.[a-f0-9]{12}\.(?:css|mjs)', stale.name):
        stale.unlink()
def pricing_asset(stem, suffix, content):
    digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    filename = f'{stem}.{digest}.{suffix}'
    (OUT / filename).write_text(content)
    return filename
model_name = pricing_asset('pricing-model', 'mjs', (HERE / 'pricing-model.mjs').read_text())
pdf_source = (HERE / 'pricing-pdf.mjs').read_text().replace("'./pricing-model.mjs'", "'./"+model_name+"'")
pdf_name = pricing_asset('pricing-pdf', 'mjs', pdf_source)
ui_source = (HERE / 'pricing-ui.mjs').read_text().replace("'./pricing-model.mjs'", "'./"+model_name+"'").replace("'./pricing-pdf.mjs'", "'./"+pdf_name+"'")
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
pricing_body = pricing_builder['content'](rate_data).replace('/pricing.css', '/'+css_name).replace('/pricing-ui.mjs', '/'+ui_name)
pricing = '<div class="v3 v3-detail">'+style+header+pricing_body+footer+'</div>'
(OUT / 'pricing').mkdir(exist_ok=True)
(OUT / 'pricing/index.html').write_text(document('pricing',pricing))
# Keep the existing asset URLs available for previously opened pages.
for asset in ('pricing.css', 'pricing-model.mjs', 'pricing-ui.mjs', 'pricing-pdf.mjs'):
    shutil.copyfile(HERE / asset, OUT / asset)
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+p+'</loc></url>' for p in paths.values())+'</urlset>')
(OUT / '_redirects').write_text('/ratecard /pricing/ 301\n/price /pricing/ 301\n')
(OUT / '_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/*.webp\n  Cache-Control: public, max-age=604800\n/*.png\n  Cache-Control: public, max-age=604800\n')
# Sharing the design comparison is on hold; publish only the profile website.
print('Public pages:',len(paths),'in',OUT)
