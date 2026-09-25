"""公開前の最終確認で直した文言 (2026-09-25)。ビルドと検査 (validate_home.py) の両方で同じ置き換えを使う。"""
REPLACEMENTS = [
    ('開発、AI導入支援、製品PR、登壇のご相談をお受けしています。', '開発、AI導入支援、製品PR、登壇、動画編集のご相談をお受けしています。'),
    ('開発、AI導入、製品PR、登壇、採用、どのご相談も入口は同じです', '開発、AI導入、製品PR、登壇、動画編集、採用、どのご相談も入口は同じです'),
    ('実務・個人でのAI活用、YouTube運営、技術登壇の実績をご紹介します。', '実務・個人でのAI活用、YouTube運営、技術登壇、個人開発の実績をご紹介します。'),
]


def apply(text):
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text
