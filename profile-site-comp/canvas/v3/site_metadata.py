"""One source for the approved site's search, sharing and bookmark information."""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
ASSETS = HERE / 'prototypes/editorial/assets/social'
BASE = 'https://studio.msyn.me'
SITE_NAME = 'Miyabiya Studio'
OWNER = 'Masaya Nishigaki'
ROLE = 'Web系のシニアエンジニア・テックリード'
SOCIAL_PROFILES = [
    'https://www.youtube.com/@masayan-ai-hack',
    'https://x.com/masayan_ai_hack',
    'https://www.instagram.com/miyabiya1126/',
    'https://note.com/msyn1126',
    'https://github.com/masayan1126',
]
# Title, description and the short text drawn into each sharing image.
PAGES = {
    '': {
        'label': SITE_NAME,
        'title': SITE_NAME + ' | ' + OWNER,
        'description': 'YouTubeでのAI発信・製品PR・個人開発・AI動画編集・技術登壇・AI活用支援。',
        'image_lines': ['AIの発信・製品PR・個人開発', 'AI動画編集・技術登壇・AI活用支援'],
    },
    'profile': {
        'label': 'プロフィール・職務経歴',
        'description': 'Web系のシニアエンジニア・テックリード、Masaya Nishigakiのプロフィール。職務経歴、開発経験、技術・スキルを紹介します。',
        'image_lines': ['Web系のシニアエンジニア', 'テックリード'],
    },
    'works': {
        'label': '実績紹介',
        'description': 'AI活用支援、MCPサーバー開発、製品PR動画、Chrome拡張機能の実績。担当工程と成果を掲載しています。',
        'image_lines': ['AI活用支援・MCPサーバー開発', '製品PR動画・Chrome拡張機能'],
    },
    'talks': {
        'label': '登壇・社内勉強会',
        'description': 'AI駆動開発、MCP、YouTube運営・動画制作の自動化に関する登壇実績。イベントや発表資料、対応テーマを掲載しています。',
        'image_lines': ['AI駆動開発・MCP・YouTube運営', '動画制作の自動化'],
    },
    'membership': {
        'label': 'YouTubeメンバーシップ',
        'description': 'YouTube「まさやん【AIギルドch】」のメンバーシップ。限定投稿・動画など、各プランの特典と料金を確認できます。',
        'image_lines': ['まさやん【AIギルドch】', '限定投稿・動画'],
    },
    'pricing': {
        'label': 'PR制作のお見積もり',
        'description': 'YouTube本編・ショート動画・X投稿の概算見積もりを作成できます。制作内容を選び、内訳の確認・PDF保存・URL共有ができます。未確定の料金は要相談です。',
        'image_lines': ['YouTube本編・ショート・X投稿', '概算料金・内訳・PDF'],
    },
    'contact': {
        'label': 'お問い合わせ',
        'description': '製品PR・動画編集・登壇・AI活用支援のご依頼を受け付けています。フォームに内容・希望時期・ご予算をお知らせください。通常2営業日以内に返信します。',
        'image_lines': ['製品PR・動画編集・登壇', 'AI活用支援のご依頼'],
    },
}


def asset_input_digest():
    editorial = HERE / 'prototypes/editorial'
    inputs = {'name': SITE_NAME, 'owner': OWNER, 'base': BASE,
              'generator': hashlib.sha256((HERE / 'build_og.py').read_bytes()).hexdigest(),
              'pages': {key: {'label': value['label'], 'lines': value['image_lines']} for key, value in PAGES.items()},
              'mark': hashlib.sha256((editorial / 'icons/miyabiya-mark.svg').read_bytes()).hexdigest(),
              'avatar': hashlib.sha256((editorial / 'assets/avatar-mono-pixel.png').read_bytes()).hexdigest(),
              'fonts': hashlib.sha256((editorial / 'assets/fonts/ibm-plex-sans-jp/manifest.json').read_bytes()).hexdigest()}
    return hashlib.sha256(json.dumps(inputs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def metadata(page):
    record = dict(PAGES[page])
    record.setdefault('title', record['label'] + ' | ' + SITE_NAME)
    record['url'] = BASE + '/' + (page + '/' if page else '')
    record['image_alt'] = OWNER + 'のモノクロドット絵'
    record['twitter_image_alt'] = SITE_NAME + ' — ' + (record['label'] if page else OWNER + 'の活動紹介')
    return record


def copy_assets(destination):
    destination = Path(destination)
    manifest = json.loads((ASSETS / 'manifest.json').read_text())
    assert manifest['input_sha256'] == asset_input_digest(), 'Sharing assets are stale; regenerate with canvas/v3/build_og.py'
    refs = {'og': {}, 'twitter': {}}
    for record in manifest['files']:
        source = ASSETS / record['file']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256'], source
        target = destination / record['public_path'].lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if 'page' in record:
            refs['og'][record['page']] = BASE + record['public_path']
        if 'twitter_page' in record:
            refs['twitter'][record['twitter_page']] = BASE + record['public_path']
    assert set(refs['og']) == set(refs['twitter']) == set(PAGES), 'Sharing image variants are incomplete'
    # Legacy bookmark addresses remain usable as well.
    shutil.copyfile(ASSETS / 'apple-touch-icon.png', destination / 'apple-touch-icon.png')
    return refs


def structured_data(page, image_url):
    info = metadata(page)
    person_id, site_id = BASE + '/#person', BASE + '/#website'
    webpage = {
        '@type': 'ProfilePage' if page == 'profile' else ('ContactPage' if page == 'contact' else 'WebPage'),
        '@id': info['url'] + '#webpage', 'url': info['url'], 'name': info['title'],
        'description': info['description'], 'inLanguage': 'ja',
        'isPartOf': {'@id': site_id}, 'about': {'@id': person_id},
        'primaryImageOfPage': {'@type': 'ImageObject', 'url': image_url, 'width': 1200, 'height': 630},
    }
    if page == 'profile':
        webpage['mainEntity'] = {'@id': person_id}
    return {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': site_id, 'name': SITE_NAME, 'url': BASE + '/',
         'inLanguage': 'ja', 'publisher': {'@id': person_id}},
        {'@type': 'Person', '@id': person_id, 'name': OWNER, 'alternateName': 'まさやん',
         'url': BASE + '/', 'jobTitle': ROLE,
         'image': BASE + '/editorial-assets/avatar-mono-pixel.png', 'sameAs': SOCIAL_PROFILES},
        webpage,
    ]}


def apply_metadata(doc, page, images, *, production):
    info, image = metadata(page), images['og'][page]
    twitter_image = images['twitter'][page]
    doc.title.string = info['title']

    def meta(key, value, attribute='name'):
        for old in doc.head.select(f'meta[{attribute}="{key}"]'):
            old.decompose()
        doc.head.append(doc.new_tag('meta', attrs={attribute: key, 'content': value}))

    for old in doc.head.select('link[rel="canonical"],link[rel~="icon"],link[rel="apple-touch-icon"],link[rel="manifest"],script[type="application/ld+json"]'):
        old.decompose()
    doc.head.append(doc.new_tag('link', attrs={'rel': 'canonical', 'href': info['url']}))
    for key, value in {
        'description': info['description'], 'author': OWNER, 'application-name': SITE_NAME,
        'theme-color': '#ffffff', 'color-scheme': 'light',
        'robots': 'index,follow,max-image-preview:large' if production else 'noindex,nofollow',
        'twitter:card': 'summary_large_image', 'twitter:site': '@masayan_ai_hack',
        'twitter:creator': '@masayan_ai_hack', 'twitter:title': info['title'],
        'twitter:description': info['description'], 'twitter:image': twitter_image,
        'twitter:image:alt': info['twitter_image_alt'],
    }.items():
        meta(key, value)
    for key, value in {
        'og:type': 'website', 'og:site_name': SITE_NAME, 'og:locale': 'ja_JP',
        'og:title': info['title'], 'og:description': info['description'],
        'og:url': info['url'], 'og:image': image, 'og:image:type': 'image/png',
        'og:image:width': '1200', 'og:image:height': '630', 'og:image:alt': info['image_alt'],
    }.items():
        meta(key, value, 'property')
    for attributes in [
        {'rel': 'icon', 'href': '/favicon.ico', 'sizes': '16x16 32x32 48x48'},
        {'rel': 'icon', 'href': '/icons/favicon-96.png', 'type': 'image/png', 'sizes': '96x96'},
        {'rel': 'icon', 'href': '/favicon.svg', 'type': 'image/svg+xml', 'sizes': 'any'},
        {'rel': 'apple-touch-icon', 'href': '/icons/apple-touch-icon.png', 'sizes': '180x180'},
        {'rel': 'manifest', 'href': '/site.webmanifest'},
    ]:
        doc.head.append(doc.new_tag('link', attrs=attributes))
    schema = doc.new_tag('script', attrs={'type': 'application/ld+json'})
    schema.string = json.dumps(structured_data(page, image), ensure_ascii=False).replace('<', '\\u003c')
    doc.head.append(schema)
