"""Download the standard Japanese/Latin font distribution, with unicode ranges."""
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
OUT = HERE / 'assets/fonts/ibm-plex-sans-jp'
CSS_URL = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;700&display=swap'
LICENSE_URL = 'https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexsansjp/OFL.txt'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'

def get(url):
    with urlopen(Request(url, headers={'User-Agent':UA}), timeout=60) as response:
        return response.read()

def fetch():
    OUT.mkdir(parents=True, exist_ok=True)
    css = get(CSS_URL).decode()
    blocks = re.findall(r'@font-face\s*\{[^}]+\}', css)
    assert blocks and 'text=' not in CSS_URL

    def face(block):
        weight = int(re.search(r'font-weight:\s*(\d+)', block)[1])
        assert weight in (400, 700)
        url = re.search(r'url\(([^)]+)\)', block)[1]
        assert url.startswith('https://fonts.gstatic.com/s/ibmplexsansjp/')
        data = get(url)
        assert data[:4] == b'wOF2'
        digest = hashlib.sha256(data).hexdigest()
        filename = f'{weight}-{digest[:16]}.woff2'
        (OUT / filename).write_bytes(data)
        relative = '/editorial-assets/fonts/ibm-plex-sans-jp/' + filename
        unicode_range = re.search(r'unicode-range:\s*([^;]+)', block)[1]
        return block.replace(url, relative), {'weight':weight,'file':filename,'bytes':len(data),'sha256':digest,'unicodeRange':unicode_range,'source':url}

    records = list(ThreadPoolExecutor(16).map(face, blocks))
    license_text = get(LICENSE_URL)
    assert b'SIL OPEN FONT LICENSE' in license_text
    (OUT / 'OFL.txt').write_bytes(license_text)
    (OUT / 'font-faces.css').write_text('/* IBM Plex Sans JP, normal distribution. License: OFL.txt. */\n'+'\n'.join(record[0] for record in records)+'\n')
    manifest = {'family':'IBM Plex Sans JP','weights':[400,700],'source':CSS_URL,'license':LICENSE_URL,'coverage':'Standard Google Fonts distribution; not limited to page text','faces':[record[1] for record in records]}
    (OUT / 'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'faces':len(records),'bytes':sum(record[1]['bytes'] for record in records)}))

if __name__ == '__main__':
    fetch()
