// Passive reading progress for the homepage; no live announcements or motion.
const progress = document.querySelector('.site-reading-progress');
if (progress) {
  const header = document.querySelector('.editorial-header');
  const percent = progress.querySelector('.reading-progress-percent');
  let pending = false;
  let headerHeight = 0;
  const update = () => {
    pending = false;
    const root = document.documentElement;
    const maximum = Math.max(0, root.scrollHeight - root.clientHeight);
    const fraction = maximum ? Math.min(1, Math.max(0, window.scrollY / maximum)) : 1;
    progress.style.setProperty('--reading-progress-fraction', fraction);
    const text = Math.round(fraction * 100) + '%';
    if (percent.textContent !== text) percent.textContent = text;
    const height = Math.ceil(header.getBoundingClientRect().height);
    if (height !== headerHeight) {
      headerHeight = height;
      document.body.style.setProperty('--reading-header-height', height + 'px');
    }
  };
  const schedule = () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(update);
  };
  window.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('resize', schedule, {passive: true});
  window.addEventListener('load', schedule, {once: true});
  window.addEventListener('pageshow', schedule);
  document.fonts?.ready.then(schedule);
  if (typeof ResizeObserver === 'function') {
    const observer = new ResizeObserver(schedule);
    for (const element of [header, document.querySelector('main'), document.querySelector('.editorial-footer')]) {
      if (element) observer.observe(element);
    }
  }
  update();
}
