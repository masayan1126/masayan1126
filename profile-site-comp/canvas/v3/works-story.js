const exhibition = document.querySelector('#works-story .works-exhibition');
if (exhibition) {
  const choices = exhibition.querySelector('.works-choices');
  const tabs = [...choices.querySelectorAll('button')];
  const panels = tabs.map(tab => document.getElementById(tab.getAttribute('aria-controls')));
  if (tabs.length && panels.every(Boolean)) {
    const select = index => {
      tabs.forEach((tab, i) => {
        tab.setAttribute('aria-selected', String(i === index));
        tab.tabIndex = i === index ? 0 : -1;
        panels[i].hidden = i !== index;
      });
    };
    choices.setAttribute('role', 'tablist');
    choices.setAttribute('aria-label', '実績を選ぶ');
    const mobile = matchMedia('(max-width: 820px)');
    const orientation = () => choices.setAttribute('aria-orientation', mobile.matches ? 'horizontal' : 'vertical');
    orientation();
    mobile.addEventListener('change', orientation);
    tabs.forEach((tab, i) => {
      tab.setAttribute('role', 'tab');
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].setAttribute('aria-labelledby', tab.id);
      panels[i].tabIndex = 0;
      tab.addEventListener('click', () => select(i));
      tab.addEventListener('keydown', event => {
        let next;
        if (['ArrowDown', 'ArrowRight'].includes(event.key)) next = (i + 1) % tabs.length;
        if (['ArrowUp', 'ArrowLeft'].includes(event.key)) next = (i + tabs.length - 1) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next !== undefined) {
          event.preventDefault();
          select(next);
          tabs[next].focus();
        }
      });
    });
    const selectFromHash = () => {
      const index = panels.findIndex(panel => '#' + panel.id === location.hash);
      if (index < 0) return false;
      select(index);
      requestAnimationFrame(() => panels[index].scrollIntoView({block: 'start'}));
      return true;
    };
    if (!selectFromHash()) select(0);
    window.addEventListener('hashchange', selectFromHash);
    choices.hidden = false;
    exhibition.classList.add('is-interactive');
  }
}
