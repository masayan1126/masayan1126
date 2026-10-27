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
W, H = 1200, 630
SAFE = (309, 48, 891, 582)
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


def draw_line(draw, text, baseline, size, weight, color=INK):
    runs = text_runs(text, size, weight)
    x = (W - sum(face.getlength(value) for face, value in runs)) / 2
    boxes = []
    for face, value in runs:
        box = draw.textbbox((x, baseline), value, font=face, anchor='ls')
        boxes.append(box)
        draw.text((x, baseline), value, font=face, fill=color, anchor='ls')
        x += face.getlength(value)
    bounds = (min(x[0] for x in boxes), min(x[1] for x in boxes),
              max(x[2] for x in boxes), max(x[3] for x in boxes))
    left, top, right, bottom = SAFE
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


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    files, layouts = [], {}

    def record(filename, public_path, **extra):
        raw = (ASSETS / filename).read_bytes()
        data = {'file': filename, 'public_path': public_path,
                'sha256': hashlib.sha256(raw).hexdigest(), **extra}
        if filename.endswith('.png'):
            with Image.open(ASSETS / filename) as image:
                data['width'], data['height'] = image.size
        files.append(data)

    for page, info in PAGES.items():
        image = Image.new('RGB', (W, H), 'white')
        image.paste(mark_image(80), (560, 82))
        draw = ImageDraw.Draw(image)
        boxes = [draw_line(draw, SITE_NAME, 250, 48, 700),
                 draw_line(draw, OWNER, 306, 28, 400, MUTED)]
        if page:
            boxes.append(draw_line(draw, info['label'], 378, 36, 700))
        baselines = (438, 480) if page else (408, 456)
        for text, baseline in zip(info['image_lines'], baselines):
            boxes.append(draw_line(draw, text, baseline, 28, 400, MUTED))
        boxes.append(draw_line(draw, urlsplit(BASE).netloc, 550, 28, 400, MUTED))
        filename = 'og-' + (page or 'home') + '.png'
        image.save(ASSETS / filename, optimize=True)
        digest = hashlib.sha256((ASSETS / filename).read_bytes()).hexdigest()[:12]
        record(filename, '/social/' + filename.replace('.png', '.' + digest + '.png'), page=page)
        layouts[page] = boxes

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
              'font_family': FONT_MANIFEST['family'], 'font_license': 'OFL-1.1',
              'font_files': sorted(USED_FONTS), 'safe_bounds': SAFE, 'layouts': layouts, 'files': files}
    (ASSETS / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'og_images': len(PAGES), 'bookmark_assets': len(files)-len(PAGES), 'safe_bounds': SAFE, 'used_font_files': len(USED_FONTS), 'output': str(ASSETS)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
