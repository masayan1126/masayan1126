# coding: utf-8
"""Build the private metadata review inside the existing site review."""
from pathlib import Path
from html import escape as esc
import json
import shutil
import sys
HERE=Path(__file__).resolve().parent
V3=HERE.parents[1]
PROJECT=HERE.parents[3]
sys.path.insert(0,str(V3))
from site_metadata import PAGES,metadata,ASSETS,structured_data
from build_options import build as build_options
from share_preview import panel as share_preview_panel
OUT=PROJECT/'output/editorial-concept/site/__review/metadata'

def image_ref(page):
    rows=json.loads((ASSETS/'manifest.json').read_text())['files']
    return next(row['public_path'] for row in rows if row.get('page',None)==page)

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    options=build_options()
    shutil.copytree(HERE/'assets', OUT/'assets', dirs_exist_ok=True)
    design_cards=''.join(f'''<article class="design-card" id="design-{item['key']}"><h3>{item['key'].upper()}｜{esc(item['name'])}{'（採用）' if item['key']=='c' else ''}</h3><p class="muted">{esc(item['description'])}</p><img class="design-image" src="assets/{item['file']}" width="1200" height="630" alt="{esc(item['name'])}のOGP完成画像"><details><summary>小さな表示で見る</summary><img class="small-preview" src="assets/{item['file']}" width="300" height="158" alt="{esc(item['name'])}の幅300pxの表示" loading="lazy"></details><details><summary>正方形で見る</summary><p class="muted">中央を正方形に切り抜いた表示です。</p><img class="square-preview" src="assets/{item['file']}" width="240" height="240" alt="{esc(item['name'])}の中央を正方形に切り抜いた表示" loading="lazy"></details></article>''' for item in options['options'])
    before=json.loads((HERE/'before.json').read_text())
    state=json.loads((HERE/'state.json').read_text())
    for source,name in [(PROJECT/'site/og-profile.png','before-og.png'),(PROJECT/'site/apple-touch-icon.png','before-apple.png'),(V3/'site/avatar.webp','before-favicon.webp')]:
        shutil.copyfile(source,OUT/name)
    for name in ['review.css','review.mjs','share-preview.css','share-preview.mjs']:
        shutil.copyfile(HERE/name,OUT/name)
    old=before['pages'][0]
    old_desc=next(x['content'] for x in old['metas'] if x.get('name')=='description')
    cards=[]
    for page in PAGES:
        info=metadata(page)
        cards.append(f'''<article class="page-card"><h2>{esc(info['label'])}</h2><p class="route">{esc(info['url'])}</p><div class="search-example" aria-label="検索結果の表示例"><p class="search-site">Miyabiya Studio</p><h3>{esc(info['title'])}</h3><p>{esc(info['description'])}</p></div><img class="og-image" src="{image_ref(page)}" width="1200" height="630" alt="{esc(info['image_alt'])}" loading="lazy"></article>''')
    code=json.dumps(structured_data('', 'https://studio.msyn.me'+image_ref('')),ensure_ascii=False,indent=2)
    status='C採用・公開確認済み' if state.get('design_status')=='published' else 'C採用・正方形の見切れを修正'
    adopted_image=image_ref('')
    share_preview=share_preview_panel()
    doc=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>OGP・メタ情報 | Miyabiya Studio</title><link rel="stylesheet" href="/editorial-assets/fonts/ibm-plex-sans-jp/font-faces.css"><link rel="stylesheet" href="review.css"><link rel="stylesheet" href="share-preview.css"><script type="module" src="review.mjs"></script><script type="module" src="share-preview.mjs"></script></head><body><main class="review-shell"><header><p class="status">{status}</p><h1>OGP・メタ情報</h1><p>Miyabiya Studioを主役に、Masaya Nishigakiを添える形へ統一。</p></header><nav class="tabs" role="tablist" aria-label="付帯情報の確認"><button role="tab" id="tab-share-preview" aria-controls="share-preview" aria-selected="true">SNSでの表示</button><button role="tab" id="tab-adopted" aria-controls="adopted" aria-selected="false" tabindex="-1">採用C</button><button role="tab" id="tab-designs" aria-controls="designs" aria-selected="false" tabindex="-1">デザイン5案</button><button role="tab" id="tab-summary" aria-controls="summary" aria-selected="false" tabindex="-1">公開中の設定</button><button role="tab" id="tab-pages" aria-controls="pages" aria-selected="false" tabindex="-1">検索・シェア</button><button role="tab" id="tab-icons" aria-controls="icons" aria-selected="false" tabindex="-1">アイコン</button><button role="tab" id="tab-details" aria-controls="details" aria-selected="false" tabindex="-1">詳細</button></nav>
{share_preview}
<section id="adopted" role="tabpanel" aria-labelledby="tab-adopted" hidden><h2>C｜ドット絵のプロフィール</h2><p>アバター・ロゴ・文字を中央に収め、正方形でも見切れない配置へ調整。</p><div class="compare-grid"><article><h3>横長の表示</h3><img class="og-image" src="{adopted_image}" width="1200" height="630" alt="採用Cの横長OGP画像"></article><article><h3>正方形の表示</h3><img class="adopted-square" src="{adopted_image}" width="630" height="630" alt="採用Cの中央を正方形に切り抜いた表示"></article></div></section>
<section id="designs" role="tabpanel" aria-labelledby="tab-designs" hidden><h2>OGP画像のデザイン5案</h2><p>C「ドット絵のプロフィール」を採用。</p><p class="muted">Cは正方形でも見切れない配置へ調整済み。ほかの4案は比較時の候補です。</p><div class="design-grid">{design_cards}</div></section>
<section id="summary" role="tabpanel" aria-labelledby="tab-summary" hidden><h2>白基調と曲線のmで、サイトと印象をそろえる</h2><ul class="points"><li>トップのタイトルを「Miyabiya Studio | Masaya Nishigaki」へ</li><li>公開7ページに、内容に合わせた説明文とOGP画像を設定</li><li>favicon・スマホ保存用アイコンを、採用済みの曲線のmへ統一</li><li>検索エンジン向け情報を整理し、正規URLと公開範囲を確認</li></ul><div class="compare-grid"><article><h3>変更前</h3><img class="og-image" src="before-og.png" width="1200" height="630" alt="変更前の青系OGP画像"><p class="muted">{esc(old['title'])}</p><p>{esc(old_desc)}</p></article><article><h3>更新後</h3><img class="og-image" src="{image_ref('')}" width="1200" height="630" alt="更新後の白基調OGP画像"><p class="muted">{esc(metadata('')['title'])}</p><p>{esc(metadata('')['description'])}</p></article></div></section>
<section id="pages" role="tabpanel" aria-labelledby="tab-pages" hidden><h2>ページごとの検索・シェア表示</h2><p class="muted">検索結果やSNSの表示例です。実際の表示は各サービス側で調整されます。</p><div class="page-grid">{''.join(cards)}</div></section>
<section id="icons" role="tabpanel" aria-labelledby="tab-icons" hidden><h2>ブラウザ・スマホ保存用アイコン</h2><div class="compare-grid"><article><h3>変更前</h3><div class="icon-row"><figure><img src="before-favicon.webp" width="48" height="48" alt="変更前のプロフィール画像favicon"><figcaption>favicon</figcaption></figure><figure><img src="before-apple.png" width="96" height="96" alt="変更前の青いMのスマホ保存用アイコン"><figcaption>スマホ保存</figcaption></figure></div></article><article><h3>更新後</h3><div class="icon-row"><figure><img src="/favicon.svg" width="48" height="48" alt="採用済みの曲線のm"><figcaption>favicon</figcaption></figure><figure><img src="/icons/apple-touch-icon.png" width="96" height="96" alt="曲線のmのスマホ保存用アイコン"><figcaption>スマホ保存</figcaption></figure></div></article></div><h2>小さいサイズでの見え方</h2><div class="icon-row">{''.join(f'<figure><img src="/favicon.svg" width="{size}" height="{size}" alt="{size}pxのfavicon"><figcaption>{size}px</figcaption></figure>' for size in [16,32,48,96])}</div><p class="muted">SVG・PNG・ICO、180pxのAppleアイコン、192px・512pxの保存用アイコンを用意。</p></section>
<section id="details" role="tabpanel" aria-labelledby="tab-details" hidden><h2>設定する情報</h2><dl class="facts"><dt>名前・説明文</dt><dd>title・description・OGP・Xカードを同じデータから生成</dd><dt>共有画像</dt><dd>1200×630px。中央の正方形にアバター・マーク・文字を収め、画像更新時はURLも更新</dd><dt>サイト・人物情報</dt><dd>WebSite・Person・ページ情報を関連付け、noteを含む現在の公開プロフィールへ統一</dd><dt>検索対象</dt><dd>公開7ページの正規URL・sitemapを維持。レビューは公開対象外</dd><dt>保存用情報</dt><dd>端末への保存に使う名前とアイコンを、屋号・白背景・曲線のmで統一</dd></dl><h2>構造化データ</h2><pre><code>{esc(code)}</code></pre><h2>参照した仕様</h2><ul><li><a href="https://ogp.me/" target="_blank" rel="noopener">Open Graph protocol →</a></li><li><a href="https://developers.google.com/search/docs/appearance/site-names" target="_blank" rel="noopener">Googleのサイト名 →</a></li><li><a href="https://developers.google.com/search/docs/appearance/favicon-in-search" target="_blank" rel="noopener">Googleのfavicon →</a></li></ul></section></main></body></html>'''
    (OUT/'index.html').write_text(doc)
    print(OUT/'index.html')

if __name__=='__main__':build()
