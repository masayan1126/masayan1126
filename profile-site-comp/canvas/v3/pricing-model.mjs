export const yen = number => number.toLocaleString('ja-JP') + '円';
export const taxIncluded = (amount, taxRate, alreadyIncluded = false) => amount == null ? null : alreadyIncluded ? amount : amount + Math.round(amount * taxRate);
export const normalizeNotes = value => typeof value === 'string' ? value.replace(/\r\n?/g,'\n').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g,'').slice(0,1000).trim() : '';
export function amountText(min, max) {
  if (min == null || max == null) return '要相談';
  return min === max ? yen(min) : yen(min) + '〜' + yen(max);
}

export function selectedFromUrl(data, url) {
  const requested = new Set(new URL(url).searchParams.getAll('items').flatMap(value => value.split(',')));
  return data.checklistItems.filter(item => !item.fixed && requested.has(item.id)).map(item => item.id);
}

export function estimateUrl(data, state = {}, base = 'https://studio.msyn.me/pricing/') {
  const modern = data.mediaSchema && Array.isArray(state.media);
  const url = new URL(base), selected = new Set(modern && !state.media.includes('main') ? [] : state.items ?? []);
  url.search = '';
  const items = data.checklistItems.filter(item => !item.fixed && selected.has(item.id) && (!modern || item.id !== 'shorts')).map(item => item.id);
  url.searchParams.set('items', items.join(','));
  url.searchParams.set('v', data.rateVersion);
  if (modern) {
    url.searchParams.set('media', MEDIA.filter(id => state.media.includes(id)).join(','));
    url.searchParams.set('revisions', state.revisions ?? 2);
    url.searchParams.set('custom', data.custom.filter(item => state.custom?.includes(item.id)).map(item => item.id).join(','));
  } else {
    if (state.revisions != null && Number(state.revisions) !== 2) url.searchParams.set('revisions',state.revisions);
    const custom = data.custom.filter(item => state.custom?.includes(item.id)).map(item => item.id);
    if (custom.length) url.searchParams.set('custom',custom.join(','));
  }
  const notes=normalizeNotes(state.notes);
  if(notes)url.searchParams.set('notes',notes);
  return url.href;
}

export const MEDIA = ['main','short','x'];
export function stateFromUrl(data, url) {
  const params = new URL(url).searchParams;
  const state = {items:selectedFromUrl(data,url)};
  if(params.has('notes'))state.notes=normalizeNotes(params.get('notes'));
  if (params.has('revisions')) state.revisions = params.get('revisions');
  if (params.has('custom')) {
    const custom = params.getAll('custom').flatMap(value => value.split(','));
    state.custom = data.custom.filter(item => custom.includes(item.id)).map(item => item.id);
  }
  if (params.has('media')) {
    if (!data.mediaSchema) throw new Error('This rate version does not support media selection');
    const ids = params.getAll('media').flatMap(value => value.split(','));
    state.media = MEDIA.filter(id => ids.includes(id));
    state.revisions = params.get('revisions') ?? 2;
    const custom = params.getAll('custom').flatMap(value => value.split(','));
    state.custom = data.custom.filter(item => custom.includes(item.id)).map(item => item.id);
  } else if (data.mediaSchema && !params.has('items') && !params.has('v')) state.media = [];
  return state;
}

export async function loadSharedRates(currentData, url, readSnapshot) {
  const version = new URL(url).searchParams.get('v');
  if (version === null || version === currentData.rateVersion) return currentData;
  if (!/^[a-f0-9]{12}$/.test(version)) throw new Error('Invalid rate version');
  const archived = await readSnapshot(version);
  if (archived.rateVersion !== version || !Array.isArray(archived.checklistItems) || !Array.isArray(archived.checklistGroups)) throw new Error('Invalid rate snapshot');
  // Keep archived calculation and selection rules, but use current descriptions.
  const currentItems = new Map(currentData.checklistItems.map(item => [item.id, item]));
  return {...archived, checklistItems: archived.checklistItems.map(item => {
    const current = currentItems.get(item.id);
    return current ? {...item, helpText: current.helpText, description: current.description} : item;
  })};
}

export function quote(data, state = {}) {
  if (data.mediaSchema && Array.isArray(state.media)) return mediaQuote(data,state);
  const selected = new Set(Array.isArray(state.items) ? state.items : []);
  const custom = data.custom.filter(item => (Array.isArray(state.custom) ? state.custom : []).includes(item.id));
  const notes=normalizeNotes(state.notes);
  if(notes)custom.push({id:'notes',label:'追加のご希望：'+notes});
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
  if (Array.isArray(result.media)) return mediaSummary(data,state,result);
  if (result.status === 'invalid') return '';
  return [
    'PR動画の制作・掲載について相談したく、ご連絡しました。','',
    '依頼したい作業と概算料金（税込）：',
    ...result.lines.flatMap(line => ['・'+line.label+'：'+amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive)), ...(line.description ? ['  内訳：'+line.description] : [])]),
    '公開前の軽微修正：'+result.revisions+'回（2回まで料金内）',
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
  return 'mailto:contact@msyn.me?subject='+encodeURIComponent('PR制作・掲載のご相談')+'&body='+encodeURIComponent(text);
}

// New media offers use the established main-video work rates. Unknown terms remain
// explicit pending items; no amount or private offer can be supplied through a URL.
function mediaQuote(data,state) {
  const media = MEDIA.filter(id => state.media.includes(id));
  const main = media.includes('main'), short = media.includes('short'), x = media.includes('x');
  const items = main ? (state.items ?? []).filter(id => ['materials','thumbnail'].includes(id)) : [];
  const rates = data.mediaRates;
  const base = quote(data,{items:main?items:[], revisions:main?state.revisions:2,custom:state.custom,notes:state.notes});
  if (base.status === 'invalid') return {...base,media};
  const revisionsRaw = state.revisions ?? 2, revisions = Number(revisionsRaw);
  if (!/^\d+$/.test(String(revisionsRaw)) || !Number.isSafeInteger(revisions) || !Number.isSafeInteger(revisions * data.revisionFee)) {
    return {status:'invalid',error:'修正回数を0以上の整数で入力してください。',lines:[],media};
  }
  const lines = main ? [...base.lines] : [];
  const pending = [...base.custom];
  const addRate = (id,label,rate,description) => lines.push({id,label,description,min:rate?.min??null,max:rate?.max??null,taxInclusive:!!rate?.taxInclusive});
  if (short) {
    if (main) {
      const bundle = data.checklistItems.find(item => item.id === 'shorts');
      addRate('additionalShort',x?'本編からの追加ショート・X告知':'本編からの追加ショート',x?bundle:rates.additionalShortWithoutX,
        '本編の内容・撮影素材を利用します。共通の検証・撮影は重ねて加算しません。');
      if (rates.additionalShortCount !== 1) pending.push({id:'shortCount',label:'追加ショート1本・60秒程度の制作範囲'});
    } else addRate('standaloneShort','ショート単独制作（1本・60秒程度）',rates.standaloneShort,'検証・構成・撮影・編集・公開の範囲は個別に確認します。');
    if (rates.shortIncludedRevisions == null || revisions > rates.shortIncludedRevisions) pending.push({id:'shortRevisions',label:'ショートの修正回数・追加料金'});
  }
  if (x) {
    if (!main && !short) addRate('xPr','X製品PR投稿（1回）',rates.xPr,'製品・サービスを紹介するPR投稿です。');
    else if (!(main && short)) addRate('videoAnnouncement','Xでの公開動画の告知シェア（1回）',rates.videoAnnouncement,'公開動画を紹介します。製品PR投稿の料金は重ねて加算しません。');
    if (rates.xIncludedRevisions == null || revisions > rates.xIncludedRevisions) pending.push({id:'xRevisions',label:'X投稿の修正回数・追加料金'});
  }
  pending.push(...lines.filter(line => line.min == null || line.max == null).map(({id,label})=>({id,label})));
  const knownLines = lines.filter(line => line.min != null && line.max != null);
  const sum = edge => knownLines.reduce((total,line)=>total+taxIncluded(line[edge],data.taxRate,line.taxInclusive),0);
  const totalMin = knownLines.length ? sum('min') : null, totalMax = knownLines.length ? sum('max') : null;
  if (totalMax != null && !Number.isSafeInteger(totalMax)) return {status:'invalid',error:'修正回数を確認してください。',lines:[],media};
  const min = totalMin == null ? null : Math.round(totalMin/(1+data.taxRate));
  const max = totalMax == null ? null : Math.round(totalMax/(1+data.taxRate));
  const status = !media.length ? 'empty' : pending.length ? 'custom' : totalMin === totalMax ? 'estimate' : 'range';
  const preparation = !media.length ? [] : main ? base.preparation : short
    ? ['検証用アカウント','製品の仕様・紹介したい機能','ロゴ・画像などの使用許諾済み素材']
    : ['製品の紹介資料・正確な仕様と料金','紹介先URL・使用許諾済み画像','検証が必要な場合のアカウント（要相談）'];
  const scope = [
    ...(main ? ['YouTube本編1本（10〜20分程度）を制作し、AIギルドchで公開します。', '本編はYouTube公開で納品完了です。動画ファイルの提供は別途ご相談ください。'] : []),
    ...(short ? [main ? '本編からショート1本（60秒程度）を制作するご希望です。本数・制作範囲は正式見積もりで確認します。' : 'ショート1本（60秒程度）を単独で制作するご希望です。', 'ショートの公開先はYouTube Shortsを想定し、納品方法・レポートの有無は要相談です。'] : []),
    ...(x ? [main||short ? 'X投稿1回は、公開動画の告知シェアです。' : 'X投稿1回は、製品・サービスを紹介するPR投稿です。', 'Xの公開先：@masayan_ai_hack。掲載内容・画像・リンクは公開前に確認します。'] : []),
  ];
  const revisionNotes = [
    ...(main ? ['本編の公開前の軽微修正：'+revisions+'回（2回まで料金内・3回目以降は1回'+yen(taxIncluded(data.revisionFee,data.taxRate))+'・税込）'] : []),
    ...(short ? ['ショートの軽微修正：'+revisions+'回を希望'+(rates.shortIncludedRevisions==null?'（無料回数・追加料金は要相談）':'（'+rates.shortIncludedRevisions+'回まで料金内・超過分は要相談）')] : []),
    ...(x ? ['X投稿の軽微修正：'+revisions+'回を希望'+(rates.xIncludedRevisions==null?'（無料回数・追加料金は要相談）':'（'+rates.xIncludedRevisions+'回まで料金内・超過分は要相談）')] : []),
  ];
  return {status,media,lines:media.length?lines:[],pending:media.length?pending:[],custom:base.custom,selected:items,
    revisions,extraRounds:main?base.extraRounds:0,extra:main?base.extra:0,min,max,
    taxMin:totalMin==null?null:totalMin-min,taxMax:totalMax==null?null:totalMax-max,totalMin,totalMax,
    quotedTotal:status==='estimate'?totalMin:null,preparation,scope,revisionNotes};
}

// Explain optional requests using the same result as the finished estimate.
export function extrasPresentation(data,state,result=quote(data,state)) {
  if (['invalid','empty'].includes(result.status)) return {status:result.status,error:result.error};
  const media=result.media??['main'];
  const baseline=quote(data,{...state,custom:[],notes:'',revisions:2});
  const revision=result.lines.find(line=>line.id==='revisions');
  const pending=new Set(result.pending.map(item=>item.id));
  const revisionEffects=[
    ...(media.includes('main')?[{id:'main',label:'本編の軽微修正',effect:revision
      ?'＋'+amountText(taxIncluded(revision.min,data.taxRate,revision.taxInclusive),taxIncluded(revision.max,data.taxRate,revision.taxInclusive))+'（'+result.extraRounds+'回分・税込）'
      :'2回まで料金内'}]:[]),
    ...['short','x'].filter(id=>media.includes(id)).map(id=>({id,label:(id==='short'?'ショート':'X投稿')+'の軽微修正',effect:pending.has(id==='short'?'shortRevisions':'xRevisions')?'料金・無料回数は要相談':'料金内'})),
  ];
  return {status:result.status,baselineLabel:baseline.pending.length?'追加条件を含める前の小計（税込）':'追加条件を含める前（税込）',baselineText:amountText(baseline.totalMin,baseline.totalMax),
    totalLabel:result.pending.length?'現在の小計（税込）':'現在の概算合計（税込）',
    totalText:amountText(result.totalMin,result.totalMax),revisionEffects,
    consultations:result.custom.map(item=>({id:item.id,label:item.label})),
    note:result.totalMin==null?'制作内容や修正条件を確認し、正式な料金をご案内します。':
      result.pending.length?'個別見積もり・要相談の項目の料金は、この小計に含みません。正式見積もりで総額をご案内します。':'選択した内容の概算金額です。',
  };
}

export function quotePresentation(data,state,result=quote(data,state)) {
  const modern = Array.isArray(result.media);
  const mediaLabel = modern ? result.media.map(id=>({main:'YouTube本編1本',short:'ショート1本',x:result.media.length===1?'X製品PR投稿1回':'X告知シェア1回'})[id]).join('＋') : 'サービス紹介動画1本・AIギルドch掲載';
  return {
    subject:'PR制作（'+mediaLabel+'）',mediaLabel,
    disclaimer:modern?'表示金額は概算です。正式な料金は、選択した制作物の内容・範囲・修正条件を確認して決定します。':'※こちらの金額はあくまで概算になります。正式な料金は動画内容や尺により変動します。',
    totalLabel:result.status==='empty'?'制作物を選択してください':result.pending?.length?(result.totalMin==null?'概算合計（税込）':'金額を算出できる項目の小計（税込）'):'概算合計（税込）',
    totalText:result.status==='empty'?'未選択':amountText(result.totalMin,result.totalMax),
    taxText:result.totalMin==null?'': 'うち消費税相当額（'+Number((data.taxRate*100).toFixed(2))+'%） '+amountText(result.taxMin,result.taxMax),
    scope:result.scope??['本編1本（10〜20分程度）の制作とAIギルドchでの公開が対象です。'],
    revisionNotes:result.revisionNotes??['公開前の軽微修正：'+result.revisions+'回（2回まで料金内）'],
    preparation:result.preparation??[],
  };
}

function mediaSummary(data,state,result) {
  if (result.status==='invalid' || result.status==='empty') return '';
  const view = quotePresentation(data,state,result);
  return [
    'PR制作について相談したく、ご連絡しました。','',view.subject,
    '依頼したい作業と概算料金（税込）：',
    ...result.lines.flatMap(line=>['・'+line.label+'：'+amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive)),...(line.description?['  内訳：'+line.description]:[])]),
    view.totalLabel+'：'+view.totalText+(result.totalMin==null?'':'（税込）'),
    ...(result.totalMin==null?[]:['税抜：'+amountText(result.min,result.max),view.taxText]),
    ...(result.pending.length?['要相談の項目：',...result.pending.map(item=>'・'+item.label),'金額が分かる項目の小計には、要相談の項目を含みません。正式見積もりで総額を確定します。']:[]),
    '制作・公開の範囲：',...view.scope.map(text=>'・'+text),...view.revisionNotes,
    'こちらで用意・担当する範囲：',...view.preparation.map(text=>'・'+text),
    '詳しい内容をもとに、正式なお見積もりをお願いいたします。','',
    '紹介したい製品・サービス：','希望する公開時期：','会社名・氏名：','',
    '料金表：'+data.updated,estimateUrl(data,state,'https://studio.msyn.me/pricing/#estimate-result'),
  ].join('\n');
}

export function comparisonQuotes(data) {
  const combinations = [['x'],['short'],['short','x'],['main'],['main','x'],['main','short'],['main','short','x']];
  return combinations.map((media,index)=>{
    const state={media,items:['materials','thumbnail']},result=quote(data,state);
    return {state,result,view:quotePresentation(data,state,result),index};
  }).sort((a,b)=> (a.result.totalMin??Infinity)-(b.result.totalMin??Infinity) || a.state.media.length-b.state.media.length || a.index-b.index);
}
