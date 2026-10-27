const pattern=document.body.dataset.scrollPattern;
const sections=[...document.querySelectorAll('.a-work > .a-entry[id]')];
const dock=document.querySelector('.scroll-cue-dock');
const link=dock?.querySelector('a');
const reading=document.querySelector('.scroll-reading');
const header=document.querySelector('.editorial-header');
let pending=false;
function update(){
  pending=false;
  const root=document.documentElement;
  const max=Math.max(0,root.scrollHeight-innerHeight);
  const fraction=max?Math.min(1,Math.max(0,scrollY/max)):1;
  if(reading){
    reading.style.setProperty('--scroll-progress',fraction);
    reading.querySelector('.scroll-reading-percent').textContent=Math.round(fraction*100)+'%';
    document.body.style.setProperty('--scroll-header-height',header.getBoundingClientRect().height+'px');
  }
  if(dock){
    const footer=document.querySelector('.editorial-footer').getBoundingClientRect().height;
    const floor=innerHeight-footer-(pattern==='a'&&innerWidth<=620?12:64);
    const last=sections.at(-1);
    const next=sections.find(section=>section.getBoundingClientRect().top>floor)||(last?.getBoundingClientRect().bottom>floor?last:null);
    const readingMain=!!document.activeElement.closest('main');
    dock.hidden=!(max>0&&scrollY<64&&next&&!readingMain)&&!dock.contains(document.activeElement);
    if(next)link.href='#'+next.id;
    root.classList.toggle('scroll-cue-reserved',!dock.hidden);
  }
}
const schedule=()=>{if(!pending){pending=true;requestAnimationFrame(update);}};
window.addEventListener('scroll',schedule,{passive:true});
window.addEventListener('resize',schedule);
window.addEventListener('load',schedule,{once:true});
document.fonts.ready.then(schedule);
if(dock){dock.addEventListener('focusout',()=>queueMicrotask(schedule));document.addEventListener('focusin',schedule);document.addEventListener('focusout',()=>queueMicrotask(schedule));}
document.querySelectorAll('.scroll-cue-link,.scroll-contents a').forEach(anchor=>anchor.addEventListener('click',event=>{
  const target=document.getElementById(anchor.hash.slice(1));
  if(!target)return;
  event.preventDefault();
  history.pushState(null,'',anchor.getAttribute('href'));
  target.scrollIntoView({block:'start',behavior:'instant'});
  const heading=target.querySelector('h2,h3');
  if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
  update();
}));
if(pattern==='c'&&typeof ResizeObserver==='function'){new ResizeObserver(schedule).observe(header);}
update();
