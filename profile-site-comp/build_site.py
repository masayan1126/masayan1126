#!/usr/bin/env python3
"""カンプ (canvas/Main.dc.html) から公開用の静的サイト (site/) を組み立てる。

  python3 build_site.py

- helmet の CSS と本文をそのまま使い、<head> (title / description / OGP / favicon) を足す
- 外部リンクは新しいタブで開く
- 「料金表を見る」を押したら折りたたみを開く小さな JS を足す
- og.png / apple-touch-icon.png / favicon.svg を生成する
"""
from __future__ import annotations
import re, pathlib, json
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE / 'site'
SITE.mkdir(exist_ok=True)
# カンプの画像素材 (サムネ・アイコン) は canvas/assets が正本。site/ へ毎回コピーして食い違いを防ぐ
import shutil
for _a in sorted((HERE / 'canvas' / 'assets').glob('*.webp')):
    shutil.copyfile(_a, SITE / _a.name)
BASE_URL = 'https://studio.msyn.me/'
TITLE = 'Miyabiya Studio ｜ AIで、開発と発信の仕組みをつくる'
DESC = ('テックリード ／ YouTube「まさやん【AIギルドch】」運営。本業でAI駆動開発の環境を構築・運用し、'
        '開発工数を50〜75%削減。AI駆動のWebプロダクト開発、AI導入支援、YouTubeでの製品PR、技術登壇のご相談をお受けしています。')
BLUE = '#133F8F'

src = (HERE / 'canvas' / 'Main.dc.html').read_text(encoding='utf-8')
css = re.search(r'<helmet>\s*<style>(.*?)</style>\s*</helmet>', src, re.S).group(1)
body = re.search(r'</helmet>\s*(.*?)\s*</x-dc>', src, re.S).group(1)
assert 'support.js' not in body and '<x-dc>' not in body

# 外部リンクは新しいタブで開く (mailto と #内部リンクは対象外)
n_before = len(re.findall(r'<a\b[^>]*href="https?://', body))
body = re.sub(r'<a\b([^>]*href="https?://[^"]*"[^>]*)>',
              lambda m: '<a' + m.group(1) + ' target="_blank" rel="noopener">' if 'target=' not in m.group(1) else m.group(0), body)
n_after = len(re.findall(r'<a\b[^>]*target="_blank"', body))
assert n_before == n_after, (n_before, n_after)

extra_css = """
/* 公開サイト用の追加 (カンプには無い挙動だけ) */
html{scroll-behavior:smooth}
[id]{scroll-margin-top:16px}
:focus-visible{outline:3px solid #7D95C1;outline-offset:2px}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

jsonld = {
    "@context": "https://schema.org", "@type": "Person",
    "name": "Masaya Nishigaki", "alternateName": "まさやん", "url": BASE_URL,
    "jobTitle": "テックリード", "image": BASE_URL + "hero-photo.webp",
    "email": "mailto:contact@msyn.me",
    "sameAs": ["https://www.youtube.com/@masayan-ai-hack", "https://x.com/masayan_ai_hack",
               "https://github.com/masayan1126", "https://www.instagram.com/miyabiya1126/",
               "https://zenn.dev/masayan1126", "https://substack.com/@masayan1126"],
}

head = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{BASE_URL}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Miyabiya Studio">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{BASE_URL}">
<meta property="og:image" content="{BASE_URL}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@masayan_ai_hack">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{BASE_URL}og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="{BLUE}">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>{css.rstrip()}
{extra_css}</style>
</head>
<body>
"""

script = """
<script>
(function(){
  var d=document.getElementById('ratecard');
  if(!d) return;
  document.querySelectorAll('a[href="#ratecard"]').forEach(function(a){a.addEventListener('click',function(){d.open=true;});});
  if(location.hash==='#ratecard') d.open=true;
})();
</script>
"""
PRICING_URL = BASE_URL + 'pricing/'
ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>')
PRICING_NOTE = f' ／ この料金表だけのページ: <a href="/pricing/">{PRICING_URL}</a>'
# 料金表の末尾 (更新日は料金表HTML側の値をそのまま使う) に、単体ページへの案内を足す
_rc_foot = re.compile(r'(<p class="rc-foot">詳細を確認したあとに、正式な見積書と制作日程をお送りします。料金表の更新日: \d{4}年\d{1,2}月\d{1,2}日)</p>')
assert len(_rc_foot.findall(body)) == 1, _rc_foot.findall(body)
body = _rc_foot.sub(lambda m: m.group(1) + PRICING_NOTE + '</p>', body)
html = head + body + '\n' + script.strip() + '\n</body>\n</html>\n'
(SITE / 'index.html').write_text(html, encoding='utf-8')

# ---- 画像 (OG / アイコン)
def font(size: int, bold=True):
    cands = ['/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc' if bold else '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
             '/System/Library/Fonts/Hiragino Sans GB.ttc',
             '/Library/Fonts/NotoSansJP-Bold.otf', '/Library/Fonts/NotoSansJP-Regular.otf']
    for c in cands:
        if pathlib.Path(c).exists():
            return ImageFont.truetype(c, size, index=0)
    raise SystemExit('日本語フォントが見つからない')

W, H = 1200, 630
im = Image.new('RGB', (W, H), '#FFFFFF')
d = ImageDraw.Draw(im)
# 右: 本人写真 (4:5 を角丸で)
photo = Image.open(HERE / 'site' / 'hero-photo.webp').convert('RGB')
pw, ph = 372, 465
photo = photo.resize((pw, ph), Image.LANCZOS)
mask = Image.new('L', (pw, ph), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=28, fill=255)
im.paste(photo, (W - pw - 80, (H - ph) // 2), mask)
# 左: マーク + サイト名 + 一言 + 肩書き
x0, y = 80, 96
d.ellipse((x0, y, x0 + 64, y + 64), fill=BLUE)
fm = font(30)
tw = d.textlength('M', font=fm)
d.text((x0 + 32 - tw / 2, y + 32 - 20), 'M', font=fm, fill='#FFFFFF')
fn = font(46)
d.text((x0 + 80, y + 4), 'Miyabiya ', font=fn, fill='#2A2926')
d.text((x0 + 80 + d.textlength('Miyabiya ', font=fn), y + 4), 'Studio', font=fn, fill=BLUE)
fh = font(58)
y = 226
d.text((x0, y), 'AIで、開発と発信の', font=fh, fill='#2A2926')
d.text((x0, y + 82), '仕組みをつくる', font=fh, fill='#2A2926')
fk = font(24, bold=False)
d.text((x0, 424), 'テックリード ／ YouTube「まさやん【AIギルドch】」運営', font=fk, fill='#6C6C68')
# 証拠3項目
fp = font(24)
items = ['テックリード', '開発工数を50〜75%削減', 'YouTube登録者3,350人']
x = x0
for it in items:
    d.ellipse((x, 484 + 10, x + 10, 484 + 20), fill=BLUE)
    d.text((x + 20, 484), it, font=fp, fill='#2A2926')
    x += d.textlength(it, font=fp) + 20 + 34
im.save(SITE / 'og.png', optimize=True)

# ---- 料金表の単体ページ /pricing/ (別サイトや返信に貼れる固定URL) と、その OG 画像
P_TITLE = 'YouTubeプロモーション動画の料金 ｜ Miyabiya Studio'
P_DESC = ('生成AIや開発者向けの製品・サービスを実際に試して紹介する、YouTubeプロモーション動画の料金表。'
          '3つのプラン、含まれる内容、追加料金、ご依頼時の条件。')
m_head = re.search(r'<header class="site-head">.*?</header>', body, re.S)
m_foot = re.search(r'<footer class="foot">.*?</footer>', body, re.S)
m_rc = re.search(r'<details class="tr ratecard" id="ratecard">.*?</details>', body, re.S)
assert m_head and m_foot and m_rc


def abs_anchor(h: str) -> str:
    return re.sub(r'href="#', 'href="/#', h)


p_header = abs_anchor(m_head.group(0)).replace('href="/#top"', 'href="/"')
# /pricing/ は1階層下なので、画像の相対パスをルート基準にする (相対のままだと /pricing/avatar.webp を探して 404)
p_header = re.sub(r'src="([^"/]+\.webp)"', r'src="/\1"', p_header)
p_footer = abs_anchor(m_foot.group(0))
rc = m_rc.group(0).replace('<details class="tr ratecard" id="ratecard">', '<details class="tr ratecard" id="ratecard" open>')
assert rc.count('<summary>') == 1  # 消すとブラウザ既定の「詳細」が出るので残し、CSS で隠す
rc = rc.replace(PRICING_NOTE, '')
assert PRICING_NOTE not in rc and 'open>' in rc
p_head = head.replace(f'<title>{TITLE}</title>', f'<title>{P_TITLE}</title>')
p_head = p_head.replace(f'content="{DESC}"', f'content="{P_DESC}"')
p_head = p_head.replace(f'content="{TITLE}"', f'content="{P_TITLE}"')
p_head = p_head.replace(f'href="{BASE_URL}">', f'href="{PRICING_URL}">')
p_head = p_head.replace(f'<meta property="og:url" content="{BASE_URL}">', f'<meta property="og:url" content="{PRICING_URL}">')
p_head = p_head.replace(f'{BASE_URL}og.png', f'{BASE_URL}og-pricing.png')
p_head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', '', p_head, flags=re.S)
p_head = p_head.replace('</style>', '\n/* 料金表の単体ページ */\n.pricing-page details.tr{margin-top:0}\n'
                        '.pricing-page details.tr summary{display:none}\n.pricing-page .sec-lead{max-width:720px}\n'
                        '.pricing-page .btns.sec-cta{margin-top:36px}\n</style>')
assert p_head.count(P_TITLE) == 3 and PRICING_URL in p_head and 'og-pricing.png' in p_head
p_body = (p_header + '\n\n<main id="top" class="pricing-page">\n  <div class="sec"><div class="wrap">\n'
          '    <span class="kicker">料金表</span>\n'
          '    <h1 class="sec-h">YouTubeプロモーション動画の料金</h1>\n'
          '    <p class="sec-lead">企業のタイアップ動画の料金です。個人の方との対談や共同企画、動画以外のご依頼は、内容に応じてお見積もりします。お見積もりは無料です。</p>\n'
          '    ' + rc + '\n'
          '    <div class="btns sec-cta"><a href="/#contact" class="btn btn-p">お問い合わせ ' + ARROW + '</a>'
          '<a href="/" class="btn btn-g">サイトのトップへ ' + ARROW + '</a></div>\n'
          '  </div></div>\n</main>\n\n' + p_footer + '\n')
(SITE / 'pricing').mkdir(exist_ok=True)
(SITE / 'pricing' / 'index.html').write_text(p_head + p_body + '</body>\n</html>\n', encoding='utf-8')

# OG 画像 (料金表用): プラン3枠。値は HTML から拾い、手で二重管理しない
plans = re.split(r'<div class="plan(?: reco)?">', re.search(r'<div class="plans">(.*?)<p class="rc-note">', rc, re.S).group(1))[1:]
plans = [(re.search(r'<h3>(.*?)</h3>', b).group(1), re.search(r'<p class="spec">(.*?)</p>', b).group(1),
          re.search(r'<span class="v">(.*?)</span>', b).group(1), 'おすすめ' in b) for b in plans]
assert len(plans) == 3, plans
im = Image.new('RGB', (W, H), '#FFFFFF')
d = ImageDraw.Draw(im)
d.ellipse((80, 56, 124, 100), fill=BLUE)
fm = font(22)
tw = d.textlength('M', font=fm)
d.text((102 - tw / 2, 63), 'M', font=fm, fill='#FFFFFF')
fn = font(28)
d.text((136, 62), 'Miyabiya ', font=fn, fill='#2A2926')
d.text((136 + d.textlength('Miyabiya ', font=fn), 62), 'Studio', font=fn, fill=BLUE)
d.text((80, 128), 'YouTubeプロモーション動画の料金', font=font(50), fill='#2A2926')
d.text((80, 204), '生成AIや開発者向けの製品・サービスを、実際に試して動画で紹介します', font=font(22, bold=False), fill='#6C6C68')
cw, ch, gap, top = 336, 296, 16, 262
for i, (name, spec, price, reco) in enumerate(plans):
    x = 80 + i * (cw + gap)
    d.rounded_rectangle((x, top, x + cw, top + ch), radius=22, fill='#FFFFFF',
                        outline=BLUE if reco else '#DDE2E6', width=3 if reco else 2)
    y = top + 26
    if reco:
        d.text((x + 26, y), 'おすすめ', font=font(17), fill=BLUE)
        y += 30
    d.text((x + 26, y), name.replace('を制作する', '').replace('検証する', '検証'), font=font(25), fill='#2A2926')
    y += 44
    for line in spec.split('・'):
        d.text((x + 26, y), line, font=font(17, bold=False), fill='#6C6C68')
        y += 26
    y += 14
    fpv = font(46)
    d.text((x + 26, y), price, font=fpv, fill='#2A2926')
    d.text((x + 26 + d.textlength(price, font=fpv) + 8, y + 22), '円 税別', font=font(18), fill='#6C6C68')
d.text((80, 586), 'studio.msyn.me/pricing', font=font(18, bold=False), fill='#8A8A86')
im.save(SITE / 'og-pricing.png', optimize=True)

# apple-touch-icon 180x180: 青丸に白い M
ic = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
di = ImageDraw.Draw(ic)
di.rounded_rectangle((0, 0, 179, 179), radius=40, fill='#FFFFFF')
di.ellipse((18, 18, 162, 162), fill=BLUE)
fi = font(84)
tw = di.textlength('M', font=fi)
di.text((90 - tw / 2, 90 - 54), 'M', font=fi, fill='#FFFFFF')
ic.save(SITE / 'apple-touch-icon.png')

(SITE / 'favicon.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#133F8F"/>'
    '<text x="32" y="43" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif" '
    'font-size="34" font-weight="700" fill="#fff">M</text></svg>\n', encoding='utf-8')
(SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n', encoding='utf-8')
(SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                  f'<url><loc>{BASE_URL}</loc></url><url><loc>{PRICING_URL}</loc></url></urlset>\n', encoding='utf-8')
(SITE / '_redirects').write_text('/ratecard /pricing/ 301\n/price /pricing/ 301\n', encoding='utf-8')
(SITE / '_headers').write_text('/*.webp\n  Cache-Control: public, max-age=604800\n/*.png\n  Cache-Control: public, max-age=604800\n', encoding='utf-8')

# ---- 検証
out = (SITE / 'index.html').read_text(encoding='utf-8')
checks = {
    '<title>': out.count('<title>') == 1,
    'ratecard details': out.count('id="ratecard"') == 1,
    'hero-photo': 'src="hero-photo.webp"' in out,
    'no support.js': 'support.js' not in out,
    'no x-dc': '<x-dc>' not in out and '<helmet>' not in out,
    'no raw & in style': '&' not in re.search(r'<style>(.*?)</style>', out, re.S).group(1),
    'sections': all(f'id="{s}"' in out for s in ['services', 'pr', 'works', 'videos', 'membership', 'talks', 'career-history', 'career', 'flow', 'contact']),
    'thumbs exist': all((SITE / f'thumb-{v}.webp').exists() for v in ['Kggm_W0w0lw', 'BxQ2nutD-_o', 'D1gsaCoJelw']),
    'headings no 。': not re.search(r'。\s*</h[1-4]>', out),
    'pricing page open': 'id="ratecard" open' in (SITE / 'pricing' / 'index.html').read_text(encoding='utf-8'),
    'pricing header links absolute': 'href="#' not in re.search(r'<header.*?</header>', (SITE / 'pricing' / 'index.html').read_text(encoding='utf-8'), re.S).group(0),
    'pricing link in main': PRICING_URL in out,
    'og-pricing': (SITE / 'og-pricing.png').exists(),
    'header avatar': 'src="avatar.webp"' in out and (SITE / 'avatar.webp').exists() and '<span class="mark">M</span>' not in out,
    'pricing avatar absolute': 'src="/avatar.webp"' in (SITE / 'pricing' / 'index.html').read_text(encoding='utf-8') and 'src="avatar.webp"' not in (SITE / 'pricing' / 'index.html').read_text(encoding='utf-8'),
}
for k, v in checks.items():
    print(('PASS' if v else 'FAIL'), k)
assert all(checks.values())
print('index.html bytes', len(out.encode('utf-8')), '/ external links', n_after)
