# coding: utf-8
"""Build five private brand-icon proposals without changing the adopted site."""
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup
import json
import shutil

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SITE = PROJECT / 'output/editorial-concept/site'
OUT = SITE / '__review/brand-icons'


def mark(key, css_class=''):
    svg = BeautifulSoup((HERE / 'marks' / f'{key}.svg').read_text(), 'html.parser').svg
    svg['class'] = css_class
    svg['aria-hidden'] = 'true'
    svg['focusable'] = 'false'
    return str(svg)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    config = json.loads((HERE / 'options.json').read_text())
    options = config['options']
    selected = config.get('selected', options[0]['id'])
    shutil.copytree(HERE / 'marks', OUT / 'marks', dirs_exist_ok=True)
    for name in ['review.css', 'review.mjs']:
        shutil.copyfile(HERE / name, OUT / name)
    cards = []
    for option in options:
        key = option['id']
        doc = BeautifulSoup((SITE / 'index.html').read_text(), 'html.parser')
        original = doc.select_one('.editorial-brand-icon')
        original.replace_with(BeautifulSoup(mark(key, 'editorial-brand-icon'), 'html.parser').svg)
        doc.title.string = f'{key.upper()}案・{option["label"]} | Miyabiya Studio'
        (OUT / f'{key}.html').write_text(str(doc))
        recommended = '<span class="recommendation">採用</span>' if option.get('adopted') else ('<span class="recommendation">おすすめ</span>' if option.get('recommended') else '')
        cards.append(f'''<li class="candidate" id="proposal-{key}"><h2>{key.upper()}｜{escape(option['label'])}{recommended}</h2><p class="note">{escape(option['note'])}</p><div class="mark-stage">{mark(key,'enlarged-mark')}</div><div class="brand-sample">{mark(key,'actual-mark')}<span>Miyabiya Studio</span></div><div class="small-sample">{mark(key,'mobile-mark')}<span>スマホでの大きさ：20px</span></div><button class="preview-button" type="button" data-preview="{key}" aria-label="{key.upper()}案をトップで確認">トップで見る <span aria-hidden="true">→</span></button></li>''')
    choices = ''.join(f'<option value="{o["id"]}"' + (' selected' if o['id'] == selected else '') + f'>{o["id"].upper()}｜{escape(o["label"])}</option>' for o in options)
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>ブランドアイコン5案 | Miyabiya Studio</title><link rel="stylesheet" href="/editorial-assets/fonts/ibm-plex-sans-jp/font-faces.css"><link rel="stylesheet" href="review.css"><script type="module" src="review.mjs"></script></head><body><main class="review-shell"><header class="review-intro"><h1>ブランドアイコン5案</h1><p>屋号の左に置くマークを、太さ・曲線・形の異なる5案で比較できます。</p></header><div class="view-tabs" role="tablist" aria-label="比較の表示"><button role="tab" id="compare-tab" aria-controls="compare-view" aria-selected="true">5案を比較</button><button role="tab" id="context-tab" aria-controls="context-view" aria-selected="false" tabindex="-1">トップで確認</button></div><section id="compare-view" role="tabpanel" aria-labelledby="compare-tab"><p class="comparison-settings">全案共通：黒1色／屋号18px／マークはPC24px・スマホ20px</p><ol class="choices">{''.join(cards)}</ol></section><section id="context-view" role="tabpanel" aria-labelledby="context-tab" hidden><div class="context-tools"><label for="context-choice">アイコン<select id="context-choice">{choices}</select></label><button id="back-to-compare" type="button">5案に戻る</button></div><div class="context-stage"><iframe id="context-frame" title="選んだアイコンをトップで確認" sandbox="allow-scripts allow-same-origin allow-popups allow-forms"></iframe></div></section></main></body></html>''')
    (OUT / 'comparison.json').write_text(json.dumps({'options':options,'selected':selected,'origin':'Original SVG proposals','icon_sizes':{'desktop':24,'mobile':20},'brand_size':18,'columns':{'desktop':2,'mobile':1},'public_modified':False,'adopted_icon_modified':False},ensure_ascii=False,indent=2)+'\n')
    print(OUT / 'index.html')


if __name__ == '__main__':
    build()
