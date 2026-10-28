"""Build five local OGP studies without changing the public sharing assets."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw
from fontTools.svgLib.path import parse_path

HERE = Path(__file__).resolve().parent
V3 = HERE.parents[1]
sys.path.insert(0, str(V3))
from build_og import text_runs, StrokePen, MARK, USED_FONTS, render_sharing_image
from site_metadata import SITE_NAME, OWNER

OUT = HERE / 'assets'
INK, MUTED, WHITE = '#202020', '#606060', '#ffffff'
LINES = ['AIの発信・製品PR・個人開発', 'AI動画編集・技術登壇・AI活用支援']
OPTIONS = [
    ('a', '横組みのロゴ', 'ロゴと屋号を一列に。余白を広く取り、端正にまとめる。'),
    ('b', '大きな2行タイトル', '屋号を大きく見せる。小さなプレビューでも名前が目に入る。'),
    ('c', 'ドット絵のプロフィール', '小さな表示でも顔が伝わる、文字なしのプロフィール画像。'),
    ('d', '大きなm', 'マークを大きく配置。シンボルで屋号を覚えてもらう。'),
    ('e', '黒地の反転', '黒地に白い文字とロゴ。サイトと同じ無彩色で印象を変える。'),
]


def logo(image, size, xy, ink=INK, bg=WHITE):
    scale = 4
    tile = Image.new('RGB', (size * scale, size * scale), bg)
    draw = ImageDraw.Draw(tile)
    factor = size * scale / 32
    svg = ET.fromstring(MARK.read_text())
    for path in svg.findall('{http://www.w3.org/2000/svg}path'):
        pen = StrokePen()
        parse_path(path.attrib['d'], pen)
        pen._endPath()
        stroke = float(path.attrib['stroke-width']) * factor
        for points in pen.paths:
            pts = [(x * factor, y * factor) for x, y in points]
            draw.line(pts, fill=ink, width=round(stroke))
            for x, y in pts:
                r = stroke / 2
                draw.ellipse((x-r, y-r, x+r, y+r), fill=ink)
    image.paste(tile.resize((size, size), Image.Resampling.LANCZOS), xy)


def render(key):
    if key == 'c':
        image, boxes, _ = render_sharing_image('')
        return image, boxes
    dark = key == 'e'
    bg, ink, muted = (INK, WHITE, '#d0d0d0') if dark else (WHITE, INK, MUTED)
    image = Image.new('RGB', (1200, 630), bg)
    draw = ImageDraw.Draw(image)
    boxes = []

    def line(text, x, baseline, size=28, weight=400, color=None, center=False):
        runs = text_runs(text, size, weight)
        width = sum(face.getlength(value) for face, value in runs)
        if center:
            x -= width / 2
        bounds = []
        for face, value in runs:
            box = draw.textbbox((x, baseline), value, font=face, anchor='ls')
            bounds.append(box)
            draw.text((x, baseline), value, font=face, anchor='ls', fill=color or ink)
            x += face.getlength(value)
        box = [min(b[0] for b in bounds), min(b[1] for b in bounds), max(b[2] for b in bounds), max(b[3] for b in bounds)]
        assert box[0] >= 64 and box[1] >= 48 and box[2] <= 1136 and box[3] <= 582, (key, text, box)
        boxes.append({'text': text, 'size': size, 'weight': weight, 'bounds': box})

    if key == 'a':
        logo(image, 96, (132, 158))
        line(SITE_NAME, 264, 232, 64, 700)
        line(OWNER, 264, 292, 36, color=muted)
        for baseline, text in zip([404, 452], LINES):
            line(text, 264, baseline, 36, color=muted)
        line('studio.msyn.me', 264, 552, 28, color=muted)
    elif key == 'b':
        logo(image, 96, (960, 104))
        line('Miyabiya', 144, 236, 96, 700)
        line('Studio', 144, 344, 96, 700)
        line(OWNER, 148, 408, 36, color=muted)
        for baseline, text in zip([490, 534], LINES):
            line(text, 148, baseline, 36, color=muted)
        line('studio.msyn.me', 838, 552, 28, color=muted)
    elif key == 'd':
        logo(image, 288, (120, 148))
        line('Miyabiya', 536, 236, 64, 700)
        line('Studio', 536, 312, 64, 700)
        line(OWNER, 536, 376, 36, color=muted)
        for baseline, text in zip([460, 504], LINES):
            line(text, 536, baseline, 36, color=muted)
        line('studio.msyn.me', 536, 564, 28, color=muted)
    elif key == 'e':
        logo(image, 80, (560, 100), ink, bg)
        line(SITE_NAME, 600, 286, 72, 700, center=True)
        line(OWNER, 600, 350, 36, color=muted, center=True)
        for baseline, text in zip([448, 492], LINES):
            line(text, 600, baseline, 36, color=muted, center=True)
        line('studio.msyn.me', 600, 564, 28, color=muted, center=True)
    else:
        raise ValueError(key)
    return image, boxes


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    for key, name, description in OPTIONS:
        image, boxes = render(key)
        path = OUT / f'ogp-{key}.png'
        image.save(path, optimize=True)
        entries.append({'key': key, 'name': name, 'description': description,
                        'file': path.name, 'width': 1200, 'height': 630,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'text': boxes})
    result = {'status': 'selected', 'selected_design': 'c', 'identity': [SITE_NAME, OWNER],
              'font': 'IBM Plex Sans JP', 'mark_sha256': hashlib.sha256(MARK.read_bytes()).hexdigest(),
              'font_files': sorted(USED_FONTS), 'options': entries}
    (OUT / 'options.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'OGP options: {len(entries)} images')
    return result


if __name__ == '__main__':
    build()
