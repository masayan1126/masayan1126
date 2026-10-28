# coding: utf-8
"""Capture the public site's real share metadata for the local review."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo
import hashlib
import json
import subprocess
import sys

from bs4 import BeautifulSoup
from PIL import Image

HERE = Path(__file__).resolve().parent
V3 = HERE.parents[1]
sys.path.insert(0, str(V3))
from site_metadata import BASE, PAGES

SNAPSHOT = HERE / 'public-preview.json'


def fetch(url):
    if urlsplit(url).scheme != 'https' or urlsplit(url).netloc != urlsplit(BASE).netloc:
        raise ValueError('Only this public site may be fetched')
    with TemporaryDirectory(prefix='studio-ogp-preview-') as temp:
        output = Path(temp) / 'body'
        result = subprocess.run([
            'curl', '--fail', '--location', '--silent', '--show-error',
            '--max-time', '30', '--max-filesize', '10485760',
            '-H', 'Cache-Control: no-cache', '--output', str(output),
            '--write-out', '%{json}', url,
        ], capture_output=True, check=True)
        info = json.loads(result.stdout)
        data = output.read_bytes()
    if urlsplit(info['url_effective']).netloc != urlsplit(BASE).netloc:
        raise ValueError('Unexpected redirected host')
    return data, {'url': url, 'final_url': info['url_effective'], 'status': info['http_code'],
                  'content_type': info['content_type'], 'bytes': len(data),
                  'sha256': hashlib.sha256(data).hexdigest()}


def capture(page):
    url = BASE + '/' + (page + '/' if page else '')
    try:
        raw, response = fetch(url)
        doc = BeautifulSoup(raw, 'html.parser')
        tags = {}
        for node in doc.select('head meta[property],head meta[name]'):
            name = node.get('property') or node.get('name')
            if name.startswith(('og:', 'twitter:')) or name == 'description':
                tags[name] = node.get('content', '')
        canonical = doc.select_one('link[rel="canonical"]')
        icon = doc.select_one('link[rel~="icon"][type="image/svg+xml"]') or doc.select_one('link[rel~="icon"]')
        images = {}
        for name in ('og:image', 'twitter:image'):
            if not tags.get(name):
                continue
            image_url = urljoin(response['final_url'], tags[name])
            if image_url not in images:
                data, image_response = fetch(image_url)
                with Image.open(BytesIO(data)) as image:
                    image_response.update(width=image.width, height=image.height, format=image.format)
                images[image_url] = image_response
        missing = [name for name in ('og:title', 'og:description', 'og:image', 'twitter:card',
                                    'twitter:title', 'twitter:description', 'twitter:image') if not tags.get(name)]
        return {'key': page, 'label': PAGES[page]['label'] if page else 'トップ', 'ok': True,
                'response': response, 'title': doc.title.get_text() if doc.title else '',
                'canonical': urljoin(response['final_url'], canonical['href']) if canonical else None,
                'favicon': urljoin(response['final_url'], icon['href']) if icon else None,
                'tags': tags, 'images': images, 'missing': missing}
    except Exception as error:
        return {'key': page, 'label': PAGES[page]['label'] if page else 'トップ',
                'ok': False, 'url': url, 'error': str(error)}


def main():
    with ThreadPoolExecutor(max_workers=4) as pool:
        pages = list(pool.map(capture, PAGES))
    result = {'version': 1, 'fetched_at': datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),
              'source': BASE, 'complete': all(page['ok'] for page in pages), 'pages': pages}
    SNAPSHOT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pages': len(pages), 'complete': result['complete'], 'snapshot': str(SNAPSHOT)}))
    if not result['complete']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
