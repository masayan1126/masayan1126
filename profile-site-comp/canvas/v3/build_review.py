"""Build one local review page. Never copy it into the public site export."""
from pathlib import Path
import base64
import html
import subprocess
HERE = Path(__file__).resolve().parent
subprocess.run(['node', str(HERE / 'build_pricing_flows.mjs')], check=True)
PAGES = [('/', 'トップ'), ('/site-review/', '今回の改善'), ('/site-audit/', '変更前の監査'), ('/profile/', 'プロフィール'), ('/works/', '実績'), ('/services/', 'サービス'), ('/media/', 'PR・発信'), ('/talks/', '登壇'), ('/membership/', 'メンバーシップ'), ('/pricing/', '見積もり'), ('/contact/', 'お問い合わせ'), ('/pricing-flows/', '以前の比較3案'), ('/pricing-review/', '料金・条件の確認')]
history_pages = []
# Local studies are optional and never enter the public site export.
if (HERE.parents[1] / 'output/editorial-concept/site/index.html').exists():
    history_pages = PAGES[1:]
    PAGES = [('http://127.0.0.1:8777/', '新デザインの試作'), ('/', '従来の構成')]
references = HERE.parents[1] / 'output/site-references/references.html'
if references.exists():
    encoded = base64.b64encode(references.read_bytes()).decode()
    PAGES.insert(2, ('data:text/html;base64,' + encoded, '参考サイト10選'))
avatar_options = HERE.parents[1] / 'output/avatar-options/comparison.html'
if avatar_options.exists():
    avatar_review = HERE.parents[1] / 'output/editorial-concept/site/__review/avatar-options/index.html'
    avatar_review.parent.mkdir(parents=True, exist_ok=True)
    avatar_review.write_bytes(avatar_options.read_bytes())
    PAGES.insert(1, ('/__review/avatar-options/', 'プロフィール画像5案'))
font_options = HERE / 'prototypes/fonts/build.py'
if font_options.exists() and (font_options.parent / 'assets/manifest.json').exists() and (HERE.parents[1] / 'output/editorial-concept/site/index.html').exists():
    subprocess.run(['python3', str(font_options)], check=True)
    PAGES.insert(1, ('/__review/fonts/', 'フォント5案'))
tabs = ''.join(f'<button role="tab" id="page-{i}" data-path="{path}" aria-controls="preview" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}">{name}</button>' for i, (path, name) in enumerate(PAGES))
source = (HERE / 'review-template.html').read_text().replace('%%TABS%%', tabs)
if history_pages:
    options = ''.join(f'<option value="{html.escape(path, quote=True)}">{name}</option>' for path, name in history_pages)
    source = source.replace('<div class="tools">', '<div class="tools"><select id="review-history" aria-label="これまでの確認"><option value="">過去の確認</option>' + options + '</select>')
    source = source.replace('title="トップ" src="/"', 'title="新デザインの試作" src="http://127.0.0.1:8777/"')
    source = source.replace('</script>', """const past=document.querySelector('#review-history');
past.onchange=()=>{if(!past.value)return;for(const tab of tabs){tab.setAttribute('aria-selected','false');tab.tabIndex=-1;}tabs[0].tabIndex=0;frame.title=past.selectedOptions[0].text;preview.setAttribute('aria-labelledby','review-history');frame.src=past.value;};
tabs.forEach(tab=>{for(const event of ['click','keydown'])tab.addEventListener(event,()=>past.value='');});
</script>""")
source = source.replace('<div class="tools">', '<div class="tools"><select id="review-width" aria-label="確認する画面幅"><option value="">PC幅</option><option value="390">390px</option><option value="320">320px</option><option value="768">768px</option></select>')
source = source.replace('<select id="review-width"', '<select id="review-section" aria-label="セクションに移動"><option value="">ページ先頭</option></select><select id="review-width"')
source = source.replace('.mobile iframe{width:390px', '.mobile iframe{width:var(--review-width,390px)')
source = source.replace('</style>', '.tools select{font:inherit;font-size:12px;min-height:38px;background:white;color:#252c33;border:1px solid #b5bec8;max-width:90px}</style>')
source = source.replace('</style>', '#review-section{max-width:170px}@media(max-width:600px){#review-section{max-width:120px}}</style>')
source = source.replace("frame.addEventListener('load',()=>{", """const outline=document.querySelector('#review-section');
outline.onchange=()=>{try{const doc=frame.contentDocument;const target=outline.value?doc.getElementById(outline.value):doc.querySelector('main');for(let parent=target?.parentElement;parent;parent=parent.parentElement){if(parent.tagName==='DETAILS')parent.open=true;}target?.scrollIntoView({block:'start',behavior:'instant'});}catch{}};
frame.addEventListener('load',()=>{outline.replaceChildren(new Option('ページ先頭',''));try{frame.contentDocument.querySelectorAll('main section[id],main details[id],main .sec[id],main .works-story[id],main .career-chapters[id],main .tech-stack[id],main .mediakit[id]').forEach(section=>{const heading=section.matches('details')?section.querySelector(':scope>summary'):section.querySelector('h2,h3');if(heading)outline.add(new Option(heading.textContent.trim(),section.id));});}catch{}
""")
source = source.replace("document.querySelector('#expand').onclick", "document.querySelector('#review-width').onchange=e=>{const width=e.target.value;preview.classList.toggle('mobile',!!width);preview.style.setProperty('--review-width',(width||390)+'px');document.querySelector('#phone').setAttribute('aria-pressed',String(!!width));document.querySelector('#phone').textContent=width?'PC幅':'スマホ幅'};\ndocument.querySelector('#expand').onclick")
source = source.replace("outline.replaceChildren(new Option('ページ先頭',''));", "outline.hidden=frame.src.startsWith('http://127.0.0.1:8777/');outline.replaceChildren(new Option('ページ先頭',''));")
if (HERE.parents[1] / 'output/editorial-concept/site/index.html').exists():
    # Keep review chrome neutral too, without filtering the compared pages.
    import re
    from prototypes.editorial.monochrome import neutralize_css
    source = re.sub(r'(<style>)(.*?)(</style>)', lambda match: match[1] + neutralize_css(match[2]) + match[3], source, flags=re.S)
out = HERE.parents[1] / 'output/3d-mode/review.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source)
print(out)
