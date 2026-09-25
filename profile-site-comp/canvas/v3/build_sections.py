"""Render excerpts and full case studies from the same editable content."""
from pathlib import Path
import hashlib
import re

HERE = Path(__file__).resolve().parent


CHROME_EXTENSIONS = [
    ('Article Date Detector', 'Webページの公開日・更新日を表示し、記事の新しさをすぐに判断できる', 74, 'https://chromewebstore.google.com/detail/article-date-detector/kcibimkobhbikanlidohhnahodekmaej'),
    ('Markdown Preview', 'Markdownをリアルタイムにプレビュー。目次・テーマ・フォントを設定できる', 59, 'https://chrome-extensions-6cv.pages.dev/rich-markdown-preview/'),
    ('Web Annotator', 'Webページにマーカーや付箋を付け、Markdownで書き出す', 28, 'https://chromewebstore.google.com/detail/web-annotator/gckpllfnimaepbbelfmhcelibclnkena'),
    ('Copy Tab Anything', '開いているタブのタイトルとURLを、Markdownなど好きな形式でまとめてコピー', 19, 'https://chromewebstore.google.com/detail/copy-tab-anything/gafkainbomdnemmdemopmechbmabgfeh'),
    ('Canvas Whiteboard', 'ブラウザで使えるホワイトボード。アイデア整理や図解に', 17, 'https://chromewebstore.google.com/detail/canvas-whiteboard/fpekokphickomacboclmogcmjeffhmle'),
]


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
        ('チャンネルの運営', '動画制作と製品紹介'),
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
            destinations = [('services', '開発・AI導入支援について'), ('services', '開発・AI導入支援について'),
                            ('media', '代表動画・PR・コラボについて'), ('talks', '登壇記録・ご依頼について'), (None, 'ソースコードを見る（GitHub）')]
            dest, label = destinations[index]
            if dest:
                revised = re.sub(r'<a class="detail-link".*?</a>', '<a class="detail-link" href="' + files[dest] + '"><span>' + label + '</span><span aria-hidden="true">↗</span></a>', revised, flags=re.S)
        source = source.replace(case, revised)
        cases[index] = revised
    if single is not None:
        case = re.sub(r'<a class="detail-link".*?</a>', '', cases[single], flags=re.S)
        case = case.replace('<h3 class="story-title"', '<h2 class="story-title"').replace('</h3>', '</h2>')
        case = case.replace('<h4>', '<h3>').replace('</h4>', '</h3>')
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
    ('言語', [('Python', '7年以上'), ('TypeScript', '5年'), ('PHP', '2年')]),
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
    tiles = [(f"{data['channel_views'] // 1000 / 10:.1f}<small>万回</small>", 'チャンネルの累計再生数'),
             (f"{data['views90'] // 1000 / 10:.1f}<small>万回</small>", '直近90日の再生数'),
             (f"{data['long_mean']:,}<small>回</small>", '本編1本あたりの平均再生数'),
             (f"{data['long_count']}<small>本</small>", '直近90日に公開した本編')]
    ages = [('18〜24歳', data['age']['18-24']), ('25〜34歳', data['age']['25-34']), ('35〜44歳', data['age']['35-44']),
            ('45〜54歳', data['age']['45-54']), ('55歳以上', data['age']['55+'])]
    bars = ''.join(f'<div class="mk-bar"><span>{label}</span><i style="width:{value / 40 * 100:.0f}%"></i><em>{value:.0f}%</em></div>' for label, value in ages)
    return ('<div class="mediakit" id="mediakit"><h3>視聴者データ</h3>'
            f'<p class="note">{data["as_of"]}時点。再生数・年齢層は直近90日（YouTube アナリティクス）。</p>'
            '<div class="mk-tiles">' + ''.join(f'<div><b>{n}</b><span>{l}</span></div>' for n, l in tiles) + '</div>'
            f'<div class="mk-aud"><div><h4>年齢層</h4>{bars}</div><div><h4>主なテーマ</h4>'
            '<p class="mk-theme">Claude Code を中心としたAI駆動開発。視聴者の中心は、AIを開発に取り入れたいエンジニアです。</p></div></div></div>')


INQUIRY_KINDS = ['開発・AI導入のご依頼', 'PR・タイアップのご依頼', '登壇のご依頼', '動画編集のご依頼', '採用・業務委託のご相談', 'その他']


def render_contact_form():
    """種別を選べる問い合わせフォーム (approved 2026-09-25)。

    送信先は Cloudflare Worker (contact-worker/) の https://studio.msyn.me/api/contact。
    Email Routing 経由で受信アドレスへ届く。送れなかったときはメールでの連絡先を案内する。
    """
    options = ''.join('<option>' + kind + '</option>' for kind in INQUIRY_KINDS)
    script = """<script>(()=>{const f=document.getElementById('inquiry-form');if(!f)return;const s=f.querySelector('.form-status'),b=f.querySelector('button');
f.addEventListener('submit',async e=>{e.preventDefault();b.disabled=true;s.className='form-status';s.textContent='送信しています…';
try{const r=await fetch('https://studio.msyn.me/api/contact',{method:'POST',body:new FormData(f)});const j=await r.json().catch(()=>({}));
if(r.ok&&j.ok){f.reset();s.className='form-status ok';s.textContent='送信しました。ありがとうございます。通常2営業日以内に、入力いただいたメールアドレスへ返信します。';}
else{s.className='form-status ng';s.textContent=(j.error||'送信できませんでした。')+' 急ぎの場合は contact@msyn.me へメールでお送りください。';}}
catch(_){s.className='form-status ng';s.textContent='送信できませんでした。通信状況をご確認のうえ、もう一度お試しいただくか、contact@msyn.me へメールでお送りください。';}
finally{b.disabled=false;}});})();</script>"""
    return ('<section class="sec contact-form-sec" id="contact-form"><div class="wrap"><div class="contact-form-card">'
            '<h2>フォームから送る</h2><p class="lead">入力して「送信する」を押すと、この場で送信されます。通常2営業日以内に、入力いただいたメールアドレスへ返信します。</p>'
            '<form id="inquiry-form" novalidate><label><span class="field">ご相談の種類<span class="req">必須</span></span><select name="kind" required><option value="">選んでください</option>' + options + '</select></label>'
            '<label><span class="field">お名前<span class="req">必須</span></span><input name="name" required maxlength="100" autocomplete="name"></label>'
            '<label><span class="field">会社名・団体名<span class="opt">任意</span></span><input name="org" maxlength="150" autocomplete="organization"></label>'
            '<label><span class="field">メールアドレス<span class="req">必須</span></span><input name="email" type="email" required maxlength="254" autocomplete="email"></label>'
            '<label><span class="field">ご相談内容<span class="req">必須</span></span><textarea name="body" rows="6" required maxlength="5000"></textarea></label>'
            '<label class="hp" aria-hidden="true">ウェブサイト<input name="website" tabindex="-1" autocomplete="off"></label>'
            '<button type="submit">送信する</button><p class="form-status" role="status" aria-live="polite"></p></form></div></div></section>' + script)
