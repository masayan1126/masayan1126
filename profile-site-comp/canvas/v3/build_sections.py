"""Render excerpts and full case studies from the same editable content."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent


CHROME_EXTENSIONS = [
    ('Article Date Detector', 'Webページの公開日・更新日を表示し、記事の新しさをすぐに判断できる', 74, 'https://chromewebstore.google.com/detail/article-date-detector/kcibimkobhbikanlidohhnahodekmaej'),
    ('Markdown Preview', 'Markdownをリアルタイムにプレビュー。目次・テーマ・フォントを設定できる', 59, 'https://chrome-extensions-6cv.pages.dev/rich-markdown-preview/'),
    ('Web Annotator', 'Webページにマーカーや付箋を付け、Markdownで書き出す', 28, 'https://chromewebstore.google.com/detail/web-annotator/gckpllfnimaepbbelfmhcelibclnkena'),
    ('Copy Tab Anything', '開いているタブのタイトルとURLを、Markdownなど好きな形式でまとめてコピー', 19, 'https://chromewebstore.google.com/detail/copy-tab-anything/gafkainbomdnemmdemopmechbmabgfeh'),
    ('Canvas Whiteboard', 'ブラウザで使えるホワイトボード。アイデア整理や図解に', 17, 'https://chromewebstore.google.com/detail/canvas-whiteboard/fpekokphickomacboclmogcmjeffhmle'),
]


# Time per video (10-15 min 4K main video + about 15 Shorts, excluding filming), approved 2026-09-25.
# (step, manual, after automation: the owner's remaining time, how it was reduced)
VIDEO_TIME_BREAKDOWN = [
    ('企画・骨子（章立て）', '1.5〜3時間', '30〜40分', 'AIが企画の意図から章立て案まで作成。並べ替えと修正だけを行う'),
    ('スライド20〜30枚と読み上げ台本', '6〜12時間', '0分', '骨子からAIがスライドと台本を作成'),
    ('レビュー', '1〜1.5時間', '30〜60分', 'トーン・伝わりやすさ・デザイン・企画との整合をAIが先に確認。最後の承認だけを行う'),
    ('撮影後の仕上げ（文字起こし・チャプター・概要欄・再生リストなど）', '4〜6.5時間', '5分', '取り込みからメタデータの検証までを自動化。挿入位置と公開日を決めるだけ'),
    ('タイトルとサムネイル', '1.5〜2.25時間', '20分', 'AIが競合とキーワードを調べて案を作成。採用する案と画像を選ぶだけ'),
    ('公開と告知（予約・カレンダー登録・コミュニティ告知・Studioの設定）', '1.5〜2時間', '15分', '予約から設定・記録までを自動化。最終承認と結果の確認だけ'),
    ('Shorts 15本（区間選定・縦長への変換・テロップ・予約）', '8〜11時間', '20〜30分', '区間選定から予約までを自動化。タイトルの採用だけを行う'),
]
VIDEO_TIME_TOTAL = ('約25〜37時間', '約2〜3時間')


def extension_icon(name):
    # Store icons (128px JPEG, a few KB each) are inlined so no extra asset files are needed.
    import base64
    path = HERE / 'works-images/extensions' / (name.lower().replace(' ', '-') + '.jpg')
    return '<img class="ext-icon" src="data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode() + '" width="40" height="40" alt="">'


def render_works(files, *, excerpt=False, single=None):
    source = (HERE / 'works-story.html').read_text().strip()
    for key in ('works', 'media'):
        source = source.replace('{{' + key + '}}', files[key])
    for image in (HERE / 'works-images').glob('*.webp'):
        url = '/site-assets/' + image.stem + '.' + hashlib.sha256(image.read_bytes()).hexdigest()[:12] + '.webp'
        source = source.replace('{{image:' + image.stem + '}}', url)
    cases = re.findall(r'<article\b.*?</article>', source, re.S)
    detail_headings = [
        ('課題', '担当したこと', '成果', '使った技術'),
        ('背景', '担当したこと', '成果', '使った技術'),
        ('チャンネルの運営', '動画制作の自動化・仕組み化'),
        ('登壇で紹介したこと', 'お話しできること'),
        ('作ったもの',),
    ]
    for index, case in enumerate(cases):
        description = re.search(r'<div class="case-description">(.*?)</div>', case, re.S)
        paragraphs = re.findall(r'<p>(.*?)</p>', description[1], re.S)
        if excerpt:
            # A literal excerpt keeps the homepage grounded in the full explanation.
            # Four-part case studies (approved 2026-09-24) excerpt the "担当したこと" paragraph.
            lead = paragraphs[1] if len(paragraphs) == 4 else paragraphs[0]
            brief = '。'.join(lead.split('。')[:2 if index == 0 else 1]) + '。'
            revised = case.replace(description[0], '<div class="case-description"><p>' + brief + '</p></div>')
            revised = re.sub(r'href="[^"]+"(?=><span>)', f'href="{files["works"]}#work-case-{index}"', revised)
            revised = re.sub(r'(<a class="detail-link"[^>]*><span>).*?(</span>)', r'\1取り組みと成果を詳しく見る\2', revised)
        else:
            body = ''.join('<div class="case-topic"><h4>' + title + '</h4>'
                           + ('<ul class="tech">' + ''.join('<li>' + item + '</li>' for item in paragraph.split('／')) + '</ul>'
                              if title == '使った技術' else '<p>' + paragraph + '</p>') + '</div>'
                           for title, paragraph in zip(detail_headings[index], paragraphs))
            revised = case.replace(description[0], '<div class="case-description">' + body + '</div>')
            if index == 4:
                # Personal projects list each extension with its users (approved 2026-09-24).
                items = ''.join('<li>' + extension_icon(name) + '<a href="' + url + '">' + name + '</a><span class="users">' + str(users) + '人</span><p>' + desc + '</p></li>'
                                for name, desc, users, url in CHROME_EXTENSIONS)
                revised = revised.replace('</div></div><a class="detail-link"', '</div><div class="case-topic"><h4>公開中の拡張機能</h4><ul class="ext-list">' + items + '</ul></div></div><a class="detail-link"', 1)
            if index == 2:
                # Where the production time went and how it was reduced, nested under the
                # automation topic so the channel overview and the breakdown are not peers (approved 2026-09-25).
                rows = ''.join('<li><p class="tb-step">' + step + '</p><p class="tb-time">手作業 ' + manual + ' → <b>' + after + '</b></p><p class="tb-how">' + how + '</p></li>'
                               for step, manual, after, how in VIDEO_TIME_BREAKDOWN)
                manual, after = VIDEO_TIME_TOTAL
                detail = ('<p class="tb-headline">動画1本あたりの作業時間 <b>' + manual + ' → ' + after + '</b><small>（約90%削減・撮影を除く）</small></p>'
                          '<p>大きく減ったのはShortsとスライド・台本で、削減分の7割ほどを占めます。週1本のペースなら、毎週3〜4日分の作業時間が空きます。残る2〜3時間は、骨子・タイトル・サムネイル・Shortsのタイトルを選ぶ時間と、スライドを承認する時間です。この判断はあえて人が行っています。</p>'
                          '<div class="tb-detail"><h5>工程ごとの内訳</h5><p class="tb-note">本編（10〜15分）1本とShorts 15本を作る場合</p>'
                          '<ol class="time-breakdown">' + rows + '</ol>'
                          '<p class="tb-total">合計 手作業 ' + manual + ' → <b>' + after + '</b>（1本あたり約23〜34時間の削減）</p></div>')
                revised = revised.replace('</p></div></div><a class="detail-link"', '</p>' + detail + '</div></div><a class="detail-link"', 1)
            destinations = [('services', '開発・AI導入支援について'), ('services', '開発・AI導入支援について'),
                            ('media', '代表動画・PR・コラボについて'), ('talks', '登壇記録・ご依頼について'), (None, 'ソースコードを見る（GitHub）')]
            dest, label = destinations[index]
            if dest:
                revised = re.sub(r'<a class="detail-link".*?</a>', '<a class="detail-link" href="' + files[dest] + '"><span>' + label + '</span><span aria-hidden="true">↗</span></a>', revised, flags=re.S)
            if index < 4 and single is None:
                from site_journeys import action
                request_label, request_url = [('開発・AI導入を相談する', '/contact/?type=web#contact-form'),
                                               ('MCPの開発を相談する', '/contact/?type=web#contact-form'),
                                               ('PR動画の料金を見積もる', '/pricing/'),
                                               ('登壇を相談する', '/contact/?type=talk#contact-form')][index]
                revised = revised.replace('</article>', '<div class="case-request">' + action(request_label, request_url) + '</div></article>')
        source = source.replace(case, revised)
        cases[index] = revised
    if single is not None:
        case = re.sub(r'<a class="detail-link".*?</a>', '', cases[single], flags=re.S)
        case = case.replace('<h3 class="story-title"', '<h2 class="story-title"').replace('</h3>', '</h2>')
        case = case.replace('<h4>', '<h3>').replace('</h4>', '</h3>').replace('<h5>', '<h4>').replace('</h5>', '</h4>')
        return '<section class="works-story detail-feature" id="' + ('channel-story' if single == 2 else 'talk-story') + '"><div class="works-wrap">' + case + '</div></section>'
    source = source.replace('class="works-story"', 'class="works-story" data-depth="' + ('excerpt' if excerpt else 'detail') + '"', 1)
    if not excerpt:
        source = source.replace('<h2>実績・成果</h2>', '<h2>取り組みと成果</h2>')
        source = source.replace('<p>実務・個人でのAI活用、YouTube運営、技術登壇、個人開発の実績をご紹介します。</p>', '')
        source = source.replace('<a href="' + files['works'] + '">すべての実績・成果を見る ↗</a>', '')
    return source.replace('<article', '<div').replace('</article>', '</div>')


CAREER_POINTS = [
    ['インフラ担当からバックエンドリードを経て、テックリードに',
     'バックエンドの開発体制を立て直し（クリーンアーキテクチャ・自動テスト・CI/CDを整備）',
     '決済機能、SSO（SAML）、監査ログなどを設計・実装',
     'MCPサーバーを企画から保守まで担当し、商談にも技術担当として同席',
     'バックエンドリードとしてチームを担当',
     '一次面接に50回以上参加し、エンジニア4名の採用に関与'],
    ['フロントエンドのチームリーダー',
     '技術選定・設計から保守まで一貫して担当',
     'E2Eテスト（Cypress）をCIに組み込み、画面のテストを自動化',
     'React・Next.jsやVue3を導入し、メンバーへの技術教育も担当'],
]

# Technologies and approximate years of experience, from the resume (approved 2026-09-24).
TECH_STACK = [
    ('言語', [('Python', '5年'), ('TypeScript', '5年'), ('PHP', '2年')]),
    ('バックエンド', [('Django / Django REST Framework', '3年'), ('FastAPI', '2年'), ('Laravel', '2年'), ('FastMCP', '1年')]),
    ('フロントエンド', [('Vue.js', '5年'), ('React / Next.js', '2年')]),
    ('データベース・分析', [('PostgreSQL', '3年'), ('BigQuery', '3年'), ('MySQL', '2年')]),
    ('クラウド・インフラ', [('Google Cloud', '3年'), ('AWS', '2年'), ('Docker', '5年'), ('GitHub Actions', '5年')]),
    ('AI', [('Claude Code / Codex CLI / Cursor / Gemini', '1.5年')]),
    ('その他', [('Stripe（決済）', '3年')]),
]


def render_tech_stack():
    cards = ''.join('<section><h3>' + category + '</h3><ul>' + ''.join('<li>' + name + '<small>' + years + '</small></li>' for name, years in items) + '</ul></section>'
                    for category, items in TECH_STACK)
    return ('<section class="tech-stack" id="tech-stack"><div class="wrap"><h2>技術スタック</h2>'
            '<p class="lead">実務で使ってきた技術と、おおよその経験年数です。</p><div class="stack-grid">' + cards + '</div></div></section>')


def render_career(files, *, excerpt=False):
    source = (HERE / 'career-chapters.html').read_text().strip().replace('{{profile}}', files['profile'])
    if not excerpt:
        source = re.sub(r'<div class="section-foot">.*?</div>', '', source, flags=re.S)
        # Career highlights from the resume, shown on the profile page only (approved 2026-09-24).
        for body, points in zip(re.findall(r'<p class="body-copy">.*?</p>', source), CAREER_POINTS):
            source = source.replace(body, body + '<ul class="career-points">' + ''.join('<li>' + p + '</li>' for p in points) + '</ul>', 1)
    source = source.replace('<article', '<div').replace('</article>', '</div>')
    return source.replace('class="career-chapters"', 'class="career-chapters" data-depth="' + ('excerpt' if excerpt else 'detail') + '"', 1)


def render_mediakit():
    """PRを検討する企業向けの視聴者データ (mediakit.json、approved 2026-09-24)。"""
    import json
    data = json.loads((HERE / 'mediakit.json').read_text())
    import youtube_stats
    tiles = [(youtube_stats.SNAPSHOT['subs'] + '<small>人</small>', 'チャンネル登録者'),
             (f"{youtube_stats.MEMBERS}<small>人</small>", 'メンバーシップのメンバー'),
             (f"{data['channel_views'] // 1000 / 10:.1f}<small>万回</small>", 'チャンネルの累計再生数'),
             (f"{data['views90'] // 1000 / 10:.1f}<small>万回</small>", '直近90日の再生数'),
             (f"{data['long_mean']:,}<small>回</small>", '本編1本あたりの平均再生数'),
             (f"{data['long_count']}<small>本</small>", '直近90日に公開した本編')]
    ages = [('18〜24歳', data['age']['18-24']), ('25〜34歳', data['age']['25-34']), ('35〜44歳', data['age']['35-44']),
            ('45〜54歳', data['age']['45-54']), ('55歳以上', data['age']['55+'])]
    bars = ''.join(f'<div class="mk-bar"><span>{label}</span><i style="width:{value / 40 * 100:.0f}%"></i><em>{value:.0f}%</em></div>' for label, value in ages)
    return ('<div class="mediakit" id="mediakit"><h3>視聴者データ</h3>'
            f'<p class="note">登録者は{youtube_stats.SNAPSHOT["date"]}、メンバーは{youtube_stats.MEMBERS_AS_OF}。再生数・本数・年齢層は{data["as_of"]}時点の直近90日（YouTube アナリティクス）。</p>'
            '<div class="mk-tiles">' + ''.join(f'<div><b>{n}</b><span>{l}</span></div>' for n, l in tiles) + '</div>'
            f'<div class="mk-aud"><div><h4>年齢層</h4>{bars}</div><div><h4>主なテーマ</h4>'
            '<p class="mk-theme">Claude Code を中心としたAI駆動開発。視聴者の中心は、AIを開発に取り入れたいエンジニアです。</p></div></div></div>')


# PR video work shown to PR clients on the media page (added 2026-09-30).
# Only public facts: the fee and contract terms are confidential and never shown.
# (video id, sponsor, title, published, length, summary, scope)
PR_WORKS = [
    ('FsA8gaup0w4', 'Notta', 'Notta Memo Pro 9/28 予約販売開始!!｜録音して終わりにしないAIボイスレコーダー 文字起こしとAI要約が次の仕事へ',
     '2026年9月28日', '8分24秒',
     'AIボイスレコーダーの予約販売開始に合わせたタイアップ動画です。実機で録音からAI要約までの流れを見せ、議事録を作ってGoogleカレンダーへ登録するところまで実演しました。概要欄には購入リンクとクーポンを掲載しています。',
     ['機能の事前検証', '構成・スライド', '撮影・編集', 'サムネイル', 'Xでの告知']),
]


def render_pr_works():
    items = ''.join(
        f'<a class="pr-work" href="https://youtu.be/{vid}"><img src="thumb-{vid}.webp" width="640" height="360" alt="" loading="lazy">'
        f'<div><p class="pr-sponsor">{sponsor} 様のタイアップ</p><h3>{title}</h3><p class="pr-meta">{date}公開 ／ {length}</p>'
        f'<p class="pr-summary">{summary}</p><div class="pr-scope">' + ''.join(f'<span>{s}</span>' for s in scope) + '</div></div></a>'
        for vid, sponsor, title, date, length, summary, scope in PR_WORKS)
    return ('<div class="sec alt" id="pr-works"><div class="wrap"><h2 class="sec-h">PR動画の制作実績</h2>'
            '<p class="sec-lead">企業様からご依頼いただき、制作・公開した動画です。</p>' + items + '</div></div>')


# YouTube・PR・コラボ page, reorganised 2026-09-30 for companies considering a PR video:
# channel (who watches, sample videos) → PR work → what can be ordered and the price → how videos are made.
PR_OFFERS = [
    ('タイアップ動画', '製品を実際に使ったうえで、YouTubeの本編動画で紹介します。機能の事前検証から構成・撮影・編集・サムネイルまで一人で担当します。'),
    ('ショート動画', '60秒程度の縦型動画で、製品の使いどころを紹介します。本編とあわせた切り抜き型、ショート向けに別撮影する制作にも対応します。'),
    ('Xでの紹介', 'X（@masayan_ai_hack）で、製品の機能や使いどころを紹介する投稿を作成します。'),
    ('対談・コラボ企画', '個人の方との対談や共同企画もお受けしています。内容に応じてお見積もりします。'),
]


def render_media(videos, ratecard, channel_story, membership_route):
    grid = re.search(r'<div class="videos">.*?</a>\s*</div>', videos, re.S).group()
    channel = ('<div class="sec" id="videos"><div class="wrap"><h2 class="sec-h">チャンネルについて</h2>'
               '<p class="sec-lead">Claude Code を中心に、AI駆動開発を扱うチャンネルです。視聴者の数と年齢層、話し方が分かる代表的な動画をご覧いただけます。</p>'
               + render_mediakit() + '<h3 class="media-sub">代表的な動画</h3>' + grid + '</div></div>')
    offers = ('<div class="sec" id="pr"><div class="wrap"><h2 class="sec-h">ご依頼いただける内容と料金</h2>'
              '<p class="sec-lead">AIツールや開発者向けサービスを、エンジニアに届けたい企業様・個人の方からのご依頼をお受けしています。</p>'
              '<div class="grid2 pr-offers">' + ''.join(f'<div class="pr-offer"><h3>{t}</h3><p>{d}</p></div>' for t, d in PR_OFFERS) + '</div>'
              + ratecard
              + '</div></div>')
    from site_journeys import action
    next_step = '<section class="sec media-next"><div class="wrap"><div class="section-invitation"><div><h2>製品に合う紹介方法から、ご相談いただけます。</h2><p>紹介したい製品・公開時期・ご予算など、決まっている範囲でお知らせください。</p></div>' + action('PR・タイアップを相談する','/contact/?type=pr#contact-form') + '</div><div class="viewer-route"><p class="section-eyebrow">動画をご覧の方へ</p>' + membership_route + '</div></div></section>'
    production = '<div class="production-disclosure-wrap"><details class="production-disclosure" id="production-method"><summary>制作の進め方・作業時間の内訳を見る</summary>' + channel_story + '</details></div>'
    return offers + render_pr_works() + channel + production + next_step


INQUIRY_KINDS = ['開発・AI導入のご依頼', 'PR・タイアップのご依頼', '登壇のご依頼', '動画編集のご依頼', '採用・業務委託のご相談', 'その他']


def render_contact_form():
    """種別を選べる問い合わせフォーム (approved 2026-09-25)。

    送信先は Cloudflare Worker (contact-worker/) の https://studio.msyn.me/api/contact。
    Email Routing 経由で受信アドレスへ届く。送れなかったときはメールでの連絡先を案内する。
    """
    options = ''.join('<option>' + kind + '</option>' for kind in INQUIRY_KINDS)
    security = json.loads((HERE / 'contact-security.json').read_text())
    assert re.fullmatch(r'0x[A-Za-z0-9_-]{20,}', security['sitekey']), 'Production Turnstile sitekey required'
    assert security['hostname'] == 'studio.msyn.me' and security['action'] == 'contact'
    script = """<script>(()=>{const f=document.getElementById('inquiry-form');if(!f)return;if(location.hostname&&location.hostname.endsWith('.pages.dev')){location.replace('https://studio.msyn.me/contact/'+location.search+location.hash);return;}const s=f.querySelector('.form-status'),b=f.querySelector('button[type="submit"]'),hint=document.getElementById('inquiry-body-hint'),count=document.getElementById('inquiry-body-count');
const check=document.getElementById('inquiry-security-status'),retry=document.getElementById('inquiry-security-retry'),tokenField=document.getElementById('inquiry-security-token');
let token='',widgetId,checkState='loading',loader;
const checkMessage=(state,message)=>{checkState=state;check.textContent=message;retry.hidden=state!=='error';if(state!=='ready'){token='';tokenField.value='';}};
const startCheck=()=>{if(!window.turnstile)return;try{widgetId=window.turnstile.render('#inquiry-security-widget',{sitekey:__CONTACT_SITEKEY__,action:'contact',theme:'light',language:'ja',size:'compact',appearance:'interaction-only','response-field':false,'before-interactive-callback':()=>checkMessage('interactive','上の確認欄にチェックを入れてください。'),callback:value=>{token=value;tokenField.value=value;checkMessage('ready','');},'expired-callback':()=>checkMessage('loading','確認を更新しています…'),'timeout-callback':()=>checkMessage('error','確認が完了しませんでした。もう一度お試しください。'),'error-callback':()=>{checkMessage('error','自動確認を読み込めませんでした。通信状況をご確認のうえ、再試行してください。');return true;}});}catch(_){checkMessage('error','自動確認を開始できませんでした。もう一度お試しください。');}};
window.onContactTurnstileReady=startCheck;
const loadCheck=()=>{if(loader)loader.remove();checkMessage('loading','迷惑送信を防ぐため、自動で確認しています…');loader=document.createElement('script');loader.src='https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onContactTurnstileReady&render=explicit';loader.async=true;loader.defer=true;loader.addEventListener('error',()=>checkMessage('error','自動確認を読み込めませんでした。通信状況をご確認のうえ、再試行してください。'));document.head.append(loader);};
const resetCheck=()=>{checkMessage('loading','確認を更新しています…');if(window.turnstile&&widgetId!==undefined){try{window.turnstile.reset(widgetId);}catch(_){checkMessage('error','確認を更新できませんでした。ページを再読み込みしてください。');}}else if(window.turnstile)startCheck();else loadCheck();};
retry.addEventListener('click',resetCheck);loadCheck();
const K={web:['開発・AI導入のご依頼','Webサービス開発について。作りたいもの・時期・ご予算の目安など、分かる範囲でお書きください。'],ai:['開発・AI導入のご依頼','AI導入支援について。使っているツール・チームの人数・困っていることなど、分かる範囲でお書きください。'],pr:['PR・タイアップのご依頼','紹介したい製品・公開の時期・ご予算の目安など、分かる範囲でお書きください。'],talk:['登壇のご依頼','イベント名・日時・形式（オンライン／会場）・持ち時間など、分かる範囲でお書きください。'],video:['動画編集のご依頼','動画の内容・長さ・本数・納期など、分かる範囲でお書きください。'],recruit:['採用・業務委託のご相談','募集内容・働き方（正社員／業務委託／技術顧問）など、分かる範囲でお書きください。']};
const H={'開発・AI導入のご依頼':'開発・AI活用でお困りのこと、希望時期・ご予算など','PR・タイアップのご依頼':'製品名・紹介したい内容・公開時期・ご予算など','登壇のご依頼':'イベント名・テーマ・日時・持ち時間・開催形式など','動画編集のご依頼':'動画の内容・長さ・本数・納期など','採用・業務委託のご相談':'募集内容・担当業務・働き方・開始時期など'};
const k=K[new URLSearchParams(location.search).get('type')];if(k&&!f.elements.kind.value){f.elements.kind.value=k[0];}
const updateCount=()=>{count.textContent=f.elements.body.value.length.toLocaleString('ja-JP')+' / 5,000文字';};
const updateHint=()=>{hint.textContent=H[f.elements.kind.value]||'ご相談の概要・希望時期・ご予算など';};
updateHint();updateCount();if(k&&f.elements.kind.value===k[0])f.elements.body.placeholder=k[1];
f.addEventListener('change',e=>{if(e.target===f.elements.kind){updateHint();f.elements.body.placeholder='決まっている範囲でご記入ください。';}updateCount();});
f.addEventListener('input',e=>{if(e.target===f.elements.name||e.target===f.elements.body)e.target.setCustomValidity('');updateCount();});
window.addEventListener('pageshow',event=>{updateHint();updateCount();if(event?.persisted)resetCheck();});
document.addEventListener('DOMContentLoaded',updateCount,{once:true});
f.addEventListener('submit',async e=>{e.preventDefault();if(b.disabled)return;
for(const [field,label] of [[f.elements.name,'お名前'],[f.elements.body,'ご相談内容']])field.setCustomValidity(field.value.trim()?'':label+'を入力してください。');
if(!f.reportValidity())return;if(!token){s.className='form-status ng';s.textContent=checkState==='interactive'?'上の確認欄にチェックを入れてから送信してください。':checkState==='error'?'自動確認を再試行してから送信してください。':'自動確認が完了するまでお待ちください。';check.focus();return;}const fields=['kind','name','org','email','body'],submitted=fields.map(key=>f.elements[key].value);b.disabled=true;b.setAttribute('aria-busy','true');const buttonContent=b.innerHTML;b.textContent='送信中…';s.className='form-status';s.textContent='送信しています…';
try{const r=await fetch('https://studio.msyn.me/api/contact',{method:'POST',body:new FormData(f)});const j=await r.json().catch(()=>({}));
if(r.ok&&j.ok){document.dispatchEvent(new CustomEvent('site:inquiry-sent',{detail:{kind:submitted[0]}}));const edited=fields.some((key,index)=>f.elements[key].value!==submitted[index]);if(!edited){f.reset();f.elements.body.placeholder='決まっている範囲でご記入ください。';}updateHint();updateCount();s.className='form-status ok';s.textContent=edited?'送信しました。送信中に変更した内容は、未送信のまま残しています。':'送信しました。ありがとうございます。通常2営業日以内に、入力いただいたメールアドレスへ返信します。';}
else{s.className='form-status ng';s.textContent=(j.error||'送信できませんでした。')+' 急ぎの場合は contact@msyn.me へメールでお送りください。';}}
catch(_){s.className='form-status ng';s.textContent='送信できませんでした。通信状況をご確認のうえ、もう一度お試しいただくか、contact@msyn.me へメールでお送りください。';}
finally{resetCheck();b.disabled=false;b.removeAttribute('aria-busy');b.innerHTML=buttonContent;s.focus();}});})();</script>""".replace("__CONTACT_SITEKEY__", json.dumps(security["sitekey"]))
    return ('<section class="sec contact-form-sec" id="contact-form"><div class="wrap"><div class="contact-form-card">'
            '<h2>お仕事の相談を送る</h2><p class="lead">ご依頼内容・時期・ご予算など、分かる範囲でお知らせください。通常2営業日以内に返信します。</p><p id="quote-handoff-status" role="status" aria-live="polite"></p>'
            '<form id="inquiry-form" method="post" action="https://studio.msyn.me/api/contact" autocomplete="on"><label for="inquiry-kind"><span class="field">ご相談の種類<span class="req">必須</span></span><select id="inquiry-kind" name="kind" required><option value="">選んでください</option>' + options + '</select></label>'
            '<label for="inquiry-name"><span class="field">お名前<span class="req">必須</span></span><input id="inquiry-name" name="name" type="text" required maxlength="100" autocomplete="name" autocapitalize="words" autocorrect="off" spellcheck="false" enterkeyhint="next"></label>'
            '<label for="inquiry-org"><span class="field">会社名・団体名<span class="opt">任意</span></span><input id="inquiry-org" name="org" type="text" maxlength="150" autocomplete="organization" autocapitalize="words" autocorrect="off" spellcheck="false" enterkeyhint="next"></label>'
            '<label for="inquiry-email"><span class="field">メールアドレス<span class="req">必須</span></span><input id="inquiry-email" name="email" type="email" inputmode="email" required maxlength="254" autocomplete="email" autocapitalize="none" autocorrect="off" spellcheck="false" enterkeyhint="next" placeholder="name@example.com"></label>'
            '<label for="inquiry-body"><span id="inquiry-body-label" class="field">ご相談内容<span class="req">必須</span></span><span id="inquiry-body-hint" class="field-hint">ご相談の概要・希望時期・ご予算など</span><textarea id="inquiry-body" name="body" rows="6" required maxlength="5000" autocomplete="off" spellcheck="true" enterkeyhint="enter" aria-labelledby="inquiry-body-label" aria-describedby="inquiry-body-hint inquiry-body-count" placeholder="決まっている範囲でご記入ください。"></textarea><span id="inquiry-body-count" class="field-count">0 / 5,000文字</span></label>'
            '<label class="hp" aria-hidden="true">ウェブサイト<input name="website" tabindex="-1" autocomplete="off"></label>'
            '<div class="inquiry-security" id="inquiry-security"><div id="inquiry-security-widget"></div><input id="inquiry-security-token" type="hidden" name="cf-turnstile-response"><p id="inquiry-security-status" role="status" aria-live="polite" tabindex="-1">迷惑送信を防ぐため、自動で確認します。</p><button id="inquiry-security-retry" type="button" hidden>自動確認を再試行</button><noscript>送信にはJavaScriptを有効にしてください。</noscript></div>'
            '<div class="form-submit"><button class="site-action site-action-primary" data-site-action="primary" type="submit">送信する<span aria-hidden="true">→</span></button></div><p class="form-status" role="status" aria-live="polite" aria-atomic="true" tabindex="-1"></p></form></div></div></section>' + script)
