// This module is loaded only by the private design study.
document.addEventListener('submit', event => {
  const form = event.target.closest('form[data-editorial-preview]');
  if (!form) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  let status = form.querySelector('[data-preview-status]');
  if (!status) {
    status = document.createElement('p');
    status.dataset.previewStatus = '';
    status.setAttribute('role', 'status');
    form.append(status);
  }
  status.textContent = '入力内容を確認しました。試作画面のため、送信は行っていません。';
}, true);

const preference = matchMedia('(prefers-reduced-motion: reduce)');
const active = new Set();
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    observer.unobserve(entry.target);
    if (preference.matches || entry.target.contains(document.activeElement)) continue;
    const animation = entry.target.animate([{opacity:.7,transform:'translateY(8px)'},{opacity:1,transform:'none'}],{duration:320,easing:'cubic-bezier(.2,.7,.2,1)'});
    active.add(animation);
    animation.addEventListener('finish',()=>active.delete(animation),{once:true});
  }
}, {threshold:.08});
document.querySelectorAll('.editorial-project, .editorial-about').forEach(element=>observer.observe(element));
const cancel=()=>{active.forEach(animation=>animation.cancel());active.clear();};
document.addEventListener('focusin', cancel);
preference.addEventListener('change',()=>{if(preference.matches)cancel();});
window.addEventListener('pagehide',()=>{cancel();observer.disconnect();},{once:true});
