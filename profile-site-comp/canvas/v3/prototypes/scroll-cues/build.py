# coding: utf-8
"""Private studies of five ways to signal content below the first viewport."""
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup
import json
import shutil

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SITE = PROJECT / 'output/editorial-concept/site'
OUT = SITE / '__review/scroll-cues'
ACTIVITIES = [('activities','技術発信'),('product-pr','製品PR'),('personal-development','個人開発'),('video-editing','AI動画編集'),('speaking','登壇・勉強会'),('ai-adoption','AI活用支援')]
ARROW = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m6 9 6 6 6-6"/></svg>'


def diagram(key):
    index = '<div class="mini-index">技術発信　製品PR　個人開発<br>AI動画編集　登壇　AI活用支援</div>' if key == 'b' else ''
    rail = '<div class="mini-rail"><span></span></div><span class="mini-percent">0%</span>' if key == 'c' else ''
    cue = '<span class="mini-cue">ほかの活動へ ↓</span>' if key == 'a' else ('<span class="mini-cue mini-arrow">'+ARROW+'</span>' if key == 'e' else '')
    peek = '<p class="mini-peek">個人開発</p>' if key == 'd' else ''
    return f'<div class="mini-window mini-{key}" role="img" aria-label="{escape(key.upper())}案の見え方の模式図"><div aria-hidden="true"><div class="mini-brand">Miyabiya Studio</div><div class="mini-bio">自己紹介・活動の概要</div>{index}<div class="mini-activities"><p>技術発信</p><span class="mini-lines"></span><p>製品PR・タイアップ</p><span class="mini-video"></span>{peek}</div>{rail}{cue}<div class="mini-footer">© Miyabiya Studio</div></div></div>'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    config = json.loads((HERE / 'options.json').read_text())
    patterns = config['patterns']
    for name in ['cue.css','cue.mjs','review.css','review.mjs']:
        shutil.copyfile(HERE / name, OUT / name)
    source = (SITE / 'index.html').read_text()
    cards = []
    for option in patterns:
        key = option['id']
        doc = BeautifulSoup(source, 'html.parser')
        doc.body.attrs.pop('data-reading-progress', None)
        for adopted in doc.select('.site-reading-progress,script[src^="/reading-progress"]'):
            adopted.decompose()
        doc.body['data-scroll-pattern'] = key
        doc.title.string = key.upper()+'案・'+option['label']+' | Miyabiya Studio'
        doc.head.append(doc.new_tag('link',attrs={'rel':'stylesheet','href':'/__review/scroll-cues/cue.css'}))
        doc.head.append(doc.new_tag('script',attrs={'type':'module','src':'/__review/scroll-cues/cue.mjs'}))
        if key == 'b':
            links = ''.join(f'<a href="#{target}">{label}</a>' for target,label in ACTIVITIES)
            doc.select_one('.a-intro').append(BeautifulSoup('<nav class="scroll-contents" aria-label="活動に移動">'+links+'</nav>','html.parser'))
        if key == 'c':
            doc.body.append(BeautifulSoup('<div class="scroll-reading" aria-hidden="true"><span class="scroll-reading-track"><span></span></span><span class="scroll-reading-percent">0%</span></div>','html.parser'))
        if key in ('a','e'):
            appearance = ' scroll-cue-circle' if key == 'e' else ''
            label = ARROW if key == 'e' else '<span>ほかの活動へ</span><span aria-hidden="true">↓</span>'
            cue = BeautifulSoup(f'<div class="scroll-cue-dock"><a class="scroll-cue-link{appearance}" href="#personal-development" aria-label="{"ほかの活動へ移動" if key == "a" else "下の活動を見る"}">{label}</a></div>','html.parser')
            if key == 'a':
                doc.select_one('.editorial-footer').insert(0, cue)
            else:
                doc.body.append(cue)
        (OUT / f'{key}.html').write_text(str(doc))
        badge = '<span class="recommendation">採用</span>' if key == config.get('adopted') else ('<span class="recommendation">おすすめ</span>' if option.get('recommended') and not config.get('adopted') else '')
        cards.append(f'<li class="candidate"><h2>{key.upper()}｜{escape(option["label"])}{badge}</h2><p class="note">{escape(option["note"])}</p>{diagram(key)}<p class="detail">{escape(option["detail"])}</p><button class="preview-button" type="button" data-preview="{key}" aria-label="{key.upper()}案をトップで確認">トップで見る <span aria-hidden="true">→</span></button></li>')
    choices = ''.join(f'<option value="{o["id"]}"{" selected" if o["id"] == config.get("adopted") else ""}>{o["id"].upper()}｜{escape(o["label"])}</option>' for o in patterns)
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>スクロールの伝え方5案 | Miyabiya Studio</title><link rel="stylesheet" href="/editorial-assets/fonts/ibm-plex-sans-jp/font-faces.css"><link rel="stylesheet" href="review.css"><script type="module" src="review.mjs"></script></head><body><main class="review-shell"><header class="review-intro"><h1>スクロールの伝え方5案</h1><p>「トップで見る」で、最初の画面とスクロール後の動きを比較できます。</p></header><div class="view-tabs" role="tablist" aria-label="比較の表示"><button role="tab" id="compare-tab" aria-controls="compare-view" aria-selected="true">5案を比較</button><button role="tab" id="context-tab" aria-controls="context-view" aria-selected="false" tabindex="-1">トップで確認</button></div><section id="compare-view" role="tabpanel" aria-labelledby="compare-tab"><ol class="choices">{''.join(cards)}</ol></section><section id="context-view" role="tabpanel" aria-labelledby="context-tab" hidden><div class="context-tools"><label for="context-choice">表示する案<select id="context-choice">{choices}</select></label><button id="back-to-compare" type="button">5案に戻る</button></div><iframe id="context-frame" title="スクロール案をトップで確認" sandbox="allow-scripts allow-same-origin allow-popups allow-forms"></iframe></section></main></body></html>''')
    (OUT / 'comparison.json').write_text(json.dumps({'patterns':patterns,'recommendation':'a','adopted':config.get('adopted'),'columns':{'desktop':2,'mobile':1},'fixed_header_footer_preserved':True,'public_modified':False},ensure_ascii=False,indent=2)+'\n')
    print(OUT / 'index.html')


if __name__ == '__main__':
    build()
