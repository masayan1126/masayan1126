const tabs=[...document.querySelectorAll('[role="tab"]')];
const compare=document.querySelector('#compare-view'),context=document.querySelector('#context-view');
const choice=document.querySelector('#context-choice'),frame=document.querySelector('#context-frame');
function show(on){compare.hidden=on;context.hidden=!on;document.body.classList.toggle('is-context',on);tabs.forEach((tab,index)=>{const selected=index===(on?1:0);tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;});if(on&&!frame.getAttribute('src'))frame.src=choice.value+'.html';if(on)choice.focus();}
function preview(id){choice.value=id;frame.src=id+'.html';frame.title=choice.selectedOptions[0].text+'をトップで確認';show(true);choice.focus();window.scrollTo({top:0,behavior:'instant'});}
document.querySelectorAll('[data-preview]').forEach(button=>button.addEventListener('click',()=>preview(button.dataset.preview)));
choice.addEventListener('change',()=>preview(choice.value));
tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>show(index===1));tab.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const next=event.key==='Home'?0:event.key==='End'?1:1-index;show(next===1);if(next===0)tabs[0].focus();});});
document.querySelector('#back-to-compare').addEventListener('click',()=>{show(false);tabs[0].focus();});
