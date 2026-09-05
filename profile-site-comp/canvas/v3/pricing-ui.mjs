import {quote, summary, mailto, amountText, taxIncluded, selectedFromUrl, estimateUrl, loadSharedRates} from './pricing-model.mjs';
const el = id => document.getElementById(id);
const currentData = JSON.parse(el('pricing-data').textContent);
let data = currentData;
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
function render(announce = true, updateUrl = true) {
  const fields = new FormData(form);
  const state = {items:fields.getAll('items'), revisions:fields.get('revisions') ?? 2, custom:fields.getAll('custom')};
  const r = quote(data, state), valid = r.status !== 'invalid', individual = r.status === 'custom';
  const changed = r.selected.length > 0 || state.custom.length > 0 || Number(state.revisions) !== 2;
  hasResult = valid && changed;
  text = summary(data, state, r); copyVersion++;
  sharedUrl = estimateUrl(data, state, 'https://studio.msyn.me/pricing/#estimate-result');
  el('estimate-share-url').value = sharedUrl;
  show('share-fallback', false); write('share-status', '');
  if (valid && updateUrl) history.replaceState(null, '', estimateUrl(data, state, location.href));
  show('result-filled', valid); show('result-error', !valid); write('result-error', r.error ?? '');
  el('estimate-result').classList.toggle('is-custom', individual);
  if (valid) {
    el('result-lines').replaceChildren(...r.lines.map(line => {
      const row = document.createElement('tr'), name = document.createElement('th'), price = document.createElement('td');
      name.scope = 'row'; name.textContent = line.label;
      if (line.description) { const detail = document.createElement('small'); detail.className = 'quote-line-detail'; detail.textContent = line.description; name.append(detail); }
      price.textContent = compactAmount(taxIncluded(line.min,data.taxRate,line.taxInclusive), taxIncluded(line.max,data.taxRate,line.taxInclusive)); row.append(name, price); return row;
    }));
    write('result-total-label', individual ? '金額を算出できる項目の小計（税込）' : '概算合計（税込）');
    write('result-range', compactAmount(r.totalMin, r.totalMax));
    write('result-tax', '税抜 ' + compactAmount(r.min, r.max));
    write('result-tax-rate', '税込表示は消費税' + Number((data.taxRate * 100).toFixed(2)) + '%で計算しています。');
    show('result-custom', individual); show('result-pending-note', individual);
    list('result-custom-list', r.pending.map(item => item.label));
    write('mobile-amount', individual ? '要相談の項目があります' : compactAmount(r.totalMin, r.totalMax) + '（税込）');
  }
  mobileResult();
  show('estimate-mail', valid); show('estimate-share', valid);
  el('estimate-mail').href = mailto(text);
  write('estimate-mail-label', changed ? 'この内容で相談する' : 'とりあえず相談する');
  if (announce) write('estimate-live', !valid ? r.error : individual ?
    '合計は相談後に決まります。金額を算出できる項目の小計は税込' + amountText(r.totalMin,r.totalMax) + 'です。' :
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
  for (const id of ['estimate-mail','estimate-share']) show(id,false);
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
    const selected = new Set(selectedFromUrl(data, location.href));
    for (const input of form.querySelectorAll('input[name="items"]')) input.checked = selected.has(input.value);
    render(false,false);
    form.inert = false;
    if (location.hash === '#estimate-result') requestAnimationFrame(() => el('estimate-result').scrollIntoView({block:'start',behavior:'instant'}));
  } catch {
    form.hidden = true; show('estimate-result',false); show('share-load-error',true); show('estimate-mobile-total',false);
  }
}
initialize();
