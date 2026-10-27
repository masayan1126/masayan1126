"""Fetch official, provider-subsetted fonts for a private design comparison."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SITE = PROJECT / 'output/editorial-concept/site'
PAGES = ['', 'profile', 'works', 'talks', 'membership', 'pricing', 'contact']

def get(url):
    request = Request(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'})
    with urlopen(request, timeout=60) as response:
        return response.read()

def fetch():
    chars = set(chr(c) for c in range(32, 127))
    for page in PAGES:
        soup = BeautifulSoup((SITE / page / 'index.html').read_text(), 'html.parser')
        for node in soup.select('script,style'):
            node.decompose()
        chars.update(soup.get_text())
    chars.update('主な活動技術発信料金を見積もるご相談の種類お名前会社名メールアドレスお問い合わせ送信する')
    text = ''.join(sorted(chars))
    assets = HERE / 'assets'
    assets.mkdir(exist_ok=True)

    def family(option):
        key = option['id']
        query = urlencode({'family':option['family'] + ':wght@400;700','text':text,'display':'swap'})
        css_url = 'https://fonts.googleapis.com/css2?' + query
        css = get(css_url).decode()
        faces = []
        for block in re.findall(r'@font-face\s*\{([^}]+)\}', css):
            weight = int(re.search(r'font-weight:\s*(\d+)', block)[1])
            url, fmt = re.search(r'url\(([^)]+)\)\s*format\([\'"]([^\'"]+)', block).groups()
            assert fmt in ('woff2', 'truetype'), fmt
            data = get(url)
            assert data[:4] in (b'wOF2', b'\x00\x01\x00\x00')
            filename = f'{key}-{weight}.' + ('woff2' if fmt == 'woff2' else 'ttf')
            (assets / filename).write_bytes(data)
            faces.append({'weight':weight,'file':filename,'format':fmt,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source':url})
        assert sorted(face['weight'] for face in faces) == [400, 700], option['family']
        license_url = f'https://raw.githubusercontent.com/google/fonts/main/ofl/{option["directory"]}/OFL.txt'
        license_text = get(license_url)
        assert b'SIL OPEN FONT LICENSE' in license_text
        (assets / f'{key}-OFL.txt').write_bytes(license_text)
        return {**option,'source':'https://fonts.google.com/specimen/' + option['family'].replace(' ', '+'),'license':'SIL Open Font License 1.1','license_url':license_url,'faces':faces}

    options = json.loads((HERE / 'options.json').read_text())
    records = list(ThreadPoolExecutor(5).map(family, options))
    manifest = {'characters':text,'characters_sha256':hashlib.sha256(text.encode()).hexdigest(),'provider':'Google Fonts','options':records}
    (assets / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'families':len(records),'files':sum(len(row['faces']) for row in records),'bytes':sum(face['bytes'] for row in records for face in row['faces'])}))

if __name__ == '__main__':
    fetch()
