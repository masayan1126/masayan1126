"""A selective, inquiry-focused edition of the local design study."""
from html import escape
from datetime import date
import json
from pathlib import Path
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
SOURCE_ROOT = HERE.parents[3] / 'canvas/v3/site'


def link(label, href, primary=False):
    external = ' target="_blank" rel="noopener noreferrer"' if href.startswith('https://') else ''
    css = 'editorial-button' if primary else 'editorial-button editorial-button-secondary'
    return f'<a class="{css}" href="{escape(href, quote=True)}"{external}>{label}<span aria-hidden="true">↗</span></a>'


def lucide_icon(name, css_class):
    folder = HERE / 'icons'
    # Retain the complete license with each locally embedded icon.
    notice = (folder / 'lucide-LICENSE.txt').read_text()
    # Consecutive hyphens are not valid inside HTML comments.
    notice = notice.replace('--', '—')
    attribution = '<!-- Lucide ' + name + ': https://lucide.dev/icons/' + name + '\n' + notice + '\n-->'
    return attribution + (folder / (name + '.svg')).read_text().replace(
        '<svg', f'<svg class="{css_class}" aria-hidden="true" focusable="false"', 1)


def studio_mark():
    # Original curved m monogram, adopted proposal B; separate from licensed icons.
    return (HERE / 'icons/miyabiya-mark.svg').read_text().replace(
        '<svg', '<svg class="editorial-brand-icon" aria-hidden="true" focusable="false"', 1)


def header(current):
    contact_link = '<a class="editorial-home-link" href="/" aria-label="トップページへ戻る"><span aria-hidden="true">←</span><span class="home-link-full" aria-hidden="true">トップページへ戻る</span><span class="home-link-short" aria-hidden="true">トップへ</span></a>' if current == 'contact' else '<a class="editorial-contact-link" href="/contact/">お問い合わせ <span aria-hidden="true">↗</span></a>'
    return f'''<header class="editorial-header"><div class="editorial-shell editorial-header-inner">
<a class="editorial-brand" href="/">{studio_mark()}Miyabiya Studio</a>
<div class="editorial-header-actions">{social_icon_links('header')}{contact_link}</div>
</div></header>'''


def footer():
    return '<footer class="editorial-footer"><div class="editorial-shell focus-footer">' + social_icon_links('footer') + '''
<p>© 2026 Miyabiya Studio</p>
</div></footer>'''


def intro(title, text=''):
    lead = f'<p>{text}</p>' if text else ''
    return f'<section class="editorial-shell focus-page-head"><h1>{title}</h1>{lead}</section>'


def section(title, body, id=''):
    attr = f' id="{id}"' if id else ''
    return f'<section class="editorial-shell focus-section"{attr}><h2>{title}</h2>{body}</section>'


def invitation(title='お仕事のご依頼・採用のご相談', text='', href='/contact/#contact-form', label='お問い合わせフォームへ'):
    lead = f'<p>{text}</p>' if text else ''
    return f'''<section class="editorial-shell focus-invitation"><div><h2>{title}</h2>{lead}</div>{link(label, href, True)}</section>'''


def talk_records(source=None):
    if source is None:
        source = BeautifulSoup((SOURCE_ROOT / 'talks/index.html').read_text(), 'html.parser')
    covers = json.loads((HERE / 'assets/talk-cards.json').read_text())
    records = []
    for item in source.select('#talks .talk'):
        title = item.select_one('a.talk-title')
        deck = item.select_one('iframe')['src']
        cover = covers[deck.rsplit('/', 1)[-1]]
        records.append({'title': title.get_text(' ', strip=True), 'date': item.select_one('.d').get_text(' ', strip=True),
                        'event': item.select_one('.ev').get_text(' ', strip=True), 'event_url': title['href'],
                        'deck_url': deck, 'short_title': cover['label'], 'page_url': cover['page_url'],
                        'image': '/editorial-assets/' + cover['image']})
    return records


def talk_previews():
    return '<div class="talk-preview-row">' + ''.join(
        f'''<a class="talk-preview" href="{escape(item['event_url'], quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="登壇テーマ：{escape(item['short_title'], quote=True)}のイベントページを見る（新しいタブ）" title="{escape(item['title'], quote=True)}">
<img src="{item['image']}" width="640" height="360" alt="" loading="lazy">
<span class="talk-preview-title">登壇テーマ：{escape(item['short_title']).replace('使いこなす', '<span class="activity-card-phrase">使いこなす</span>')}</span></a>'''
        for item in talk_records()
    ) + '</div>'


def activity_list(items):
    marker = '<span class="activity-list-marker" aria-hidden="true"><svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="m4 8 2.5 2.5L12 5"/></svg></span>'
    return '<ul class="activity-highlights" role="list">' + ''.join(f'<li>{marker}<span>{item}</span></li>' for item in items) + '</ul>'


def social_icon_links(placement):
    profiles = [
        ('youtube', 'YouTube', 'https://www.youtube.com/@masayan-ai-hack'),
        ('x', 'X', 'https://x.com/masayan_ai_hack'),
        ('instagram', 'Instagram', 'https://www.instagram.com/miyabiya1126/'),
        ('note', 'note', 'https://note.com/msyn1126'),
        ('github', 'GitHub', 'https://github.com/masayan1126'),
    ]
    links = []
    for slug, name, url in profiles:
        if slug == 'note':
            icon = '<img class="site-social-icon site-social-icon-note" src="/editorial-assets/note-icon.svg" width="44" height="44" alt="" aria-hidden="true">'
            label = name + 'を開く（新しいタブ）'
            links.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{label}" title="{name}">{icon}</a>')
            continue
        svg = BeautifulSoup((HERE / 'icons/simple-icons' / (slug + '.svg')).read_text(), 'html.parser').svg
        svg.attrs.pop('role', None)
        svg.attrs.update({'class': 'site-social-icon' + (' site-social-icon-youtube' if slug == 'youtube' else ''), 'aria-hidden': 'true', 'focusable': 'false', 'fill': 'currentColor'})
        for title in svg.select('title'):
            title.decompose()
        label = name + 'を開く（新しいタブ）'
        links.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{label}" title="{name}">{svg}</a>')
    landmark = 'ヘッダー' if placement == 'header' else 'フッター'
    return f'<nav class="site-social-links" aria-label="{landmark}のSNS・公開プロフィール">' + ''.join(links) + '</nav>'


def youtube_audience_count(metric, label):
    audience = json.loads((HERE.parents[1] / 'youtube-audience.json').read_text())
    value = audience[metric]
    observed = date.fromisoformat(value['as_of'])
    return (f'<span class="audience-count"><span>{label}：<strong>{value["count"]:,}人</strong></span>'
            f'<time datetime="{observed.isoformat()}">（{observed.year}年{observed.month}月{observed.day}日時点）</time></span>')


def technical_activities():
    return activity_list([
        '<a id="youtube" href="https://www.youtube.com/@masayan-ai-hack" target="_blank" rel="noopener noreferrer">YouTube「まさやん【AIギルドch】」</a>でAI駆動開発・AIエージェント・動画制作の自動化を発信' + youtube_audience_count('subscribers', '登録者数'),
        '<a id="membership" href="/membership/">YouTubeメンバーシップ</a>で限定投稿・動画を提供' + youtube_audience_count('members', 'メンバー数'),
        '<a href="https://x.com/masayan_ai_hack" target="_blank" rel="noopener noreferrer">X（@masayan_ai_hack）</a>',
        '<a href="https://www.instagram.com/miyabiya1126/" target="_blank" rel="noopener noreferrer">Instagram（@miyabiya1126）</a>',
        '<a href="https://note.com/msyn1126" target="_blank" rel="noopener noreferrer">note（@msyn1126）</a>',
    ])


def extension_records():
    return json.loads((HERE / 'assets/extensions/manifest.json').read_text())['extensions']


def extension_icon_links():
    links = []
    for item in extension_records():
        name = escape(item['name'], quote=True)
        first_line, last_word = item['name'].rsplit(' ', 1)
        label = escape(first_line) + '<br>' + escape(last_word)
        links.append(f'''<a href="{escape(item['store_url'], quote=True)}" target="_blank" rel="noopener noreferrer" title="{name}" aria-label="{name}のChromeウェブストア掲載ページ（新しいタブ）"><img src="/editorial-assets/extensions/{item['image']}" width="48" height="48" alt="" loading="lazy"><span class="project-extension-name">{label}</span></a>''')
    return '<nav class="project-extension-links" aria-label="公開中のChrome拡張機能">' + ''.join(links) + '</nav>'


def personal_projects():
    usage = json.loads((HERE / 'assets/extension-user-counts.json').read_text())
    observed = date.fromisoformat(usage['as_of'])
    total = sum(usage['user_counts'])
    usage_label = f'<span class="extension-users"><span>ユーザー数：合計<strong>{total:,}人</strong></span><time datetime="{observed.isoformat()}">（{observed.year}年{observed.month}月{observed.day}日時点）</time></span>'
    return '<div class="project-extensions">' + activity_list([
        '<a id="tools" href="https://github.com/masayan1126/chrome-extensions" target="_blank" rel="noopener noreferrer">Chrome拡張機能を5本公開</a>' + usage_label,
    ]) + extension_icon_links() + '</div>'


def ai_video_editing():
    return activity_list([
        'YouTube制作の自動化で、本編1本・ショート15本の工数を<strong>約90%</strong>削減（約25〜37時間→約2〜3時間、<span class="activity-qualifier">撮影除く）</span>',
        '教育・ビジネス系の動画編集：カット・テロップ・効果音に対応。モーショングラフィックスなどの高度な演出は対象外',
    ])


def ai_support():
    return activity_list([
        '業務・開発環境に合わせたAIツールの選定・導入',
        '設計・実装・コードレビューにAIを組み込む開発フローの整備',
        '社内勉強会・作業手順の共有によるチームへの定着',
        '<span id="ai-results">勤務先での実績：AI駆動開発環境の構築により、企画からリリースまでの開発工数を<strong>約50〜75%</strong>削減<span class="activity-qualifier">（AI導入前比）</span></span>',
        '<a href="/works/#work-case-1">MCPサーバーの企画・開発、社内外への導入</a>',
    ]) + '<details class="focus-details ai-support-details" id="other-services"><summary>その他の対応業務</summary>' + activity_list([
        '<span id="web-development">Webサービス・MCPサーバーの開発：要件整理・設計・実装・運用、フロントエンド・バックエンド・クラウドの開発・構築</span>',
    ]) + '</details>'


def home():
    # Keep A's adopted layout; the earlier three studies remain historical.
    activity_icons = {'ai': 'brain-circuit', 'pr': 'clapperboard', 'talk': 'presentation', 'activity': 'rss', 'development': 'code-xml', 'video': 'clapperboard'}
    entries = [
        ('activity', '技術発信', ''),
        ('pr', 'YouTube や SNS での製品PR・タイアップ', 'Notta 株式会社様の Notta Memo ProのPR動画'),
        ('development', '個人開発', ''),
        ('video', 'AI動画編集', ''),
        ('talk', '登壇・社内勉強会', ''),
        ('ai', 'AI活用支援', ''),
    ]
    def video_card(title):
        return f'''<a class="pr-video-card pr-video-plain" href="https://youtu.be/FsA8gaup0w4" target="_blank" rel="noopener noreferrer" aria-label="{escape(title, quote=True)}をYouTubeで見る（新しいタブ）">
<img src="/thumb-FsA8gaup0w4.webp" width="640" height="360" alt="" loading="lazy">
<span class="pr-video-copy"><strong class="pr-video-title">{title.replace('PR動画', '<span class="pr-video-kind">PR動画</span>')}</strong><span class="pr-video-action">YouTubeで見る <span aria-hidden="true">→</span></span></span></a>'''
    anchors = {'ai': 'ai-adoption', 'pr': 'product-pr', 'talk': 'speaking', 'activity': 'activities', 'development': 'personal-development', 'video': 'video-editing'}
    renderers = {'ai': ai_support, 'talk': talk_previews, 'activity': technical_activities, 'development': personal_projects, 'video': ai_video_editing}
    def entry_content(category, title, proof):
        heading = f'<h2 class="activity-title-with-icon">{lucide_icon(activity_icons[category], "activity-title-icon")}<span>{title}</span></h2>'
        if category == 'pr':
            action = '<a class="pr-estimate-link" href="/pricing/" aria-label="PR動画の料金を見積もる">' + lucide_icon('calculator', 'pr-estimate-icon') + '<span>料金を見積もる</span><span class="arrow" aria-hidden="true">→</span></a>'
            return '<div class="pr-section-header">' + heading + action + '</div>' + video_card(proof)
        return heading + renderers[category]()
    rows = ''.join(
        f'<article class="a-entry" data-category="{category}"' + (f' id="{anchors[category]}"' if anchors[category] else '') + '><div class="activity-group">'
        + entry_content(category, title, proof)
        + '</div></article>'
        for category, title, proof in entries
    )
    return '''<div class="a-shell compact-home-content"><section class="a-intro" aria-labelledby="a-title">
<div class="a-person"><img src="/editorial-assets/avatar-mono-pixel.png" width="40" height="40" alt=""><div><h1 id="a-title">Masaya Nishigaki</h1><p class="eyebrow">Web系のシニアエンジニア・テックリード</p></div></div>
<p class="a-bio">YouTubeでのAI関連の発信・PR・個人開発・AI動画編集・技術登壇などを中心に活動</p></section>
<div class="a-work">''' + rows + '</div></div>'


def works(source):
    return intro('実績紹介', '勤務先でのAI導入と、個人で担当した制作・開発の実績です。') + section('AI開発フローのチーム導入', '''<p class="focus-kicker">勤務先での実績</p><p class="focus-result">AI駆動開発環境の構築により、企画からリリースまでの開発工数を約50〜75%削減 <small class="focus-note">（AI導入前比）</small></p>
<dl class="focus-facts"><div><dt>担当業務</dt><dd>企画からリリースまでの開発工程にAIを導入しました。Issueを起点とした開発フローと、生成・評価を分担するAIの仕組みを整え、チームへ展開しました。</dd></div><div><dt>業務効率化の成果</dt><dd>商談用デモの準備などにかかる時間を、1件8〜12時間から20分へ短縮しました。月平均30件で、月230〜350時間の削減です。</dd></div></dl>''', 'work-case-0') + section('MCPサーバーの企画・開発', '''<p class="focus-result">社外クライアントと社内チームへ導入</p><dl class="focus-facts"><div><dt>担当業務</dt><dd>自社製品をAIから利用するMCPサーバーを、企画・要件定義から設計・実装、導入支援まで担当しました。</dd></div><div><dt>導入後の利用状況</dt><dd>作業手順をAIへ伝えるスキルも配布しました。勉強会2回で約20名へ共有し、約10名が実務で活用しています。</dd></div></dl>''', 'work-case-1') + section('製品PR・個人開発', '''<div class="focus-two-col"><article id="work-case-2"><h3>Notta Memo Proのタイアップ動画</h3><p>実機検証、構成・スライド、撮影・編集、サムネイル、公開とXでの告知を担当しました。</p>''' + link('制作動画を見る', '/#product-pr') + '''</article><article id="work-case-4"><h3>Chrome拡張機能を5本公開</h3><p>Markdownのプレビューやタブのコピーなど、日常の作業を効率化するツールを企画し、開発・公開しました。</p>''' + link('ソースコードを見る', 'https://github.com/masayan1126/chrome-extensions') + '''</article></div>''') + invitation()


def profile(source):
    return intro('プロフィール・職務経歴') + section('Masaya Nishigaki', '''<div class="focus-person"><img src="/hero-photo.webp" width="800" height="1000" alt="Masaya Nishigaki" loading="lazy"><div><p class="focus-result">Web系のシニアエンジニア・テックリード</p><p>Web系企業でテックリードを務め、開発チームへのAI導入に取り組んでいます。個人では製品PR、技術登壇、YouTubeでの発信とツール開発を行っています。Miyabiya Studioは個人の屋号です。</p></div></div>''') + section('主な活動', activity_links()) + section('職務経歴', '''<ol class="focus-career">
<li><p class="focus-kicker">現職・Web系企業 · 3年</p><h3>インフラからバックエンドリード、テックリードへ</h3><p>開発体制の整備、MCPサーバーの開発、AI開発フローのチーム展開を担当しました。</p><details class="focus-details"><summary>担当業務の詳細</summary><p>クリーンアーキテクチャ・自動テスト・CI/CDの導入、決済・SSO（SAML）・監査ログの設計と実装を担当しました。一次面接50回以上、エンジニア4名の採用に関与しました。</p></details></li>
<li><p class="focus-kicker">前職・Web系企業 · 2年</p><h3>フロントエンドのチームリーダー</h3><p>技術選定から保守まで担当しました。React・Next.js・Vue3の導入、CypressによるE2EテストのCI組み込み、メンバーの技術教育を進めました。</p></li>
<li><p class="focus-kicker">SIer · 4年</p><h3>営業・システム開発</h3><p>営業と、詳細設計・実装・テストを担当しました。</p></li></ol>''', 'career-history') + section('技術・スキル', '''<dl class="focus-facts"><div><dt>開発</dt><dd>Python・TypeScript（各5年） / Django・FastAPI・FastMCP / Vue.js・React・Next.js</dd></div><div><dt>基盤・運用</dt><dd>PostgreSQL・BigQuery / Google Cloud・AWS / Docker・GitHub Actions</dd></div><div><dt>AI活用</dt><dd>Claude Code・Codex・Cursor / 開発フローの設計・MCPサーバー開発</dd></div></dl>''', 'tech-stack') + section('採用・業務委託をご検討の方へ', '''<p>正社員・業務委託・技術顧問のご相談をお受けしています。職務経歴書はお問い合わせ後にお送りします。</p><div class="editorial-actions">''' + link('採用・業務委託を相談する', '/contact/?type=recruit#contact-form', True) + link('実績を見る', '/works/') + '''</div>''', 'career')


def activity_links():
    return '<nav class="focus-activity-links" aria-label="活動の詳細"><a href="/#activities">技術発信 ↗</a><a href="/#product-pr">製品PR・タイアップ ↗</a><a href="/#personal-development">個人開発 ↗</a><a href="/#video-editing">AI動画編集 ↗</a><a href="/talks/">登壇・社内勉強会 ↗</a><a href="/#ai-adoption">AI活用支援 ↗</a></nav>'


def talks(source):
    records = []
    for item in talk_records(source):
        records.append(f'''<article class="focus-talk"><p class="focus-kicker">{escape(item['date'])} · {escape(item['event'])}</p><h3>{escape(item['title'])}</h3><div class="editorial-actions">{link('イベントを見る', item['event_url'])}{link('スライドを見る', item['deck_url'])}</div></article>''')
    return intro('登壇・社内勉強会') + section('テーマ・対応形式', '''<p>AI駆動開発のチーム導入、MCPサーバー開発、YouTube運営・動画制作の自動化を主なテーマとしています。LT（5〜15分）からセッション（30〜45分）、社内勉強会に対応します。オンライン・会場での登壇に対応します。</p>''', 'talk-request') + section('登壇実績', ''.join(records), 'talks') + invitation('登壇のご相談', 'イベント名・日時・持ち時間をお知らせください。', '/contact/?type=talk#contact-form', '登壇を相談する')


def membership(source):
    return intro('YouTubeメンバーシップ') + section('特典・加入方法', youtube_audience_count('members', 'メンバー数') + '''<p>月額390円から、3つの料金プランをご用意しています。メンバー限定の投稿・動画・Shortsに加え、上位プランではAI活用のドキュメントやソースコードを配布します。いつでも解約できます。</p><div class="editorial-actions">''' + link('特典・料金プランを見る', 'https://masayan-ai-tech-ch.pages.dev/membership/', True) + link('YouTubeで加入する', 'https://www.youtube.com/@masayan-ai-hack/join') + '''</div>''')


def contact(source):
    form_section = source.select_one('#contact-form')
    form_section.select_one('h2').decompose()
    for paragraph in form_section.select('.sec-lead, .contact-form-card > .lead'):
        paragraph.decompose()
    script = form_section.find_next_sibling('script')
    return intro('お問い合わせ', 'AI活用支援・製品PR・登壇などのご依頼を承っています。内容・希望時期・ご予算を、分かる範囲でお知らせください。通常2営業日以内に返信します。') + str(form_section) + (str(script) if script else '')


def page_content(page, source):
    if page == 'pricing':
        # Preserve every quote DOM contract, including historical link restoration.
        return None
    body = home() if not page else globals()[page](source)
    classes = 'focus-main compact-home' if not page else 'focus-main'
    return f'<main id="main-content" tabindex="-1" class="{classes}">{body}</main>'
