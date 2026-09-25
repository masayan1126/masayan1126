const menus=[...document.querySelectorAll('.site-menu')];
for(const menu of menus){
 menu.addEventListener('toggle',()=>{if(menu.open)for(const other of menus)if(other!==menu)other.open=false});
 menu.addEventListener('click',e=>{if(e.target.closest('a'))menu.open=false});
}
document.addEventListener('click',e=>{for(const menu of menus)if(menu.open&&!menu.contains(e.target))menu.open=false});
document.addEventListener('keydown',e=>{if(e.key!=='Escape')return;for(const menu of menus)if(menu.open){menu.open=false;menu.querySelector('summary').focus();e.preventDefault()}});
const hero=document.querySelector('.immersive-hero'),header=document.querySelector('.v3>.v3-head');
if(hero&&header){
 const setHeader=show=>{document.body.classList.toggle('past-hero',show);header.inert=!show;header.setAttribute('aria-hidden',String(!show));if(!show)for(const menu of header.querySelectorAll('.site-menu'))menu.open=false};
 setHeader(false);
 new IntersectionObserver(entries=>{const e=entries[0];setHeader(!e.isIntersecting&&e.boundingClientRect.bottom<100)},{rootMargin:'-80px 0px 0px 0px',threshold:0}).observe(hero);
}
