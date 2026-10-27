const tabs=[...document.querySelectorAll('[role="tab"]')];
const panels=[document.querySelector('#compare-view'),document.querySelector('#context-view')];
const fontChoice=document.querySelector('#context-choice');
const pageChoice=document.querySelector('#context-page');
const frame=document.querySelector('#context-frame');
frame.addEventListener('load',async()=>{
  const doc=frame.contentDocument;
  const match=frame.contentWindow.location.pathname.match(/\/([a-e])-(home|profile|works|talks|membership|pricing|contact)\.html$/);
  if(!doc||!match)return;
  fontChoice.value=match[1];
  if([...pageChoice.options].some(option=>option.value===match[2]))pageChoice.value=match[2];
  frame.title=fontChoice.selectedOptions[0].text+'・'+pageChoice.selectedOptions[0].text;
  await doc.fonts.ready;
  if(frame.contentDocument!==doc)return;
  const sizes=new Set();
  const walker=doc.createTreeWalker(doc.body,frame.contentWindow.NodeFilter.SHOW_TEXT);
  for(let node;node=walker.nextNode();){
    if(!node.textContent.trim()||node.parentElement.closest('script,style,noscript'))continue;
    if(node.parentElement.checkVisibility())sizes.add(frame.contentWindow.getComputedStyle(node.parentElement).fontSize);
  }
  const status=document.querySelector('#context-status');
  if(!status){const node=document.createElement('p');node.id='context-status';node.className='context-note';node.setAttribute('role','status');document.querySelector('.context-stage').before(node);}
  document.querySelector('#context-status').textContent='表示中：'+fontChoice.selectedOptions[0].text+' ／ '+[...sizes].sort((a,b)=>Number.parseFloat(a)-Number.parseFloat(b)).join('・');
});
function view(index){
  tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.tabIndex=i===index?0:-1;panels[i].hidden=i!==index;});
}
function preview(id=fontChoice.value){
  fontChoice.value=id;
  const current=frame.getAttribute('src')?frame.contentWindow.location:null;
  const samePage=current?.pathname.endsWith('-'+pageChoice.value+'.html');
  const suffix=samePage?current.search+current.hash:'';
  frame.src=id+'-'+pageChoice.value+'.html'+suffix;
  frame.title=fontChoice.selectedOptions[0].text+'・'+pageChoice.selectedOptions[0].text;
  view(1);
}
document.querySelectorAll('[data-preview]').forEach(button=>button.addEventListener('click',()=>{
  preview(button.dataset.preview);tabs[1].focus();document.querySelector('#review-top').scrollIntoView({block:'start'});
}));
fontChoice.addEventListener('change',()=>preview());
pageChoice.addEventListener('change',()=>preview());
tabs.forEach((tab,index)=>{
  tab.addEventListener('click',()=>{if(index===1&&!frame.getAttribute('src'))preview();else view(index);});
  tab.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
    event.preventDefault();const next=event.key==='Home'?0:event.key==='End'?1:1-index;tabs[next].click();tabs[next].focus();
  });
});
const loading=document.querySelector('#font-loading');
Promise.all(['A','B','C','D','E'].flatMap(id=>[400,700].map(weight=>document.fonts.load(`${weight} 14px StudioFont${id}`,'技術発信 Miyabiya Studio')))).then(loaded=>{
  loading.textContent=loaded.every(list=>list.length>0)?'5書体の読み込み完了':'書体を読み込めませんでした。再読み込みしてください。';
}).catch(()=>{loading.textContent='書体を読み込めませんでした。再読み込みしてください。';});
