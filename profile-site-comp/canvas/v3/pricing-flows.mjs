import {quote,quotePresentation,summary,estimateUrl,amountText,taxIncluded} from './pricing-model.mjs';

const data = REVIEW_PRICING_DATA;
const workspace = document.querySelector('#workspace');
const demo = document.querySelector('#demo');
const state = {media:[],items:['materials','thumbnail'],custom:[],revisions:2};
let pattern = 'a', question = 'media', complete = false, everCompleted = false;
let revisionError = '', recipient = '', lastPdfButton;
const answered = new Set();
const titles = {media:'何をつくりますか？',assets:'本編の資料・サムネイルもお任せしますか？',extras:'ほかに希望はありますか？'};
const captions = {
  a:'A：1問に集中して答え、最後に見積書をつくります。初めて依頼する方におすすめです。',
  b:'B：答えた質問を閉じて、次の質問を開きます。回答を見返しながら進められます。',
  c:'C：必要な質問を一覧で答えます。全体を見渡し、好きな順番で選べます。',
};
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
  if(key==='assets') return ['materials','thumbnail'].map(id=>(id==='materials'?'動画用資料':'サムネイル')+'：'+(state.items.includes(id)?'制作を依頼':'自分で用意')).join('\n');
  const list=data.custom.filter(item=>state.custom.includes(item.id)).map(item=>item.label);
  return list.length ? list.join('・') : `軽微修正${state.revisions}回を希望・その他の希望なし`;
}
function questionContent(key) {
  const idx=questions().indexOf(key);
  let hint='', body='';
  if(key==='media') {
    hint='複数選べます。YouTube本編は10〜20分、ショートは60秒程度を想定しています。';
    body='<div class="choices">'+[
      {group:'media',id:'main',title:'YouTube本編',description:'10〜20分程度・1本を制作し、YouTubeで公開',icon:'main'},
      {group:'media',id:'short',title:'ショート動画',description:hasMain()?'本編の内容・撮影素材から60秒程度を1本':'60秒程度・1本を単独で制作',icon:'short'},
      {group:'media',id:'x',title:state.media.some(id=>id!=='x')?'Xで動画を告知':'Xで製品をPR',description:state.media.some(id=>id!=='x')?'公開した動画を紹介する告知シェア・1回':'製品・サービスを紹介するPR投稿・1回',icon:'x'},
    ].map(selectChoice).join('')+'</div><p class="hint">Xのみの場合は製品PR、動画と組み合わせる場合は公開動画の告知です。</p>';
  } else if(key==='assets') {
    hint='制作を依頼するものを選んでください。選択を外したものは、お客様にご用意いただきます。';
    const items=data.checklistItems.filter(item=>['materials','thumbnail'].includes(item.id));
    body='<div class="choices">'+items.map(item=>selectChoice({group:'items',id:item.id,
      title:item.id==='materials'?'動画用の説明資料を依頼':'サムネイル制作を依頼',
      description:item.id==='materials'?'動画で説明する内容と順番をまとめた資料を作成':'動画に使用するサムネイルを制作',
      price:'＋'+amountText(taxIncluded(item.min,data.taxRate,item.taxInclusive),taxIncluded(item.max,data.taxRate,item.taxInclusive))+'（税込）',
    })).join('')+'</div><p class="mini-note">事前検証・撮影・編集・YouTubeでの公開は本編の料金に含まれます。資料とサムネイルは、初期状態では制作を依頼する設定です。</p>';
  } else {
    hint='必要なものだけ選んでください。追加の希望がなければ、そのまま見積書をつくれます。';
    const choices='<div class="choices">'+data.custom.map(item=>selectChoice({group:'custom',id:item.id,title:item.label})).join('')+'</div>';
    body=(pattern==='c'?'<details class="optional-details"><summary>二次利用・複数本などの希望を選ぶ</summary>'+choices+'</details>':choices)
      +`<div class="revisions"><label for="revisions">公開前の軽微修正の希望回数</label><input id="revisions" data-key="revisions" type="number" inputmode="numeric" min="0" step="1" value="${esc(state.revisions)}" aria-describedby="revision-note"><span>回</span></div>`
      +`<p class="rev-note" id="revision-note">${hasMain()?'本編は2回まで料金内、3回目以降は1回5,500円（税込）です。':'希望回数をもとに正式見積もりで確認します。'}${state.media.some(id=>id==='short'||id==='x')?' ショート・Xの無料回数と追加料金は要相談です。':''}</p>`;
  }
  return `<section class="question" aria-labelledby="question-${key}"><p class="question-kicker">QUESTION ${String(idx+1).padStart(2,'0')}${key==='extras'?' ・ 任意':''}</p><h2 id="question-${key}" tabindex="-1">${titles[key]}</h2><p class="question-hint">${hint}</p>${body}</section>`;
}
function answers(completed=false) {
  return questions().map(key=>`<${completed?'div':'li'}><small>${{media:'制作物',assets:'本編の追加制作',extras:'その他の希望'}[key]}</small><div class="answer-row"><p class="answer-value">${esc(answerText(key))}</p><button type="button" class="text-button" data-edit="${key}">${completed?'変更する':'選び直す'}</button></div></${completed?'div':'li'}>`).join('');
}
function aside(result,view) {
  return `<aside class="flow-aside" aria-label="回答の確認"><h2>ここまでの回答</h2><ul class="answer-list">${answers()}</ul>${everCompleted&&state.media.length?`<p class="aside-price-label">${result.pending?.length?'変更後の小計（税込）':'変更後の概算（税込）'}</p><p class="aside-price">${esc(view.totalText)}</p>`:''}<p class="aside-foot">回答はあとから変更できます。最後に明細と金額をまとめて確認します。</p></aside>`;
}
function navigation(key) {
  const qs=questions(),index=qs.indexOf(key),last=index===qs.length-1;
  return `<div class="navigation">${index>0?'<button type="button" class="text-button" data-prev>← 前の質問へ</button>':''}${everCompleted&&!last?'<button type="button" class="button secondary" data-complete>見積書を更新</button>':''}<button type="button" class="button primary" ${last?'data-complete':'data-next'} ${!state.media.length?'disabled':''}>${last?(everCompleted?'見積書を更新する':'概算見積書をつくる'):'次へ'}<span class="button-arrow" aria-hidden="true">→</span></button></div>`;
}
function renderForm(result,view) {
  const qs=questions();if(!qs.includes(question)) question='media';
  let content='';
  if(pattern==='a') content=`<ol class="progress" aria-label="${qs.indexOf(question)+1}問目／全${qs.length}問">${qs.map((key,index)=>`<li class="${index<qs.indexOf(question)?'done':key===question?'current':''}" ${key===question?'aria-current="step"':''}><span class="sr-only">${titles[key]}</span></li>`).join('')}</ol>${questionContent(question)}${navigation(question)}`;
  if(pattern==='b') content=qs.map((key,index)=>`<section class="accordion-question"><button type="button" id="accordion-${key}" class="accordion-heading" data-open="${key}" aria-expanded="${question===key}" aria-controls="body-${key}"><span class="question-number">${answered.has(key)?'✓':String(index+1).padStart(2,'0')}</span><span class="heading-copy"><b>${titles[key]}</b>${question!==key?`<small>${esc(answerText(key))}</small>`:''}</span><span class="accordion-toggle" aria-hidden="true">${question===key?'−':'＋'}</span></button><div class="accordion-body" id="body-${key}" ${question===key?'':'hidden'}>${questionContent(key)}${navigation(key)}</div></section>`).join('');
  if(pattern==='c') content=qs.map(key=>`<div class="inline-question" id="inline-${key}">${questionContent(key)}</div>`).join('')+`<div class="complete-actions"><button type="button" class="button primary" data-complete ${!state.media.length?'disabled':''}>${everCompleted?'見積書を更新する':'概算見積書をつくる'}<span aria-hidden="true"> →</span></button></div>`;
  return `<div class="flow-layout"><div class="flow-main">${revisionError?`<p class="error" role="alert">${esc(revisionError)}</p>`:''}${content}</div>${aside(result,view)}</div>`;
}
function renderEstimate(result,view) {
  const amount=line=>amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive));
  return `<section class="estimate-complete"><div class="completion-heading"><span class="complete-mark" aria-hidden="true">✓</span><div><h2 id="complete-title" tabindex="-1">概算見積書ができました</h2><p>内容を確認し、PDFで保存できます。回答を変えると、見積書も更新できます。</p></div></div><div class="completed-answers" aria-label="回答を変更する">${answers(true)}</div>
  <article class="estimate-paper" aria-labelledby="document-title"><header class="paper-heading"><div><h2 id="document-title">概算見積書</h2><p>${esc(new Intl.DateTimeFormat('ja-JP',{dateStyle:'long'}).format(new Date()))}</p></div><div class="paper-sender"><b>Miyabiya Studio</b>PR制作・掲載</div></header><p class="paper-subject">${esc(view.mediaLabel)}</p>
  <table class="estimate-lines"><thead><tr><th scope="col">制作・作業内容</th><th scope="col">金額（税込）</th></tr></thead><tbody>${result.lines.map(line=>`<tr><th scope="row">${esc(line.label)}${line.description?`<small>${esc(line.description)}</small>`:''}</th><td>${esc(amount(line))}</td></tr>`).join('')}</tbody></table>
  <div class="totals"><div class="total-row"><span>${result.pending.length?'金額が分かる項目の小計（税抜）':'小計（税抜）'}</span><span id="document-subtotal">${esc(amountText(result.min,result.max))}</span></div><div class="total-row"><span>消費税相当額（10%）</span><span>${esc(amountText(result.taxMin,result.taxMax))}</span></div><div class="grand-total"><span id="document-total-label">${esc(view.totalLabel)}</span><strong id="document-total">${esc(view.totalText)}</strong></div></div>
  ${result.pending.length?`<section class="pending-box" aria-label="要相談の内容"><strong>正式見積もりで確認する項目があります</strong><ul>${result.pending.map(item=>'<li>'+esc(item.label)+'</li>').join('')}</ul><p>表示した小計に、未確定の料金は含みません。制作範囲と条件を確認して、正式な総額をお伝えします。</p></section>`:''}
  <details class="document-details"><summary>制作範囲・準備するもの・修正条件を見る</summary><h3>制作・公開の範囲</h3><ul>${view.scope.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul><h3>お客様にご用意いただくもの</h3><ul>${view.preparation.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul><h3>修正条件</h3><ul>${view.revisionNotes.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul></details>
  <p class="document-foot">${esc(view.disclaimer)}</p></article>
  <div class="pdf-recipient"><label for="recipient">見積書の宛名 <small>任意・「御中」を付けて出力</small></label><input id="recipient" data-key="recipient" type="text" maxlength="80" placeholder="会社名・お名前" value="${esc(recipient)}" autocomplete="organization"></div>
  <div class="document-actions"><button type="button" class="button primary" id="save-pdf">概算見積書をPDFで保存 <span aria-hidden="true">↓</span></button><button type="button" class="button secondary" id="preview-inquiry">相談内容を確認する</button><button type="button" class="text-button" data-edit="media">回答を選び直す</button></div><p class="pdf-message" id="pdf-message" role="status"></p>
  <p class="sheet-note">宛名はPDFの作成にだけ使い、外部に送信しません。</p>
  <details class="document-details"><summary>同じ見積もりを開く共有URL</summary><p class="sheet-note">現在の公開サイトで、同じ選択内容と料金を確認できるURLです。</p><textarea class="estimate-url" aria-label="見積もりの共有URL" readonly>${esc(estimateUrl(data,state))}</textarea></details>
  <div class="restart-row"><button type="button" class="text-button" data-edit="media">← 制作物の選択へ戻る</button><button type="button" class="text-button" id="restart">すべての回答をリセット</button></div></section>`;
}
function render(focusKey) {
  const result=quote(data,state),view=quotePresentation(data,state,result);
  workspace.innerHTML=complete?renderEstimate(result,view):renderForm(result,view);
  if(focusKey) workspace.querySelector(`[data-key="${CSS.escape(focusKey)}"]`)?.focus({preventScroll:true});
}
function goTo(key) {
  complete=false;question=key;revisionError='';render();
  const target=pattern==='b'?document.querySelector(`#accordion-${key}`):document.querySelector(`#question-${key}`);
  target?.focus({preventScroll:true});target?.scrollIntoView({block:'center',behavior:'auto'});
}
function finish() {
  const result=quote(data,state);
  if(result.status==='empty') return goTo('media');
  if(result.status==='invalid') {revisionError=result.error;question='extras';render();document.querySelector('#revisions')?.focus();return;}
  questions().forEach(key=>answered.add(key));complete=true;everCompleted=true;revisionError='';render();
  document.querySelector('#complete-title').focus({preventScroll:true});workspace.scrollIntoView({block:'start',behavior:'auto'});
  document.querySelector('#announcement').textContent='概算見積書を更新しました。'+quotePresentation(data,state,result).totalText;
}
function selectPattern(id,focus=false) {
  pattern=id;demo.dataset.pattern=id;complete=false;question='media';revisionError='';
  for(const tab of document.querySelectorAll('[data-pattern][role=tab]')) {
    const on=tab.dataset.pattern===id;tab.setAttribute('aria-selected',on);tab.tabIndex=on?0:-1;
    if(on&&focus)tab.focus();
  }
  demo.setAttribute('aria-labelledby','tab-'+id);
  document.querySelector('#pattern-note').textContent=captions[id];render();
}
document.querySelector('.pattern-tabs').addEventListener('click',event=>{
  const tab=event.target.closest('[role=tab]');if(tab)selectPattern(tab.dataset.pattern);
});
document.querySelector('.pattern-tabs').addEventListener('keydown',event=>{
  const tab=event.target.closest('[role=tab]');if(!tab)return;
  const ids=['a','b','c'],index=ids.indexOf(tab.dataset.pattern);
  const next=event.key==='ArrowRight'?(index+1)%3:event.key==='ArrowLeft'?(index+2)%3:event.key==='Home'?0:event.key==='End'?2:null;
  if(next!==null){event.preventDefault();selectPattern(ids[next],true);}
});
workspace.addEventListener('change',event=>{
  const target=event.target;
  if(target.matches('[data-group]')) {
    const values=new Set(state[target.dataset.group]);target.checked?values.add(target.value):values.delete(target.value);
    state[target.dataset.group]=[...values];answered.add(target.dataset.group==='media'?'media':target.dataset.group==='items'?'assets':'extras');
    render(target.dataset.key);
  } else if(target.id==='revisions') {
    state.revisions=target.value;revisionError='';
    // Keep the field and the clicked button in place while focus moves away.
    const result=quote(data,state),node=workspace.querySelector('.flow-aside');
    if(node)node.outerHTML=aside(result,quotePresentation(data,state,result));
  }
});
workspace.addEventListener('input',event=>{
  if(event.target.id==='recipient')recipient=event.target.value;
  if(event.target.id==='revisions')state.revisions=event.target.value;
});
workspace.addEventListener('click',async event=>{
  const button=event.target.closest('button');if(!button)return;
  if(button.dataset.edit)return goTo(button.dataset.edit);
  if(button.dataset.open)return goTo(button.dataset.open);
  const qs=questions(),idx=qs.indexOf(question);
  if(button.hasAttribute('data-next')){answered.add(question);return goTo(qs[idx+1]);}
  if(button.hasAttribute('data-prev'))return goTo(qs[idx-1]);
  if(button.hasAttribute('data-complete'))return finish();
  if(button.id==='restart') {
    Object.assign(state,{media:[],items:['materials','thumbnail'],custom:[],revisions:2});
    answered.clear();everCompleted=false;recipient='';return goTo('media');
  }
  if(button.id==='preview-inquiry') {
    document.querySelector('#inquiry-text').value=summary(data,state);
    document.querySelector('#inquiry-dialog').showModal();return;
  }
  if(button.id==='save-pdf') {
    const message=document.querySelector('#pdf-message');button.disabled=true;lastPdfButton=button;
    message.textContent='PDFを作成しています。';
    try {
      const {downloadEstimatePdf}=await import('/pricing-pdf.mjs');
      await downloadEstimatePdf(data,structuredClone(state),recipient,'御中');
      message.textContent='概算見積書をPDFで保存しました。';
    } catch(error) {message.textContent=/^宛名/.test(error.message)?error.message:'PDFを作成できませんでした。もう一度お試しください。';}
    finally {if(lastPdfButton?.isConnected)lastPdfButton.disabled=false;}
  }
});
document.querySelectorAll('[data-close-dialog]').forEach(button=>button.addEventListener('click',()=>document.querySelector('#inquiry-dialog').close()));
document.querySelector('#inquiry-dialog').addEventListener('close',()=>document.querySelector('#preview-inquiry')?.focus());
selectPattern('a');
