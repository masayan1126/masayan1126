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
      'download':'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
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
    return '<div id="ratecard" class="short-route"><h3>'+icon()+' PR動画の料金・見積もり</h3><p>YouTube本編・ショート・X投稿を組み合わせて、制作範囲と概算料金をご確認いただけます。未確定の料金・条件は要相談です。</p><p>本編では、公開前の軽微修正は2回まで料金に含まれます。3回目以降は1回5,500円（税込）です。ショート・Xの修正条件、二次利用や撮り直しの料金は要相談です。</p><a class="v3-primary" href="https://studio.msyn.me/pricing/">料金をシミュレーションする <span aria-hidden="true">→</span></a></div>'

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
                row='<div class="work-row work-fixed"><span class="fixed-check">'+icon('check')+'</span><span class="work-label">'+label+'</span>'+price+help_text+'</div>'
            else:
                row=f'<label class="work-row"><input type="checkbox" name="items" value="{item["id"]}"><span class="work-label">{label}</span>{price}{help_text}</label>'
            rows.append(row)
        result.append(f'<fieldset class="estimate-group"><legend>{icon(group["icon"])} {group["title"]}</legend><div class="work-list">'+''.join(rows)+'</div></fieldset>')
    return ''.join(result)

def public_rates():
    return {key:DATA[key] for key in ('updated','taxRate','revisionFee','rateMode','baseDescription','checklistGroups','checklistItems','custom','mediaSchema','mediaRates','legacyUnversionedRateVersion','researchPolicy')}

def content(public_data=None):
    if public_data is None: public_data=public_rates()
    return f'''<link rel="stylesheet" href="/pricing.css"><link rel="stylesheet" href="/pricing-wizard.css">
<main id="main-content" class="estimate-page">
  <section class="estimate-intro"><div class="v3-wrap">
    <a class="v3-breadcrumb" href="/media/">← YouTube・PR・コラボ</a>
    <h1>PR動画制作の見積もり</h1>
    <p class="estimate-lead">YouTubeやXでの製品・サービスのPRをご検討中の方へ。ご希望の内容を選ぶと、概算金額と明細をご確認いただけます。</p>
    <p id="base-scope-hint" class="estimate-hint">{html.escape(public_data['baseDescription'])}</p>
    <div id="share-load-error" class="estimate-error" role="alert" hidden><p>共有された見積もりを読み込めませんでした。URLをご確認ください。</p><a href="/pricing/">新しく見積もる</a></div>
  </div></section>
  <section id="pricing-wizard" class="pricing-wizard v3-wrap" aria-label="PRのご依頼内容を選ぶ">
    <div class="simulator-launch">
      <div><h2>ご希望のPRから、見積もりを作れます</h2><p>本編・ショート動画・X投稿を選び、事前検証や企画・台本作成、ショートの制作方法を指定できます。最後に概算見積書と、ほかの組み合わせの見積もりをご確認いただけます。</p><button type="button" id="wizard-open" class="button primary" aria-haspopup="dialog">料金シミュレーターを開く <span aria-hidden="true">↗</span></button><p class="sheet-note">回答はあとから変更できます。共有URL・PDF保存にも対応しています。</p></div>
      <aside id="wizard-launch-summary" class="launch-summary" aria-label="見積もりの概要"></aside>
    </div>
    <dialog id="wizard-dialog" class="pricing-simulator" aria-labelledby="wizard-dialog-title">
      <header class="simulator-header"><div><p>PR制作・掲載のお見積もり</p><h2 id="wizard-dialog-title" tabindex="-1">料金シミュレーター</h2></div><button type="button" id="wizard-close" class="simulator-close">閉じる <span aria-hidden="true">×</span></button></header>
      <div id="wizard-scroll" class="simulator-scroll"><div id="wizard-workspace"><p>見積もりの選択項目を読み込んでいます。</p></div></div>
      <footer id="wizard-comparison-dock" class="comparison-dock" aria-label="別の組み合わせのご案内" hidden></footer>
      <div id="wizard-live" class="estimate-sr-only" role="status" aria-live="polite" aria-atomic="true"></div>
    </dialog>
    <p class="wizard-contact-note">どの内容が合うか迷われる場合は、<a href="/contact/?type=pr#contact-form">PRについて相談する</a>から、お気軽にお問い合わせください。</p>
    <noscript><p>見積もりの自動計算にはJavaScriptが必要です。ご希望の内容は、お問い合わせからもご相談いただけます。</p></noscript>
  </section>
  <div id="legacy-estimate" hidden>
  <section class="v3-wrap estimate-comparison" aria-labelledby="comparison-heading">
    <h2 id="comparison-heading">7つの組み合わせを比較する</h2>
    <p class="estimate-hint">本編10〜20分程度・ショート60秒程度を各1本、X投稿を1回とした比較です。本編は資料作成とサムネイル制作を含みます。金額が分かる構成から低い順に表示し、料金・条件が未確定の構成は要相談とします。</p>
    <div class="comparison-scroll"><table class="quote-table"><thead><tr><th scope="col">制作物</th><th scope="col">概算料金（税込）</th></tr></thead><tbody id="comparison-lines"></tbody></table></div>
  </section>
  <div class="v3-wrap estimate-layout">
    <form id="estimate-form" aria-label="PR動画制作の見積もり条件">
      <fieldset id="media-selection" class="estimate-group"><legend>1. 依頼する制作物を選ぶ</legend>
        <div class="media-options">
          <label class="media-option"><input type="checkbox" name="media" value="main"><span><b>YouTube本編1本</b><small>10〜20分程度・AIギルドchで公開</small></span></label>
          <label class="media-option"><input type="checkbox" name="media" value="short"><span><b>ショート1本</b><small id="short-selection-help">60秒程度・単独制作は要相談</small></span></label>
          <label class="media-option"><input type="checkbox" name="media" value="x"><span><b>X投稿1回</b><small id="x-selection-help">Xのみなら製品PR、動画と組み合わせると公開動画の告知シェア</small></span></label>
        </div>
      </fieldset>
      <p id="legacy-selection-note" class="estimate-hint" hidden>従来の本編見積もりです。共有時の作業選択と料金を表示しています。<a href="/pricing/">新しい媒体選択で見積もる</a></p>
      <p id="media-rate-note" class="estimate-hint"></p>
      <div class="sheet-hint">
        <p class="estimate-hint" id="preparation-hint"></p>
      </div>
      <div id="estimate-groups" hidden>{groups()}</div>
      <details class="estimate-additional" id="additional-options"><summary>追加修正・二次利用などを相談する</summary><div class="estimate-additional-content">
        <label class="estimate-revisions-label" for="revisions">公開前に希望する軽微修正の回数</label>
        <div class="estimate-revisions"><input id="revisions" name="revisions" type="number" min="0" step="1" value="2" inputmode="numeric" aria-describedby="revision-hint"><span>回</span></div>
        <p id="revision-hint" class="estimate-hint">本編は2回まで料金内です。ショート・Xの無料回数と追加料金は要相談です。</p>
        <fieldset class="estimate-custom-options"><legend>個別に相談する項目</legend>{''.join('<label class="estimate-check"><input type="checkbox" name="custom" value="'+item['id']+'"><span>'+html.escape(item['label'])+'</span><small>要相談</small></label>' for item in public_data['custom'])}</fieldset>
      </div></details>
      <section class="estimate-notes" id="selected-scope" aria-labelledby="selected-scope-heading"><h2 id="selected-scope-heading">選択した制作・公開の範囲</h2><ul id="scope-list"></ul><ul id="revision-list"></ul><h3>ご用意いただくもの</h3><ul id="preparation-list"></ul></section>
      <div id="other-media-terms" class="estimate-notes" hidden><h2>ご依頼前の確認事項</h2><p>制作範囲・修正回数・公開日・お支払い・キャンセル条件は、正式見積もりで確認します。製品の仕様・料金・使用素材の権利は、公開前に双方で確認します。PRであることが分かる表記を入れます。二次利用・掲載期間・ファイル納品・レポートは要相談です。</p></div>
      <div id="main-terms" hidden>
      <section class="estimate-notes" aria-labelledby="estimate-notes-heading">
        <h2 id="estimate-notes-heading">{icon('info')} 本編の注意事項</h2>
        <div class="estimate-notes-copy">
          <h3>修正回数</h3>
          <ul>
            <li>公開前の軽微修正は、2回まで追加料金なしで承ります。<span class="note-example">軽微修正の例</span><ul class="note-examples"><li>テロップの誤字修正</li><li>不要な部分のカット</li><li>事実関係の訂正</li></ul></li>
            <li>1回のご連絡でまとめていただいた修正内容への対応を、1回と数えます。</li>
            <li>3回目以降の軽微修正は、1回につき5,500円（税込）を頂戴いたします。</li>
            <li>構成・尺の変更を伴う修正は、要相談とさせていただきます。</li>
          </ul>
          <h3>お客様のご都合によるキャンセル</h3>
          <ul data-cancellation-terms>
            <li>事前検証の開始前のキャンセルは、費用をいただきません。</li>
            <li>正式なお見積もりと取引条件にご承諾いただいた後に、サービスの事前検証を開始します。</li>
            <li>サービスの事前検証を開始した時点を「着手」といたします。</li>
            <li>着手後〜撮影開始前のキャンセルは、正式に確定したお見積もり総額（税込）の30%を頂戴いたします。</li>
            <li>撮影開始時点〜編集完了前のキャンセルは、正式に確定したお見積もり総額（税込）の50%を頂戴いたします。</li>
            <li>編集完了後のキャンセルは、正式に確定したお見積もり総額（税込）の100%を頂戴いたします。</li>
          </ul>
          <h3>制作・公開の範囲</h3>
          <ul>
            <li>10分未満や20分を超え30分以内の動画は、内容と尺を確認して正式料金をご提示します。</li>
            <li>本編動画1本の制作と、Masaya Nishigakiが運営するYouTubeチャンネル「AIギルドch」での公開を承ります。</li>
            <li>当チャンネルへの掲載費は、お見積もり総額に含まれます。別途の掲載料は発生しません。</li>
            <li>本編動画は、YouTubeでの公開をもって納品完了といたします。MP4などの動画ファイルの納品は含まれておりません。ファイルの提供をご希望の場合は、正式見積もり時にご相談ください。</li>
            <li>当チャンネルで通常公開している動画と同水準の編集・テロップ追加に対応いたします。モーショングラフィックスやアニメーションなどの高度な編集は、対象に含まれておりません。</li>
          </ul>
          <h3>日程・お支払い</h3>
          <ul>
            <li>正式見積もりでは、金額を確定してご提示いたします。</li>
            <li>料金に幅がある項目は、検証する機能の数・範囲や、資料の分量・撮影時間により金額が変わります。</li>
            <li>正式なお見積もりと取引条件へのご承諾をもって、ご発注の確定といたします。メールでのご承諾も承ります。</li>
            <li>お客様に内容をご確認いただく期間を含め、ご発注の確定から公開までは2〜3週間を目安としております。</li>
            <li>ご確認・修正のご連絡をいただく期日は、制作前にお客様と決めます。</li>
            <li>アカウントのご提供やご確認が予定より遅れる場合は、公開日を調整いたします。</li>
            <li>原則、お支払いは動画公開月の月末締め・翌月末払いでお願いいたします。振込手数料はお客様にご負担いただきます。</li>
            <li>お支払いは銀行振込でお願いいたします。振込先は請求書に記載いたします。</li>
            <li>表示料金には消費税を含んでおります。適格請求書発行事業者には登録しておりません。</li>
            <li>適格請求書は発行できません。</li>
            <li>免税事業者等からの仕入れに係る経過措置では、要件を満たす場合に仕入税額相当額の一定割合を控除できます。</li>
            <li>控除割合は、課税仕入れの日を基準に決まります。</li>
            <li>2026年9月30日までの控除割合は80%です。</li>
            <li>2026年10月1日〜2028年9月30日の控除割合は70%です。</li>
            <li>2028年10月1日〜2030年9月30日の控除割合は50%です。</li>
            <li>2030年10月1日〜2031年9月30日の控除割合は30%です。</li>
            <li>2031年10月1日以降は、この経過措置による控除はできません。</li>
            <li>適用には、経過措置を適用する旨を記載した帳簿の保存が必要です。</li>
            <li>当方発行の請求書等も保存してください。区分記載請求書等と同じ記載事項が必要です。</li>
            <li>仕入税額控除の適用については、ご発注前に貴社の経理担当者へご確認ください。</li>
            <li>法令に基づき源泉徴収が必要な場合は、対象額・税額・振込額を事前に確認します。</li>
            <li>税務手続に必要な住所などの情報は、個別にご案内いたします。</li>
          </ul>
          <h3>事前検証・秘密保持</h3>
          <ul>
            <li data-term-research>事前検証の結果、当方の判断で制作を見送る場合は、検証費を含め費用を請求いたしません。</li>
            <li>有料プランなどの利用料が発生する場合は、制作前に費用負担を確認いたします。</li>
            <li>検証用アカウントは本件の制作にのみ使用し、ログイン情報を第三者に開示いたしません。</li>
            <li>未公開情報は本件の制作にのみ使用し、お客様の許可なく公開・第三者への開示はいたしません。</li>
            <li>公開または制作中止後は検証用アカウントを使用せず、保管したログイン情報を削除いたします。</li>
          </ul>
          <h3 data-report-heading>PR表記・評価・効果レポート</h3>
          <ul>
            <li>サービスの仕様・料金・利用条件は、ご提供いただいた情報をもとに確認します。公開前に、お客様にも内容のご確認をお願いいたします。</li>
            <li>動画もしくは概要欄の冒頭に「PR」「プロモーションを含む」などの表記を入れます。</li>
            <li>概要欄では、折りたたみ前に表示される範囲に記載します。</li>
            <li>YouTubeの「有料プロモーション」設定を有効にします。</li>
            <li data-term-report>公開30日後に、動画の再生数・視聴維持率をまとめたレポートをお渡しいたします。</li>
            <li>お客様に計測用リンクをご用意いただける場合は、動画の概要欄に掲載いたします。リンクのクリック数は、お客様側で計測をお願いいたします。</li>
            <li>動画公開によるサービス利用者数・有料プランの契約数・売上の増加は、保証しておりません。</li>
          </ul>
          <h3>著作権・二次利用・掲載期間</h3>
          <ul>
            <li>ご提供素材は、動画での使用・公開に必要な権利・許諾を確認済みのものをご用意ください。</li>
            <li>動画・資料の著作権は、個別のご契約で取り決めます。</li>
            <li>自社サイト・SNS・広告などでの二次利用は、顔・声の利用範囲も含めて要相談とさせていただきます。</li>
            <li>公開後の動画は原則継続掲載します。ただし、サービス終了・大幅な仕様変更、YouTubeの規約への対応、当チャンネルの運営終了・方針変更により非公開・削除する場合がございます。</li>
            <li>公開後にお客様のご都合で非公開・削除をご希望の場合は、対応内容と費用の扱いをご相談ください。</li>
            <li>掲載期間のご指定や、複数本の制作・継続契約は要相談とさせていただきます。</li>
          </ul>
          <h3>その他</h3>
          <ul>
            <li>記載のない事項は、お客様と協議のうえ決定いたします。</li>
          </ul>
        </div>
      </section>
      </div>
    </form>
    <aside id="estimate-result" class="estimate-result" aria-labelledby="result-heading" tabindex="-1">
      <div class="quote-heading"><h2 id="result-heading">{icon()} 概算見積書</h2><p id="rate-updated" class="quote-updated">料金表の更新日：{html.escape(public_data['updated'])}</p><p class="estimate-hint result-disclaimer">※こちらの金額はあくまで概算になります。正式な料金は動画内容や尺により変動します。</p></div>
      <p id="shared-rate-note" class="estimate-hint" hidden>共有時の料金表で表示しています。</p>
      <p id="result-error" class="estimate-error" role="alert" hidden></p>
      <p id="result-empty" class="estimate-hint">本編・ショート・X投稿から、依頼する制作物を選択してください。</p>
      <div id="result-filled">
        <p id="result-media" class="result-media"></p>
        <table class="quote-table"><thead><tr><th scope="col">項目</th><th scope="col">金額（税込）</th></tr></thead><tbody id="result-lines"></tbody></table>
        <div id="result-custom" class="result-custom" hidden><p>以下の項目は、相談後に料金が決まります。</p><ul id="result-custom-list"></ul></div>
        <div class="quote-total" id="result-amount">
          <p id="result-total-label">概算合計（税込）</p>
          <p class="result-amount"><strong id="result-range"></strong></p>
          <p class="result-tax" id="result-tax"></p>
          <p class="result-tax-rate" id="result-tax-rate"></p>
          <p class="estimate-hint" id="result-pending-note" hidden>要相談の項目の金額は、小計に含まれていません。</p>
        </div>
      </div>
      <a id="estimate-mail" class="estimate-button" href="mailto:contact@msyn.me"><span id="estimate-mail-label">とりあえず相談する</span> <span aria-hidden="true">↗</span></a>
      <button id="estimate-share" type="button" class="estimate-copy-button">見積もりURLをコピー</button>
      <button id="estimate-pdf" type="button" class="estimate-copy-button" aria-haspopup="dialog" hidden>{icon('download')} 概算見積書をダウンロード</button>
      <div id="share-fallback" hidden><label for="estimate-share-url">以下のURLをコピーして共有してください。</label><input id="estimate-share-url" type="url" readonly></div>
      <p id="share-status" role="status" class="estimate-hint"></p>
      <noscript><p>自動計算を使うには、JavaScriptを有効にしてください。各工程の料金はチェック欄でも確認できます。</p></noscript>
    </aside>
  </div>
  <dialog id="pdf-dialog" class="estimate-pdf-dialog" aria-labelledby="pdf-dialog-title">
    <form id="pdf-form">
      <div class="pdf-dialog-heading"><h2 id="pdf-dialog-title">概算見積書をダウンロード</h2><button id="pdf-close" type="button" aria-label="閉じる">×</button></div>
      <p class="pdf-dialog-lead">ご検討や社内共有に使える概算見積書をダウンロードできます。</p>
      <label class="pdf-recipient-label" for="pdf-recipient">宛先（お客様の会社名・お名前） <span>任意</span></label>
      <div class="pdf-recipient-fields"><input id="pdf-recipient" name="recipient" type="text" value="〇〇会社" maxlength="80" autocomplete="organization" placeholder="会社名・お名前" aria-describedby="pdf-recipient-hint"><select id="pdf-honorific" name="honorific" aria-label="宛名の敬称"><option>御中</option><option>様</option></select></div>
      <p id="pdf-recipient-hint" class="estimate-hint">宛先は変更できます。空欄の場合は「〇〇会社」と記載します。</p>
      <p id="pdf-error" class="estimate-error" role="alert" hidden></p>
      <button id="pdf-download" class="estimate-button" type="submit">PDFをダウンロード</button>
      <p id="pdf-status" class="estimate-hint" role="status"></p>
    </form>
  </dialog>
  <a id="estimate-mobile-total" class="estimate-mobile-total" href="#estimate-result" aria-controls="estimate-result" hidden><span id="mobile-amount"></span><span>明細を見る ↓</span></a>
  <div id="estimate-live" role="status" aria-live="polite" aria-atomic="true" class="estimate-sr-only"></div>
  </div>
</main><script id="pricing-data" type="application/json">{json.dumps(public_data,ensure_ascii=False)}</script><script type="module" src="/pricing-ui.mjs"></script>'''
