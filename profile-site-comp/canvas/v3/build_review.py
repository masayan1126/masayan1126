"""Build one local review page. Never copy it into the public site export."""
from pathlib import Path
import subprocess
HERE = Path(__file__).resolve().parent
subprocess.run(['node', str(HERE / 'build_pricing_flows.mjs')], check=True)
PAGES = [('/', 'トップ'), ('/site-review/', '今回の改善'), ('/site-audit/', '変更前の監査'), ('/profile/', 'プロフィール'), ('/works/', '実績'), ('/services/', 'サービス'), ('/media/', 'PR・発信'), ('/talks/', '登壇'), ('/membership/', 'メンバーシップ'), ('/pricing/', '見積もり'), ('/contact/', 'お問い合わせ'), ('/pricing-flows/', '以前の比較3案'), ('/pricing-review/', '料金・条件の確認')]
tabs = ''.join(f'<button role="tab" id="page-{i}" data-path="{path}" aria-controls="preview" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}">{name}</button>' for i, (path, name) in enumerate(PAGES))
source = (HERE / 'review-template.html').read_text().replace('%%TABS%%', tabs)
source = source.replace('<div class="tools">', '<div class="tools"><select id="review-width" aria-label="確認する画面幅"><option value="">PC幅</option><option value="390">390px</option><option value="320">320px</option><option value="768">768px</option></select>')
source = source.replace('.mobile iframe{width:390px', '.mobile iframe{width:var(--review-width,390px)')
source = source.replace('</style>', '.tools select{font:inherit;font-size:12px;min-height:38px;background:white;color:#252c33;border:1px solid #b5bec8;max-width:90px}</style>')
source = source.replace("document.querySelector('#expand').onclick", "document.querySelector('#review-width').onchange=e=>{const width=e.target.value;preview.classList.toggle('mobile',!!width);preview.style.setProperty('--review-width',(width||390)+'px');document.querySelector('#phone').setAttribute('aria-pressed',String(!!width));document.querySelector('#phone').textContent=width?'PC幅':'スマホ幅'};\ndocument.querySelector('#expand').onclick")
out = HERE.parents[1] / 'output/3d-mode/review.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source)
print(out)
