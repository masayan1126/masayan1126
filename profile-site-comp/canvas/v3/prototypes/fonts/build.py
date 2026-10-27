# coding: utf-8
"""Build five private font proposals; never modify the public site or selected font."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SITE = PROJECT / 'output/editorial-concept/site'
OUT = SITE / '__review/fonts'
PAGES = {'home':'','profile':'profile','works':'works','talks':'talks','membership':'membership','pricing':'pricing','contact':'contact'}

SAMPLE = '''<h3>Masaya Nishigaki</h3><p class="role">Web系のシニアエンジニア・テックリード</p><p>YouTubeでのAI関連の発信・PR・個人開発・<br>AI動画編集・技術登壇などを中心に活動</p><h4>技術発信</h4><ul><li><span>YouTubeでAI駆動開発・動画制作の自動化を発信</span></li><li><span>登録者数：<strong>4,697人</strong></span></li></ul><span class="sample-action">料金を見積もる <span class="sample-arrow" aria-hidden="true">→</span></span><p class="numbers">Miyabiya Studio　0123456789<br>お問い合わせ・ご相談内容</p>'''

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((HERE / 'assets/manifest.json').read_text())
    options = json.loads((HERE / 'options.json').read_text())
    shutil.copytree(HERE / 'assets', OUT / 'assets', dirs_exist_ok=True)
    for name in ['review.css','review.mjs']:
        shutil.copyfile(HERE / name, OUT / name)
    faces = []
    for option in manifest['options']:
        for face in option['faces']:
            file = HERE / 'assets' / face['file']
            assert hashlib.sha256(file.read_bytes()).hexdigest() == face['sha256']
            faces.append(f'@font-face{{font-family:StudioFont{option["id"].upper()};font-style:normal;font-weight:{face["weight"]};font-display:swap;src:url("assets/{face["file"]}") format("{face["format"]}")}}')
    (OUT / 'fonts.css').write_text('\n'.join(faces)+'\n')
    candidates = []
    for option in options:
        key = option['id'];font = 'StudioFont'+key.upper()
        context_css = f'''@layer font-proposals{{body.site-renewal.editorial.compact-local,body.site-renewal.editorial.compact-local *{{font-family:{font},sans-serif!important;font-synthesis:none!important;font-size:14px!important;font-weight:400!important}}body.site-renewal.editorial.compact-local :is(h1,h1 a,h1 span){{font-size:24px!important;font-weight:700!important}}body.site-renewal.editorial.compact-local :is(h2,h3,h4,h5,h6,h2 span,h3 span,h4 span,.editorial-brand){{font-size:18px!important;font-weight:700!important}}body.site-renewal.editorial.compact-local :is(strong,b,button,.site-action,.pr-estimate-link){{font-weight:700!important}}}}'''
        (OUT / f'{key}.css').write_text(context_css+'\n')
        for page_key, page in PAGES.items():
            proposal = BeautifulSoup((SITE / page / 'index.html').read_text(), 'html.parser')
            proposal.title.string = key.upper()+'案・'+option['family']+' | '+proposal.title.get_text()
            for link in proposal.select('link[href="/typography.css"]'):
                link.decompose()
            for href in ['fonts.css',key+'.css']:
                proposal.head.append(proposal.new_tag('link',attrs={'rel':'stylesheet','href':'/__review/fonts/'+href}))
            for link in proposal.select('a[href]'):
                parsed = urlsplit(link['href'])
                if parsed.scheme or parsed.netloc or not parsed.path.startswith('/'):
                    continue
                target = parsed.path.strip('/')
                target_key = next((k for k,v in PAGES.items() if v == target), None)
                if target_key:
                    link['href'] = f'/__review/fonts/{key}-{target_key}.html'+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
            (OUT / f'{key}-{page_key}.html').write_text(str(proposal))
        recommended = '<span class="recommendation">おすすめ</span>' if option.get('recommended') else ''
        source = 'https://fonts.google.com/specimen/'+option['family'].replace(' ', '+')
        candidates.append(f'''<li class="candidate" id="proposal-{key}"><h2>{key.upper()}｜{escape(option['label'])}{recommended}</h2><p class="family">{escape(option['family'])}</p><p class="note">{escape(option['note'])}</p><div class="specimen" data-font="{key}" style="font-family:{font},sans-serif">{SAMPLE}</div><div class="candidate-tools"><button class="preview-button" type="button" data-preview="{key}" aria-label="{key.upper()}案をサイトで確認">サイトで見る <span aria-hidden="true">→</span></button><a class="font-source" href="{source}" target="_blank" rel="noopener noreferrer" aria-label="{option['family']}の公式配布ページ（新しいタブ）">書体の詳細 ↗</a></div></li>''')
    choices = ''.join(f'<option value="{o["id"]}">{o["id"].upper()}｜{escape(o["family"])}</option>' for o in options)
    html = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>フォント5案 | Miyabiya Studio</title><link rel="stylesheet" href="review.css"><link rel="stylesheet" href="fonts.css"><script type="module" src="review.mjs"></script></head><body><main class="review-shell" id="review-top"><header class="review-intro"><h1>フォント5案</h1><p>同じ文章・大きさ・太さ・余白で比較できます。「サイトで見る」からページ全体の印象も確認できます。</p></header><div class="view-tabs" role="tablist" aria-label="比較の表示"><button role="tab" id="compare-tab" aria-controls="compare-view" aria-selected="true">5案を比較</button><button role="tab" id="context-tab" aria-controls="context-view" aria-selected="false" tabindex="-1">サイトで確認</button></div><section id="compare-view" role="tabpanel" aria-labelledby="compare-tab"><p class="comparison-settings">全案共通：24・18・14px／本文400・見出し700</p><ol class="choices">{''.join(candidates)}</ol><p id="font-loading" class="font-loading" role="status">書体を読み込んでいます…</p><a class="back-top" href="#review-top">先頭へ戻る ↑</a></section><section id="context-view" role="tabpanel" aria-labelledby="context-tab" hidden><div class="context-tools"><label for="context-choice">フォント<select id="context-choice">{choices}</select></label><label for="context-page">ページ<select id="context-page"><option value="home">トップ</option><option value="contact">お問い合わせ</option><option value="pricing">見積もり</option><option value="profile">プロフィール</option><option value="works">実績</option><option value="talks">登壇</option><option value="membership">メンバーシップ</option></select></label></div><p class="context-note">採用前の比較用表示です。文字サイズは24・18・14px、本文400・見出し700で統一しています。</p><div class="context-stage"><iframe id="context-frame" title="フォントをサイトで確認" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe></div></section></main></body></html>'''
    (OUT / 'index.html').write_text(html)
    (OUT / 'comparison.json').write_text(json.dumps({'options':options,'sizes':[24,18,14],'weights':[400,700],'columns':{'desktop':2,'mobile':1},'public_modified':False,'selected_font_modified':False},ensure_ascii=False,indent=2)+'\n')
    print(OUT / 'index.html')

if __name__ == '__main__':
    build()
