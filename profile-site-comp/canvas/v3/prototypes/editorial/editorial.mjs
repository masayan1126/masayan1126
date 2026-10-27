// This module is loaded only by the private design study.
import {saveHandoff, CONTACT_PATH, HANDOFF_KEY} from './editorial-quote-contact.mjs';

document.addEventListener('click', event => {
  const entry = event.target.closest('.editorial-contact-link');
  if (!entry || location.pathname !== '/pricing/') return;
  entry.href = '/contact/#contact-form';
  const legacy = document.querySelector('#legacy-estimate');
  const field = legacy && !legacy.hidden
    ? legacy.querySelector('[data-quote-text]')
    : document.querySelector('#wizard-dialog [data-quote-text]');
  if (!field?.value.trim()) return;
  try {
    saveHandoff(sessionStorage, location.origin, field.value);
    entry.href = CONTACT_PATH;
  } catch {
    try { sessionStorage.removeItem(HANDOFF_KEY); } catch {}
    entry.href = '/contact/?type=pr&quote=unavailable#contact-form';
  }
});

if (location.pathname === '/contact/' && new URL(location.href).searchParams.get('quote') === 'unavailable') {
  const status = document.querySelector('#quote-handoff-status');
  if (status) status.textContent = '見積もり内容を引き継げませんでした。見積もりの共有URLをご相談内容に貼り付けてください。';
}

const filters = [...document.querySelectorAll('[data-filter]')];
filters.forEach(button => button.addEventListener('click', () => {
  const category = button.dataset.filter;
  filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
  let count = 0;
  document.querySelectorAll('.a-entry').forEach(entry => {
    entry.hidden = category !== 'all' && entry.dataset.category !== category;
    if (!entry.hidden) count++;
  });
  document.querySelector('#filter-result').textContent = `${count}件を表示しています`;
}));

// Existing fragment links still reveal secondary information inside details.
const revealFragment = () => {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = id && document.getElementById(id);
  if (!target) return;
  for (let item = target; item; item = item.parentElement) {
    if (item.tagName === 'DETAILS') item.open = true;
  }
};
revealFragment();
window.addEventListener('hashchange', revealFragment);

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
document.querySelectorAll('.a-person, .a-entry, .focus-person').forEach(element=>observer.observe(element));
const cancel=()=>{active.forEach(animation=>animation.cancel());active.clear();};
document.addEventListener('focusin', cancel);
preference.addEventListener('change',()=>{if(preference.matches)cancel();});
window.addEventListener('pagehide',()=>{cancel();observer.disconnect();},{once:true});
