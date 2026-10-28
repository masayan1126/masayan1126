#!/usr/bin/env python3
# coding: utf-8
"""Render the current sharing images and bookmark icons from shared metadata.

Uses the adopted IBM Plex Sans JP files and the original curved-m SVG. Text is
rasterized directly with Pillow; no browser, network, or AI image edit is needed.
Generated assets are committed, and normal site builds verify their hashes.
"""
from io import BytesIO
from pathlib import Path
from functools import lru_cache
import hashlib
import json
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.svgLib.path import parse_path
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urlsplit
from site_metadata import PAGES, SITE_NAME, OWNER, ASSETS, BASE, asset_input_digest

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / 'prototypes/editorial/assets/fonts/ibm-plex-sans-jp'
FONT_MANIFEST = json.loads((FONT_DIR / 'manifest.json').read_text())
MARK = HERE / 'prototypes/editorial/icons/miyabiya-mark.svg'
AVATAR = HERE / 'prototypes/editorial/assets/avatar-mono-pixel.png'
W, H = 1200, 630
SAFE = (309, 48, 891, 582)
LANDSCAPE_SAFE = (128, 48, 1072, 582)
INK, MUTED = '#202020', '#606060'
USED_FONTS = set()


def contains(record, code):
    for value in record['unicodeRange'].split(','):
        bounds = value.strip().removeprefix('U+').split('-')
        if int(bounds[0], 16) <= code <= int(bounds[-1], 16):
            return True
    return False


@lru_cache(None)
def font_record(weight, char):
    for record in FONT_MANIFEST['faces']:
        if record['weight'] == weight and contains(record, ord(char)):
            return record['file']
    raise ValueError('Font missing character: ' + repr(char))


@lru_cache(None)
def font(filename, size):
    record = next(x for x in FONT_MANIFEST['faces'] if x['file'] == filename)
    raw = (FONT_DIR / filename).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record['sha256'], filename
    USED_FONTS.add(filename)
    face = TTFont(BytesIO(raw))
    face.flavor = None
    output = BytesIO()
    face.save(output)
    face.close()
    return ImageFont.truetype(BytesIO(output.getvalue()), size)


def text_runs(text, size, weight):
    runs = []
    for char in text:
        filename = font_record(weight, char)
        if runs and runs[-1][0] == filename:
            runs[-1][1] += char
        else:
            runs.append([filename, char])
    return [(font(filename, size), value) for filename, value in runs]


def draw_line(draw, text, baseline, size, weight, color=INK, *, x=None, safe=SAFE):
    runs = text_runs(text, size, weight)
    if x is None:
        x = (W - sum(face.getlength(value) for face, value in runs)) / 2
    else:
        # Align the visible ink, including Latin glyphs with negative bearings.
        first_face, first_text = runs[0]
        x += x - draw.textbbox((x, baseline), first_text, font=first_face, anchor='ls')[0]
    boxes = []
    for face, value in runs:
        box = draw.textbbox((x, baseline), value, font=face, anchor='ls')
        boxes.append(box)
        draw.text((x, baseline), value, font=face, fill=color, anchor='ls')
        x += face.getlength(value)
    bounds = (min(x[0] for x in boxes), min(x[1] for x in boxes),
              max(x[2] for x in boxes), max(x[3] for x in boxes))
    left, top, right, bottom = safe
    assert left <= bounds[0] and top <= bounds[1] and bounds[2] <= right and bounds[3] <= bottom, (text, bounds)
    return {'text': text, 'size': size, 'weight': weight, 'bounds': bounds}


class StrokePen(BasePen):
    """Sample the adopted SVG path without maintaining a second logo shape."""
    def __init__(self):
        super().__init__(None)
        self.paths, self.points = [], []

    def _moveTo(self, point):
        if self.points:
            self.paths.append(self.points)
        self.points = [point]

    def _lineTo(self, point):
        self.points.append(point)

    def _curveToOne(self, a, b, c):
        p = self._getCurrentPoint()
        for step in range(1, 33):
            t, u = step / 32, 1 - step / 32
            self.points.append(tuple(u**3*p[i] + 3*u*u*t*a[i] + 3*u*t*t*b[i] + t**3*c[i] for i in (0, 1)))

    def _closePath(self):
        self.points.append(self.points[0])
        self._endPath()

    def _endPath(self):
        if self.points:
            self.paths.append(self.points)
        self.points = []


def mark_image(size):
    factor = size * 4 / 32
    image = Image.new('RGB', (size * 4, size * 4), 'white')
    draw = ImageDraw.Draw(image)
    svg = ET.fromstring(MARK.read_text())
    for path in svg.findall('{http://www.w3.org/2000/svg}path'):
        pen = StrokePen()
        parse_path(path.attrib['d'], pen)
        pen._endPath()
        thickness = float(path.attrib['stroke-width']) * factor
        for points in pen.paths:
            scaled = [(x * factor, y * factor) for x, y in points]
            draw.line(scaled, fill=INK, width=round(thickness))
            # A disk at every sampled vertex makes a continuous round stroke;
            # Pillow's curved joins can leave seams on densely sampled arcs.
            for x, y in scaled:
                r = thickness / 2
                draw.ellipse((x-r, y-r, x+r, y+r), fill=INK)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def render_sharing_image(page):
    """Text-free portrait for OG cards that already show title and description."""
    image = Image.new('RGB', (W, H), 'white')
    with Image.open(AVATAR) as source:
        avatar = source.convert('RGBA')
    avatar.thumbnail((512, 512), Image.Resampling.NEAREST)
    x, y = (W - avatar.width) // 2, (H - avatar.height) // 2
    image.paste(avatar, (x, y), avatar)
    visuals = [{'role': 'avatar', 'bounds': (x, y, x + avatar.width, y + avatar.height)}]
    for visual in visuals:
        x1, y1, x2, y2 = visual['bounds']
        assert SAFE[0] <= x1 < x2 <= SAFE[2] and SAFE[1] <= y1 < y2 <= SAFE[3], visual
    return image, [], visuals


def render_landscape_sharing_image(page):
    """Adopted C in a wider composition for the explicit X image tag."""
    image = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(image)
    left, avatar_size, gap = 144, 240, 48
    text_x = left + avatar_size + gap
    with Image.open(AVATAR) as source:
        avatar = source.convert('RGBA')
    avatar.thumbnail((avatar_size, avatar_size), Image.Resampling.NEAREST)
    image.paste(avatar, (left, 172), avatar)
    image.paste(mark_image(56), (text_x, 100))

    def line(text, baseline, size, weight=400, color=INK, *, x=text_x):
        return draw_line(draw, text, baseline, size, weight, color, x=x, safe=LANDSCAPE_SAFE)

    boxes = [line(SITE_NAME, 264, 80, 700), line(OWNER, 328, 36, color=MUTED)]
    if page:
        boxes.append(line(PAGES[page]['label'], 406, 36, 700))
    for text, baseline in zip(PAGES[page]['image_lines'], (480, 528)):
        boxes.append(line(text, baseline, 36, color=MUTED))
    boxes.append(line(urlsplit(BASE).netloc, 566, 28, color=MUTED))
    visuals = [{'role': 'avatar', 'bounds': (left, 172, left + avatar.width, 172 + avatar.height)},
               {'role': 'mark', 'bounds': (text_x, 100, text_x + 56, 156)}]
    for visual in visuals:
        x1, y1, x2, y2 = visual['bounds']
        assert LANDSCAPE_SAFE[0] <= x1 < x2 <= LANDSCAPE_SAFE[2] and LANDSCAPE_SAFE[1] <= y1 < y2 <= LANDSCAPE_SAFE[3], visual
    return image, boxes, visuals


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    files, layouts, visual_bounds = [], {}, {}
    landscape_layouts, landscape_visual_bounds = {}, {}

    def record(filename, public_path, **extra):
        raw = (ASSETS / filename).read_bytes()
        data = {'file': filename, 'public_path': public_path,
                'sha256': hashlib.sha256(raw).hexdigest(), **extra}
        if filename.endswith('.png'):
            with Image.open(ASSETS / filename) as image:
                data['width'], data['height'] = image.size
        files.append(data)

    for page in PAGES:
        image, boxes, visuals = render_sharing_image(page)
        filename = 'og-' + (page or 'home') + '.png'
        image.save(ASSETS / filename, optimize=True)
        digest = hashlib.sha256((ASSETS / filename).read_bytes()).hexdigest()[:12]
        record(filename, '/social/' + filename.replace('.png', '.' + digest + '.png'), page=page)
        layouts[page] = boxes
        visual_bounds[page] = visuals
        wide_image, wide_boxes, wide_visuals = render_landscape_sharing_image(page)
        wide_filename = 'x-' + (page or 'home') + '.png'
        wide_image.save(ASSETS / wide_filename, optimize=True)
        wide_digest = hashlib.sha256((ASSETS / wide_filename).read_bytes()).hexdigest()[:12]
        record(wide_filename, '/social/' + wide_filename.replace('.png', '.' + wide_digest + '.png'), twitter_page=page)
        landscape_layouts[page] = wide_boxes
        landscape_visual_bounds[page] = wide_visuals

    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg = ET.fromstring(MARK.read_text())
    svg.insert(0, ET.Element('{http://www.w3.org/2000/svg}rect', {'width': '32', 'height': '32', 'fill': '#ffffff'}))
    for path in svg.findall('{http://www.w3.org/2000/svg}path'):
        path.set('stroke', INK)
    (ASSETS / 'favicon.svg').write_text(ET.tostring(svg, encoding='unicode') + '\n')
    record('favicon.svg', '/favicon.svg')
    for size, filename in [(96, 'favicon-96.png'), (180, 'apple-touch-icon.png'), (192, 'icon-192.png'), (512, 'icon-512.png')]:
        mark_image(size).save(ASSETS / filename, optimize=True)
        record(filename, '/icons/' + filename)
    mark_image(256).save(ASSETS / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    record('favicon.ico', '/favicon.ico')
    manifest = {'name': SITE_NAME, 'short_name': SITE_NAME, 'lang': 'ja', 'start_url': '/', 'scope': '/',
                'display': 'browser', 'background_color': '#ffffff', 'theme_color': '#ffffff',
                'icons': [{'src': '/icons/icon-' + str(size) + '.png', 'sizes': f'{size}x{size}', 'type': 'image/png', 'purpose': 'any'} for size in (192, 512)]}
    (ASSETS / 'site.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    record('site.webmanifest', '/site.webmanifest')
    result = {'generator': 'canvas/v3/build_og.py', 'input_sha256': asset_input_digest(), 'mark_source': str(MARK.relative_to(HERE)),
              'mark_sha256': hashlib.sha256(MARK.read_bytes()).hexdigest(),
              'design': 'C: text-free portrait OG and wide X composition',
              'avatar_source': str(AVATAR.relative_to(HERE)),
              'avatar_sha256': hashlib.sha256(AVATAR.read_bytes()).hexdigest(),
              'font_family': FONT_MANIFEST['family'], 'font_license': 'OFL-1.1',
              'font_files': sorted(USED_FONTS), 'safe_bounds': SAFE, 'layouts': layouts,
              'visual_bounds': visual_bounds,
              'landscape_safe_bounds': LANDSCAPE_SAFE, 'landscape_layouts': landscape_layouts,
              'landscape_visual_bounds': landscape_visual_bounds, 'files': files}
    (ASSETS / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'og_images': len(PAGES), 'x_images': len(PAGES), 'bookmark_assets': len(files)-2*len(PAGES), 'safe_bounds': SAFE, 'landscape_safe_bounds': LANDSCAPE_SAFE, 'used_font_files': len(USED_FONTS), 'output': str(ASSETS)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
