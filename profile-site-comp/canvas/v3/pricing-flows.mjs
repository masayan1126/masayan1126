import {quote,quotePresentation,amountText,taxIncluded,normalizeNotes} from './pricing-model.mjs';
import {fixedReviewRates,relatedQuotes,reviewSummary} from './pricing-flows-model.mjs';

const source=REVIEW_PRICING_DATA, data=fixedReviewRates(source);
const workspace=document.querySelector('#workspace'), dialog=document.querySelector('#simulator');
let dialogOpener=document.querySelector('#open-simulator');
const state={media:[],items:['materials','thumbnail'],revisions:2,custom:[],notes:''};
let pattern='a', question='media', complete=false, error='', comparisonOpen=false;
const names={a:'完成直後に並べる',b:'固定バーで案内する',c:'比較画面へ切り替える'};
const captions={a:'案1：完成画面の最初に、選んだ見積もりと別の2案を表示します。スクロールする前に比較に気づけます。',b:'案2：見積書を読み進めている間も、画面下の固定バーから別の6案を確認できます。',c:'案3：「選んだ見積書」と「ほかの6案」を切り替えて比較します。見積書の上にも比較ボタンを置きます。'};
const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
const titles={media:'どのPRをご希望ですか？',assets:'資料・サムネイル制作も依頼しますか？',extras:'追加のご希望はありますか？'};
const esc=text=>String(text).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const main=()=>state.media.includes('main');
const questions=()=>main()?['media','assets','extras']:['media','extras'];
const money=line=>amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive));
function choice(group,id,title,description,price='') {
  return '<label class="choice"><input type="checkbox" data-group="'+group+'" data-key="'+group+'-'+id+'" value="'+id+'" '+(state[group].includes(id)?'checked':'')+'><strong>'+esc(title)+'</strong><small>'+esc(description)+'</small>'+(price?'<span class="choice-price">'+esc(price)+'</span>':'')+'</label>';
}
function mediaText() {return quotePresentation(data,state).mediaLabel||'まだ選択していません';}
function assetText() {return ['materials','thumbnail'].map(id=>(id==='materials'?'動画用資料':'サムネイル')+'：'+(state.items.includes(id)?'制作を依頼':'お客様でご用意')).join('\n');}
function extraText() {return ['軽微修正'+state.revisions+'回をご希望',normalizeNotes(state.notes)].filter(Boolean).join('\n');}
function fieldContent(key) {
  let hint='',body='';
  if(key==='media') {
    hint='ご希望の制作・掲載先をお選びください。複数選択できます。';
    body='<div class="choices">'+choice('media','main','YouTube本編で紹介','10分から20分程度・1本を制作し、AIギルドchで公開')+choice('media','short','ショート動画で紹介',main()?'本編の内容・撮影素材から60秒程度を1本（詳細は要相談）':'60秒程度・1本を単独制作（料金・条件は要相談）')+choice('media','x',state.media.some(id=>id!=='x')?'Xで動画を告知':'Xで製品をPR',state.media.some(id=>id!=='x')?'公開動画の告知シェア・1回（料金・条件は要相談）':'製品・サービスのPR投稿・1回（料金・条件は要相談）')+'</div><p class="mini-note">Xのみの場合は製品PR、動画と組み合わせる場合は公開動画の告知です。</p>';
  } else if(key==='assets') {
    hint='こちらで制作するものをお選びください。選択を外したものは、お客様にご用意をお願いします。';
    body='<div class="choices">'+data.checklistItems.filter(item=>['materials','thumbnail'].includes(item.id)).map(item=>choice('items',item.id,item.id==='materials'?'動画用の説明資料も依頼する':'サムネイル制作も依頼する',item.id==='materials'?'※動画で紹介する項目をまとめた台本や構成案などをご用意いただける場合は、この項目の選択を外せます。':'YouTubeで表示するサムネイルを制作します。','＋'+money(item)+'（税込・仮設定）')).join('')+'</div><p class="mini-note">製品マニュアルなどをもとに動画用の説明資料の作成を依頼される場合は、資料制作をご選択ください。</p>';
  } else {
    hint='追加費用は個別にお見積もりし、表示中の小計には含みません。';
    body='<label class="request-label" for="notes">ご希望の内容（任意）</label><textarea class="request-input" id="notes" data-key="notes" maxlength="1000" rows="4" placeholder="準備物や作業の分担を相談したい\n目安より大幅に長い動画を依頼したい">'+esc(state.notes)+'</textarea><p class="small-note">1,000文字まで入力できます。</p><div class="revisions"><label for="revisions">公開前の軽微修正の希望回数</label><input id="revisions" data-key="revisions" type="number" min="0" step="1" inputmode="numeric" value="'+esc(state.revisions)+'" aria-describedby="revision-note"><span>回</span></div><p class="revision-note" id="revision-note">'+(main()?'本編は2回まで料金内、3回目以降は1回5,500円（税込）です。':'希望回数をもとに正式見積もりで確認します。')+(state.media.some(id=>id!=='main')?' ショート・Xの無料回数と追加料金は要相談です。':'')+'</p>';
  }
  return '<section class="question" aria-labelledby="question-'+key+'"><h3 id="question-'+key+'" tabindex="-1">'+titles[key]+'</h3><p class="question-hint">'+hint+'</p>'+body+'</section>';
}
function amountPanel(result,view) {
  if(result.status==='invalid')return '<div class="summary-total"><p class="error">'+esc(result.error)+'</p></div>';
  return '<div class="summary-total"><small>'+esc(view.totalLabel)+'</small><strong>'+esc(view.totalText)+'</strong><p>'+(result.pending?.length?'要相談の料金は含みません。':'税込の固定料金案です。')+'</p></div>';
}
function lineTable(result) {
  return '<table class="estimate-lines"><thead><tr><th scope="col">制作・作業内容</th><td>金額（税込）</td></tr></thead><tbody>'+result.lines.map(item=>'<tr><th scope="row">'+esc(item.label)+'</th><td>'+esc(money(item))+'</td></tr>').join('')+'</tbody></table>';
}
function pendingBox(result) {
  return result.pending?.length?'<section class="pending-box" aria-label="要相談の内容"><strong>正式見積もりで確認する内容</strong><ul>'+result.pending.map(item=>'<li>'+esc(item.label)+'</li>').join('')+'</ul><p>要相談の料金は小計に含みません。正式な総額は、ご希望を確認してご案内します。</p></section>':'';
}
function liveSummary(result,view) {
  return '<aside class="live-summary" aria-label="選択中の見積もり"><h3>選択中の見積もり</h3><div class="summary-line"><small>制作・掲載先</small><p>'+esc(mediaText())+'</p></div>'+(main()?'<div class="summary-line"><small>資料・サムネイル</small><p>'+esc(assetText())+'</p></div>':'')+'<div class="summary-line"><small>その他の希望</small><p>'+esc(extraText())+'</p></div>'+amountPanel(result,view)+'</aside>';
}
function navigation() {
  const qs=questions(),idx=qs.indexOf(question),last=idx===qs.length-1;
  return '<div class="navigation">'+(idx?'<button class="text-button" type="button" data-prev>前の質問へ</button>':'')+'<button class="button primary" type="button" '+(last?'data-complete':'data-next')+' '+(!state.media.length?'disabled':'')+'>'+(last?'見積書と別のプランを確認':'次へ')+'</button></div>';
}
function form(result,view) {
  const qs=questions();if(!qs.includes(question))question='media';
  const body='<ol class="progress" aria-label="質問の進み具合">'+qs.map((key,idx)=>'<li class="'+(key===question?'current':'')+'" '+(key===question?'aria-current="step"':'')+'>'+String(idx+1)+'. '+({media:'制作・掲載先',assets:'資料・サムネイル',extras:'追加のご希望'})[key]+'</li>').join('')+'</ol>'+fieldContent(question)+navigation();
  return '<div class="editor"><div class="editor-main">'+(error?'<p class="error" role="alert">'+esc(error)+'</p>':'')+body+'</div>'+liveSummary(result,view)+'</div>';
}
function answerControls() {
  return '<aside class="result-controls"><h4>ご依頼内容を変更する</h4>'+questions().map(key=>'<div class="answer-row"><small>'+({media:'制作・掲載先',assets:'資料・サムネイル',extras:'その他の希望'})[key]+'</small><p>'+esc(key==='media'?mediaText():key==='assets'?assetText():extraText())+'</p><button class="text-button" type="button" data-edit="'+key+'">変更する</button></div>').join('')+'</aside>';
}
function relatedCard(item) {
  const delta=item.knownDelta==null?'差額は、要相談の内容を確認してご案内します。':item.knownDelta===0?'現在の案と同額です。':(item.knownDelta>0?'現在の案から＋':'現在の案から−')+Math.abs(item.knownDelta).toLocaleString('ja-JP')+'円（税込）';
  return '<article class="related-card"><p class="related-label">'+esc(item.label)+'</p><h4>'+esc(item.view.mediaLabel)+'</h4><p class="related-total-label">'+esc(item.view.totalLabel)+'</p><strong>'+esc(item.view.totalText)+'</strong><p class="related-delta">'+esc(delta)+'</p><details class="alt-breakdown"><summary>この案の見積もり明細を見る</summary>'+lineTable(item.result)+pendingBox(item.result)+'</details><button type="button" class="button secondary" data-alt="'+item.state.media.join(',')+'">この案で見積書を作る</button></article>';
}
function selectedOverview(view) {
  return '<div class="selected-overview"><div><p class="eyebrow">選んだ内容の見積もり</p><h4>'+esc(view.mediaLabel)+'</h4></div><div><small>'+esc(view.totalLabel)+'</small><strong>'+esc(view.totalText)+'</strong></div></div>';
}
function comparisonSection(alternatives,all=false) {
  return '<section class="related-section" aria-labelledby="related-title"><div class="comparison-heading"><div><p class="eyebrow">別の組み合わせも自動でお見積もりしました</p><h3 id="related-title" tabindex="-1">ほかの組み合わせもご検討いただけます</h3></div><span class="count-badge">6案</span></div><p>資料・サムネイルの選択、修正回数、ご希望の内容を引き継いでいます。案を選ぶまで、現在の見積書は変わりません。</p><div class="related-grid">'+alternatives.slice(0,all?6:2).map(relatedCard).join('')+'</div>'+(all?'':'<details class="all-patterns"><summary>残り4パターンの見積もりも見る</summary><div class="related-grid">'+alternatives.slice(2).map(relatedCard).join('')+'</div></details>')+'</section>';
}
function resultNavigation() {
  return '<div class="result-tabs" role="tablist" aria-label="見積書とほかの案を切り替える"><button id="result-selected" type="button" role="tab" aria-controls="result-panel" aria-selected="'+!comparisonOpen+'" tabindex="'+(comparisonOpen?-1:0)+'" data-view="selected">選んだ見積書</button><button id="result-compare" type="button" role="tab" aria-controls="result-panel" aria-selected="'+comparisonOpen+'" tabindex="'+(comparisonOpen?0:-1)+'" data-view="compare">ほかの組み合わせ<span>6案</span></button></div>';
}
function results(result,view) {
  const alternatives=relatedQuotes(data,state),spotlight=alternatives[0];
  const heading='<div class="result-heading"><div><p class="completion-mark"><span aria-hidden="true">✓</span> ご希望の内容で計算しました</p><h3 id="complete-title" tabindex="-1">見積書ができました</h3></div><button class="text-button" type="button" data-edit="media">回答を選び直す</button></div>';
  const paper='<div class="result-grid"><article class="estimate-paper" aria-label="選択した見積書"><header class="paper-header"><div><h4>概算見積書</h4><p>固定料金の確認用・未承認</p></div><span>Miyabiya Studio</span></header><p class="paper-subject">'+esc(view.mediaLabel)+'</p>'+lineTable(result)+'<div class="totals"><div class="total-row"><span>小計（税抜）</span><span>'+esc(amountText(result.min,result.max))+'</span></div><div class="total-row"><span>消費税相当額（10%）</span><span>'+esc(amountText(result.taxMin,result.taxMax))+'</span></div><div class="grand-total"><span>'+esc(view.totalLabel)+'</span><strong id="document-total">'+esc(view.totalText)+'</strong></div></div>'+pendingBox(result)+'<p class="document-note">この見積書は画面確認用です。現行の上限額を固定料金にした仮設定で、正式見積もりではありません。</p></article>'+answerControls()+'</div><div class="result-actions"><button type="button" id="print-estimate" class="button primary">見積書を印刷・PDF保存</button><button type="button" id="copy-estimate" class="button secondary">見積内容をコピー</button><button type="button" id="reset" class="text-button">最初から選び直す</button></div><p class="copy-status" role="status" id="copy-status"></p><details class="inquiry-preview"><summary>この内容の相談文を見る</summary><p class="small-note">確認用の文章です。この画面からメールは送信されません。</p><textarea readonly aria-label="相談文のプレビュー">'+esc(reviewSummary(data,state))+'</textarea></details>';
  const compareLead='<div class="compare-invitation"><div><p class="eyebrow">ほかの6案もできています</p><h4>'+esc(spotlight.label)+'</h4><p>選んだ内容はそのままで、別の組み合わせと比べられます。</p></div><button type="button" class="button primary" data-compare>6案を比べる <span aria-hidden="true">→</span></button></div>';
  let body='';
  if(pattern==='a')body='<div class="comparison-first">'+selectedOverview(view)+comparisonSection(alternatives)+'</div><h3 class="document-divider">選んだ内容の見積書・明細</h3>'+paper;
  if(pattern==='b')body=selectedOverview(view)+paper+comparisonSection(alternatives,true);
  if(pattern==='c')body=resultNavigation()+'<div id="result-panel" role="tabpanel" aria-labelledby="'+(comparisonOpen?'result-compare':'result-selected')+'">'+(comparisonOpen?selectedOverview(view)+comparisonSection(alternatives,true)+'<button class="button secondary back-to-estimate" type="button" data-view="selected">選んだ見積書に戻る</button>':compareLead+paper)+'</div>';
  return '<section class="results">'+heading+body+'</section>';
}
function animateEntry(mode) {
  if(reducedMotion.matches)return;
  const target=workspace.querySelector(complete?'.results':'.question');
  target?.animate([{opacity:0,transform:'translate'+(complete?'Y(14px)':'X('+(mode==='back'?'-':'')+'18px)')},{opacity:1,transform:'translate(0)'}],{duration:280,easing:'cubic-bezier(.2,.7,.2,1)'});
  if(complete)workspace.querySelectorAll('.related-card').forEach((card,index)=>card.animate([{opacity:0,transform:'translateY(12px)'},{opacity:1,transform:'translateY(0)'}],{duration:300,delay:70+Math.min(index,3)*55,fill:'backwards',easing:'ease-out'}));
}
function render(focusKey,motion) {
  const result=quote(data,state),view=quotePresentation(data,state,result);
  workspace.innerHTML=complete?results(result,view):form(result,view);
  dialog.querySelector('.comparison-dock')?.remove();
  if(complete&&pattern==='b') {
    const first=relatedQuotes(data,state)[0],dock=document.createElement('footer');
    dock.className='comparison-dock';dock.setAttribute('aria-label','別の組み合わせのご案内');
    dock.innerHTML='<div><p>ほかの6案もできています</p><strong>'+esc(first.label)+'</strong></div><button type="button" class="button primary" data-compare>6案を比べる <span aria-hidden="true">↑</span></button>';
    dialog.append(dock);
  }
  updateLanding();
  if(focusKey) {
    const input=workspace.querySelector('[data-key="'+CSS.escape(focusKey)+'"]');input?.focus({preventScroll:true});
    if(input?.checked&&!reducedMotion.matches)input.closest('.choice')?.animate([{transform:'scale(.985)'},{transform:'scale(1)'}],{duration:180,easing:'ease-out'});
  }
  if(motion)animateEntry(motion);
}
function updateLanding() {
  const sample=state.media.length?state:{media:['main'],items:['materials','thumbnail'],revisions:2};
  const result=quote(data,sample),view=quotePresentation(data,sample,result);
  document.querySelector('#landing-price').innerHTML='<small>'+(state.media.length?'選択中の内容':'料金の例・固定料金の仮設定')+'</small><h2>'+esc(view.mediaLabel)+'</h2><small>'+esc(view.totalLabel)+'</small><strong>'+esc(view.totalText)+'</strong><p>'+(result.status==='invalid'?'修正回数をご確認ください。':result.pending?.length?'要相談の料金は含みません。':state.media.length?'選択した内容の固定料金案です。':'説明資料・サムネイル込みの例です。')+'</p>';
}
function refreshSummary() {
  const result=quote(data,state),view=quotePresentation(data,state,result),summary=workspace.querySelector('.live-summary');
  if(summary)summary.outerHTML=liveSummary(result,view);
  updateLanding();
}
function goTo(key) {
  const back=questions().indexOf(key)<questions().indexOf(question);
  complete=false;comparisonOpen=false;question=key;error='';render(null,back?'back':'forward');
  const target=document.querySelector('#question-'+key);target?.focus({preventScroll:true});target?.scrollIntoView({block:'start'});
}
function finish() {
  const result=quote(data,state);
  if(result.status==='empty')return goTo('media');
  if(result.status==='invalid'){error=result.error;question='extras';render();document.querySelector('#revisions')?.focus();return;}
  complete=true;comparisonOpen=false;error='';render(null,'complete');document.querySelector('#dialog-scroll').scrollTop=0;document.querySelector('#complete-title').focus({preventScroll:true});
  document.querySelector('#announcement').textContent='見積書と別パターンの見積もりを作成しました。';
}
function selectPattern(id,focus=false) {
  pattern=id;comparisonOpen=false;error='';
  document.querySelector('#demo').dataset.pattern=id;document.querySelector('#demo').setAttribute('aria-labelledby','tab-'+id);dialog.dataset.pattern=id;
  for(const tab of document.querySelectorAll('.pattern-tabs [role=tab]')){const on=tab.dataset.pattern===id;tab.setAttribute('aria-selected',on);tab.tabIndex=on?0:-1;if(on&&focus)tab.focus();}
  for(const tab of document.querySelectorAll('[data-variant]'))tab.setAttribute('aria-pressed',String(tab.dataset.variant===id));
  document.querySelector('#pattern-note').textContent=captions[id];document.querySelector('#dialog-pattern').textContent='A案の操作 / 案'+({a:1,b:2,c:3})[id]+'：'+names[id];render(null,'forward');document.querySelector('#dialog-scroll').scrollTop=0;
}
document.querySelector('.pattern-tabs').addEventListener('click',event=>{const tab=event.target.closest('[role=tab]');if(tab)selectPattern(tab.dataset.pattern);});
document.querySelector('.pattern-tabs').addEventListener('keydown',event=>{const ids=['a','b','c'],tab=event.target.closest('[role=tab]');if(!tab)return;const index=ids.indexOf(tab.dataset.pattern),next=event.key==='ArrowRight'?(index+1)%3:event.key==='ArrowLeft'?(index+2)%3:event.key==='Home'?0:event.key==='End'?2:null;if(next!==null){event.preventDefault();selectPattern(ids[next],true);}});
document.querySelector('.dialog-variants').addEventListener('click',event=>{const tab=event.target.closest('[data-variant]');if(tab)selectPattern(tab.dataset.variant);});
function openSimulator(event) {
  dialogOpener=event?.currentTarget||document.querySelector('#open-simulator');
  render();dialog.showModal();document.body.style.overflow='hidden';document.querySelector('#dialog-title').focus({preventScroll:true});animateEntry('forward');
}
document.querySelector('#open-simulator').addEventListener('click',openSimulator);
document.querySelector('#preview-result').addEventListener('click',event=>{if(!state.media.length)state.media=['main'];openSimulator(event);finish();});
function showComparison() {
  if(pattern==='c') {comparisonOpen=true;render(null,'forward');document.querySelector('#dialog-scroll').scrollTop=0;}
  document.querySelector('#related-title')?.focus({preventScroll:true});
  document.querySelector('#related-title')?.scrollIntoView({behavior:reducedMotion.matches?'instant':'smooth',block:'start'});
}
dialog.addEventListener('click',event=>{if(event.target.closest('[data-compare]'))showComparison();});
workspace.addEventListener('keydown',event=>{
  const tab=event.target.closest('.result-tabs [role="tab"]');if(!tab||!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
  event.preventDefault();comparisonOpen=event.key==='Home'?false:event.key==='End'?true:!comparisonOpen;
  render(null,'forward');document.querySelector(comparisonOpen?'#result-compare':'#result-selected').focus({preventScroll:true});
});
document.querySelector('#close-simulator').addEventListener('click',()=>dialog.close());
dialog.addEventListener('close',()=>{document.body.style.overflow='';dialogOpener.focus();});
workspace.addEventListener('change',event=>{const target=event.target;if(target.matches('[data-group]')){const values=new Set(state[target.dataset.group]);target.checked?values.add(target.value):values.delete(target.value);state[target.dataset.group]=[...values];render(target.dataset.key);}else if(target.id==='notes'||target.id==='revisions')refreshSummary();});
workspace.addEventListener('input',event=>{if(event.target.id==='notes')state.notes=event.target.value;if(event.target.id==='revisions')state.revisions=event.target.value;refreshSummary();});
workspace.addEventListener('click',async event=>{
  const button=event.target.closest('button');if(!button)return;
  if(button.dataset.edit)return goTo(button.dataset.edit);
  if(button.hasAttribute('data-view')){comparisonOpen=button.dataset.view==='compare';render(null,'forward');document.querySelector('#dialog-scroll').scrollTop=0;document.querySelector(comparisonOpen?'#result-compare':'#result-selected').focus({preventScroll:true});return;}
  if(button.hasAttribute('data-alt')){state.media=button.dataset.alt.split(',');return finish();}
  if(button.hasAttribute('data-next'))return goTo(questions()[questions().indexOf(question)+1]);
  if(button.hasAttribute('data-prev'))return goTo(questions()[questions().indexOf(question)-1]);
  if(button.hasAttribute('data-complete'))return finish();
  if(button.id==='reset'){Object.assign(state,{media:[],items:['materials','thumbnail'],revisions:2,custom:[],notes:''});return goTo('media');}
  if(button.id==='print-estimate')return window.print();
  if(button.id==='copy-estimate'){try{await navigator.clipboard.writeText(reviewSummary(data,state));document.querySelector('#copy-status').textContent='確認用の見積内容をコピーしました。';}catch{document.querySelector('#copy-status').textContent='下の相談文を開いてコピーしてください。';workspace.querySelector('.inquiry-preview').open=true;}return;}
});
document.querySelector('#rate-details').innerHTML='<div class="rate-grid">'+data.checklistItems.map(item=>'<div><span>'+esc(item.label)+'</span><b>'+esc(money(item))+'</b></div>').join('')+'</div>';
selectPattern('a');
