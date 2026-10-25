// Motion only enhances visible content; the readable page is the fallback.
const page = document.querySelector('body.site-renewal');

if (page && typeof window.matchMedia === 'function') {
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const active = new Set();
  const entered = new WeakSet();
  const excluded = 'dialog, [role="dialog"], #pricing-wizard, .estimate-pdf-dialog, form';
  const entranceSelectors = [
    '.v3-page-head > .v3-wrap',
    '.business-gallery .business-heading',
    '.business-gallery .business-title',
    '.business-gallery .business-proof',
    '.works-story .head',
    '.works-story .case-summary',
    '.career-chapters .heading',
    '.tech-stack .wrap > h2',
    '.tech-stack .stack-grid > section',
    '.latest .latest-head',
    '.latest .latest-cards > a',
    '.sec .wrap > .sec-h',
    '.sec .wrap > .sec-lead',
    '.sec .wrap > .hero-lead',
    '.sec .wrap > .profile-intro',
    '.sec .wrap > .talks > .talk',
    '.v3-contact > .v3-wrap',
    '.page-actions',
    '.section-cta',
    '.estimate-intro > .v3-wrap',
  ].join(',');

  const canAnimate = element => !preference.matches
    && typeof element.animate === 'function'
    && element.isConnected
    && !element.closest(excluded)
    && !element.contains(document.activeElement)
    && element.getClientRects().length > 0;

  function enter(element, { delay = 0, distance = 12, duration = 380 } = {}) {
    if (!canAnimate(element)) return;
    // Avoid moving an entire article when its text spans several screens.
    const heightLimit = Math.max(480, Math.min(window.innerHeight * 0.9, 800));
    if (element.getBoundingClientRect().height > heightLimit) return;
    try {
      const animation = element.animate([
        { opacity: 0.65, transform: `translateY(${distance}px)` },
        { opacity: 1, transform: 'translateY(0)' },
      ], {
        duration,
        delay,
        easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
        fill: 'backwards',
      });
      active.add(animation);
      animation.addEventListener('finish', () => active.delete(animation), { once: true });
      animation.addEventListener('cancel', () => active.delete(animation), { once: true });
    } catch {
      // Missing or restricted animation APIs must never affect content or links.
    }
  }

  let observer;
  if (typeof IntersectionObserver === 'function') {
    observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      visible.forEach((entry, index) => {
        observer.unobserve(entry.target);
        if (entered.has(entry.target)) return;
        entered.add(entry.target);
        enter(entry.target, { delay: Math.min(index * 40, 120) });
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });

    page.querySelectorAll(entranceSelectors).forEach(element => {
      if (element.closest(excluded)) return;
      // Only the outermost matching unit receives a viewport entrance.
      if (element.parentElement?.closest(entranceSelectors)) return;
      observer.observe(element);
    });
  }

  const panelSelector = '.works-exhibition .case[id], .career-chapters .chapter-panel[role="tabpanel"]';
  const panels = [...page.querySelectorAll(panelSelector)];
  const hiddenState = new WeakMap(panels.map(panel => [panel, panel.hidden]));
  let panelObserver;
  if (panels.length && typeof MutationObserver === 'function') {
    panelObserver = new MutationObserver(records => {
      const changed = new Set(records.map(record => record.target));
      changed.forEach(panel => {
        if (!hiddenState.has(panel)) return;
        const wasHidden = hiddenState.get(panel);
        hiddenState.set(panel, panel.hidden);
        if (!wasHidden || panel.hidden) return;
        panel.querySelectorAll(entranceSelectors).forEach(element => {
          entered.add(element);
          observer?.unobserve(element);
        });
        // The interaction code owns visibility and focus; we only acknowledge
        // the result, leaving long panels and form/dialog controls untouched.
        const target = panel.getBoundingClientRect().height > Math.max(480, window.innerHeight * 0.9)
          ? panel.querySelector('.story-title, .career-title') : panel;
        if (target) enter(target, { distance: 8, duration: 260 });
      });
    });
    panels.forEach(panel => panelObserver.observe(panel, { attributes: true, attributeFilter: ['hidden'] }));
  }

  function cancelMotion() {
    active.forEach(animation => animation.cancel());
    active.clear();
  }
  function preferenceChanged() {
    if (preference.matches) cancelMotion();
  }
  if (typeof preference.addEventListener === 'function') {
    preference.addEventListener('change', preferenceChanged);
  } else if (typeof preference.addListener === 'function') {
    preference.addListener(preferenceChanged);
  }
  // Focusing a link or heading should reveal its final, stable position at once.
  page.addEventListener('focusin', cancelMotion);
  window.addEventListener('pagehide', () => {
    cancelMotion();
    observer?.disconnect();
    panelObserver?.disconnect();
  }, { once: true });
}
