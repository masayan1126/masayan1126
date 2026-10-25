"""Build the owner-facing site review, kept outside the public export."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = [
    ('トップ', '相談とPRの見積もりを最初に提示', '実績 → 事業内容 → 詳しい経歴'),
    ('事業内容', '対応する仕事を選んで相談', '対応範囲 → 担当実績 → 種別を引き継いだフォーム'),
    ('実績・成果', '担当したことと成果を確認', '事例ごとに開発・PR・登壇の相談先へ'),
    ('YouTube・PR・コラボ', '制作内容と費用を確認', '料金 → PR制作例 → 視聴者データ → 一般の動画'),
    ('技術登壇', 'テーマと対応形式を確認して相談', '依頼条件 → 登壇実績・スライド'),
    ('プロフィール', '採用・業務委託を相談', '担当領域 → 経歴 → 技術スタック'),
    ('メンバーシップ', '特典・料金を確認して加入', '確認用のリンクと加入用のリンクを区別'),
    ('見積もり', '完成した内容でPRを相談', '相談を主操作、PDF保存と共有を補助操作に'),
    ('お問い合わせ', 'フォームから相談を送る', 'フォーム → メール・SNS → ご依頼の流れ'),
]

def build():
    rows = ''.join('<tr><th scope="row">'+name+'</th><td>'+action+'</td><td>'+order+'</td></tr>' for name, action, order in ROWS)
    page = '''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>サイト全体の改善</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f5f7;color:#202833;font:16px/1.9 -apple-system,BlinkMacSystemFont,'Hiragino Sans',sans-serif;color-scheme:light}main{max-width:1120px;margin:auto;padding:48px 24px 80px}h1{font-size:36px;line-height:1.4}h2{font-size:25px;line-height:1.5}h3{font-size:19px;margin:0 0 12px}p{max-width:48em}section{margin-top:48px}.lead{font-size:18px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.item{padding:28px;background:#fff}.item p{margin:0;color:#4c5866}.status{background:#e9eef6;padding:24px}table{width:100%;border-collapse:collapse;background:white}th,td{padding:18px;text-align:left;vertical-align:top}th{font-weight:650}tbody tr:nth-child(even){background:#f7f9fb}a{color:#133f8f;text-underline-offset:5px}a:focus-visible{outline:3px solid #133f8f;outline-offset:4px}.note{font-size:14px;color:#4c5866}.table-scroll{overflow:auto}ul{padding-left:1.3em}@media(max-width:700px){main{padding:28px 20px 56px}h1{font-size:28px}.grid{grid-template-columns:1fr}.item{padding:22px}.table-scroll table{min-width:650px}}
</style></head><body><main><h1>依頼につながる入口と、読みやすさをそろえる</h1><p class="lead">全9ページを見直し、相談する操作・依頼の判断材料・詳しい補足情報に、見た目と並びの差をつけています。</p>
<div class="status"><strong>確認する場所</strong><p>上の「トップ」「サービス」「PR・発信」「見積もり」などのタブで実画面を切り替えられます。右上の画面幅から、390px・320pxも確認できます。</p><p class="note">現在の3Dヒーローと実績の根拠、確定料金、旧見積もりURLは維持します。成約率の向上は、公開後の問い合わせ状況で確かめる必要があります。</p></div>
<section><h2>今回の変更</h2><div class="grid">
<article class="item"><h3>次の行動が分かるボタン</h3><p>相談・見積もりなどの主な操作を濃い青、詳しい内容の確認を淡い背景や下線リンクにそろえました。メニューは依頼先と人物情報に分けています。</p></article>
<article class="item"><h3>実績を、装飾より読みやすく</h3><p>カード上辺・左辺の色線と、まとまりを細かく分ける罫線を外しました。実績・料金・対応範囲を読める大きさで示し、余白と背景の違いで整理しています。</p></article>
<article class="item"><h3>短い動きで反応を伝える</h3><p>見出しや要約の出現、実績・経歴の切り替え、ボタンへの反応に短い動きを加えました。動きを減らす設定では停止し、背景映像も画面から止められます。</p></article>
<article class="item"><h3>文字・背景・入力欄を見分けやすく</h3><p>本文と背景の明暗差、補足文字、入力欄の輪郭を見直しました。キーボードの現在位置を示し、入力の誤りを対象の欄で確認できるようにしています。</p></article>
</div></section><section><h2>各ページで判断できること</h2><div class="table-scroll"><table><thead><tr><th>ページ</th><th>主な行動</th><th>情報の並び</th></tr></thead><tbody>''' + rows + '''</tbody></table></div></section>
<section><h2>変更前の点検</h2><p>「変更前の監査」タブには、実画面と30項目の診断をまとめています。変更前のAIっぽさは3/10で、主な問題は配色よりも、強調の優先順位・色線の反復・小さな文字でした。制作方法や著者を判定する点数ではありません。</p></section>
<section><h2>確認状況</h2><p id="verification-status">ビルド・料金テスト・既存本文の保持を確認しています。PC・スマホ・キーボードと公開画面の最終確認を続けています。</p><p><a href="/pricing/?items=materials%2Cthumbnail&amp;v=17268bfca1d6">以前の本編見積もりを確認する</a></p><p class="note">Gmailの下書きは変更していません。</p></section></main></body></html>'''
    target = HERE.parents[1] / 'output/3d-mode/site-improvements.html'
    target.write_text(page)
    return target

if __name__ == '__main__':
    print(build())
