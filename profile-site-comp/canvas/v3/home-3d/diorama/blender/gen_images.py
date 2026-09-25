from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
F = '/System/Library/Fonts/'
def font(name, size, idx=0): return ImageFont.truetype(F + name, size, index=idx)
G6 = lambda s: font('ヒラギノ角ゴシック W6.ttc', s)
G3 = lambda s: font('ヒラギノ角ゴシック W3.ttc', s)
MIN = lambda s: font('ヒラギノ明朝 ProN.ttc', s, 1)
HAND = lambda s: ImageFont.truetype('/System/Library/AssetsV2/com_apple_MobileAsset_Font8/81e879dcb4d596ab140f7cffcd5ccaaf8108519b.asset/AssetData/Klee.ttc', s, index=1)
S = 2  # 2x of the web canvas sizes

def editor():
    im = Image.new('RGB', (1024 * S, 576 * S), '#1d2125'); d = ImageDraw.Draw(im); k = S
    d.rectangle([0, 0, 1024 * k, 34 * k], fill='#262b30'); d.rectangle([0, 34 * k, 200 * k, 414 * k], fill='#262b30')
    for i in range(9): d.rectangle([14 * k, (50 + i * 38) * k, 186 * k, (78 + i * 38) * k], fill='#3d5a78' if i == 2 else '#30363c')
    pv = Image.new('RGB', (560 * k, 315 * k)); pd = ImageDraw.Draw(pv)
    for y in range(315 * k):
        t = y / (315 * k); c = tuple(int(a + (b - a) * t) for a, b in zip((0x34, 0x59, 0x7a), (0x16, 0x22, 0x2e))); pd.line([0, y, 560 * k, y], fill=c)
    im.paste(pv, (232 * k, 50 * k))
    d.text((262 * k, 128 * k), 'AI活用', font=G6(86 * k), fill='#f5f7f8')
    d.text((266 * k, 225 * k), 'まさやん【AIギルドch】', font=G3(30 * k), fill='#cfe0ee')
    d.rectangle([262 * k, 290 * k, 482 * k, 334 * k], fill='#e5eef4'); d.text((294 * k, 298 * k), '新しい動画', font=G6(26 * k), fill='#16222e')
    d.rectangle([812 * k, 50 * k, 1008 * k, 365 * k], fill='#262b30')
    for i in range(6): d.rectangle([826 * k, (66 + i * 48) * k, 994 * k, (78 + i * 48) * k], fill='#353b42'); d.rectangle([826 * k, (84 + i * 48) * k, 936 * k, (92 + i * 48) * k], fill='#353b42')
    d.rectangle([0, 420 * k, 1024 * k, 576 * k], fill='#23282d')
    for i, (cl, y) in enumerate([('#4c7396', 20), ('#5d8a6a', 60), ('#b0835a', 100)]):
        x = 30
        while x < 1000:
            w = 60 + ((x * 7 + i * 13) % 150); d.rectangle([x * k, (430 + y) * k, (x + w) * k, (460 + y) * k], fill=cl); x += w + 10
    d.rectangle([470 * k, 424 * k, 473 * k, 574 * k], fill='#e8574a')
    im.save('img/screen_editor.png')

def channel():
    im = Image.new('RGB', (1024 * S, 576 * S), '#f7f8f9'); d = ImageDraw.Draw(im); k = S
    d.rectangle([0, 0, 1024 * k, 48 * k], fill='#ffffff'); d.rectangle([0, 48 * k, 1024 * k, 50 * k], fill='#e4e7ea')
    d.ellipse([36 * k, 74 * k, 124 * k, 162 * k], fill='#2f4a66'); d.text((80 * k, 118 * k), 'AI', font=G6(38 * k), fill='#f2f5f7', anchor='mm')
    d.text((144 * k, 80 * k), 'まさやん【AIギルドch】', font=G6(34 * k), fill='#1f2a33')
    d.text((144 * k, 128 * k), 'チャンネル登録者 3,462人', font=G3(24 * k), fill='#56636d')
    d.rectangle([820 * k, 92 * k, 980 * k, 142 * k], fill='#1f2a33'); d.text((900 * k, 117 * k), '登録済み', font=G6(24 * k), fill='#f7f8f9', anchor='mm')
    titles = ['Claude Code', 'MCPサーバー', 'AI導入の相談', '自動化の設計', 'API開発', '仕事の効率化', 'デモの準備', 'ライブ配信']
    cols = ['#34597a', '#3f6b5a', '#6a4a3a', '#44506a', '#2f4a66', '#5a6a3a', '#6a3a4a', '#3a5a6a']
    for i, tt in enumerate(titles):
        x, y = 40 + (i % 4) * 244, 196 + (i // 4) * 188
        d.rectangle([x * k, y * k, (x + 224) * k, (y + 126) * k], fill=cols[i]); d.text(((x + 14) * k, (y + 46) * k), tt, font=G6(26 * k), fill='#f5f7f8')
        d.rectangle([x * k, (y + 136) * k, (x + 190) * k, (y + 148) * k], fill='#1f2a33'); d.rectangle([x * k, (y + 156) * k, (x + 120) * k, (y + 166) * k], fill='#9aa7b1')
    im.save('img/screen_channel.png')

def outside(mode):
    W, H = 1600, 1200
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    stops = {'day': [(0, (0x8f, 0xb2, 0xcc)), (0.7, (0xdc, 0xe7, 0xee)), (1, (0xee, 0xf2, 0xf3))],
             'dusk': [(0, (0x2c, 0x3a, 0x60)), (0.55, (0xc9, 0x78, 0x6a)), (1, (0xf0, 0xa8, 0x78))],
             'night': [(0, (0x07, 0x0b, 0x16)), (0.7, (0x1a, 0x23, 0x40)), (1, (0x2a, 0x30, 0x50))]}[mode]
    for y in range(H):
        t = y / H
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= t <= b: u = (t - a) / (b - a); d.line([0, y, W, y], fill=tuple(int(x + (z - x) * u) for x, z in zip(ca, cb))); break
    rnd = random.Random(77)
    for layer in range(2):
        x = -30
        while x < W + 30:
            w = rnd.uniform(90, 210); hh = rnd.uniform(250, 590) if layer else rnd.uniform(440, 820)
            col = {'day': ('#a4b3bd', '#7d8e9a'), 'dusk': ('#3b3a4c', '#2a2b3a'), 'night': ('#161a26', '#0d0f18')}[mode][layer]
            d.rectangle([x, H - hh, x + w, H], fill=col)
            p = {'day': 0.25, 'dusk': 0.45, 'night': 0.55}[mode]
            for yy in range(int(H - hh + 30), H - 10, 44):
                for xx in range(int(x + 18), int(x + w - 18), 36):
                    if rnd.random() < p: d.rectangle([xx, yy, xx + 15, yy + 19], fill='#ffc478' if mode != 'day' else '#e6eef4')
            x += w + rnd.uniform(6, 30)
    im = im.filter(ImageFilter.GaussianBlur(3))   # a real window view is out of focus
    im.save(f'img/outside_{mode}.png')

def note():
    im = Image.new('RGB', (768, 576), '#fbfbf8'); d = ImageDraw.Draw(im)
    for y in range(120, 576, 88): d.line([32, y, 736, y], fill='#d6dfe7', width=3)
    d.text((384, 192), '登録者', font=HAND(88), fill='#23303a', anchor='mm'); d.text((384, 380), '3,462', font=HAND(172), fill='#23303a', anchor='mm')
    im.save('img/note.png')

def calendar():
    im = Image.new('RGB', (768, 960), '#fdfdfc'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 768, 140], fill='#2f4a66'); d.text((384, 72), '9月', font=MIN(80), fill='#f2f5f7', anchor='mm')
    n = 1
    for r in range(5):
        for c in range(7):
            if r * 7 + c < 1 or n > 30: continue
            d.text((60 + c * 108, 224 + r * 104), str(n), font=G3(40), fill='#56636d', anchor='mm'); n += 1
    st = Image.new('RGBA', (400, 240), '#cfe3f0'); sd = ImageDraw.Draw(st)
    sd.text((200, 80), 'デモ準備', font=HAND(60), fill='#1f2a33', anchor='mm'); sd.text((200, 168), '4時間 → 20分', font=HAND(58), fill='#1f2a33', anchor='mm')
    st = st.rotate(3.5, expand=True, resample=Image.BICUBIC); im.paste(st, (200, 560), st)
    im.save('img/calendar.png')

def badge(color, i):
    im = Image.new('RGB', (320, 440), '#fbfbf8'); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 320, 108], fill=color); d.text((160, 250), '登壇者', font=G6(68), fill='#1f2a33', anchor='mm')
    d.rectangle([60, 320, 260, 336], fill='#9aa7b1'); d.rectangle([88, 360, 232, 376], fill='#9aa7b1')
    im.save(f'img/badge_{i}.png')

def plate():
    im = Image.new('RGB', (2244, 290), '#b8904a'); d = ImageDraw.Draw(im)
    d.text((1122, 150), 'Miyabiya Studio ・ 縮尺 1/12', font=MIN(120), fill='#2a2014', anchor='mm')
    im.save('img/plate.png')

editor(); channel(); note(); calendar(); plate()
for m in ('day', 'dusk', 'night'): outside(m)
for i, c in enumerate(['#2f4a66', '#6b2a24', '#2e4a3a', '#44506a', '#8a6628']): badge(c, i)
print('ok')
