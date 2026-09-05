export const yen = number => number.toLocaleString('ja-JP') + '円';
export const taxIncluded = (amount, taxRate, alreadyIncluded = false) => amount == null ? null : alreadyIncluded ? amount : amount + Math.round(amount * taxRate);
export function amountText(min, max) {
  if (min == null || max == null) return '要相談';
  return min === max ? yen(min) : yen(min) + '〜' + yen(max);
}

export function selectedFromUrl(data, url) {
  const requested = new Set(new URL(url).searchParams.getAll('items').flatMap(value => value.split(',')));
  return data.checklistItems.filter(item => !item.fixed && requested.has(item.id)).map(item => item.id);
}

export function estimateUrl(data, state = {}, base = 'https://studio.msyn.me/pricing/') {
  const url = new URL(base), selected = new Set(state.items ?? []);
  const items = data.checklistItems.filter(item => !item.fixed && selected.has(item.id)).map(item => item.id);
  url.searchParams.set('items', items.join(','));
  url.searchParams.set('v', data.rateVersion);
  return url.href;
}

export async function loadSharedRates(currentData, url, readSnapshot) {
  const version = new URL(url).searchParams.get('v');
  if (version === null || version === currentData.rateVersion) return currentData;
  if (!/^[a-f0-9]{12}$/.test(version)) throw new Error('Invalid rate version');
  const archived = await readSnapshot(version);
  if (archived.rateVersion !== version || !Array.isArray(archived.checklistItems) || !Array.isArray(archived.checklistGroups)) throw new Error('Invalid rate snapshot');
  // Keep archived prices and scope, but use current help text for display.
  const currentItems = new Map(currentData.checklistItems.map(item => [item.id, item]));
  return {...archived, checklistItems: archived.checklistItems.map(item => {
    const current = currentItems.get(item.id);
    return current ? {...item, helpText: current.helpText} : item;
  })};
}

export function quote(data, state = {}) {
  const selected = new Set(Array.isArray(state.items) ? state.items : []);
  const custom = data.custom.filter(item => (Array.isArray(state.custom) ? state.custom : []).includes(item.id));
  const chosen = data.checklistItems.filter(item => item.fixed || selected.has(item.id));
  const optional = chosen.filter(item => !item.fixed).map(item => item.id);
  const raw = state.revisions ?? 2, revisions = Number(raw);
  if (!/^\d+$/.test(String(raw)) || !Number.isSafeInteger(revisions) || revisions < 0 || !Number.isSafeInteger(revisions * data.revisionFee)) {
    return {status:'invalid', error:'修正回数を0以上の整数で入力してください。', lines:[], custom, selected:optional};
  }
  const lines = chosen.map(item => ({
    id:item.id, label:item.label, description:item.description, min:item.min, max:item.max, taxInclusive:!!item.taxInclusive, fixed:!!item.fixed
  }));
  const extraRounds = Math.max(0, revisions - 2), extra = extraRounds * data.revisionFee;
  if (extra) lines.push({id:'revisions', label:'追加修正（'+extraRounds+'回）', min:extra, max:extra});
  const pending = [
    ...lines.filter(line => line.min == null).map(line => ({id:line.id,label:line.label})),
    ...custom
  ];
  const totalMin = lines.reduce((sum,line) => sum + (taxIncluded(line.min,data.taxRate,line.taxInclusive) ?? 0),0);
  const totalMax = lines.reduce((sum,line) => sum + (taxIncluded(line.max,data.taxRate,line.taxInclusive) ?? 0),0);
  if (!Number.isSafeInteger(totalMax)) return {status:'invalid',error:'修正回数を確認してください。',lines:[],custom,selected:optional};
  const min = Math.round(totalMin / (1 + data.taxRate)), max = Math.round(totalMax / (1 + data.taxRate));
  const taxMin = totalMin - min, taxMax = totalMax - max;
  const status = pending.length ? 'custom' : totalMin === totalMax ? 'estimate' : 'range';
  const preparation=['検証用アカウント'];
  const included = new Set(chosen.map(item => item.id));
  if (data.checklistItems.some(item => item.id === 'research') && !included.has('research')) preparation.push('紹介する機能・操作手順の検証結果');
  if (!included.has('materials')) preparation.push('動画で使用する資料');
  if (!included.has('materials')) preparation.push('台本');
  if (!included.has('editing')) preparation.push('撮影素材の編集・完成データの提供');
  if (!included.has('thumbnail')) preparation.push('サムネイルの制作');
  return {status,lines,pending,custom,selected:optional,revisions,extraRounds,extra,
    min,max,taxMin,taxMax,totalMin,totalMax,
    quotedTotal:status === 'estimate' ? totalMin : null,preparation};
}

export function summary(data, state, result = quote(data,state)) {
  if (result.status === 'invalid') return '';
  return [
    'PR動画の制作・掲載について相談したく、ご連絡しました。','',
    '依頼したい作業と概算料金（税込）：',
    ...result.lines.flatMap(line => ['・'+line.label+'：'+amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive)), ...(line.description ? ['  内訳：'+line.description] : [])]),
    '公開前の修正：'+result.revisions+'回（2回まで料金内）',
    '動画の長さの目安：10〜20分程度（30分を超える場合は要相談）',
    (result.pending.length ? '金額を算出できる項目の小計：' : '概算合計：')+amountText(result.totalMin,result.totalMax)+'（税込）',
    '税抜：'+amountText(result.min,result.max),
    ...(result.pending.length ? ['要相談の項目：',...result.pending.map(item=>'・'+item.label),'上記の小計には、要相談の項目の金額を含みません。'] : []),
    ...(result.preparation.length ? ['こちらで用意・担当する範囲：',...result.preparation.map(item=>'・'+item)] : []),
    '詳しい内容をもとに、正式なお見積もりをお願いいたします。','',
    '紹介したい製品・サービス：','希望する公開時期：','会社名・氏名：','',
    '料金表：'+data.updated,data.rateVersion ? estimateUrl(data,state,'https://studio.msyn.me/pricing/#estimate-result') : 'https://studio.msyn.me/pricing/'
  ].join('\n');
}
export function mailto(text) {
  return 'mailto:contact@msyn.me?subject='+encodeURIComponent('PR動画の制作・掲載のご相談')+'&body='+encodeURIComponent(text);
}
