"""A selective, inquiry-focused edition of the local design study."""
from html import escape
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]


def link(label, href, primary=False):
    external = ' target="_blank" rel="noopener noreferrer"' if href.startswith('https://') else ''
    css = 'editorial-button' if primary else 'editorial-text-link'
    return f'<a class="{css}" href="{escape(href, quote=True)}"{external}>{label}<span aria-hidden="true">↗</span></a>'


def header(current):
    items = [('works', '実績'), ('services', '依頼できること'), ('profile', '経歴')]
    links = ''.join(f'<a href="/{slug}/"' + (' aria-current="page"' if current == slug else '') + f'>{label}</a>' for slug, label in items)
    return f'''<header class="editorial-header"><div class="editorial-shell editorial-header-inner">
<a class="editorial-brand" href="/">Miyabiya Studio<span>Masaya Nishigaki</span></a>
<nav class="editorial-nav" aria-label="メインメニュー">{links}</nav>
<a class="editorial-contact-link" href="/contact/#contact-form">相談する <span aria-hidden="true">↗</span></a>
</div></header>'''


def footer():
    return '''<footer class="editorial-footer"><div class="editorial-shell focus-footer">
<p>© 2026 Masaya Nishigaki</p><nav aria-label="外部の活動"><a href="https://github.com/masayan1126" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="https://www.youtube.com/@masayan-ai-hack" target="_blank" rel="noopener noreferrer">YouTube ↗</a></nav>
</div></footer>'''


def intro(title, text):
    return f'<section class="editorial-shell focus-page-head"><h1>{title}</h1><p>{text}</p></section>'


def section(title, body, id=''):
    attr = f' id="{id}"' if id else ''
    return f'<section class="editorial-shell focus-section"{attr}><h2>{title}</h2>{body}</section>'


def invitation(title='仕事・採用のご相談', text='内容・時期・ご予算など、決まっている範囲でお知らせください。', href='/contact/#contact-form', label='相談内容を送る'):
    return f'''<section class="editorial-shell focus-invitation"><div><h2>{title}</h2><p>{text}</p></div>{link(label, href, True)}</section>'''


def home():
    return '''<section class="editorial-shell editorial-intro" aria-labelledby="editorial-title">
<div><p class="editorial-byline">Webエンジニア・テックリード</p><h1 id="editorial-title">Web開発とAI活用を、<br>仕事の現場へ。</h1></div>
<div class="editorial-intro-copy"><p>Masaya Nishigakiです。Webサービス開発と、チームへのAI導入を担当しています。製品PRや技術登壇もお受けしています。</p><div class="editorial-actions">''' + link('仕事を相談する', '/contact/#contact-form', True) + link('採用をご検討の方へ', '/profile/#career') + '''</div></div></section>
''' + section('主な実績', '''<div class="focus-highlights">
<article class="focus-highlight"><p class="focus-kicker">勤務先の開発チームへのAI導入</p><h3>設計・実装・レビューの工数を<br>約50〜75%削減</h3><p>AI導入前の実績工数との比較。開発フローの設計から、チームへの展開・定着まで担当しました。</p>''' + link('取り組みを見る', '/works/#work-case-0') + '''</article>
<article class="focus-highlight"><p class="focus-kicker">勤務先でのMCPサーバー開発</p><h3>自社製品をAIから使える仕組みを、<br>企画から導入まで</h3><p>要件定義・設計・実装と、社外クライアント・社内チームへの導入を担当しました。</p>''' + link('担当範囲と成果を見る', '/works/#work-case-1') + '''</article>
<article class="focus-highlight focus-highlight-media"><a href="/media/#pr-works" aria-label="Notta Memo Proの制作実績を見る"><img src="/thumb-FsA8gaup0w4.webp" width="640" height="360" alt="制作したNotta Memo Pro紹介動画のサムネイル" loading="lazy"></a><div><p class="focus-kicker">製品PR動画の制作</p><h3>Notta Memo Proを、<br>実機で検証して紹介</h3><p>構成から撮影・編集・公開まで担当しました。</p>''' + link('動画と制作内容を見る', '/media/#pr-works') + '''</div></article></div>''', 'selected-work') + invitation(text='Web開発・AI導入・製品PRのご依頼、採用・業務委託についてご相談いただけます。')


def works(source):
    return intro('実績', '勤務先での担当業務と、個人で公開した制作物です。勤務先の社名は伏せて掲載しています。') + section('AI開発フローのチーム導入', '''<p class="focus-result">開発工数を約50〜75%削減</p><p class="focus-note">設計・実装・コードレビューの実績工数を、AI導入前と比較。</p>
<dl class="focus-facts"><div><dt>担当</dt><dd>テックリードとして導入を推進。Issueから開発を進める流れと、生成役・評価役のAIを組み合わせた仕組みを設計・実装し、勉強会でチームへ展開しました。</dd></div><div><dt>業務への展開</dt><dd>商談用デモの準備なども、1件8〜12時間から20分へ短縮。月平均30件で、月230〜350時間の削減です。</dd></div></dl>''', 'work-case-0') + section('MCPサーバーの企画・開発', '''<p class="focus-result">社外クライアントと社内チームへ導入</p><dl class="focus-facts"><div><dt>担当</dt><dd>自社製品をAIから利用するMCPサーバーを、企画・要件定義から設計・実装、導入支援まで担当しました。</dd></div><div><dt>定着</dt><dd>作業手順をAIへ伝えるスキルも配布。勉強会2回で約20名へ共有し、約10名が実務で活用しています。</dd></div></dl>''', 'work-case-1') + section('製品PR・公開したプロダクト', '''<div class="focus-two-col"><article id="work-case-2"><h3>Notta Memo Proのタイアップ動画</h3><p>実機検証、構成・スライド、撮影・編集、サムネイル、公開とXでの告知を担当しました。</p>''' + link('制作した動画を見る', '/media/#pr-works') + '''</article><article id="work-case-4"><h3>Chrome拡張機能を5本公開</h3><p>Markdownのプレビューやタブのコピーなど、自分が不便に感じた作業を減らすツールを、企画から開発・公開まで担当しました。</p>''' + link('公開物とソースコードを見る', 'https://github.com/masayan1126/chrome-extensions') + '''</article></div>''') + invitation()


def profile(source):
    return intro('経歴', 'Webサービスの開発から、チームの技術選定・AI導入まで担当してきました。') + section('Masaya Nishigaki', '''<div class="focus-person"><img src="/hero-photo.webp" width="800" height="1000" alt="Masaya Nishigaki" loading="lazy"><div><p class="focus-result">Webエンジニア・テックリード</p><p>Miyabiya Studioは個人の屋号です。現在はWeb系企業でテックリードを務め、MCPサーバーとAPIの開発、開発チームへのAI導入に取り組んでいます。</p></div></div>''') + section('これまでの担当', '''<ol class="focus-career">
<li><p class="focus-kicker">現職・Web系企業 · 3年</p><h3>インフラからバックエンドリード、テックリードへ</h3><p>クリーンアーキテクチャ・自動テスト・CI/CDによる開発体制の整備、決済・SSO（SAML）・監査ログの設計と実装、MCPサーバー開発を担当。一次面接50回以上、エンジニア4名の採用に関与しました。</p></li>
<li><p class="focus-kicker">前職・Web系企業 · 2年</p><h3>フロントエンドのチームリーダー</h3><p>技術選定から保守まで担当。React・Next.js・Vue3の導入、CypressによるE2EテストのCI組み込み、メンバーの技術教育を進めました。</p></li>
<li><p class="focus-kicker">SIer · 4年</p><h3>営業・システム開発</h3><p>営業と、詳細設計・実装・テストを担当しました。</p></li></ol>''', 'career-history') + section('主に使ってきた技術', '''<dl class="focus-facts"><div><dt>開発</dt><dd>Python・TypeScript（各5年） / Django・FastAPI・FastMCP / Vue.js・React・Next.js</dd></div><div><dt>基盤・運用</dt><dd>PostgreSQL・BigQuery / Google Cloud・AWS / Docker・GitHub Actions</dd></div><div><dt>AI活用</dt><dd>Claude Code・Codex・Cursor / 開発フローの設計・MCPサーバー開発</dd></div></dl>''', 'tech-stack') + section('採用・業務委託をご検討の方へ', '''<p>正社員・業務委託・技術顧問のご相談をお受けしています。職務経歴書は、ご連絡いただいた方へお送りします。</p><div class="editorial-actions">''' + link('採用・業務委託を相談する', '/contact/?type=recruit#contact-form', True) + link('実績を見る', '/works/') + '''</div>''', 'career')


def services(source):
    return intro('依頼できること', 'Web開発、チームへのAI導入、製品PRを中心にお受けしています。') + section('Webサービス・MCPサーバーの開発', '''<p>要件整理から設計・実装・運用まで。フロントエンド、バックエンド、クラウドを横断して担当します。既存製品をAIから使えるMCPサーバーの企画・開発にも対応します。</p><div class="editorial-actions">''' + link('開発を相談する', '/contact/?type=web#contact-form') + link('開発の実績を見る', '/works/#work-case-1') + '''</div>''', 'web-development') + section('チームへのAI導入', '''<p>AIツールの選定・導入、開発フローの設計、社内勉強会、導入後の定着まで支援します。AIを入れた後の品質や、チーム内での使い方を整えたい場合もご相談ください。</p><div class="editorial-actions">''' + link('AI導入を相談する', '/contact/?type=ai#contact-form') + link('導入と改善結果を見る', '/works/#work-case-0') + '''</div>''', 'ai-adoption') + section('製品PR・動画制作', '''<p>AIツールや開発者向けサービスを実際に使い、YouTube本編・ショート・Xで紹介します。制作例、視聴者データ、概算料金はPRページで確認できます。</p>''' + link('制作例と料金を見る', '/media/') , 'product-pr') + section('登壇・動画編集', '''<div class="focus-two-col"><article><h3>技術登壇・社内勉強会</h3><p>AI駆動開発、MCP、動画制作の自動化など、実際に運用している事例をお話しします。</p>''' + link('登壇実績・対応形式を見る', '/talks/') + '''</article><article id="video-editing"><h3>教育・ビジネス系の動画編集</h3><p>カット、テロップ、効果音などの一般的な編集に対応します。モーショングラフィックスなどの高度な演出は対象外です。</p>''' + link('動画編集を相談する', '/contact/?type=video#contact-form') + '''</article></div>''') + invitation('内容が固まる前でも、ご相談ください。', '対応範囲・進め方・費用を確認してご提案します。お見積もりは無料です。')


def media(source):
    prices = str(source.select_one('#ratecard .price-examples'))
    basis = escape(source.select_one('#ratecard .ratecard-basis').get_text(' ', strip=True))
    stats = json.loads((PROJECT / 'canvas/v3/youtube-stats.json').read_text())
    stats_date = stats['date'].split('-')
    stamp = f'{stats_date[0]}年{int(stats_date[1])}月{int(stats_date[2])}日'
    return intro('製品PR・動画制作', 'AIツールや開発者向けサービスを、実際に使ってエンジニアへ紹介します。') + section('Notta Memo Proのタイアップ動画', '''<div class="focus-pr-example"><a href="https://youtu.be/FsA8gaup0w4" target="_blank" rel="noopener noreferrer" aria-label="Notta Memo ProのPR動画をYouTubeで見る"><img src="/thumb-FsA8gaup0w4.webp" width="640" height="360" alt="制作したNotta Memo Pro紹介動画のサムネイル"></a><div><p>AIボイスレコーダーの予約販売開始に合わせて制作。録音・AI要約から、議事録作成とGoogleカレンダーへの登録までを実演しました。</p><p class="focus-note">担当：実機検証、構成・スライド、撮影・編集、サムネイル、公開・X告知。2026年9月28日公開。</p>''' + link('制作した動画を見る', 'https://youtu.be/FsA8gaup0w4') + '''</div></div>''', 'pr-works') + section('視聴者とチャンネル', f'''<p>Claude Codeを中心にAI駆動開発を扱う「まさやん【AIギルドch】」です。AIを開発へ取り入れたいエンジニアを中心にご覧いただいています。</p><dl class="focus-metrics"><div><dt>チャンネル登録者</dt><dd>{stats['subs']:,}人</dd></div><div><dt>本編1本あたりの平均再生数</dt><dd>911回</dd></div></dl><p class="focus-note">登録者は{stamp}時点。平均再生数は2026年9月24日時点の直近90日、本編（3分超の動画）36本を対象とした実績です。</p>''' + link('チャンネルで動画を見る', 'https://www.youtube.com/@masayan-ai-hack'), 'videos') + section('制作費の目安', prices + f'''<p class="focus-note">{basis}</p><p>本編・ショート・Xを組み合わせ、明細つきの概算見積書を作れます。Xのみの製品PR、二次利用・撮り直しは個別にお見積もりします。</p><div class="editorial-actions">''' + link('料金を見積もる', '/pricing/', True) + link('PRを相談する', '/contact/?type=pr#contact-form') + '''</div>''', 'ratecard') + '''<div class="editorial-shell focus-secondary"><p>対談・共同企画もお受けしています。''' + '<a href="/contact/?type=pr#contact-form">企画を相談する</a>' + '''</p><p>動画をご覧の方へ：<a href="/membership/">メンバーシップについて</a></p></div>'''


def talks(source):
    records = []
    for item in source.select('#talks .talk'):
        title = item.select_one('a.talk-title')
        deck = item.select_one('iframe')
        records.append(f'''<article class="focus-talk"><p class="focus-kicker">{escape(item.select_one('.d').get_text(' ', strip=True))} · {escape(item.select_one('.ev').get_text(' ', strip=True))}</p><h3>{escape(title.get_text(' ', strip=True))}</h3><div class="editorial-actions">{link('イベントを見る', title['href'])}{link('スライドを見る', deck['src'])}</div></article>''')
    return intro('技術登壇', '実務で使っているAI開発・MCP・動画制作の仕組みをお話しします。') + section('登壇実績', ''.join(records), 'talks') + section('お話しできるテーマ・形式', '''<p>AI駆動開発のチーム導入、MCPサーバーの開発、YouTube運営・動画制作の自動化。LT（5〜15分）からセッション（30〜45分）、社内勉強会に対応します。オンライン・会場のどちらも可能です。</p>''', 'talk-request') + invitation('登壇のご相談', 'イベント名・日時・形式・持ち時間を、決まっている範囲でお知らせください。', '/contact/?type=talk#contact-form', '登壇を相談する')


def membership(source):
    return intro('メンバーシップ', 'YouTubeで発信しているAI活用の内容を、さらに詳しく知りたい方へ。') + section('特典・加入方法', '''<p>月額390円からの3ランクです。メンバー限定の投稿・動画・Shortsに加え、上位ランクではAI活用のドキュメントやソースコードを配布します。いつでも解約できます。</p><div class="editorial-actions">''' + link('特典・各ランクの詳細を見る', 'https://masayan-ai-tech-ch.pages.dev/membership/', True) + link('YouTubeで加入する', 'https://www.youtube.com/@masayan-ai-hack/join') + '''</div>''')


def contact(source):
    form_section = source.select_one('#contact-form')
    form_section.select_one('h2').decompose()
    for paragraph in form_section.select('.sec-lead, .contact-form-card > .lead'):
        paragraph.decompose()
    script = form_section.find_next_sibling('script')
    return intro('仕事・採用のご相談', '内容・時期・ご予算など、分かる範囲でお知らせください。通常2営業日以内に返信します。') + str(form_section) + (str(script) if script else '') + section('ご相談から着手まで', '''<p>内容を確認し、必要に応じてオンラインでヒアリングします。進め方・期間・費用をご提案し、合意してから着手します。お見積もりは無料です。</p><p class="focus-note">メールでのご連絡をご希望の場合：<a href="mailto:contact@msyn.me">contact@msyn.me</a></p>''', 'flow')


def page_content(page, source):
    if page == 'pricing':
        # Preserve every quote DOM contract, including historical link restoration.
        return None
    body = home() if not page else globals()[page](source)
    return f'<main id="main-content" tabindex="-1" class="focus-main">{body}</main>'
