# -*- coding: utf-8 -*-
"""Shared presentation layer; copy and calculator contracts remain upstream."""
from pathlib import Path
import hashlib
import re
import site_journeys
HERE=Path(__file__).resolve().parent
def build(output):
    assets=output/'site-assets';assets.mkdir(exist_ok=True)
    def asset(stem,suffix,data):
        if isinstance(data,str):data=data.encode()
        name=f'{stem}.{hashlib.sha256(data).hexdigest()[:12]}.{suffix}'
        (assets/name).write_bytes(data)
        return '/site-assets/'+name
    # Case illustrations ship as 800px WebP made from the PNG originals (approved 2026-09-25).
    for image in (HERE/'works-images').glob('*.webp'):
        asset(image.stem,'webp',image.read_bytes())
    jp=asset('studio-jp','woff2',(HERE/'site-assets/studio-jp.woff2').read_bytes())
    en=asset('studio-sans','woff2',(HERE/'site-assets/studio-sans.woff2').read_bytes())
    css=(HERE/'site-design.css').read_text().replace('%%JP%%',jp).replace('%%EN%%',en)
    css+='\n'+(HERE/'works-story.css').read_text()
    css+='\n'+(HERE/'career-chapters.css').read_text()
    css+='\n'+(HERE/'site-palette.css').read_text()
    css+='\n'+(HERE/'page-consistency.css').read_text()
    css+='\n'+(HERE/'site-journeys.css').read_text()
    css+='\n'+(HERE/'site-motion.css').read_text()
    css_url=asset('site','css',css);js_url=asset('navigation','mjs',(HERE/'site-navigation.js').read_text())
    career_js=asset('career','mjs',(HERE/'career-chapters.js').read_text())
    works_js=asset('works','mjs',(HERE/'works-story.js').read_text())
    motion_js=asset('motion','mjs',(HERE/'site-motion.mjs').read_text())
    for name in ['NotoSansJP-OFL.txt','Manrope-OFL.txt']:(assets/name).write_bytes((HERE/'site-assets'/name).read_bytes())
    return {'head':f'<link rel="preload" href="{jp}" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{css_url}"><script type="module" src="{js_url}"></script><script type="module" src="{career_js}"></script><script type="module" src="{works_js}"></script><script type="module" src="{motion_js}"></script>'}
def decorate(key,body,paths,titles):
    body=body.replace('>実績<', '>実績・成果<')
    menu_paths={**paths,'pricing':'/pricing/'};labels={**titles,'pricing':'PR動画制作の見積もり'}
    # Membership is for viewers and is reached from the YouTube page, not the site menu (approved 2026-09-25).
    menu='<details class="site-menu"><summary aria-label="ページ一覧"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path class="menu-line-a" d="M3 7h18"/><path class="menu-line-b" d="M3 17h18"/></svg></summary><div class="menu-panel">'+site_journeys.menu_links(key, menu_paths, labels)+'</div></details>'
    # The desktop navigation prioritizes requests; the full index keeps biography and talks reachable.
    body=re.sub(r'(<header class="(?:v3-head|masthead)">.*?)<nav\b.*?</nav>', lambda m:m[1]+site_journeys.main_nav(key), body, count=2, flags=re.S)
    body=re.sub(r'<a class="v3-contact-link"[^>]*>.*?</a>', site_journeys.action('相談する', '/contact/#contact-form').replace('site-action ', 'v3-contact-link site-action '), body, count=1, flags=re.S)
    body=body.replace('</nav></header>', '</nav>'+site_journeys.action('相談する', '/contact/#contact-form')+'</header>', 1) if key == 'home' else body
    if key in site_journeys.PAGE_TOOLS:
        body=re.sub(r'(<section class="v3-page-head">.*?)(</div></section>)', lambda m:m[1]+site_journeys.page_tools(key)+m[2], body, count=1, flags=re.S)
    body=re.sub(r'(<header class="v3-head">.*?)(</div></header>)',lambda m:m[1]+menu+m[2],body,count=1,flags=re.S)
    body=re.sub(r'(<header class="masthead">.*?)(</header>)',lambda m:m[1]+menu+m[2],body,count=1,flags=re.S)
    body=re.sub(r'(<section class="v3-page-head">.*?<h1>)([^<]+)(</h1>)',lambda m:m[1]+'<span>'+m[2].replace('・','・</span><wbr><span>')+'</span>'+m[3],body,count=1,flags=re.S)
    body=body.replace('<span>Webサービス開発・AI導入支援</span>','<span><span class="type-unit">Webサービス開発・</span><wbr><span class="type-unit">AI導入支援</span></span>')
    # Emphasize one key term per business or case heading, without changing copy.
    def emphasize_heading(match):
        content = match[2]
        for term in ('AI導入支援', 'AI駆動開発', 'MCPサーバー', 'YouTube', '技術登壇'):
            if term in content:
                content = content.replace(term, '<strong class="accent-key">' + term + '</strong>', 1)
                break
        return match[1] + content + match[3]
    body=re.sub(r'(<h[23] class="(?:business-title|story-title)"[^>]*>)(.*?)(</h[23]>)', emphasize_heading, body, flags=re.S)
    body=body.replace('<main>','<main id="main-content" tabindex="-1">',1).replace('<main class="estimate-page"','<main id="main-content" tabindex="-1" class="estimate-page"',1)
    styles=''.join(re.findall(r'<style>.*?</style>',body,re.S));body=re.sub(r'<style>.*?</style>','',body,flags=re.S)
    return '<a class="skip-link" href="#main-content">本文へ移動</a>'+body,styles
