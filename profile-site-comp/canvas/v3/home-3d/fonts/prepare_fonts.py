"""Refresh the self-hosted subsets after adding new Japanese site copy.

Maintenance only; requires fonttools[woff]. Regular builds use the saved WOFF2.
"""
from pathlib import Path
import tempfile
from urllib.request import urlretrieve
from fontTools import subset

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
copy = ''.join(p.read_text() for p in [ROOT.parent/'Main.dc.html', ROOT/'build_v3.py', ROOT/'build_home.py', ROOT/'home-3d/home.html', ROOT/'home-3d/runtime.js', ROOT/'home-3d/studio-scene.js'])
fonts = [
    ('notosansjp/NotoSansJP%5Bwght%5D.ttf', 'noto-sans-jp.woff2', copy),
    ('manrope/Manrope%5Bwght%5D.ttf', 'manrope.woff2', ''.join(chr(i) for i in range(32,256))+'↗→←–—©'),
]
with tempfile.TemporaryDirectory() as temp:
    for path, name, chars in fonts:
        source = Path(temp) / 'font.ttf'
        urlretrieve('https://raw.githubusercontent.com/google/fonts/main/ofl/' + path, source)
        options = subset.Options()
        options.flavor = 'woff2'
        options.layout_features = ['*']
        font = subset.load_font(str(source), options)
        glyphs = subset.Subsetter(options=options)
        glyphs.populate(text=chars)
        glyphs.subset(font)
        subset.save_font(font, str(HERE / name), options)
        print(name, (HERE / name).stat().st_size)
