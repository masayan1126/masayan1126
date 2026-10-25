// トップのヒーロー: Blender で描いた書斎ジオラマ (背景透過、48 秒で昼 → 夕暮れ → 夜 → 朝が巡るループ)。
// 白いヒーローの右側 (スマホでは見出しとボタンの間) に置き、映像の中のモニターの位置にチャンネルへのリンクを重ねる。
const host = document.querySelector('.immersive-hero');
const video = host.querySelector('#scene'), wrap = host.querySelector('.world'), link = host.querySelector('.monitor-link');
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const set = JSON.parse(video.dataset.sets);   // { webm, hevc, poster, w, h }
let track = null, raf = 0, visible = true, userPaused = false;
const motionToggle = host.querySelector('.hero-motion-toggle');
function updatePlayback() {
  const playing = visible && !reduce.matches && !userPaused && !document.hidden;
  if (playing) video.play().catch(() => {}); else video.pause();
  motionToggle.hidden = reduce.matches;
  motionToggle.setAttribute('aria-pressed', String(userPaused));
  motionToggle.textContent = userPaused ? '背景の動きを再生する' : '背景の動きを止める';
}
motionToggle.addEventListener('click', () => { userPaused = !userPaused; updatePlayback(); });
document.addEventListener('visibilitychange', updatePlayback);

// Transparent video: Safari only keeps the alpha channel in HEVC; Chrome, Edge and Firefox in VP9 WebM.
const safari = /^((?!chrome|chromium|android|crios|fxios|edg).)*safari/i.test(navigator.userAgent);
const source = document.createElement('source');
Object.assign(source, safari ? { src: set.hevc, type: 'video/mp4; codecs="hvc1"' } : { src: set.webm, type: 'video/webm' });
video.poster = set.poster;
video.append(source);
wrap.style.setProperty('--diorama-ratio', `${set.w} / ${set.h}`);

// The video fills .world exactly, so the monitor boxes (0–1 of the frame) map straight to percentages.
function placeLink() {
  raf = 0;
  if (!track) return;
  const boxes = track.boxes;
  const i = Math.floor((video.currentTime % track.duration) / track.duration * boxes.length) % boxes.length;
  const [x0, y0, x1, y1] = boxes[i];
  Object.assign(link.style, { left: `${x0 * 100}%`, top: `${y0 * 100}%`, width: `${(x1 - x0) * 100}%`, height: `${(y1 - y0) * 100}%` });
  link.hidden = false;
  if (!video.paused) raf = requestAnimationFrame(placeLink);
}
const schedule = () => { if (!raf) raf = requestAnimationFrame(placeLink); };

video.addEventListener('playing', () => { host.classList.add('ready'); schedule(); });
video.addEventListener('loadeddata', () => { host.classList.add('ready'); schedule(); });
video.addEventListener('seeked', schedule);
fetch(video.dataset.track).then(r => r.json()).then(j => { track = j; schedule(); }).catch(() => {});
new IntersectionObserver(entries => {
  visible = entries[0].isIntersecting;
  updatePlayback();
}, { threshold: 0 }).observe(host);
reduce.addEventListener('change', updatePlayback);
video.load();
updatePlayback();
