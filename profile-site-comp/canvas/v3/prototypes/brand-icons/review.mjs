const tabs=[...document.querySelectorAll('[role="tab"]')];
const compare=document.querySelector('#compare-view');
const context=document.querySelector('#context-view');
const choice=document.querySelector('#context-choice');
const frame=document.querySelector('#context-frame');
function showContext(on){
  compare.hidden=on;context.hidden=!on;
  tabs.forEach((tab,index)=>{const selected=index===(on?1:0);tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;});
  if(on&&!frame.getAttribute('src'))frame.src=`${choice.value}.html`;
}
tabs.forEach((tab,index)=>{
  tab.addEventListener('click',()=>showContext(index===1));
  tab.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const target=event.key==='Home'?0:event.key==='End'?1:1-index;showContext(target===1);tabs[target].focus();});
});
choice.addEventListener('change',()=>{frame.src=`${choice.value}.html`;});
document.querySelectorAll('[data-preview]').forEach(button=>button.addEventListener('click',()=>{choice.value=button.dataset.preview;frame.src=`${choice.value}.html`;showContext(true);tabs[1].focus();window.scrollTo({top:0,behavior:'instant'});}));
document.querySelector('#back-to-compare').addEventListener('click',()=>{showContext(false);tabs[0].focus();});
