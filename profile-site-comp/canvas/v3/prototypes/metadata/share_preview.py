# coding: utf-8
"""Render a private share-card preview from a captured public response."""
from html import escape as esc
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent


def panel():
    snapshot = json.loads((HERE / 'public-preview.json').read_text())
    options = ''.join(f'<option value="{esc(row["key"])}">{esc(row["label"])}</option>' for row in snapshot['pages'])
    payload = json.dumps(snapshot, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<section id="share-preview" role="tabpanel" aria-labelledby="tab-share-preview">
<h2>SNSでの表示プレビュー</h2>
<p>公開中の画像・タイトル・説明文を使った表示例です。実際のカードは、アプリの仕様やキャッシュによって異なります。</p>
<form class="share-controls" onsubmit="return false"><label for="share-page">確認するページ<select id="share-page">{options}</select></label>
<fieldset><legend>カードの表示幅</legend><label><input type="radio" name="share-width" value="pc" checked>PC</label><label><input type="radio" name="share-width" value="mobile">スマホ</label></fieldset>
<button type="button" id="share-copy">公開URLをコピー</button></form>
<p class="muted" id="share-captured"></p><p class="share-feedback" id="share-feedback" role="status" aria-live="polite"></p>
<label id="share-copy-fallback" hidden>公開URL<input id="share-copy-value" readonly></label>
<div id="share-source-line"><a id="share-live-page" target="_blank" rel="noopener">公開ページを開く →</a><a id="share-live-image" target="_blank" rel="noopener">OGPの元画像を開く →</a></div>
<p id="share-error" role="alert" hidden></p>
<div class="share-grid" id="share-cards" data-width="pc">
<article class="share-study"><h3>X風・横長カード</h3><p class="muted">横長 2:1 ／ タイトルを2行まで表示</p><div class="share-stage"><a class="share-card x-preview" data-page-link target="_blank" rel="noopener"><img data-share-img="twitter" class="x-picture" alt=""><div class="share-card-copy"><p data-share-domain class="muted"></p><h4 data-share-text="twitter:title" class="clamp-two"></h4></div></a><p class="share-image-error" hidden>画像を読み込めませんでした。</p></div></article>
<article class="share-study"><h3>LINE風・正方形カード</h3><p class="muted">中央を正方形に切り抜いて表示</p><div class="share-stage"><a class="share-card line-preview" data-page-link target="_blank" rel="noopener"><img data-share-img="og" class="line-picture" alt=""><div class="share-card-copy"><h4 data-share-text="og:title" class="clamp-two"></h4><p data-share-text="og:description" class="clamp-two muted"></p><p data-share-domain class="muted"></p></div></a><p class="share-image-error" hidden>画像を読み込めませんでした。</p></div></article>
<article class="share-study"><h3>チャット風・小さなカード</h3><p class="muted">80pxのサムネイルと文字を横並び</p><div class="share-stage"><a class="share-card compact-preview" data-page-link target="_blank" rel="noopener"><img data-share-img="og" class="compact-picture" alt=""><div class="share-card-copy"><h4 data-share-text="og:title" class="clamp-two"></h4><p data-share-text="og:description" class="clamp-two muted"></p><p data-share-domain class="muted"></p></div></a><p class="share-image-error" hidden>画像を読み込めませんでした。</p></div></article>
<article class="share-study"><h3>元画像の全体</h3><p class="muted">切り抜きなし ／ 幅300pxの表示</p><div class="share-stage"><img data-share-img="og" class="share-original" alt=""><p class="share-image-error" hidden>画像を読み込めませんでした。</p><p id="share-image-spec" class="muted"></p></div></article>
</div>
<details class="share-inspection"><summary>取得した掲載情報を見る</summary><p id="share-http" class="muted"></p><dl id="share-values" class="share-values"></dl></details>
<details class="share-inspection"><summary>表示例の参照元</summary><p>枠の寸法と文字の省略は、この確認画面での表示例です。</p><ul><li><a href="https://developers.line.biz/en/faq/tags/line-app/" target="_blank" rel="noopener">LINE：URLプレビューに使うOGP →</a></li><li><a href="https://docs.slack.dev/messaging/unfurling-links-in-messages/" target="_blank" rel="noopener">Slack：リンクのプレビュー →</a></li></ul></details>
<script type="application/json" id="share-preview-data">{payload}</script></section>'''
