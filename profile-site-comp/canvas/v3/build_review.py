"""Build one local review page. Never copy it into the public site export."""
from pathlib import Path
import subprocess
HERE = Path(__file__).resolve().parent
subprocess.run(['node', str(HERE / 'build_pricing_flows.mjs')], check=True)
PAGES = [('/pricing/', '採用した見積もり'), ('/pricing-flows/', '以前の比較3案'), ('/pricing-review/', '料金・条件の確認'), ('/', 'トップ'), ('/profile/', 'プロフィール'), ('/works/', '実績'), ('/services/', 'サービス'), ('/media/', '発信'), ('/talks/', '登壇'), ('/membership/', 'メンバーシップ'), ('/contact/', 'お問い合わせ')]
tabs = ''.join(f'<button role="tab" id="page-{i}" data-path="{path}" aria-controls="preview" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}">{name}</button>' for i, (path, name) in enumerate(PAGES))
source = (HERE / 'review-template.html').read_text().replace('%%TABS%%', tabs).replace('title="トップ" src="/"', 'title="採用した見積もり" src="/pricing/"')
out = HERE.parents[1] / 'output/3d-mode/review.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source)
print(out)
