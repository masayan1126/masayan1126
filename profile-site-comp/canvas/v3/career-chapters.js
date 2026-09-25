// Keep all records readable until the controls are ready.
document.querySelectorAll('.career-chapters').forEach(root => {
  const nav = root.querySelector('.chapter-nav');
  const tabs = [...nav.querySelectorAll('[role="tab"]')];
  const panels = tabs.map(tab => root.querySelector('#' + tab.getAttribute('aria-controls')));
  const progress = root.querySelector('.chapter-progress');
  const counter = root.querySelector('#chapter-progress-text');
  const next = root.querySelector('#chapter-next');
  if (!tabs.length || panels.some(panel => !panel) || !progress || !counter || !next) return;
  let current = 0;
  const mobile = matchMedia('(max-width: 820px)');
  const orientation = () => nav.setAttribute('aria-orientation', mobile.matches ? 'horizontal' : 'vertical');
  orientation();
  mobile.addEventListener('change', orientation);
  function choose(index) {
    current = index;
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      panels[i].hidden = i !== index;
    });
    counter.textContent = `${String(index + 1).padStart(2, '0')} / ${String(tabs.length).padStart(2, '0')}`;
    next.textContent = index === tabs.length - 1 ? '現在の経歴に戻る ↶' : '次の経歴を見る →';
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => choose(i));
    tab.addEventListener('keydown', event => {
      let index;
      if (['ArrowRight', 'ArrowDown'].includes(event.key)) index = (i + 1) % tabs.length;
      if (['ArrowLeft', 'ArrowUp'].includes(event.key)) index = (i + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') index = 0;
      if (event.key === 'End') index = tabs.length - 1;
      if (index !== undefined) {
        event.preventDefault();
        choose(index);
        tabs[index].focus();
      }
    });
  });
  next.addEventListener('click', () => choose((current + 1) % tabs.length));
  choose(0);
  nav.hidden = false;
  progress.hidden = false;
  root.setAttribute('data-enhanced', '');
});
