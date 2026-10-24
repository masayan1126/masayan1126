import {quote, summary, mailto, amountText, taxIncluded, stateFromUrl, estimateUrl, loadSharedRates, quotePresentation, comparisonQuotes} from './pricing-model.mjs';
const el = id => document.getElementById(id);
const currentData = JSON.parse(el('pricing-data').textContent);
let data = currentData;
let legacy = false;
const form = el('estimate-form');
const write = (id, text) => { el(id).textContent = text; };
const show = (id, visible) => { el(id).hidden = !visible; };
const compactAmount = (min, max) => min == null ? '要相談' :
  min === max ? min.toLocaleString('ja-JP') + '円' : min.toLocaleString('ja-JP') + '〜' + max.toLocaleString('ja-JP') + '円';
const list = (id, texts) => el(id).replaceChildren(...texts.map(text => {
  const item = document.createElement('li'); item.textContent = text; return item;
}));
let text = '', sharedUrl = '', copyVersion = 0, hasResult = false, resultInView = false;
function mobileResult(){ show('estimate-mobile-total', hasResult && !resultInView); }
function readState() {
  const fields = new FormData(form);
  return {items:fields.getAll('items'),revisions:fields.get('revisions')??2,custom:fields.getAll('custom'),...(!legacy?{media:fields.getAll('media')}: {})};
}
function render(announce = true, updateUrl = true) {
  const state = readState();
  const r = quote(data, state), valid = !['invalid','empty'].includes(r.status), individual = r.status === 'custom';
  const view = quotePresentation(data,state,r);
  document.querySelector('.result-disclaimer').textContent = view.disclaimer;
  const main = legacy || state.media.includes('main'), short = !legacy && state.media.includes('short');
  show('estimate-groups', main);show('main-terms',main);show('other-media-terms',!main && valid);
  show('selected-scope',valid);show('additional-options',legacy || !!state.media.length);
  for (const row of el('estimate-groups').querySelectorAll('.work-row')) if (row.querySelector('input[value="shorts"]')) row.hidden = !legacy;
  write('short-selection-help', main?'60秒程度・本編の内容と撮影素材から制作（本数・範囲は要相談）':'60秒程度・単独制作は要相談');
  write('x-selection-help',main||short?'公開動画の告知シェア1回（料金・条件は要相談）':'製品・サービスを紹介するPR投稿1回（要相談）');
  write('base-scope-hint',main?data.baseDescription:'制作物を選ぶと、必要な作業と準備物を表示します。');
  write('preparation-hint',valid?'下の「ご用意いただくもの」で、選択した制作物の準備物をご確認ください。':'');
  write('media-rate-note',!legacy && (short||state.media.includes('x'))?'ショート・Xの料金や未確定条件は、正式見積もりで確認します。追加料金なしとは確定していません。':'');
  const changed = !legacy || r.selected.length > 0 || state.custom.length > 0 || Number(state.revisions) !== 2;
  hasResult = valid && changed;
  text = summary(data, state, r); copyVersion++;
  sharedUrl = estimateUrl(data, state, 'https://studio.msyn.me/pricing/#estimate-result');
  el('estimate-share-url').value = sharedUrl;
  show('share-fallback', false); write('share-status', '');
  if (r.status !== 'invalid' && updateUrl) history.replaceState(null, '', estimateUrl(data, state, location.href));
  show('result-filled', valid); show('result-error', r.status==='invalid');show('result-empty',r.status==='empty'); write('result-error', r.error ?? '');
  el('estimate-result').classList.toggle('is-custom', individual);
  if (valid) {
    el('result-lines').replaceChildren(...r.lines.map(line => {
      const row = document.createElement('tr'), name = document.createElement('th'), price = document.createElement('td');
      name.scope = 'row'; name.textContent = line.label;
      if (line.description) { const detail = document.createElement('small'); detail.className = 'quote-line-detail'; detail.textContent = line.description; name.append(detail); }
      price.textContent = compactAmount(taxIncluded(line.min,data.taxRate,line.taxInclusive), taxIncluded(line.max,data.taxRate,line.taxInclusive)); row.append(name, price); return row;
    }));
    write('result-media',view.mediaLabel);
    write('result-total-label', view.totalLabel);
    write('result-range', view.totalText);
    write('result-tax', view.taxText);
    list('scope-list',view.scope);list('revision-list',view.revisionNotes);list('preparation-list',view.preparation);
    write('result-tax-rate', '税込表示は消費税' + Number((data.taxRate * 100).toFixed(2)) + '%で計算しています。');
    show('result-custom', individual); show('result-pending-note', individual);
    list('result-custom-list', r.pending.map(item => item.label));
    write('mobile-amount', individual ? '要相談の項目があります' : compactAmount(r.totalMin, r.totalMax) + '（税込）');
  }
  mobileResult();
  show('estimate-mail', valid); show('estimate-share', valid); show('estimate-pdf',valid);
  el('estimate-mail').href = mailto(text);
  write('estimate-mail-label', changed ? 'この内容で相談する' : 'とりあえず相談する');
  if (announce) write('estimate-live', !valid ? r.error??'制作物を選択してください。' : individual ?
    (r.totalMin==null?'概算料金は要相談です。':'合計は相談後に決まります。金額を算出できる項目の小計は税込' + amountText(r.totalMin,r.totalMax) + 'です。') :
    '概算合計は税込' + amountText(r.totalMin,r.totalMax) + 'です。');
}
form.addEventListener('input', () => render());
form.addEventListener('submit', event => event.preventDefault());
el('estimate-share').addEventListener('click', async () => {
  const current = copyVersion, url = sharedUrl;
  try {
    await navigator.clipboard.writeText(url);
    if (current === copyVersion) write('share-status', '見積もりURLをコピーしました。');
  } catch {
    if (current !== copyVersion) return;
    show('share-fallback', true);
    write('share-status', '自動でコピーできませんでした。下のURLをコピーしてください。');
    el('estimate-share-url').focus(); el('estimate-share-url').select();
  }
});
el('estimate-mobile-total').addEventListener('click', () => el('estimate-result').focus({preventScroll:true}));
el('estimate-pdf').addEventListener('click',()=>{
  show('pdf-error',false);write('pdf-status','');el('pdf-dialog').showModal();
});
el('pdf-close').addEventListener('click',()=>el('pdf-dialog').close());
el('pdf-dialog').addEventListener('close',()=>el('estimate-pdf').focus({preventScroll:true}));
el('pdf-form').addEventListener('submit',async event=>{
  event.preventDefault();
  if(el('pdf-download').disabled) return;
  const state=readState();
  const recipient=el('pdf-recipient').value,honorific=el('pdf-honorific').value;
  el('pdf-download').disabled=true;show('pdf-error',false);write('pdf-status','PDFを作成しています。');
  try {
    const {downloadEstimatePdf}=await import('./pricing-pdf.mjs');
    await downloadEstimatePdf(data,state,recipient,honorific);
    write('pdf-status','PDFをダウンロードしました。');
  } catch(error) {
    const message=error instanceof Error && /^(宛名|PDF用フォント)/.test(error.message)?error.message:'PDFを作成できませんでした。通信状況をご確認のうえ、もう一度お試しください。';
    show('pdf-error',true);write('pdf-error',message);write('pdf-status','');
  } finally {el('pdf-download').disabled=false;}
});
const resultObserver = new IntersectionObserver(entries => {
  resultInView = entries[0].isIntersecting && entries[0].intersectionRatio >= 1; mobileResult();
}, {threshold:1, rootMargin:'-90px 0px -20px 0px'});
resultObserver.observe(el('result-amount'));

function renderArchivedGroups() {
  const icons = new Map(currentData.checklistGroups.map((group, index) => [group.icon, el('estimate-groups').querySelectorAll('legend svg')[index]]));
  const groups = data.checklistGroups.map(group => {
    const fieldset = document.createElement('fieldset'), legend = document.createElement('legend'), rows = document.createElement('div');
    fieldset.className = 'estimate-group'; rows.className = 'work-list';
    if (icons.get(group.icon)) legend.append(icons.get(group.icon).cloneNode(true));
    legend.append(document.createTextNode(' ' + group.title));
    for (const item of data.checklistItems.filter(item => group.items.includes(item.id))) {
      const row = document.createElement(item.fixed ? 'div' : 'label'), name = document.createElement('span'), price = document.createElement('span');
      row.className = 'work-row' + (item.fixed ? ' work-fixed' : '');
      name.className = 'work-label'; name.textContent = item.label;
      for (const description of [item.description].filter(Boolean)) {
        const detail = document.createElement('small'); detail.textContent = description; name.append(detail);
      }
      price.className = 'check-price'; price.textContent = compactAmount(taxIncluded(item.min,data.taxRate,item.taxInclusive),taxIncluded(item.max,data.taxRate,item.taxInclusive));
      const control = document.createElement(item.fixed ? 'span' : 'input');
      if (item.fixed) { control.className = 'fixed-check'; control.textContent = '✓'; }
      else { control.type = 'checkbox'; control.name = 'items'; control.value = item.id; }
      row.append(control,name,price);
      if (item.helpText) { const help = document.createElement('small'); help.className = 'work-help'; help.textContent = item.helpText; row.append(help); }
      rows.append(row);
    }
    fieldset.append(legend,rows); return fieldset;
  });
  el('estimate-groups').replaceChildren(...groups);
}

async function initialize() {
  form.inert = true;
  for (const id of ['estimate-mail','estimate-share','estimate-pdf']) show(id,false);
  try {
    data = await loadSharedRates(currentData, location.href, async version => {
      const response = await fetch('/pricing-rates/' + version + '.json');
      if (!response.ok) throw new Error('Rate snapshot unavailable');
      return response.json();
    });
    if (data !== currentData) renderArchivedGroups();
    write('base-scope-hint', currentData.baseDescription);
    write('rate-updated', '料金表の更新日：' + data.updated);
    show('shared-rate-note',data !== currentData);
    const restored = stateFromUrl(data,location.href);
    legacy = !Array.isArray(restored.media);
    show('media-selection',!legacy);show('legacy-selection-note',legacy);
    document.querySelector('.estimate-comparison').hidden = legacy;
    const selected = new Set(restored.items);
    for (const input of form.querySelectorAll('input[name="items"]')) input.checked = selected.has(input.value);
    for (const input of form.querySelectorAll('input[name="media"]')) input.checked = restored.media?.includes(input.value)??false;
    for (const input of form.querySelectorAll('input[name="custom"]')) input.checked = restored.custom?.includes(input.value)??false;
    el('revisions').value = restored.revisions??2;
    if (!legacy) el('comparison-lines').replaceChildren(...comparisonQuotes(data).map(({state:choice,result,view:comparison})=>{
      const row=document.createElement('tr'),name=document.createElement('th'),button=document.createElement('button'),price=document.createElement('td');
      name.scope='row';button.type='button';button.textContent=comparison.mediaLabel;
      button.addEventListener('click',()=>{
        for (const input of form.querySelectorAll('input[name="media"]')) input.checked=choice.media.includes(input.value);
        for (const input of form.querySelectorAll('input[name="items"]')) input.checked=choice.items.includes(input.value);
        render();el('media-selection').scrollIntoView({block:'start'});form.querySelector('input[name="media"]').focus({preventScroll:true});
      });
      name.append(button);price.textContent=result.pending.length?'要相談':comparison.totalText;
      if (result.pending.length && result.totalMin!=null) {const note=document.createElement('small');note.textContent='金額が分かる項目の小計：'+comparison.totalText;price.append(note);}
      row.append(name,price);return row;
    }));
    render(false,false);
    form.inert = false;
    if (location.hash === '#estimate-result') requestAnimationFrame(() => el('estimate-result').scrollIntoView({block:'start',behavior:'instant'}));
  } catch {
    form.hidden = true; show('estimate-result',false); show('share-load-error',true); show('estimate-mobile-total',false);
  }
}
initialize();
