"""Build a local-only design study without changing the public export.

Run from any directory. The generated pages use the existing asset files and
pricing modules through serve.py, keeping the original URL paths intact.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import html
import json
import shutil
from monochrome import neutralize_css, neutralize_paint

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
PUBLIC = PROJECT / 'canvas/v3/site'
OUT = PROJECT / 'output/editorial-concept/site'
PAGES = ['', 'profile', 'works', 'services', 'media', 'talks', 'membership', 'pricing', 'contact']


def header(current):
    items = [('works', '実績'), ('services', 'できること'), ('profile', 'プロフィール'), ('media', 'YouTube・PR')]
    links = ''.join(f'<a href="/{slug}/"' + (' aria-current="page"' if slug == current else '') + f'>{name}</a>' for slug, name in items)
    return f'''<header class="editorial-header"><div class="editorial-shell editorial-header-inner">
<a class="editorial-brand" href="/">Miyabiya Studio<span>Masaya Nishigaki</span></a>
<nav class="editorial-nav" aria-label="メインメニュー">{links}</nav>
<a class="editorial-contact-link" href="/contact/#contact-form">仕事の相談 <span aria-hidden="true">↗</span></a>
</div></header>'''


def footer():
    return '''<footer class="editorial-footer"><div class="editorial-shell"><div class="editorial-footer-main">
<div><a class="editorial-brand" href="/">Miyabiya Studio<span>Masaya Nishigaki</span></a><p>Web開発・AI導入支援・動画制作・技術登壇</p></div>
<nav aria-label="関連ページ"><a href="/pricing/">PR動画の見積もり</a><a href="/talks/">技術登壇</a><a href="/membership/">メンバーシップ</a><a href="/contact/">お問い合わせ</a></nav>
<nav aria-label="SNS・外部サイト"><a href="https://www.youtube.com/@masayan-ai-hack" target="_blank" rel="noopener noreferrer">YouTube ↗</a><a href="https://x.com/masayan_ai_hack" target="_blank" rel="noopener noreferrer">X ↗</a><a href="https://github.com/masayan1126" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="https://zenn.dev/masayan1126" target="_blank" rel="noopener noreferrer">Zenn ↗</a><a href="https://www.instagram.com/miyabiya1126/" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="https://substack.com/@masayan1126" target="_blank" rel="noopener noreferrer">Substack ↗</a></nav>
</div><p class="editorial-copyright">© 2026 Masaya Nishigaki</p></div></footer>'''


def home():
    return '''<main id="main-content" tabindex="-1"><section class="editorial-intro editorial-shell" aria-labelledby="editorial-title">
<div><p class="editorial-byline">Webエンジニア・テックリード</p><h1 id="editorial-title">Web開発とAI活用を、<br>仕事の現場へ。</h1></div>
<div class="editorial-intro-copy"><p class="editorial-name">Masaya Nishigaki</p><p>Webサービスの開発と、チームへのAI導入をお手伝いしています。YouTubeでの製品PRや技術登壇もお受けしています。</p><div class="editorial-actions"><a class="editorial-button" href="/contact/#contact-form">仕事を相談する <span aria-hidden="true">↗</span></a><a class="editorial-text-link" href="/pricing/">PR動画の料金を見積もる</a></div></div>
</section>
<section class="editorial-shell editorial-projects" id="selected-work" aria-labelledby="selected-title"><div class="editorial-section-heading"><h2 id="selected-title">制作・発信したもの</h2><a class="editorial-text-link" href="/works/">実績・成果をすべて見る</a></div>
<div class="editorial-project-grid">
<article class="editorial-project"><a class="editorial-project-image" href="/media/#pr-works" aria-label="Notta Memo ProのPR動画制作を見る"><img src="/thumb-FsA8gaup0w4.webp" width="640" height="360" alt="制作したNotta Memo Pro紹介動画のサムネイル" fetchpriority="high"></a><div class="editorial-project-meta"><span>製品PR・動画制作</span><span>YouTube</span></div><h3><a href="/media/#pr-works">Notta Memo Proを、実際に使って紹介</a></h3><p>製品を試し、紹介する構成から撮影・編集・公開まで担当しました。</p></article>
<article class="editorial-project"><a class="editorial-project-image editorial-extension-art" href="/works/#work-case-4" aria-label="公開した5本のChrome拡張機能を見る"><div class="editorial-extension-icons"><img src="/editorial-assets/markdown-preview.jpg" width="128" height="128" alt="Markdown Preview"><img src="/editorial-assets/copy-tab-anything.jpg" width="128" height="128" alt="Copy Tab Anything"><img src="/editorial-assets/web-annotator.jpg" width="128" height="128" alt="Web Annotator"></div><p>毎日の「ちょっと面倒」を、<br>ブラウザから減らす。</p><span>Chrome Extensions</span></a><div class="editorial-project-meta"><span>企画・開発・公開</span><span>Chrome拡張機能</span></div><h3><a href="/works/#work-case-4">自分の困りごとから、5本の拡張機能を公開</a></h3><p>Markdownの確認、タブのコピー、ページへの書き込みなどを使いやすくしました。</p></article>
<article class="editorial-project"><a class="editorial-project-image editorial-talk-art" href="/talks/#talks" aria-label="Claude Codeと回すYouTube運営の登壇を見る"><span>ClaudeCodeMeetupOsaka · 2026.06</span><p>Claude Code と回す、<br>YouTube運営のPDCA</p><div><span>企画</span><span aria-hidden="true">→</span><span>制作</span><span aria-hidden="true">→</span><span>公開</span><span aria-hidden="true">→</span><span>振り返り</span></div></a><div class="editorial-project-meta"><span>技術登壇</span><span>AI活用・自動化</span></div><h3><a href="/talks/#talks">YouTube運営で使っているAIの仕組みを共有</a></h3><p>企画から公開後の振り返りまで、実際の運用を題材にお話ししました。</p></article>
<article class="editorial-project"><a class="editorial-project-image" href="https://youtu.be/fyblZf3oIUo" target="_blank" rel="noopener noreferrer" aria-label="OpenAI DevDayの紹介動画をYouTubeで見る（新しいタブ）"><img src="/latest-thumb-fyblZf3oIUo.webp" width="640" height="360" alt="OpenAI DevDay 2026の新機能を紹介する動画のサムネイル" loading="lazy"></a><div class="editorial-project-meta"><span>検証・解説動画</span><span>YouTube</span></div><h3><a href="https://youtu.be/fyblZf3oIUo" target="_blank" rel="noopener noreferrer">AIの新機能を試し、使い方を動画で伝える</a></h3><p>AIツールと開発の話題を、エンジニアに向けて発信しています。</p></article>
</div></section>
<section class="editorial-shell editorial-business" id="business-results" aria-labelledby="business-title"><div class="editorial-section-heading"><h2 id="business-title">開発の現場で取り組んだこと</h2></div><div class="editorial-business-grid">
<article><p class="editorial-small-label">チームへのAI導入</p><h3>AIを使う開発の流れを、<br>チームに定着させる。</h3><p class="editorial-result">開発工数 <strong>50〜75<span>%削減</span></strong></p><p>設計・実装・コードレビューの工数を、AI導入前と比較した実績です。課題の登録から開発を進める流れと、生成役・評価役のAIを組み合わせる仕組みを設計しました。</p><a class="editorial-text-link" href="/works/#work-case-0">取り組みと成果を見る</a></article>
<article><p class="editorial-small-label">MCPサーバーの企画・開発</p><h3>自社製品を、<br>AIから使えるようにする。</h3><p>製品の操作をAIから呼び出せるMCPサーバーを企画・開発しました。社内での導入と勉強会も担当しています。</p><a class="editorial-text-link" href="/works/#work-case-1">担当したことを見る</a></article>
</div></section>
<section class="editorial-shell editorial-services" id="request-work" aria-labelledby="request-title"><div class="editorial-section-heading"><h2 id="request-title">お手伝いできること</h2><a class="editorial-text-link" href="/services/">対応範囲を詳しく見る</a></div><div class="editorial-service-grid">
<article><h3><a href="/services/#web-development">Webサービス開発</a></h3><p>要件整理から設計・実装・運用まで。</p></article><article><h3><a href="/services/#ai-adoption">AI導入支援</a></h3><p>ツールの導入、勉強会、業務への組み込み。</p></article><article><h3><a href="/media/">製品PR・動画制作</a></h3><p>実際に使って伝える、YouTubeとショート。</p></article><article><h3><a href="/talks/">技術登壇・社内勉強会</a></h3><p>開発や動画制作での、実務のAI活用。</p></article><article><h3><a href="/services/#video-editing">動画編集</a></h3><p>教育・ビジネス系の動画を、公開できる形に。</p></article>
</div></section>
<section class="editorial-shell editorial-about" id="about-me" aria-labelledby="about-title"><div class="editorial-portrait"><img src="/hero-photo.webp" width="800" height="1000" alt="Masaya Nishigaki" loading="lazy"></div><div><p class="editorial-small-label">プロフィール</p><h2 id="about-title">Masaya Nishigaki</h2><p>Webエンジニア・テックリードとして、開発とチームへのAI導入に取り組んでいます。</p><p>SIerからWeb系企業へ移り、フロントエンド・バックエンド・インフラを経験してきました。個人ではYouTubeを運営し、技術登壇やChrome拡張機能の開発も続けています。</p><a class="editorial-text-link" href="/profile/">プロフィール・経歴を見る</a></div></section>
<section class="editorial-shell editorial-invitation" aria-labelledby="invitation-title"><div><h2 id="invitation-title">一緒につくりたいことを、<br>お聞かせください。</h2><p>開発、AI活用、製品PR、登壇。ご相談の段階からお受けします。</p></div><div class="editorial-invitation-actions"><a class="editorial-button" href="/contact/#contact-form">仕事を相談する <span aria-hidden="true">↗</span></a><a class="editorial-text-link" href="/pricing/">PR動画の料金を見積もる</a></div></section></main>'''


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ('editorial.css', 'editorial.mjs'):
        shutil.copyfile(HERE / name, OUT / name)
    asset_dir = OUT / 'editorial-assets'
    asset_dir.mkdir(exist_ok=True)
    for name in ('markdown-preview.jpg', 'copy-tab-anything.jpg', 'web-annotator.jpg'):
        shutil.copyfile(PROJECT / 'canvas/v3/works-images/extensions' / name, asset_dir / name)
    checks = []
    for page in PAGES:
        path = Path(page) / 'index.html'
        original = (PUBLIC / path).read_text()
        soup = BeautifulSoup(original, 'html.parser')
        soup.body['class'] = list(dict.fromkeys(soup.body.get('class', []) + ['editorial']))
        soup.select_one('.v3-head').replace_with(BeautifulSoup(header(page), 'html.parser'))
        soup.select_one('.v3-footer').replace_with(BeautifulSoup(footer(), 'html.parser'))
        for art in list(soup.select('.detail-page-art')):
            art.decompose()
        for intro in soup.select('.detail-page-intro'):
            intro['class'] = [name for name in intro.get('class', []) if name != 'detail-page-intro']
        # Analytics and the immersive hero belong to the existing public site.
        for script in list(soup.select('script')):
            if 'googletagmanager' in script.get('src', '') or 'gtag(' in script.get_text():
                script.decompose()
            elif not page and '/home-assets/' in script.get('src', ''):
                script.decompose()
        if not page:
            soup.select_one('main').replace_with(BeautifulSoup(home(), 'html.parser'))
            for link in list(soup.head.select('link[href^="/home-assets/"]')):
                link.decompose()
        # Keep form validation and quote handoff, but the local study never sends.
        for form in soup.select('form#inquiry-form'):
            form['action'] = '/__preview/contact'
            form['data-editorial-preview'] = 'true'
        # Local neutral copies cover every interaction state without changing
        # the public palette, pricing data or calculation/PDF modules.
        for link in soup.select('link[rel="stylesheet"]'):
            href = link.get('href', '')
            source = (PUBLIC / href.lstrip('/')).resolve()
            if not source.is_relative_to(PUBLIC.resolve()) or not source.is_file():
                raise ValueError(f'Unexpected stylesheet: {href}')
            css = neutralize_css(source.read_text())
            name = f'neutral-{hashlib.sha256(css.encode()).hexdigest()[:12]}.css'
            (asset_dir / name).write_text(css)
            link['href'] = '/editorial-assets/' + name
        for style in soup.select('style'):
            style.string = neutralize_css(style.get_text())
        for element in soup.select('[style]'):
            element['style'] = neutralize_css(element['style'])
        for element in soup.select('svg, svg *'):
            for attribute in ('fill', 'stroke', 'stop-color', 'flood-color', 'lighting-color'):
                if element.has_attr(attribute):
                    element[attribute] = neutralize_paint(element[attribute])
        for meta in soup.select('meta[name="theme-color"]'):
            meta['content'] = '#ffffff'
        for meta in list(soup.head.select('meta[name="robots"]')):
            meta.decompose()
        soup.head.append(soup.new_tag('meta', attrs={'name': 'robots', 'content': 'noindex,nofollow'}))
        soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '/editorial.css'}))
        soup.head.append(soup.new_tag('script', attrs={'type': 'module', 'src': '/editorial.mjs'}))
        result = str(soup).replace('https://studio.msyn.me/api/contact', '/__preview/contact')
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result)
        before = BeautifulSoup(original, 'html.parser').select_one('#pricing-data')
        after = soup.select_one('#pricing-data')
        if before:
            assert before.get_text() == after.get_text(), 'Pricing data changed in preview'
        checks.append({'path': '/' + (page + '/' if page else ''), 'source_sha256': hashlib.sha256(original.encode()).hexdigest(), 'pricing_data_unchanged': before is None or before.get_text() == after.get_text()})
    manifest = {'preview_url': 'http://127.0.0.1:8777/', 'pages': checks, 'public_export_modified': False, 'forms_send': False}
    (OUT.parent / 'build.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(checks)} local preview pages: {OUT}')


if __name__ == '__main__':
    build()
