"""Visitor actions and local indexes shared by the public pages."""
from html import escape

PRIMARY_NAV = (
    ('services', '/services/', '事業内容'),
    ('works', '/works/', '実績・成果'),
    ('media', '/media/', 'YouTube・PR・コラボ'),
    ('pricing', '/pricing/', 'PR動画の見積もり'),
)

PAGE_TOOLS = {
    'profile': (('採用・業務委託を相談する', '/contact/?type=recruit#contact-form'),
                ('実績・成果を見る', '/works/'),
                (('経歴', '#career-history'), ('技術スタック', '#tech-stack'), ('採用・業務委託について', '#career'))),
    'works': (('開発・AI導入を相談する', '/contact/?type=web#contact-form'),
              ('依頼できることを見る', '/services/'), ()),
    'services': (('仕事を相談する', '/contact/#contact-form'),
                 ('実績・成果を見る', '/works/'),
                 (('Webサービス開発', '#web-development'), ('AI導入支援', '#ai-adoption'),
                  ('製品PR', '#product-pr'), ('技術登壇', '#tech-talks'), ('動画編集', '#video-editing'))),
    'media': (('PR動画の料金を見積もる', '/pricing/'),
              ('PR・コラボを相談する', '/contact/?type=pr#contact-form'),
              (('PR動画の制作実績', '#pr-works'), ('視聴者データ', '#mediakit'),
               ('代表的な動画', '#videos'), ('制作の進め方', '#channel-story'))),
    'talks': (('登壇を相談する', '/contact/?type=talk#contact-form'),
              ('登壇実績・スライドを見る', '#talks'),
              (('テーマ・対応形式', '#talk-request'), ('過去の登壇', '#talks'))),
    'membership': (('特典・料金を詳しく見る', 'https://masayan-ai-tech-ch.pages.dev/membership/'),
                   ('YouTubeで加入する', 'https://www.youtube.com/@masayan-ai-hack/join'), ()),
    'contact': (None, None, (('相談フォーム', '#contact-form'), ('メール・SNSで連絡する', '#contact'), ('ご依頼の流れ', '#flow'))),
}


def action(label, href, tier='primary'):
    return f'<a class="site-action site-action-{tier}" data-site-action="{tier}" href="{escape(href, quote=True)}">{escape(label)}<span aria-hidden="true">→</span></a>'


def page_tools(key):
    primary, secondary, index = PAGE_TOOLS[key]
    actions = '<div class="page-actions">' + action(*primary) + action(*secondary, tier='secondary') + '</div>' if primary else ''
    links = '<nav class="page-index" aria-label="このページの内容">' + ''.join(f'<a href="{href}">{label}</a>' for label, href in index) + '</nav>' if index else ''
    return actions + links


def main_nav(key):
    return '<nav aria-label="メインメニュー">' + ''.join(
        '<a href="' + href + '"' + (' aria-current="page"' if key == page else '') + '>' + label + '</a>'
        for page, href, label in PRIMARY_NAV) + '</nav>'


def menu_links(key, paths, titles):
    groups = (('ご依頼・ご相談', ('services', 'media', 'pricing', 'talks', 'contact')),
              ('人物・活動', ('home', 'works', 'profile')))
    return ''.join('<div class="menu-group"><p>' + heading + '</p><nav class="menu-links" aria-label="' + heading + '">' + ''.join(
        '<a href="' + paths[page] + '"' + (' aria-current="page"' if key == page else '') + '>' + titles[page] + '</a>'
        for page in pages) + '</nav></div>' for heading, pages in groups)
