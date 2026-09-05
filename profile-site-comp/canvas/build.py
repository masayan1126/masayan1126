#!/usr/bin/env python3
"""サイトカンプのアートボードを組み立て、公開用アーティファクトHTMLまで作る。

  python3 build.py <元アーティファクトの保存HTML> <出力HTML>

- Main.dc.html / Mobile.dc.html = helmet_orig.html の CSS + extra.css + body.tmpl.html
- RateCard.dc.html はそのまま
- canvas.json は annotations を書き換える
- 元アーティファクトの appifact-doc (JSON) の files を差し替えて出力する
"""
from __future__ import annotations
import json, re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = pathlib.Path('/private/tmp/claude-501/-Users-masayan-git-content-youtube-deep-tech/f2ee690b-61a3-4244-ab08-9a4ffa13fef6/scratchpad')

def svg(size: int, inner: str) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')

ICONS = {
    'ARROW': svg(16, '<path d="M4 12h14"></path><path d="M13 6l6 6-6 6"></path>'),
    'CHECK': svg(16, '<path d="M5 12.5l4.5 4.5L19 7"></path>'),
    'MIC': svg(16, '<rect x="9" y="3.5" width="6" height="11" rx="3"></rect><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0"></path><path d="M12 18v2.5"></path>'),
    'CODE': svg(24, '<path d="M8.5 7.5L4 12l4.5 4.5"></path><path d="M15.5 7.5L20 12l-4.5 4.5"></path><path d="M13.5 5l-3 14"></path>'),
    'CODE16': svg(16, '<path d="M8.5 7.5L4 12l4.5 4.5"></path><path d="M15.5 7.5L20 12l-4.5 4.5"></path><path d="M13.5 5l-3 14"></path>'),
    'ARCH': svg(24, '<rect x="3" y="4" width="6" height="5" rx="1.5"></rect><rect x="15" y="4" width="6" height="5" rx="1.5"></rect><rect x="9" y="15" width="6" height="5" rx="1.5"></rect><path d="M6 9v3h12V9"></path><path d="M12 12v3"></path>'),
    'PEOPLE': svg(24, '<path d="M4 7.5h8"></path><path d="M17.5 7.5H20"></path><circle cx="14.5" cy="7.5" r="2.5"></circle><path d="M4 16.5h3"></path><path d="M12.5 16.5H20"></path><circle cx="9.5" cy="16.5" r="2.5"></circle>'),
    'VIDEO': svg(24, '<rect x="3" y="6" width="13" height="12" rx="2"></rect><path d="M16 10.5l5-2.5v8l-5-2.5"></path>'),
    'VIDEO16': svg(16, '<rect x="3" y="6" width="13" height="12" rx="2"></rect><path d="M16 10.5l5-2.5v8l-5-2.5"></path>'),
    'CHAT': svg(16, '<path d="M4 5h16v11h-9l-4 3.5V16H4z"></path>'),
    'DOC': svg(16, '<path d="M7 3h7l4 4v14H7z"></path><path d="M14 3v4h4"></path><path d="M10 12h4.5"></path><path d="M10 16h4.5"></path>'),
    'PEN': svg(16, '<path d="M4 20l4-1L19 8l-3-3L5 16z"></path><path d="M13 8l3 3"></path>'),
}
# 発信するカードのアイコンだけ 24px のマイクにする
ICONS['MIC24'] = svg(24, '<rect x="9" y="3.5" width="6" height="11" rx="3"></rect><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0"></path><path d="M12 18v2.5"></path>')

from urllib.parse import quote
MAIL = 'contact@msyn.me'
def mailto(subject: str, body: str) -> str:
    return f'mailto:{MAIL}?subject={quote(subject)}&amp;body={quote(body)}'
MAILTOS = {
    'MAILTO_GENERAL': mailto('ご相談 (Miyabiya Studio)', '相談内容:\n希望時期:\n予算 (未定でも可):\n'),
    'MAILTO_DEV': mailto('開発・AI導入の相談', '相談内容 (Webサービスの開発 / AIの品質改善 / 社内へのAI導入):\n現状と困りごと:\n希望時期:\n予算 (未定でも可):\n'),
    'MAILTO_PR': mailto('製品PRの相談', '製品・サービス名:\n希望するプラン (未定でも可):\n希望時期:\n予算:\n'),
    'MAILTO_PLAN1': mailto('製品PRの相談 (新機能を短く紹介する / 10分未満)', '製品・サービス名:\n紹介したい機能:\n希望時期:\n'),
    'MAILTO_PLAN2': mailto('製品PRの相談 (操作を実演して紹介する / 10〜20分)', '製品・サービス名:\n紹介したい内容:\n希望時期:\n'),
    'MAILTO_PLAN3': mailto('製品PRの相談 (複数機能を比較・検証する / 20〜30分)', '製品・サービス名:\n比較・検証したい機能:\n希望時期:\n'),
    'MAILTO_COLLAB': mailto('コラボ企画の相談', '企画内容:\n出演先 (どちらのチャンネルか):\n費用の有無:\n希望時期:\n'),
    'MAILTO_TALK': mailto('登壇のご依頼', '開催日:\n形式 (オンライン / オフライン・場所):\n対象者:\n持ち時間:\n希望テーマ:\n'),
    'MAILTO_HIRE': mailto('採用について', '企業名:\n募集職種:\n雇用形態 (正社員 / 業務委託 / 技術顧問):\n'),
    'MAILTO_CV': mailto('職務経歴書の依頼', '企業名:\n用途:\n'),
    'MAILTO_CONTRACT': mailto('業務委託・技術顧問の相談', '内容:\n想定する稼働量:\n期間:\n'),
}
ICONS['DOC18'] = svg(18, '<path d="M7 3h7l4 4v14H7z"></path><path d="M14 3v4h4"></path><path d="M10 12h4.5"></path><path d="M10 16h4.5"></path>')

HEAD = ('<!doctype html>\n<html lang="ja">\n<head>\n  <meta charset="utf-8">\n'
        '  <script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n')
TAIL = '\n</x-dc>\n</body>\n</html>\n'


def build_main(orig_main: str) -> str:
    helmet = (SCRATCH / 'helmet_orig.html').read_text(encoding='utf-8')
    extra = (HERE / 'extra.css').read_text(encoding='utf-8')
    assert helmet.count('</style>') == 1
    helmet = helmet.replace('</style>', extra + '\n  </style>')
    # 色地: 生成り #F9F7F3 → 案A #F7F7F5 (2026-09-04 ユーザー選択)
    assert helmet.count('#F9F7F3') == 3, helmet.count('#F9F7F3')
    helmet = helmet.replace('#F9F7F3', '#F7F7F5')
    body = (HERE / 'body.tmpl.html').read_text(encoding='utf-8')
    body = body.replace('{RATECARD}', (HERE / 'ratecard.tmpl.html').read_text(encoding='utf-8'))
    vids = json.loads((HERE / 'videos.json').read_text(encoding='utf-8'))
    cards = ''.join(
        f'      <a class="vcard" href="https://youtu.be/{v["id"]}"><img src="thumb-{v["id"]}.webp" alt=""><div class="vb"><h3>{v["title"]}</h3>'
        f'<p class="vm">{v["views"]:,}回再生 ／ {v["month"]}</p></div></a>\n' for v in vids)
    videos = ('  <div class="sec" id="videos"><div class="wrap">\n    <h2 class="sec-h">代表的な動画</h2>\n'
              '    <p class="sec-lead">Claude Codeを中心に、チャンネルの方向性が分かる本編3本です。話し方と内容は、こちらでご確認いただけます。</p>\n'
              '    <div class="videos">\n' + cards + '    </div>\n'
              '    <div class="aud grid1">\n' + (HERE / 'membership-card.tmpl.html').read_text(encoding='utf-8') + '    </div>\n  </div></div>\n')
    body = body.replace('{VIDEOS}', videos)
    # 発信するカードのマイクだけ 24px
    body = body.replace('<div class="icochip">{MIC}</div>', '<div class="icochip">{MIC24}</div>')
    for k, v in ICONS.items():
        body = body.replace('{' + k + '}', v)
    left = re.findall(r'\{[A-Z0-9]+\}', body)
    assert not left, f'unreplaced placeholders: {left}'
    # DS の文言規則: 見出しの末尾に句点を付けない
    for tag in ('h1', 'h2', 'h3', 'h4'):
        assert not re.search(r'。\s*</' + tag + '>', body), f'句点で終わる見出しがある ({tag})'
    # helmet 内に生の & が無いこと (あると全スタイルが死ぬ)
    assert '&' not in helmet, 'helmet に生の & がある'
    return HEAD + helmet + '\n' + body + TAIL


def build_v2() -> str:
    helmet = (SCRATCH / 'helmet_orig.html').read_text(encoding='utf-8')
    extra = (HERE / 'extra.css').read_text(encoding='utf-8') + (HERE / 'extra-v2.css').read_text(encoding='utf-8')
    helmet = helmet.replace('</style>', extra + '\n  </style>').replace('#F9F7F3', '#F7F7F5')
    body = (HERE / 'body-v2.tmpl.html').read_text(encoding='utf-8')
    body = body.replace('{RATECARD}', (HERE / 'ratecard-v2.tmpl.html').read_text(encoding='utf-8'))
    vids = json.loads((HERE / 'videos.json').read_text(encoding='utf-8'))
    cards = ''.join(
        f'      <a class="vcard" href="https://youtu.be/{v["id"]}"><img src="thumb-{v["id"]}.webp" alt=""><div class="vb">'
        + ('<span class="first">まず見る1本</span>' if v.get('first') else '')
        + f'<h3>{v["title"]}</h3><p class="vd">{v["desc"]}</p><p class="vm">{v["views"]:,}回再生 ／ {v["month"]}公開</p></div></a>\n' for v in vids)
    body = body.replace('{VIDEO_CARDS_V2}', cards.rstrip('\n'))
    for k, v in MAILTOS.items():
        body = body.replace('{' + k + '}', v)
    for k, v in ICONS.items():
        body = body.replace('{' + k + '}', v)
    left = re.findall(r'\{[A-Z0-9_]+\}', body)
    assert not left, f'unreplaced placeholders (v2): {left}'
    for tag in ('h1', 'h2', 'h3', 'h4'):
        assert not re.search(r'。\s*</' + tag + '>', body), f'句点で終わる見出しがある (v2, {tag})'
    assert '&' not in helmet
    return HEAD + helmet + '\n' + body + TAIL


STRUCTURE = json.loads((HERE / 'structure.json').read_text(encoding='utf-8'))


def annotation_text(sec: dict) -> str:
    return (f"{sec['title']}\n誰に: {sec['who']}\n何のために: {sec['purpose']}\n"
            f"なぜこの位置: {sec['why_here']}\n何を載せるか: {sec['content']}\nCTA: {sec['cta']}")


ANNOTATIONS = [
    {"id": "note-purpose", "x": -420, "y": -260, "w": 340,
     "text": "このカンプの狙い\n見る人は5種類: " + " / ".join(STRUCTURE['readers'].values())
             + "。ヒーローで「誰か」を示し、直下の「ご用件から選ぶ」で5人を各セクションへ振り分け、どの入口も最後は「XのDMかメール」に着地させる。各セクションの意味付け (誰に / 何のために / なぜこの位置 / 何を載せるか / CTA) は左の付箋と structure.md が正本。配色と部品は design-system-blue (web.css)。並ぶボタンは横幅を必ず揃える"},
] + [
    {"id": f"note-{sec['id']}", "x": -420, "y": sec['y'], "w": 340, "text": annotation_text(sec)}
    for sec in STRUCTURE['sections']
] + [
    {"id": "note-mobile", "x": 2030, "y": 0, "w": 300,
     "text": "スマホ表示\n同じ内容を390px幅で組んだもの。ナビは省略してDMボタンだけ残す。ボタン群は縦積みで全幅、「ご用件から選ぶ」は縦1列。縦に長いので、公開時は実績カードの折りたたみを検討。"},
    {"id": "note-ratecard", "x": 2070, "y": -150, "w": 420,
     "text": "料金の折りたたみ (開いた状態の見本)\n本体では「YouTubeプロモーション動画の料金を見る」を押すと開く。中身は notta-partner-program の料金表 (2026-09-04版) をそのまま移した。"},
]


def write_structure_md() -> None:
    lines = ['# Miyabiya Studio サイトカンプ 構成の意味付け', '',
             '見る人は5種類。各セクションは「誰に / 何のために / なぜこの位置 / 何を載せるか / CTA」で意味付けし、答えられない要素は置かない。', '']
    for k, v in STRUCTURE['readers'].items():
        lines.append(f'- {v}')
    lines.append('')
    for i, sec in enumerate(STRUCTURE['sections'], 1):
        lines += [f"## {i}. {sec['title']} (`#{sec['id']}`)", '',
                  f"- **誰に**: {sec['who']}", f"- **何のために**: {sec['purpose']}",
                  f"- **なぜこの位置**: {sec['why_here']}", f"- **何を載せるか**: {sec['content']}",
                  f"- **CTA**: {sec['cta']}", '']
    (HERE.parent / 'structure.md').write_text('\n'.join(lines), encoding='utf-8')


def build_canvas(orig: str) -> str:
    c = json.loads(orig)
    for ab in c['artboards']:
        if ab['file'] == 'Main.dc.html':
            ab['h'] = 9600
        if ab['file'] == 'Mobile.dc.html':
            ab['h'] = 16000
    if not any(ab['file'] == 'Main-v2.dc.html' for ab in c['artboards']):
        c['artboards'].append({"file": "Main-v2.dc.html", "x": 3400, "y": 0, "w": 1440, "h": 11200,
                               "title": "デスクトップ 1440 (改訂案)", "print": "flow"})
    c['annotations'] = ANNOTATIONS + [
        {"id": "note-v2", "x": 3400, "y": -300, "w": 560,
         "text": "改訂案 (2026-09-05、35項目のレビューを反映)\n公開中のサイトは左のまま。この案は別アートボードとして置き、採用が決まってから本体に取り込む。"
                 "\n主な変更: 冒頭を名前と依頼できる仕事に具体化 / 数字は証拠の1行だけに / 用件ごとの相談ボタン (件名と本文入りのメール) / 連絡先はメールが主・X・Instagramは補助 / 事業内容を「Webサービスの開発・AIの品質改善・社内へのAI導入」に分け、納品物と完了の条件を明記 / 実績を課題・担当・実施・結果に整理 / 製品PRに数字 (直近90日の本編の再生実績・テーマの割合) と具体例、有償PRとコラボを分離 / 料金表は目的で選べる見出し・プランごとの相談ボタン・進め方と初稿の定義・二次利用の条件を整理 / メンバーシップはランクごとの特典と見本が主ボタン / 登壇テーマに対象と持ち帰り / 経歴に職務要約と、正社員・業務委託の枠を分離 / ご依頼の流れは開発・AI導入向けと明示"
                 "\n値待ち (ゲート): 在籍期間・チーム規模 / 工数削減の対象・期間・測定方法 / 月110時間の算出 / MCP実績の具体 / 勉強会の確認時点 / 制作日程の目安 / 二次利用・機密情報・納品物の文面の確認 / 登壇スライドと録画 / 発信方針の実例 / 代表リポジトリ"},
    ]
    return json.dumps(c, ensure_ascii=False, indent=2)


def main():
    src_html, out_html = sys.argv[1], sys.argv[2]
    # 元HTML (Artifact read で落とした最新版) の appifact-doc をそのまま土台にする
    _s = open(src_html, encoding='utf-8').read()
    _m = re.search(r'<script type="application/json" id="appifact-doc">\n(.*?)\n</script>', _s, re.S)
    doc = json.loads(_m.group(1))
    files = doc['content']['files']
    doc['title'] = 'Miyabiya Studio サイトカンプ'
    main_html = build_main(files['Main.dc.html'])
    (HERE / 'Main.dc.html').write_text(main_html, encoding='utf-8')
    (HERE / 'Mobile.dc.html').write_text(main_html, encoding='utf-8')
    write_structure_md()
    canvas = build_canvas(files['canvas.json'])
    (HERE / 'canvas.json').write_text(canvas, encoding='utf-8')
    files['Main.dc.html'] = main_html
    files['Mobile.dc.html'] = main_html
    files['RateCard.dc.html'] = (HERE / 'RateCard.dc.html').read_text(encoding='utf-8')
    v2 = build_v2()
    (HERE / 'Main-v2.dc.html').write_text(v2, encoding='utf-8')
    files['Main-v2.dc.html'] = v2
    files['canvas.json'] = canvas
    import base64
    for a in sorted((HERE / 'assets').glob('*.webp')):
        files[a.name] = base64.b64encode(a.read_bytes()).decode('ascii')

    s = open(src_html, encoding='utf-8').read()
    # 公開時に付く外側の骨組みを外す (先頭の <body>\n まで と 末尾の </body></html>)
    WRAP = '<!doctype html><html><head><meta charset=utf8>'
    if s.startswith(WRAP):
        i = s.index('<body>\n') + len('<body>\n')
        inner = s[i:]
        inner = re.sub(r'\n</body></html>\s*$', '\n', inner)
    else:
        inner = s  # 骨組み無しで保存された版はそのまま
    assert inner.lstrip().startswith('<!doctype html>\n<html lang="en">'), inner[:80]
    inner = inner.replace('まさやん.dev サイトカンプ', doc['title'])  # <title> と README meta
    m = re.search(r'(<script type="application/json" id="appifact-doc">\n)(.*?)(\n</script>)', inner, re.S)
    assert m
    new_json = json.dumps(doc, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    assert '</script' not in new_json
    inner = inner[:m.start(2)] + new_json + inner[m.end(2):]
    open(out_html, 'w', encoding='utf-8').write(inner)
    print('Main.dc.html chars', len(main_html))
    print('artifact html bytes', len(inner.encode('utf-8')))
    print('starts with', inner[:60].replace('\n', ' '))


if __name__ == '__main__':
    main()
