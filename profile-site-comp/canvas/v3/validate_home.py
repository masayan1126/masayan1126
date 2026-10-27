"""Validate the complete site export and its preserved content contracts."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import subprocess
import os
import sys
from collections import Counter
from urllib.parse import urlsplit, unquote

import youtube_stats
import copy_updates

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
SITE = Path(os.environ.get('STUDIO_SITE_ROOT', ROOT / 'site'))
if 'STUDIO_SITE_ROOT' not in os.environ and 'compact-local' in (SITE / 'index.html').read_text():
    from validate_public import validate
    validate(SITE)
    sys.exit(0)
BASELINE = PROJECT / 'output/before-full-site-20260906'
YOUTUBE = youtube_stats.load(fetch=False)
ROUTES = ['', 'profile', 'works', 'services', 'media', 'talks', 'membership', 'contact', 'pricing']

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.text = [], [], []
        self.h1 = self.main = 0
        self.incomplete_actions = []
        self.in_body = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get('class', '').split())
        if tag in ('a', 'button') and classes.intersection({'v3-primary','v3-secondary','btn-p','btn-g','btn-w','business-cta'}):
            self.incomplete_actions.append(attrs.get('class'))
        if 'site-action' in classes and len(classes.intersection({'site-action-primary','site-action-secondary'})) != 1:
            self.incomplete_actions.append(attrs.get('class'))
        if tag == 'body': self.in_body = True
        if tag == 'h1': self.h1 += 1
        if tag == 'main': self.main += 1
        if attrs.get('id'): self.ids.append(attrs['id'])
        for key in ('src', 'href', 'data-hdr', 'data-environment'):
            value = attrs.get(key, '')
            if value.startswith(('/', '#')) and not value.startswith('//'): self.refs.append(value)
    def handle_endtag(self, tag):
        if tag == 'body': self.in_body = False
    def handle_data(self, value):
        if self.in_body: self.text.append(value)

def content(source):
    # Navigation and action labels carry no new claims; compare the underlying prose.
    source = re.sub(r'<div class="(?:page-actions|case-request)"[^>]*>.*?</div>', '', source, flags=re.S)
    source = re.sub(r'<nav class="page-index"[^>]*>.*?</nav>', '', source, flags=re.S)
    # Decorative business artwork is excluded from the prose contract.
    source = re.sub(r'<div class="business-art" aria-hidden="true">.*?</div>', '', source, flags=re.S)
    source = re.sub(r'<(script|style|header|footer)\b[^>]*>.*?</\1>', '', source, flags=re.S)
    source = re.sub(r'<section class="(?:v3-hero|immersive-hero)"[^>]*>.*?</section>', '', source, flags=re.S)
    source = re.sub(r'<a class="skip-link".*?</a>', '', source, flags=re.S)
    page = Page(); page.feed(source)
    return re.sub(r'\s+', ' ', ''.join(page.text)).strip()

def element(source, ident):
    match = re.search(r'<([a-z][\w-]*)\b[^>]*\bid="'+re.escape(ident)+r'"[^>]*>', source)
    assert match, ident
    depth = 1
    for token in re.finditer(r'</?'+match[1]+r'\b[^>]*>', source[match.end():]):
        depth += -1 if token[0].startswith('</') else 1
        if depth == 0:
            return source[match.start():match.end()+token.end()]
    raise AssertionError(ident)


def target(ref, current):
    path = unquote(urlsplit(ref).path)
    item = (SITE / path.lstrip('/')) if path.startswith('/') else current.parent / path
    if not path: item = current
    if item.is_dir(): item /= 'index.html'
    return item

# Pages rebuilt after the baseline: (facts the page must carry, links it must have, headings in order).
RESTRUCTURED = {
    # 2026-10-24: media combinations, unknown fees and optional consultation.
    'pricing': (['7つの組み合わせを比較する', 'YouTube本編1本', 'ショート1本', 'X投稿1回',
                 '追加修正・二次利用などを相談する', '要相談の項目の金額は、小計に含まれていません。',
                 '自社サイト・SNS・広告などで二次利用したい', '要相談'],
                ['/media/'], ['id="comparison-heading"', 'id="media-selection"', 'id="selected-scope"']),
    # Request decisions precede general videos: offers → PR proof → audience → production.
    'media': (['チャンネルについて', '視聴者データ', '代表的な動画', '最新の動画', 'PR動画の制作実績', 'Notta Memo Pro',
               'ご依頼いただける内容と料金', 'タイアップ動画', 'Xでの紹介', '対談・コラボ企画', 'PR動画の料金',
               'YouTube横動画（本編動画）：2回まで料金内。3回目以降は1回5,500円（税込）です。',
               'ショート動画：2回まで料金内。3回目以降は1回3,300円（税込）です。',
               'X：2回まで料金内。3回目以降は1回1,000円（税込）です。', 'メンバーシップについて',
               f"{YOUTUBE['subs']:,}", f'{youtube_stats.MEMBERS}人'],
              ['/pricing/', '/contact/?type=pr#contact-form', '/membership/', 'https://youtu.be/FsA8gaup0w4'],
              ['id="pr"', 'id="pr-works"', 'id="videos"', 'id="channel-story"', 'メンバーシップについて']),
    # 2026-09-30: every business card from the top page, with the scope and tags only this page carries.
    'services': (['AIエージェントの設計・ハーネス構築', 'Python / TypeScript', 'モーショングラフィックスなどの高度な演出は対象外です。',
                  'お見積もりは無料です。'],
                 ['/contact/?type=web#contact-form', '/contact/?type=ai#contact-form', '/pricing/', '/contact/?type=talk#contact-form',
                  '/contact/?type=video#contact-form', '/media/', '/talks/'],
                 ['id="web-development"', 'id="ai-adoption"', 'id="product-pr"', 'id="tech-talks"', 'id="video-editing"']),
}

pages = {}
for key in ROUTES:
    path = SITE / key / 'index.html'
    source = path.read_text()
    page = Page(); page.feed(source)
    assert page.h1 == page.main == 1, (key, page.h1, page.main)
    assert not page.incomplete_actions, (key, 'Incomplete action components', page.incomplete_actions)
    assert len(set(page.ids)) == len(page.ids), ('Duplicate IDs', key)
    assert 'main-content' in page.ids, key
    assert '127.0.0.1' not in source and '%%' not in source, key
    for ref in page.refs:
        resolved = target(ref, path)
        assert resolved.is_file(), (key, ref)
        anchor = unquote(urlsplit(ref).fragment)
        if anchor and resolved.suffix == '.html':
            destination = Page(); destination.feed(resolved.read_text())
            assert anchor in destination.ids, (key, ref, 'Missing anchor')
    assert not re.search(r'<(?:p|span) class="(?:lbl|tag|eyebrow)">(?:本業|個人|[0-9]{2} / (?:本業|個人)|SELECTED WORKS|CAREER JOURNEY)</', source), key
    assert 'data-label="' not in source and 'MIYABIYA STUDIO / 01' not in source, key
    preserved = None
    if BASELINE.exists() and key not in RESTRUCTURED:
        original = (BASELINE / 'site' / key / 'index.html').read_text()
        if key == '':
            approved = (ROOT / 'test-fixtures/approved-works-story.html').read_text().strip()
            approved = approved.replace('{{works}}', '/works/').replace('{{media}}', '/media/')
            old_works = re.search(r'<section class="sec home-overview">.*?</section>', original, re.S)
            assert old_works and 'home-work-grid' in old_works.group(), 'Missing original works section'
            original = original[:old_works.start()] + approved + original[old_works.end():]
            approved_career = (ROOT / 'test-fixtures/approved-career-chapters.html').read_text().strip().replace('{{profile}}', '/profile/')
            start = original.index('<div class="sec" id="career-history"')
            end = original.index('<section class="v3-contact"', start)
            original = original[:start] + approved_career + original[end:]
        # User-provided career durations, newest first.
        original = original.replace('<p class="st">Web系企業 (現職)</p>', '<p class="st">Web系企業 (現職) · 3年</p>')
        original = original.replace('<p class="st">Web系企業</p>', '<p class="st">Web系企業 · 2年</p>')
        original = original.replace('<p class="st">SIer</p>', '<p class="st">SIer · 4年</p>')
        # User-selected titles for the two professional case studies.
        original = original.replace('AI駆動開発環境の構築・運用', 'AI駆動開発環境の構築・チーム展開')
        original = original.replace('MCPサーバーの開発とプロジェクト推進', 'MCPサーバーの企画・開発と成果創出')
        original = original.replace('実務でMCPサーバーの企画・開発と成果創出を担当しています。', '実務でMCPサーバーの開発とプロジェクト推進を担当しています。')
        # Approved 2026-09-22 Studio snapshot; preserve every other content claim.
        original = original.replace('3,350', '3,462').replace('30人以上', '37人')
        # Approved removal of category labels; keep all substantive copy intact.
        original = re.sub(r'<p class="lbl">(?:本業|個人)</p>', '', original)
        # Layout unification changes presentation and excerpts, while preserving
        # the detailed records and the untouched destination-page content.
        comparable = source
        if key == '':
            original = original.replace('プロダクト開発・AI導入支援、製品PR、技術登壇のご相談をお受けします。', 'Webサービス開発、AI導入支援、製品PR、技術登壇のご相談をお受けします。')
            approved_split = '<a><h3>Webサービス開発</h3><p>要件整理から設計・実装・運用まで、一貫して対応します。</p><span>Webサービス開発の詳細を見る →</span></a><a><h3>AI導入支援</h3><p>ツールの導入から現場への定着までを支援します。</p><span>AI導入支援の詳細を見る →</span></a>'
            original, count = re.subn(r'<a class="card work home-summary-card" href="/services/">.*?</a>', approved_split, original, count=1, flags=re.S)
            assert count == 1
        if key == 'works':
            original = original.replace(element(original, 'works'), (ROOT / 'test-fixtures/approved-works-detail.html').read_text())
        if key == 'profile':
            # Approved 2026-09-24: photo, name and role added above the existing lead.
            note = re.search(r'<p class="name-note">.*?</ul>', source, re.S).group()
            original = original.replace('<p class="hero-lead">', '<p class="profile-name">Masaya Nishigaki</p><p class="profile-role">Webエンジニア・テックリード</p>' + note + '<p class="hero-lead">', 1)
            old_career = element(original, 'career-history')
            remaining = re.sub(r'<h2.*?</ul>', '<div class="career">', old_career, count=1, flags=re.S).replace('id="career-history"', 'id="career-details"')
            # Approved 2026-09-24: technology stack section between the career and its details.
            original = original.replace(old_career, (ROOT / 'test-fixtures/approved-career-detail.html').read_text()+element(source, 'tech-stack')+remaining)
        if key in ('media', 'talks'):
            comparable = re.sub(r'<section class="works-story detail-feature".*?</section>', '', comparable, flags=re.S)
        # User-requested label change; all factual descriptions stay intact.
        original = original.replace('>実績<', '>実績・成果<').replace('すべての実績を見る', 'すべての実績・成果を見る')
        # Approved 2026-09-24: comparison basis for the reduction rate.
        original = original.replace('削減</p><p class="support">商談用デモ', '削減<small class="result-basis">（AI導入前の実績工数と比較）</small></p><p class="support">商談用デモ')
        # Approved 2026-09-24: video editing added as a fifth business item.
        if key == '':
            original = original.replace('技術登壇のご相談をお受けします。', '技術登壇、動画編集のご相談をお受けします。', 1)
            assert '登壇の詳細を見る →</span></a>' in original
            original = original.replace('登壇の詳細を見る →</span></a>', '登壇の詳細を見る →</span></a><a><h3>動画編集</h3><p>教育系・ビジネス系の動画に、テロップや効果音を入れて仕上げます。</p><span>動画編集の詳細を見る →</span></a>', 1)
        if key == 'services':
            video = re.search(r'<div class="group">\s*<div class="group-h">(?:(?!<div class="group">).)*?id="video-editing".*?</div></div>\s*</div>', source, re.S).group()
            assert '定着フォロー</span></div>' in original
            original = original.replace('定着フォロー</span></div>', '定着フォロー</span></div> ' + video, 1)
            original = original.replace('製品PR・登壇まで対応します。', '製品PR・登壇・動画編集まで対応します。', 1)
        # Approved 2026-09-24: audience data block before the PR group on the media page.
        if key == 'media':
            kit = re.search(r'<div class="mediakit" id="mediakit">.*?</div></div></div>', source, re.S).group()
            assert '<div class="group" id="pr">' in original
            original = original.replace('<div class="group" id="pr">', kit + '<div class="group" id="pr">', 1)
        # Approved 2026-09-24: the talk title links to the event page; the arrow link opens the slides
        # (works page) or is replaced by the embedded slides (talks page).
        if key in ('works', 'talks'):
            label = 'スライド' if key == 'works' else ''
            original, count = re.subn(r'(<a class="lk" href="https://(?:aiau|aid)\.connpass\.com/event/\d+/"[^>]*>)イベントページ', r'\g<1>' + label, original)
            assert count == 2, (key, count)
        # Approved 2026-09-25: the services page is named 事業内容 and uses Webサービス開発 throughout.
        if key == 'services':
            original = re.sub(r'(<h1>).*?(</h1>)', r'\g<1>事業内容\g<2>', original, count=1, flags=re.S)
            original = re.sub(r'(</h1>\s*<p>).*?(</p>)', r'\g<1>ご依頼いただける内容と、それぞれの対応範囲をご紹介します。\g<2>', original, count=1, flags=re.S)
            original = original.replace('AI駆動のWebプロダクト開発', 'AI駆動のWebサービス開発')
        original = original.replace('プロダクト開発・AI導入支援', 'Webサービス開発・AI導入支援')
        # Approved 2026-09-25: reply time and the contact form on the contact page.
        if key == 'contact':
            assert 'メールのいずれかでお送りください。' in original
            original = original.replace('メールのいずれかでお送りください。', 'メールのいずれかでお送りください。通常2営業日以内に返信します。', 1)
            original = original.replace('</main>', element(source, 'contact-form') + '</main>', 1)
        # Approved 2026-09-25: latest videos (refreshed at build time) before the career section on the home page.
        if key == '':
            latest = element(source, 'latest')
            marker = '<section class="career-chapters"'
            assert marker in original
            original = original.replace(marker, latest + marker, 1)
        # Final copy fixes before release (2026-09-25).
        original = copy_updates.apply(original)
        if key == 'services':
            original = re.sub(r'<h2 class="sec-h">事業内容</h2>', '', original, count=1)
        # YouTube figures are refreshed at build time from the approved snapshot values.
        original = youtube_stats.apply(original, YOUTUBE)
        # Approved 2026-09-26: business cards rewritten as pain → offer → proof → action (checked below).
        if key == '':
            original = re.sub(r'<section class="sec alt home-overview">.*?</section>', '', original, count=1, flags=re.S)
            comparable = comparable.replace(element(comparable, 'business-gallery'), '')
        if key == 'contact':
            original = original.replace('ご依頼の流れと、メール・SNSの連絡先をご案内します。',
                'ご相談内容をフォームからお送りいただけます。通常2営業日以内に返信します。メール・SNSの連絡先と、ご依頼の流れもご案内しています。')
            original = original.replace('まずはお気軽にご相談ください', 'メール・SNSからもご相談いただけます')
            original = original.replace('XのDMかメールで、相談したい内容をお送りください。', 'フォーム・メール・SNSのいずれかで、相談したい内容をお送りください。')
        if key in ('talks', 'contact'):
            # These two pages deliberately move existing sections. Every prose block
            # must still occur the same number of times; only their order may change.
            def blocks(value):
                value = re.sub(r'<(script|style|header|footer|nav)\b[^>]*>.*?</\1>', '', value, flags=re.S)
                return Counter(re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', part)) for part in re.findall(r'<(?:h[1-6]|p|li)\b[^>]*>.*?</(?:h[1-6]|p|li)>', value, flags=re.S))
            preserved = blocks(original) == blocks(comparable)
        else:
            preserved = content(original) == content(comparable)
        assert preserved, ('Content changed', key)
    if key in RESTRUCTURED:
        # Approved 2026-09-30: these pages were rebuilt, so check their order and required facts instead of the baseline text.
        text = content(source)
        required, links, order = RESTRUCTURED[key]
        missing = [item for item in required if item not in text]
        assert not missing, ('Missing on', key, missing)
        for ref in links:
            assert 'href="' + ref + '"' in source, ('Missing link on', key, ref)
        positions = [source.index(h) for h in order]
        assert positions == sorted(positions), ('Section order', key, order)
        preserved = True
    if key == 'media':
        assert 'id="latest"' not in element(source, 'production-method'), 'Latest videos must remain outside production details'
    pages['/' + key + ('/' if key else '')] = {'singleH1AndMain': True, 'uniqueIds': True, 'validReferences': len(page.refs), 'expectedContentPreserved': preserved, 'approvedChange': ['works-story', 'career-chapters'] if key == '' else None}

# The top page is an excerpt of the detail pages: every piece of text in a top-page section must also
# appear on its detail page. Link labels (「詳細を見る」など) are navigation and are not compared.
TOP_TO_DETAIL = {'business-gallery': 'services', 'works-story': 'works', 'latest': 'media', 'career-history': 'profile'}
def text_pieces(html):
    html = re.sub(r'<(script|style|svg)\b.*?</\1>', '', html, flags=re.S)
    html = re.sub(r'<a\b[^>]*>.*?</a>', '', html, flags=re.S)
    html = re.sub(r'<div class="section-foot">.*?</div>', '', html, flags=re.S)
    return [piece for piece in (re.sub(r'\s+', '', part) for part in re.split(r'<[^>]+>', html)) if len(piece) >= 4]
def flat(html):
    return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', re.sub(r'<(script|style|svg)\b.*?</\1>', '', html, flags=re.S)))
top_page = (SITE / 'index.html').read_text()
for section, detail_key in TOP_TO_DETAIL.items():
    detail = flat((SITE / detail_key / 'index.html').read_text())
    extra = [piece for piece in text_pieces(element(top_page, section)) if piece not in detail]
    assert not extra, ('Top page has content missing from its detail page', section, '/' + detail_key + '/', extra)

for css in [*SITE.glob('site-assets/*.css'), *SITE.glob('home-assets/*.css')]:
    for ref in re.findall(r'url\([\'\"]?([^\)\'\"]+)', css.read_text()):
        if not ref.startswith(('data:', 'http:', 'https:')):
            assert target(ref, css).is_file(), (css.name, ref)
for script in [*SITE.glob('site-assets/*.mjs'), *SITE.glob('home-assets/*.mjs')]:
    subprocess.run(['node', '--check', str(script)], check=True, capture_output=True)
pricing = {}
if BASELINE.exists():
    # The media selector is an authorized pricing implementation change (2026-10-24).
    # The owner adopted the existing upper amounts as fixed prices (2026-10-25).
    # Preserve those amounts, tax treatment, inclusion rules, and all archive bytes.
    original = json.loads((BASELINE / 'site/pricing/index.html').read_text().split('<script id="pricing-data" type="application/json">')[1].split('</script>')[0])
    current = json.loads((ROOT / 'pricing-data.json').read_text())
    for item in current['checklistItems']:
        old = next(row for row in original['checklistItems'] if row['id'] == item['id'])
        # Research became optional at the owner's request (2026-10-25).
        pricing[item['id']] = item['min'] == old['max'] and all(item.get(key) == old.get(key) for key in ('max','taxInclusive')) and (item.get('fixed') is False if item['id']=='research' else item.get('fixed') == old.get('fixed'))
    pricing['taxRate'] = current['taxRate'] == original['taxRate']
    pricing['revisionFee'] = current['revisionFee'] == original['revisionFee']
    assert all(pricing.values()), pricing
    rate_files = list((BASELINE / 'site/pricing-rates').glob('*.json'))
    assert rate_files, 'Expected archived pricing versions'
    for old in rate_files:
        assert old.read_bytes() == (SITE / 'pricing-rates' / old.name).read_bytes(), old.name
hero = (ROOT / 'home-3d/immersive/hero.html').read_text()
assert re.sub('<[^>]+>', '', re.search(r'<h1.*?</h1>', hero, re.S).group()).replace('\n', '').strip() == 'AIで「ちゃんと」生産性を上げる'
assert 'enter-studio' not in hero and '作業場に入る' not in hero
runtime = (ROOT / 'home-3d/diorama/video-hero.js').read_text()
assert 'setImmersed' not in runtime and 'enter-studio' not in runtime
home = (SITE / 'index.html').read_text()
business = element(home, 'business-gallery')
assert business.count('class="card work home-summary-card"') == 5
for kind in ('web', 'ai', 'talk', 'video'):
    assert f'href="/contact/?type={kind}#contact-form"' in business
assert 'href="/pricing/"' in business
assert 'href="/services/#video-editing"' in business
assert 'href="/services/#web-development"' in business
assert 'href="/services/#ai-adoption"' in business

# Check the CSS actually linked by the nine pages, including hover/selected rules.
# Pale blue surfaces are disallowed; photos, videos and archived unused assets are outside this rule.
def pale_blue_colors(value):
    colors = []
    for match in re.finditer(r'#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)', value):
        color = match.group()
        if color.startswith('#'):
            digits = color[1:]
            if len(digits) in (3, 4): digits = ''.join(c * 2 for c in digits)
            if len(digits) not in (6, 8): continue
            r, g, b = [int(digits[i:i+2], 16) for i in (0, 2, 4)]
            alpha = int(digits[6:8], 16) / 255 if len(digits) == 8 else 1
        else:
            numbers = re.findall(r'[\d.]+%?', color)
            if len(numbers) < 3: continue
            r, g, b = [float(n[:-1]) * 2.55 if n.endswith('%') else float(n) for n in numbers[:3]]
            alpha = (float(numbers[3][:-1]) / 100 if numbers[3].endswith('%') else float(numbers[3])) if len(numbers) > 3 else 1
        r, g, b = [channel * alpha + 255 * (1 - alpha) for channel in (r, g, b)]
        if alpha > 0 and min(r, g, b) >= 160 and b > r + 2 and b > g:
            colors.append(color)
    return colors

# This static check covers hex/RGB literals. Browser checks also resolve variables and computed colors.
def validate_surface_declarations(label, css):
    for prop, value in re.findall(r'(background(?:-color|-image)?|--(?:site-paper|surface[\w-]*|paper|selection-surface|blue-light|light))\s*:\s*([^;}]+)', css):
        assert not pale_blue_colors(value), ('Pale blue UI surface', label, prop, value)

current_styles = set()
for route in ROUTES:
    source = (SITE / route / 'index.html').read_text()
    for href in re.findall(r'<link[^>]+href="([^"?]+\.css)"', source):
        current_styles.add(target(href, SITE / route / 'index.html'))
    for css in re.findall(r'<style[^>]*>(.*?)</style>', source, re.S):
        validate_surface_declarations(route + ' inline style', css)
    for quote, css in re.findall(r'\bstyle=([\"\'])(.*?)\1', source, re.S):
        validate_surface_declarations(route + ' style attribute', css)
    for svg in re.findall(r'<svg\b.*?</svg>', source, re.S):
        assert not pale_blue_colors(svg), ('Pale blue SVG surface', route, pale_blue_colors(svg))
for sheet in current_styles:
    validate_surface_declarations(sheet.name, sheet.read_text())

report = {'pages': pages, 'pricingSourcePreserved': pricing, 'assetReferencesValid': True, 'neutralSurfaces': {'linkedStylesheets': len(current_styles), 'paleBlueSurfaces': 0}, 'heroHeadline': 'AIで「ちゃんと」生産性を上げる', 'scope': 'Local generated site; not deployed'}
out = PROJECT / 'output/site-renewal-validation.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
