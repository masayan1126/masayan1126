import {quote,quotePresentation,extrasPresentation,summary,mailto,estimateUrl,amountText,taxIncluded} from './pricing-model.mjs';

export function startWizard(data,restored,currentData) {
const workspace = document.querySelector('#wizard-workspace');
const root = document.querySelector('#pricing-wizard');
const state = {media:restored.media,items:restored.media.includes('main')&&new URL(location.href).searchParams.has('items')?restored.items:['materials','thumbnail'],custom:restored.custom??[],revisions:restored.revisions??2};
let question = 'media', complete = state.media.length>0, everCompleted = complete;
let revisionError = '', recipient = '', honorific='御中', lastPdfButton,copyVersion=0;
const terms = document.querySelector('#main-terms').cloneNode(true);
terms.removeAttribute('id');terms.hidden=false;
terms.querySelectorAll('[id],[aria-labelledby]').forEach(node=>{node.removeAttribute('id');node.removeAttribute('aria-labelledby')});
const answered = new Set();
const titles = {media:'どのPRをご希望ですか？',assets:'本編の資料・サムネイル制作も依頼しますか？',extras:'追加のご希望はありますか？'};
const esc = text => String(text).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const hasMain = () => state.media.includes('main');
const questions = () => hasMain()?['media','assets','extras']:['media','extras'];
const icons = {
  main:'<rect x="2" y="5" width="23" height="17"/><path d="m11 10 6 4-6 4z"/>',
  short:'<rect x="7" y="1" width="13" height="25"/><path d="m12 10 5 4-5 3z"/>',
  x:'<path d="m5 3 17 22H17L1 3h5Zm16 0L4 25"/>',
};
const selectChoice = ({group,id,title,description='',price='',icon=''}) => {
  const checked = state[group].includes(id);
  return `<label class="choice${icon?'':' compact'}"><input type="checkbox" data-group="${group}" data-key="${group}-${id}" value="${id}" ${checked?'checked':''}><span class="choice-icon" ${icon?'':'hidden'}><svg aria-hidden="true" viewBox="0 0 28 28">${icons[icon]??''}</svg></span><span class="choice-title">${esc(title)}</span>${description?`<span class="choice-description">${esc(description)}</span>`:''}${price?`<span class="choice-price">${esc(price)}</span>`:''}</label>`;
};
function answerText(key) {
  if(key==='media') return state.media.map(id=>({main:'YouTube本編1本',short:'ショート1本',x:state.media.some(id=>id!=='x')?'Xで動画を告知':'Xで製品をPR'})[id]).join('・') || 'まだ選択していません';
  if(key==='assets') return ['materials','thumbnail'].map(id=>(id==='materials'?'動画用資料':'サムネイル')+'：'+(state.items.includes(id)?'制作を依頼':'お客様でご用意')).join('\n');
  const list=data.custom.filter(item=>state.custom.includes(item.id)).map(item=>item.label);
  return [`軽微修正${state.revisions}回をご希望`,...list].join('・');
}
function questionContent(key) {
  const idx=questions().indexOf(key);
  let hint='', body='';
  if(key==='media') {
    hint='ご希望の制作・掲載先をお選びください。複数選択できます。';
    body='<div class="choices">'+[
      {group:'media',id:'main',title:'YouTube本編で紹介',description:'10〜20分程度・1本を制作し、AIギルドchで公開',icon:'main'},
      {group:'media',id:'short',title:'ショート動画で紹介',description:hasMain()?'本編の内容・撮影素材から60秒程度を1本（範囲は要相談）':'60秒程度・1本を制作し、YouTube Shortsで公開（詳細は要相談）',icon:'short'},
      {group:'media',id:'x',title:state.media.some(id=>id!=='x')?'Xで動画を告知':'Xで製品をPR',description:state.media.some(id=>id!=='x')?'公開動画をXで告知・1回（料金・条件は要相談）':'製品・サービスをXで紹介・1回（要相談）',icon:'x'},
    ].map(selectChoice).join('')+'</div><p class="hint">Xのみの場合は製品PR、動画と組み合わせる場合は公開動画の告知です。</p>';
  } else if(key==='assets') {
    hint='こちらで制作するものをお選びください。選択を外したものは、お客様にご用意をお願いします。';
    const items=data.checklistItems.filter(item=>['materials','thumbnail'].includes(item.id));
    body='<div class="choices">'+items.map(item=>selectChoice({group:'items',id:item.id,
      title:item.id==='materials'?'動画用の説明資料も依頼する':'サムネイル制作も依頼する',
      description:item.id==='materials'?'動画で紹介する内容と順番をまとめます。':'YouTubeで表示するサムネイルを制作します。',
      price:'＋'+amountText(taxIncluded(item.min,data.taxRate,item.taxInclusive),taxIncluded(item.max,data.taxRate,item.taxInclusive))+'（税込）',
    })).join('')+'</div><p class="mini-note">動画用の構成や説明資料をご用意いただける場合は、資料作成の選択を外せます。製品マニュアルなどをもとに動画用の資料を作成する場合は、ご選択ください。</p>';
  } else {
    hint='二次利用などの料金は、ご希望の内容を確認して個別にお見積もりします。選択した項目の料金は、表示中の小計には含まれません。';
    const descriptions={preparation:'準備物と作業の分担を確認します。',reuse:'利用先・期間・広告利用の有無を確認します。',reshoot:'撮り直しの内容と範囲を確認します。',long:'動画の長さと必要な作業を確認します。',multiple:'本数・制作内容・契約期間を確認します。',period:'ご希望の掲載期間と条件を確認します。'};
    const choices='<div class="choices extras-choices">'+data.custom.map(item=>selectChoice({group:'custom',id:item.id,title:item.label,description:descriptions[item.id]??'',price:state.custom.includes(item.id)?'別途お見積もり（小計に含みません）':'料金は個別見積もり'})).join('')+'</div>';
    body=choices
      +`<div class="revisions"><label for="wizard-revisions">公開前の軽微修正の希望回数</label><input id="wizard-revisions" data-key="revisions" type="number" inputmode="numeric" min="0" step="1" value="${esc(state.revisions)}" aria-describedby="revision-note"><span>回</span></div>`
      +`<p class="rev-note" id="revision-note">${hasMain()?'本編は2回まで料金内、3回目以降は1回'+amountText(taxIncluded(data.revisionFee,data.taxRate),taxIncluded(data.revisionFee,data.taxRate))+'（税込）です。':'希望回数をもとに正式見積もりで確認します。'}${state.media.some(id=>id==='short'||id==='x')?' ショート・Xの無料回数と追加料金は要相談です。':''}</p>`
      +extrasImpact();
  }
  return `<section class="question" aria-labelledby="question-${key}"><p class="question-kicker">質問 ${idx+1} / ${questions().length}${key==='extras'?' ・ 任意':''}</p><h2 id="question-${key}" tabindex="-1">${titles[key]}</h2><p class="question-hint">${hint}</p>${body}</section>`;
}
function extrasImpact() {
  const view=extrasPresentation(data,state);
  if(view.status==='invalid')return `<section id="extras-impact" class="extras-impact"><p class="error">${esc(view.error)}</p></section>`;
  if(view.status==='empty')return '<div id="extras-impact"></div>';
  return `<section id="extras-impact" class="extras-impact" aria-labelledby="extras-impact-title"><h3 id="extras-impact-title">選択による金額の変化</h3>
    <dl class="extras-amounts"><div><dt>${esc(view.baselineLabel)}</dt><dd id="extras-before">${esc(view.baselineText)}</dd></div></dl>
    <ul class="extras-revision-effects">${view.revisionEffects.map(item=>`<li><span>${esc(item.label)}</span><strong>${esc(item.effect)}</strong></li>`).join('')}</ul>
    ${view.consultations.length?`<div class="extras-consultations"><h4>選択した個別見積もりの項目</h4><ul>${view.consultations.map(item=>`<li>${esc(item.label)}<small>この料金は小計に含みません。</small></li>`).join('')}</ul></div>`:'<p class="extras-no-consultation">個別見積もりのご希望は選択されていません。</p>'}
    <dl class="extras-amounts extras-current"><div><dt id="extras-total-label">${esc(view.totalLabel)}</dt><dd id="extras-after">${esc(view.totalText)}</dd></div></dl><p class="extras-explanation">${esc(view.note)}</p>
  </section>`;
}
function refreshExtras(announce=false) {
  const panel=workspace.querySelector('#extras-impact');if(!panel)return;
  panel.outerHTML=extrasImpact();
  const result=quote(data,state),view=quotePresentation(data,state,result),asideNode=workspace.querySelector('.flow-aside');
  if(asideNode)asideNode.outerHTML=aside(result,view);
  if(announce){const impact=extrasPresentation(data,state,result);document.querySelector('#wizard-live').textContent=impact.status==='invalid'?impact.error:impact.status==='empty'?'ご希望のPRを選択してください。':impact.totalLabel+'、'+impact.totalText+'。'+(impact.consultations.length?'個別見積もりの'+impact.consultations.length+'項目の料金は含みません。':'');}
}
function answers(completed=false) {
  return questions().map(key=>`<${completed?'div':'li'}><small>${{media:'制作物',assets:'資料・サムネイル',extras:'その他の希望'}[key]}</small><div class="answer-row"><p class="answer-value">${esc(answerText(key))}</p><button type="button" class="text-button" data-edit="${key}">${completed?'変更する':'選び直す'}</button></div></${completed?'div':'li'}>`).join('');
}
function aside(result,view) {
  const showAmount=(everCompleted||question==='extras')&&state.media.length&&result.status!=='invalid';
  return `<aside class="flow-aside" aria-label="回答の確認"><h2>ご依頼内容</h2><ul class="answer-list">${answers()}</ul>${showAmount?`<p class="aside-price-label">${question==='extras'?(result.pending?.length?'現在の小計（税込）':'現在の概算合計（税込）'):(result.pending?.length?'変更後の小計（税込）':'変更後の概算（税込）')}</p><p class="aside-price">${esc(view.totalText)}</p>${result.pending?.length?'<p class="sheet-note">個別見積もり・要相談の料金は含みません。</p>':''}`:''}<p class="aside-foot">選択内容はあとから変更できます。最後に概算金額と明細をご確認いただけます。</p></aside>`;
}
function navigation(key) {
  const qs=questions(),index=qs.indexOf(key),last=index===qs.length-1;
  return `<div class="navigation">${index>0?'<button type="button" class="text-button" data-prev>← 前の質問へ</button>':''}${everCompleted&&!last?'<button type="button" class="button secondary" data-complete>見積書を更新</button>':''}<button type="button" class="button primary" ${last?'data-complete':'data-next'} ${!state.media.length?'disabled':''}>${last?(everCompleted?'見積書を更新する':'概算見積書を確認する'):'次へ'}<span class="button-arrow" aria-hidden="true">→</span></button></div>`;
}
function renderForm(result,view) {
  const qs=questions();if(!qs.includes(question)) question='media';
  const content=`<ol class="progress" aria-label="${qs.indexOf(question)+1}問目／全${qs.length}問">${qs.map((key,index)=>`<li class="${index<qs.indexOf(question)?'done':key===question?'current':''}" ${key===question?'aria-current="step"':''}><span class="sr-only">${titles[key]}</span></li>`).join('')}</ol>${questionContent(question)}${navigation(question)}`;
  return `<div class="flow-layout"><div class="flow-main">${revisionError?`<p class="error" role="alert">${esc(revisionError)}</p>`:''}${content}</div>${aside(result,view)}</div>`;
}
function renderEstimate(result,view) {
  const amount=line=>amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive));
  return `<section class="estimate-complete" id="estimate-result"><div class="completion-heading"><span class="complete-mark" aria-hidden="true">✓</span><div><h2 id="complete-title" tabindex="-1">ご依頼内容の概算見積書</h2><p>ご検討や社内共有にご利用ください。選択内容の変更とPDF保存ができます。</p></div></div><div class="completed-answers" aria-label="回答を変更する">${answers(true)}</div>
  <article class="estimate-paper" aria-labelledby="document-title"><header class="paper-heading"><div><h2 id="document-title">概算見積書</h2><p>${esc(new Intl.DateTimeFormat('ja-JP',{dateStyle:'long',timeZone:'Asia/Tokyo'}).format(new Date()))}</p></div><div class="paper-sender"><b>Miyabiya Studio</b>PR制作・掲載</div></header><p class="paper-subject">${esc(view.mediaLabel)}</p>
  <table class="estimate-lines"><thead><tr><th scope="col">制作・作業内容</th><th scope="col">金額（税込）</th></tr></thead><tbody>${result.lines.map(line=>`<tr><th scope="row">${esc(line.label)}${line.description?`<small>${esc(line.description)}</small>`:''}</th><td>${esc(amount(line))}</td></tr>`).join('')}</tbody></table>
  <div class="totals"><div class="total-row"><span>${result.pending.length?'金額が分かる項目の小計（税抜）':'小計（税抜）'}</span><span id="document-subtotal">${esc(amountText(result.min,result.max))}</span></div><div class="total-row"><span>消費税相当額（10%）</span><span>${esc(amountText(result.taxMin,result.taxMax))}</span></div><div class="grand-total"><span id="document-total-label">${esc(view.totalLabel)}</span><strong id="document-total">${esc(view.totalText)}</strong></div></div>
  ${result.pending.length?`<section class="pending-box" aria-label="要相談の内容"><strong>正式見積もりで確認する項目があります</strong><ul>${result.pending.map(item=>'<li>'+esc(item.label)+'</li>').join('')}</ul><p>表示した小計に、未確定の料金は含みません。ご依頼内容を確認のうえ、正式な総額をご案内します。</p></section>`:''}
  <details class="document-details"><summary>制作範囲・準備するもの・修正条件を見る</summary><h3>制作・公開の範囲</h3><ul>${view.scope.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul><h3>お客様にご用意いただくもの</h3><ul>${view.preparation.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul><h3>修正条件</h3><ul>${view.revisionNotes.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul></details>
  <p class="document-foot">${esc(view.disclaimer)}</p><p class="document-foot">料金表の更新日：${esc(data.updated)}${data!==currentData?'（共有時の料金で表示しています）':''}</p></article>
  <div class="pdf-recipient"><label for="wizard-recipient">見積書の宛名 <small>任意</small></label><input id="wizard-recipient" data-key="recipient" type="text" maxlength="80" placeholder="会社名・お名前" value="${esc(recipient)}" autocomplete="organization"><select id="wizard-honorific" aria-label="宛名の敬称"><option ${honorific==='御中'?'selected':''}>御中</option><option ${honorific==='様'?'selected':''}>様</option></select></div>
  <div class="document-actions"><button type="button" class="button primary" id="save-pdf">概算見積書をPDFで保存 <span aria-hidden="true">↓</span></button><a class="button secondary" id="estimate-inquiry" href="${esc(mailto(summary(data,state)))}">この内容でPRを相談する</a><button type="button" class="text-button" data-edit="media">回答を選び直す</button></div><p class="pdf-message" id="pdf-message" role="status"></p>
  <p class="sheet-note">宛名はPDFの作成にだけ使い、外部に送信しません。</p>
  <details class="document-details"><summary>同じ見積もりを開く共有URL</summary><p class="sheet-note">同じご依頼内容と概算金額を開くURLです。社内でのご相談にもご利用いただけます。</p><button class="button secondary" type="button" id="wizard-copy-url">見積もりURLをコピー</button><p id="wizard-share-status" role="status"></p><textarea class="estimate-url" aria-label="見積もりの共有URL" readonly>${esc(estimateUrl(data,state,'https://studio.msyn.me/pricing/#estimate-result'))}</textarea></details>
  <details class="document-details" id="wizard-full-terms"><summary>ご依頼前の確認事項・取引条件を見る</summary><div id="wizard-terms-content"></div></details><div class="restart-row"><button type="button" class="text-button" data-edit="media">← 制作物の選択へ戻る</button><button type="button" class="text-button" id="restart">すべての回答をリセット</button></div></section>`;
}
function render(focusKey) {
  const result=quote(data,state),view=quotePresentation(data,state,result);
  if(complete&&['invalid','empty'].includes(result.status)){complete=false;question=result.status==='invalid'?'extras':'media';revisionError=result.error??'';}
  workspace.innerHTML=complete?renderEstimate(result,view):renderForm(result,view);
  if(complete){const host=document.querySelector('#wizard-terms-content');if(hasMain())host.append(terms.cloneNode(true));else host.textContent='制作範囲・修正回数・公開日・お支払い・キャンセル条件は、正式見積もりでご案内します。二次利用・掲載期間・ファイル納品・レポートは個別にご相談ください。';}
  copyVersion++;
  if(result.status!=='invalid')history.replaceState(null,'',estimateUrl(data,state,location.href));
  if(focusKey) workspace.querySelector(`[data-key="${CSS.escape(focusKey)}"]`)?.focus({preventScroll:true});
}
function goTo(key) {
  complete=false;question=key;revisionError='';document.querySelector('#wizard-live').textContent='';render();
  const target=document.querySelector(`#question-${key}`);
  target?.focus({preventScroll:true});target?.scrollIntoView({block:'center',behavior:'auto'});
}
function finish() {
  const result=quote(data,state);
  if(result.status==='empty') return goTo('media');
  if(result.status==='invalid') {revisionError=result.error;question='extras';render();document.querySelector('#wizard-revisions')?.focus();return;}
  questions().forEach(key=>answered.add(key));complete=true;everCompleted=true;revisionError='';render();
  document.querySelector('#complete-title').focus({preventScroll:true});workspace.scrollIntoView({block:'start',behavior:'auto'});
  document.querySelector('#wizard-live').textContent='概算見積書を更新しました。'+quotePresentation(data,state,result).totalText;
}
workspace.addEventListener('change',event=>{
  const target=event.target;
  if(target.id==='wizard-honorific'){honorific=target.value;return;}
  if(target.matches('[data-group]')) {
    const values=new Set(state[target.dataset.group]);target.checked?values.add(target.value):values.delete(target.value);
    state[target.dataset.group]=[...values];answered.add(target.dataset.group==='media'?'media':target.dataset.group==='items'?'assets':'extras');
    render(target.dataset.key);
    if(question==='extras')refreshExtras(true);
  } else if(target.id==='wizard-revisions') {
    state.revisions=target.value;revisionError='';
    // Keep the field and the clicked button in place while focus moves away.
    const result=quote(data,state),node=workspace.querySelector('.flow-aside');
    if(node)node.outerHTML=aside(result,quotePresentation(data,state,result));
  }
});
workspace.addEventListener('input',event=>{
  if(event.target.id==='wizard-recipient')recipient=event.target.value;
  if(event.target.id==='wizard-revisions')state.revisions=event.target.value;
  if(event.target.id==='wizard-revisions')refreshExtras(true);
});
workspace.addEventListener('click',async event=>{
  const button=event.target.closest('button');if(!button)return;
  if(button.dataset.edit)return goTo(button.dataset.edit);
  const qs=questions(),idx=qs.indexOf(question);
  if(button.hasAttribute('data-next')){answered.add(question);return goTo(qs[idx+1]);}
  if(button.hasAttribute('data-prev'))return goTo(qs[idx-1]);
  if(button.hasAttribute('data-complete'))return finish();
  if(button.id==='restart') {
    Object.assign(state,{media:[],items:['materials','thumbnail'],custom:[],revisions:2});document.querySelector('#wizard-live').textContent='選択内容をリセットしました。';
    answered.clear();everCompleted=false;recipient='';return goTo('media');
  }
  if(button.id==='wizard-copy-url') {
    const current=copyVersion,url=estimateUrl(data,state,'https://studio.msyn.me/pricing/#estimate-result');
    try{await navigator.clipboard.writeText(url);if(current===copyVersion)document.querySelector('#wizard-share-status').textContent='見積もりURLをコピーしました。';}
    catch{if(current===copyVersion){document.querySelector('#wizard-share-status').textContent='下のURLをコピーして共有してください。';document.querySelector('.estimate-url').focus();document.querySelector('.estimate-url').select();}}
    return;
  }
  if(button.id==='save-pdf') {
    const message=document.querySelector('#pdf-message');button.disabled=true;lastPdfButton=button;
    message.textContent='PDFを作成しています。';
    try {
      const {downloadEstimatePdf}=await import('./pricing-pdf.mjs');
      await downloadEstimatePdf(data,structuredClone(state),recipient,honorific);
      message.textContent='概算見積書をPDFで保存しました。';
    } catch(error) {message.textContent=/^宛名/.test(error.message)?error.message:'PDFを作成できませんでした。もう一度お試しください。';}
    finally {if(lastPdfButton?.isConnected)lastPdfButton.disabled=false;}
  }
});
render();
if(complete&&location.hash==='#estimate-result')requestAnimationFrame(()=>document.querySelector('#estimate-result').scrollIntoView({block:'start'}));
}
