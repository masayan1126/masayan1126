#!/usr/bin/env python3
"""リンクを共有したときのプレビュー画像 (site/og-profile.png, 1200×630) を生成する。

  python3 canvas/v3/build_og.py

プレビュー画像は、表示先の枠に合わせて中央から切り抜かれる。X・Facebook は 1.91:1、
チャットやノートアプリの細いカードは 1.5:1 前後、小さいカードは正方形になる。そのため
文字はすべて中央の 630×630 (正方形に切り抜かれても残る範囲) に収め、左右の端には背景だけを置く。
生成時に文字の位置を測り、範囲からはみ出したら止める。比率ごとの見え方は
output/og-profile-crops.png に保存する。

Google Chrome か Chromium と Pillow を使う (見つからないときは CHROME にパスを指定する)。
生成した PNG は Git に含めるので、npm run build ではこのスクリプトを実行しない。
"""
import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = ROOT / 'site/og-profile.png'
CROPS = ROOT / 'output/og-profile-crops.png'
W, H = 1200, 630
# 正方形に切り抜かれても余白が残るよう、左右は 24px、上下は 2.2:1 まで切り詰められても残る範囲。
SAFE = ((W - H) // 2 + 24, 48, (W + H) // 2 - 24, H - 48)

BRAND = 'Miyabiya Studio'
NAME = ('Masaya', 'Nishigaki')
ROLE = 'Webエンジニア・テックリード'
TAGLINE = ('Claude Code・MCPで、', 'チームの開発を速くする')
JP_FONT = HERE / 'site-assets/studio-jp.woff2'
SANS_FONT = HERE / 'site-assets/studio-sans.woff2'


def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()


def page():
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
@font-face{{font-family:"Studio Sans";src:url({data_uri(SANS_FONT, 'font/woff2')}) format("woff2");font-weight:200 800}}
@font-face{{font-family:"Studio JP";src:url({data_uri(JP_FONT, 'font/woff2')}) format("woff2");font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;font-family:"Studio Sans","Studio JP",sans-serif;-webkit-font-smoothing:antialiased;color:#282828;
  background:linear-gradient(90deg,#133F8F 0 600px,#fff 600px)}}
.edge{{position:absolute;top:0;width:{(W - H) // 2}px;height:{H}px;background-size:22px 22px}}
.edge-left{{left:0;background-image:radial-gradient(rgba(255,255,255,.14) 1.6px,transparent 1.8px)}}
.edge-right{{right:0;background-image:radial-gradient(#E3E6EC 1.6px,transparent 1.8px)}}
.photo{{position:absolute;left:0;top:0;width:600px;height:{H}px;overflow:hidden}}
.photo img{{position:absolute;width:448px;left:232px;top:72px}}
.card{{position:absolute;left:630px;top:0;width:{SAFE[2] - 630}px;height:{H}px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start}}
.brand{{display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;margin-bottom:34px}}
.brand img{{width:36px;height:36px;border-radius:50%;border:1px solid #DDE2E6}}
h1{{font-weight:800;font-size:56px;line-height:1.06;letter-spacing:-.02em}}
.role{{font-family:"Studio JP";font-weight:700;font-size:18px;color:#133F8F;margin-top:16px}}
.rule{{width:64px;height:2px;background:#133F8F;margin:26px 0 22px}}
.tagline{{font-family:"Studio JP";font-weight:700;font-size:22px;line-height:1.55}}
</style></head><body>
<div class="edge edge-left"></div><div class="edge edge-right"></div>
<div class="photo"><img src="{data_uri(ROOT / 'site/hero-photo.webp', 'image/webp')}" alt=""></div>
<div class="card">
<div class="brand" data-measure="brand"><img src="{data_uri(ROOT / 'canvas/assets/avatar.webp', 'image/webp')}" alt="">{BRAND}</div>
<h1 data-measure="name">{'<br>'.join(NAME)}</h1>
<div class="role" data-measure="role">{ROLE}</div>
<div class="rule"></div>
<div class="tagline" data-measure="tagline">{'<br>'.join(TAGLINE)}</div>
</div>
<script>
document.fonts.ready.then(() => {{
  const boxes = {{}};
  for (const el of document.querySelectorAll('[data-measure]')) {{
    const range = document.createRange();
    range.selectNodeContents(el);
    const r = range.getBoundingClientRect();
    boxes[el.dataset.measure] = [r.left, r.top, r.right, r.bottom].map(Math.round);
  }}
  const fonts = [...document.fonts].map(f => f.family + ':' + f.status);
  document.body.dataset.layout = JSON.stringify({{boxes, fonts, viewport: [innerWidth, innerHeight]}});
}});
</script>
</body></html>'''


def chrome():
    for candidate in (os.environ.get('CHROME'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                      shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser'),
                      '/opt/pw-browsers/chromium'):
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit('Chrome が見つかりません。CHROME にパスを指定してください。')


def run_chrome(html_path, *args):
    # 新しいヘッドレスモードは表示領域がウィンドウより少し低くなるので、縦に余裕を取って後で切り出す。
    command = [chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
               f'--window-size={W},{H + 370}', '--virtual-time-budget=5000', *args, html_path.as_uri()]
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        command.insert(1, '--no-sandbox')
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def check_layout(dom):
    found = re.search(r'data-layout="([^"]*)"', dom)
    assert found, 'レイアウトを測れませんでした (フォントの読み込みを待てていません)'
    layout = json.loads(found.group(1).replace('&quot;', '"').replace('&amp;', '&'))
    assert layout['viewport'][0] == W and layout['viewport'][1] >= H, layout['viewport']
    assert all(f.endswith(':loaded') for f in layout['fonts']), layout['fonts']
    left, top, right, bottom = SAFE
    for name, (x0, y0, x1, y1) in layout['boxes'].items():
        assert left <= x0 and x1 <= right and top <= y0 and y1 <= bottom, \
            f'{name} が中央の安全範囲 {SAFE} からはみ出しています: {(x0, y0, x1, y1)}'
    return layout['boxes']


def crop_sheet(image):
    """比率ごとに中央から切り抜いた見本を並べる。"""
    ratios = (('2.2:1', 2.2), ('1.91:1 X / Facebook', 1.91), ('1.5:1', 1.5), ('1.2:1', 1.2), ('1:1', 1.0))
    height, gap = 240, 24
    tiles = []
    for label, ratio in ratios:
        cw, ch = (W, round(W / ratio)) if ratio >= W / H else (round(H * ratio), H)
        x0, y0 = (W - cw) // 2, (H - ch) // 2
        tiles.append((label, image.crop((x0, y0, x0 + cw, y0 + ch)).resize((round(height * ratio), height), Image.LANCZOS)))
    sheet = Image.new('RGB', (sum(t.width for _, t in tiles) + gap * (len(tiles) + 1), height + 64), '#22272E')
    draw = ImageDraw.Draw(sheet)
    x = gap
    for label, tile in tiles:
        sheet.paste(tile, (x, 44))
        draw.text((x, 18), label, fill='#FFFFFF')
        x += tile.width + gap
    return sheet


def main():
    covered = TTFont(JP_FONT).getBestCmap()
    missing = sorted({c for c in ROLE + ''.join(TAGLINE) if ord(c) > 0x2000 and ord(c) not in covered})
    assert not missing, f'日本語フォントに無い文字があります: {"".join(missing)}'
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / 'og.html'
        html_path.write_text(page(), encoding='utf-8')
        boxes = check_layout(run_chrome(html_path, '--dump-dom'))
        shot = Path(tmp) / 'shot.png'
        run_chrome(html_path, f'--screenshot={shot}')
        image = Image.open(shot).convert('RGB').crop((0, 0, W, H))
    image.save(OUTPUT, optimize=True)
    CROPS.parent.mkdir(exist_ok=True)
    crop_sheet(image).save(CROPS)
    for name, box in boxes.items():
        print(f'{name:8} {box}')
    print('Saved', OUTPUT.relative_to(ROOT), 'and', CROPS.relative_to(ROOT))


if __name__ == '__main__':
    main()
