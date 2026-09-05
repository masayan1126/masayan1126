"""Public-only pricing content; confidential source notes are never exported."""
import html
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE/'pricing-data.json').read_text())
def money(value): return f'{value:,}円'
def icon(kind='calculator'):
    paths = {'calculator':'<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 11h1m6 0h1M8 15h1m6 0h1M8 19h1m6 0h1"/>',
      'file':'<path d="M14 2H5v20h14V7zM14 2v5h5M8 12h8M8 16h8"/>',
      'video':'<rect x="2" y="5" width="14" height="14" rx="2"/><path d="m16 10 6-3v10l-6-3"/>',
      'share':'<circle cx="5" cy="12" r="3"/><circle cx="19" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><path d="m8 10 8-4M8 14l8 4"/>',
      'info':'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
      'check':'<path d="m5 12 4 4L19 6"/>',
      'settings':'<path d="M3 6h6m4 0h8M3 18h10m4 0h4"/><circle cx="11" cy="6" r="2"/><circle cx="15" cy="18" r="2"/>'}
    return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[kind]+'</svg>'

def amount(item):
    if item['min'] is None: return '要相談'
    low = item['min'] if item.get('taxInclusive') else item['min'] + round(item['min'] * DATA['taxRate'])
    high = item['max'] if item.get('taxInclusive') else item['max'] + round(item['max'] * DATA['taxRate'])
    if low == high: return money(low)
    return f'{low:,}〜{high:,}円'

def media_summary():
    return '<div id="ratecard" class="short-route"><h3>'+icon()+' PR動画の料金・見積もり</h3><p>資料作成・サムネイル制作・ショート動画など、追加で依頼したい作業を選んで概算料金をご確認いただけます。本編1本の制作と、YouTubeでの掲載が対象です。</p><p>公開前の修正は2回まで料金に含まれます。3回目以降は1回5,500円（税込）です。二次利用や撮り直しの料金は、個別にご相談いただけます。</p><a class="v3-primary" href="https://studio.msyn.me/pricing/">料金をシミュレーションする <span aria-hidden="true">→</span></a></div>'

def groups():
    result=[]
    for group in DATA['checklistGroups']:
        rows=[]
        for item in (i for i in DATA['checklistItems'] if i['id'] in group['items']):
            label=html.escape(item['label'])
            if item.get('description'): label += '<small>'+html.escape(item['description'])+'</small>'
            price='<span class="check-price">'+amount(item)+'</span>'
            help_text = '<small class="work-help">'+html.escape(item['helpText'])+'</small>' if item.get('helpText') else ''
            if item.get('fixed'):
                row='<div class="work-row work-fixed"><span class="fixed-check">'+icon('check')+'</span><span class="work-label">'+label+'<small>基本料金に含まれます</small></span>'+price+help_text+'</div>'
            else:
                row=f'<label class="work-row"><input type="checkbox" name="items" value="{item["id"]}"><span class="work-label">{label}</span>{price}{help_text}</label>'
            rows.append(row)
        result.append(f'<fieldset class="estimate-group"><legend>{icon(group["icon"])} {group["title"]}</legend><div class="work-list">'+''.join(rows)+'</div></fieldset>')
    return ''.join(result)

def public_rates():
    return {key:DATA[key] for key in ('updated','taxRate','revisionFee','rateMode','baseDescription','checklistGroups','checklistItems','custom')}

def content(public_data=None):
    if public_data is None: public_data=public_rates()
    return f'''<link rel="stylesheet" href="/pricing.css">
<main id="main-content" class="estimate-page">
  <section class="estimate-intro"><div class="v3-wrap">
    <a class="v3-breadcrumb" href="/media/">← YouTube・PR・コラボ</a>
    <h1>PR動画制作の見積もり</h1>
    <div id="share-load-error" class="estimate-error" role="alert" hidden><p>共有された見積もりを読み込めませんでした。URLをご確認ください。</p><a href="/pricing/">新しく見積もる</a></div>
  </div></section>
  <div class="v3-wrap estimate-layout">
    <form id="estimate-form" aria-label="PR動画制作の見積もり条件">
      <div class="sheet-hint">
        <p id="base-scope-hint" class="estimate-hint">{html.escape(public_data['baseDescription'])}</p>
        <p class="estimate-hint">PRするサービスの検証用アカウントをご用意いただくようお願いいたします。</p>
        <p class="estimate-hint">10〜20分程度の動画を想定しております。30分を超える長尺動画は、個別にご相談いただけます。</p>
      </div>
      <div id="estimate-groups">{groups()}</div>
      <section class="estimate-notes" aria-labelledby="estimate-notes-heading">
        <h2 id="estimate-notes-heading">{icon('info')} 注意事項</h2>
        <div class="estimate-notes-copy">
          <h3>修正回数</h3>
          <ul>
            <li>公開前の修正は、2回まで追加料金なしで承ります。</li>
            <li>3回目以降の修正は、1回につき5,500円（税込）を頂戴いたします。</li>
          </ul>
          <h3>キャンセル料</h3>
          <ul>
            <li>着手後〜撮影前のキャンセルは、正式に確定したお見積もり総額（税込）の30%を頂戴いたします。</li>
            <li>撮影後のキャンセルは、正式に確定したお見積もり総額（税込）の50%を頂戴いたします。</li>
            <li>編集完了後のキャンセルは、正式に確定したお見積もり総額（税込）の100%を頂戴いたします。</li>
          </ul>
          <h3>制作・公開の範囲</h3>
          <ul>
            <li>本編動画1本の制作と、Masaya NishigakiのYouTubeチャンネルでの公開を承ります。</li>
            <li>通常公開している動画と同水準の編集・テロップ追加に対応いたします。モーショングラフィックスやアニメーションなどの高度な編集は、対象に含まれておりません。</li>
            <li>本編は10〜20分程度を想定しております。30分を超える動画や撮り直しの料金は、個別にご相談いただけます。</li>
          </ul>
          <h3>日程・お支払い</h3>
          <ul>
            <li>ご発注の確定から公開までは、1〜2週間を目安としております。</li>
            <li>お客様に内容をご確認いただく期間は、上記の日数に含まれておりません。</li>
            <li>お支払いは、動画公開月の月末締め・翌月末払いでお願いいたします。</li>
            <li>表示料金には消費税を含んでおります。適格請求書発行事業者には登録しておりません。</li>
          </ul>
          <h3>PR表記・評価・効果レポート</h3>
          <ul>
            <li>動画と概要欄には「PR」「プロモーションを含む」などの表記を入れます。</li>
            <li>動画の構成・表現は、Masaya Nishigakiが判断いたします。サービスに対する率直な評価や指摘も含みます。</li>
            <li>事実と異なる内容がございましたら、修正をご依頼いただけます。</li>
            <li>公開30日後に、効果レポートをお渡しいたします。再生数・視聴維持率と、概要欄の計測用リンク（UTM）から集計したクリック数をご確認いただけます。</li>
            <li>再生回数や登録者増加数などの成果は、保証しておりません。</li>
          </ul>
          <h3>著作権・二次利用・掲載期間</h3>
          <ul>
            <li>動画・資料の著作権は、個別のご契約で取り決めます。</li>
            <li>自社サイト・SNS・広告などでの二次利用をご希望の場合は、利用範囲を個別にご相談いただけます。</li>
            <li>公開後の動画は、原則として継続して掲載いたします。</li>
            <li>掲載期間のご指定や、複数本の制作・継続契約も個別にご相談いただけます。</li>
          </ul>
          <p>料金表の更新日：{DATA['updated']}　／　税込表示は消費税10%で計算しています。</p>
        </div>
      </section>
    </form>
    <aside id="estimate-result" class="estimate-result" aria-labelledby="result-heading" tabindex="-1">
      <div class="quote-heading"><h2 id="result-heading">{icon()} 概算見積書</h2><p class="estimate-hint result-disclaimer">※こちらの金額はあくまで概算になります。正式な料金は動画内容や尺により変動します。</p></div>
      <p id="shared-rate-note" class="estimate-hint" hidden>共有時の料金表で表示しています。</p>
      <p id="result-error" class="estimate-error" role="alert" hidden></p>
      <div id="result-filled">
        <table class="quote-table"><thead><tr><th scope="col">項目</th><th scope="col">金額（税込）</th></tr></thead><tbody id="result-lines"></tbody></table>
        <div id="result-custom" class="result-custom" hidden><p>以下の項目は、相談後に料金が決まります。</p><ul id="result-custom-list"></ul></div>
        <div class="quote-total" id="result-amount">
          <p id="result-total-label">概算合計（税込）</p>
          <p class="result-amount"><strong id="result-range"></strong></p>
          <p class="result-tax" id="result-tax"></p>
          <p class="estimate-hint" id="result-pending-note" hidden>要相談の項目の金額は、小計に含まれていません。</p>
        </div>
      </div>
      <a id="estimate-mail" class="estimate-button" href="mailto:contact@msyn.me"><span id="estimate-mail-label">とりあえず相談する</span> <span aria-hidden="true">↗</span></a>
      <button id="estimate-share" type="button" class="estimate-copy-button">見積もりURLをコピー</button>
      <div id="share-fallback" hidden><label for="estimate-share-url">以下のURLをコピーして共有してください。</label><input id="estimate-share-url" type="url" readonly></div>
      <p id="share-status" role="status" class="estimate-hint"></p>
      <noscript><p>自動計算を使うには、JavaScriptを有効にしてください。各工程の料金はチェック欄でも確認できます。</p></noscript>
    </aside>
  </div>
  <a id="estimate-mobile-total" class="estimate-mobile-total" href="#estimate-result" aria-controls="estimate-result" hidden><span id="mobile-amount"></span><span>明細を見る ↓</span></a>
  <div id="estimate-live" role="status" aria-live="polite" aria-atomic="true" class="estimate-sr-only"></div>
</main><script id="pricing-data" type="application/json">{json.dumps(public_data,ensure_ascii=False)}</script><script type="module" src="/pricing-ui.mjs"></script>'''
