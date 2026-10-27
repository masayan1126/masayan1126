"""Local website copy and contact entry; quote content stays unchanged."""
import re
from urllib.parse import urlsplit

# Only interface labels and instructions. Do not rename priced work or archived
# terms: those descriptions are shared by the screen, PDF and inquiry summary.
UI_COPY = {
    'AI導入支援': 'AI活用支援',
    'PR動画制作の見積もり': 'PR制作のお見積もり',
    '← YouTube・PR・コラボ': '← 製品PR・動画制作',
    'ご希望のPRから、見積もりを作れます': 'PR制作の概算料金を確認する',
    '本編・ショート動画・X投稿を選び、事前検証や企画・台本作成、ショートの制作方法を指定できます。最後に概算見積書と、ほかの組み合わせの見積もりをご確認いただけます。': '制作内容を選ぶと、概算料金と明細を確認できます。',
    '<p class="sheet-note">回答はあとから変更できます。共有URL・PDF保存にも対応しています。</p>': '',
    'どの内容が合うか迷われる場合は、<a href="/contact/?type=pr#contact-form">PRについて相談する</a>から、お気軽にお問い合わせください。': '制作内容がお決まりでない場合は、<a href="/contact/?type=pr#contact-form">PR制作についてご相談ください</a>。',
    'どのPRをご希望ですか？': 'ご希望のPR形式をお選びください',
    'ショート動画をどのように制作しますか？': 'ショート動画の制作方法をお選びください',
    'ご希望の制作・掲載先をお選びください。複数選択できます。': '複数選択できます。',
    '本編の素材を使う範囲であれば、追加の制作料金はかかりません。Xでのシェアは、制作物の選択画面で別に選べます。': 'Xでのシェアは別に選択できます。',
    '選択内容はあとから変更できます。最後に概算金額と明細をご確認いただけます。': '選択内容はあとから変更できます。',
    '<p>ご検討や社内共有にご利用ください。選択内容の変更とPDF保存ができます。</p>': '',
    '選んだ内容の見積もり': '選択した内容の見積もり',
    'この見積もりでPRを相談する': 'この見積もりについて相談する',
    'この内容でPRを相談する': 'この見積もりについて相談する',
    '選んだ案と同額です。': '選択中の見積もりと同額です。',
    '選んだ案から＋': '選択中の見積もりとの差額：＋',
    '選んだ案から−': '選択中の見積もりとの差額：−',
    'この案の明細・条件を見る': '明細・条件を確認する',
    'この案で見積書を作る': 'この組み合わせで見積もる',
    '別の組み合わせも自動でお見積もりしました': '組み合わせ別の概算料金',
    'ほかの組み合わせもご検討いただけます': 'ほかの組み合わせと料金を比較',
    '資料・サムネイルの選択、修正回数、ご希望の内容を引き継いでいます。案を選ぶまで、現在の見積書は変わりません。金額が分かる案から低い順に表示しています。': '選択したオプション・修正回数・ご希望を反映しています。',
    '↑ 選んだ見積書に戻る': '↑ 選択中の見積書に戻る',
    'ほかの6案もできています': 'ほかの6通りの見積もり',
    '本編・ショート・Xの別の組み合わせと比べられます': '本編・ショート・Xの組み合わせ別に料金を比較できます',
    '6案を比べる': 'ほかの見積もりを比較する',
    '概算見積書をPDFで保存しました。': '概算見積書のPDFダウンロードを開始しました。',
    'とりあえず相談する': 'この見積もりについて相談する',
    '見積もり内容を入力しました。製品名・公開時期・お名前などを追記し、内容を確認して送信してください。': '見積もりを入力しました。製品名・公開希望時期を追記してください。',
    '見積もり内容を引き継げませんでした。見積もり画面で相談文をコピーして、ご相談内容へ貼り付けてください。': '見積もり内容を引き継げませんでした。見積もりの共有URLをご相談内容に貼り付けてください。',
    '見積もり内容を引き継げませんでした。表示した相談文をコピーし、PRの相談フォームへ貼り付けてください。': '見積もり内容を引き継げませんでした。見積もりの共有URLをご相談内容に貼り付けてください。',
    '入力中のご相談内容を保持しました。見積もり内容は、見積もり画面からコピーして追記できます。': '入力中のご相談内容を保持しました。見積もりの共有URLを追記できます。',
}


def refine_ui_copy(text):
    for before, after in UI_COPY.items():
        text = text.replace(before, after)
    return text


def centralize_quote_controls(text):
    """Remove inquiry actions from local calculator templates, keeping summaries."""
    text = re.sub(r'<a\b(?=[^>]*\bdata-quote-(?:inquiry|fallback)\b)[^>]*>.*?</a>', '', text, flags=re.S)
    text = re.sub(r'<button\b(?=[^>]*\bdata-quote-copy\b)[^>]*>.*?</button>', '', text, flags=re.S)
    return re.sub(r'<a\b(?=[^>]*\bid="estimate-inquiry-email")[^>]*>.*?</a>', '', text, flags=re.S)


def relocate_pr_links(soup):
    """The local PR destination is the homepage video, including old breadcrumbs."""
    for anchor in soup.select('a[href]'):
        url = urlsplit(anchor['href'])
        if not url.scheme and not url.netloc and url.path.rstrip('/') in ('/media', '/media/index.html'):
            anchor['href'] = '/#product-pr'


def centralize_contact_page(soup, page):
    """Keep the header as the only contact entry outside the contact page."""
    if page == 'contact':
        return
    main = soup.select_one('main')
    if main is None:
        return
    for section in list(main.select('.focus-invitation, .a-invitation')):
        section.decompose()
    for anchor in list(main.select('a[href]')):
        if urlsplit(anchor['href']).path.rstrip('/') != '/contact':
            continue
        paragraph = anchor.find_parent('p')
        if paragraph and paragraph.find_parent(id='pricing-wizard'):
            paragraph.decompose()
        else:
            anchor.decompose()
    # The archived calculator still writes to these IDs. Keep its DOM contract
    # without exposing an email action outside the contact page.
    for control in main.select('#estimate-mail'):
        control['data-centralized-contact'] = ''
        control['hidden'] = ''
    for group in list(main.select('.actions, .editorial-actions')):
        if not group.find(['a', 'button']):
            group.decompose()
