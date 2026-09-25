// トップのヒーロー: 1/12 の書斎ジオラマ。部屋の中が見える範囲で左右に振れ、昼 → 夕暮れ → 夜 → 朝が自動で巡る。
import * as THREE from 'three';

const host = document.querySelector('.immersive-hero');
const canvas = host.querySelector('#scene'), wrap = host.querySelector('.world');
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const CHANNEL_URL = 'https://www.youtube.com/@masayan-ai-hack';
const V3 = THREE.Vector3, PI = Math.PI;
const C = (s) => new THREE.Color(s);
const hsl = (h, s, l) => new THREE.Color().setStyle(`hsl(${h}, ${s}%, ${l}%)`);
const FONT_MINCHO = '"Hiragino Mincho ProN", "Yu Mincho", "YuMincho", serif';
const FONT_GOTHIC = '"Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif';
const FONT_HAND = '"Klee", "Klee One", "Hiragino Maru Gothic ProN", "Yu Gothic", sans-serif';

// ---------- random & noise ----------
let seed = 1212;
function rnd() { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }
const rr = (a, b) => a + (b - a) * rnd();
const pick = (arr) => arr[Math.floor(rnd() * arr.length)];
function hash2(x, y) { let h = (Math.imul(x, 374761393) + Math.imul(y, 668265263)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
function hash3(x, y, z) { let h = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 2147483647)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
const fade = (t) => t * t * (3 - 2 * t);
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smoothstep = (a, b, x) => fade(clamp01((x - a) / (b - a)));
function vnoise(x, y, P) {
  const xi = Math.floor(x), yi = Math.floor(y), u = fade(x - xi), v = fade(y - yi);
  const w = (a) => P ? ((a % P) + P) % P : a;
  const a = hash2(w(xi), w(yi)), b = hash2(w(xi + 1), w(yi)), c = hash2(w(xi), w(yi + 1)), d = hash2(w(xi + 1), w(yi + 1));
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function fbm(x, y, oct = 4, P = 0) { let s = 0, a = 0.5, f = 1; for (let i = 0; i < oct; i++) { s += a * vnoise(x * f, y * f, P ? P * f : 0); f *= 2; a *= 0.5; } return s / (1 - Math.pow(0.5, oct)); }
function vnoise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z), u = fade(x - xi), v = fade(y - yi), w = fade(z - zi);
  const L = (a, b, t) => a + (b - a) * t, c = (i, j, k) => hash3(xi + i, yi + j, zi + k);
  return L(L(L(c(0,0,0), c(1,0,0), u), L(c(0,1,0), c(1,1,0), u), v), L(L(c(0,0,1), c(1,0,1), u), L(c(0,1,1), c(1,1,1), u), v), w);
}

// ---------- textures ----------
function makeCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
let ANISO = 1;
function tex(c, { srgb = true, repeat = true } = {}) {
  const t = new THREE.CanvasTexture(c);
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = ANISO; return t;
}
function pixels(w, h, fn) {
  const c = makeCanvas(w, h), g = c.getContext('2d'), im = g.createImageData(w, h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const o = (y * w + x) * 4, v = fn(x, y); im.data[o] = v[0]; im.data[o + 1] = v[1]; im.data[o + 2] = v[2]; im.data[o + 3] = 255; }
  g.putImageData(im, 0, 0); return c;
}
const srgb255 = (c) => { c.convertLinearToSRGB(); return [c.r * 255, c.g * 255, c.b * 255]; };
function woodCan(h, s, l) {
  return pixels(256, 256, (x, y) => { const n = fbm(x / 64, y / 6, 4, 4), ring = 0.5 + 0.5 * Math.sin((y / 3.5 + n * 9)); const k = 0.74 + 0.18 * ring + 0.16 * (fbm(x / 10, y / 1.5, 3, 25) - 0.5); return srgb255(hsl(h, s, l * k)); });
}
function planks() {
  const size = 1024, c = makeCanvas(size, size), g = c.getContext('2d'), pw = 64;
  for (let x = 0; x < size; x += pw) {
    let y = -rr(0, 400);
    while (y < size) { const L = rr(260, 520); g.fillStyle = `hsl(${rr(26, 32)},${rr(22, 30)}%,${rr(46, 58)}%)`; g.fillRect(x, y, pw, L); g.fillStyle = 'rgba(30,20,12,0.5)'; g.fillRect(x, y, pw, 2); y += L; }
    g.fillStyle = 'rgba(30,20,12,0.55)'; g.fillRect(x, 0, 2, size);
  }
  // grain: a stretched noise tile drawn with multiply keeps this cheap
  const n = pixels(128, 128, (x, y) => { const v = 205 + 50 * fbm(x / 3, y / 40, 3, 0); return [v, v, v]; });
  g.globalCompositeOperation = 'multiply';
  for (let x = 0; x < size; x += 128) for (let y = 0; y < size; y += 512) g.drawImage(n, x, y, 128, 512);
  g.globalCompositeOperation = 'source-over';
  return c;
}
function textPlate(text, w, h, bg, fg, font) {
  const c = makeCanvas(w, h), g = c.getContext('2d');
  g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.fillStyle = fg; g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, w / 2, h / 2 + 2);
  return tex(c, { repeat: false });
}
function screenTex(kind) {
  const c = makeCanvas(1024, 576), g = c.getContext('2d');
  if (kind === 'editor') {
    g.fillStyle = '#1d2125'; g.fillRect(0, 0, 1024, 576);
    g.fillStyle = '#262b30'; g.fillRect(0, 0, 1024, 34); g.fillRect(0, 34, 200, 380);
    for (let i = 0; i < 9; i++) { g.fillStyle = i === 2 ? '#3d5a78' : '#30363c'; g.fillRect(14, 50 + i * 38, 172, 28); }
    const gr = g.createLinearGradient(232, 50, 792, 365); gr.addColorStop(0, '#34597a'); gr.addColorStop(1, '#16222e');
    g.fillStyle = gr; g.fillRect(232, 50, 560, 315);
    g.fillStyle = '#f5f7f8'; g.font = `700 86px ${FONT_GOTHIC}`; g.fillText('AI活用', 262, 200);
    g.font = `500 30px ${FONT_GOTHIC}`; g.fillStyle = '#cfe0ee'; g.fillText('まさやん【AIギルドch】', 266, 250);
    g.fillStyle = '#e5eef4'; g.fillRect(262, 290, 220, 44); g.fillStyle = '#16222e'; g.font = `700 26px ${FONT_GOTHIC}`; g.fillText('新しい動画', 294, 321);
    g.fillStyle = '#262b30'; g.fillRect(812, 50, 196, 315);
    for (let i = 0; i < 6; i++) { g.fillStyle = '#353b42'; g.fillRect(826, 66 + i * 48, 168, 12); g.fillRect(826, 84 + i * 48, 110, 8); }
    g.fillStyle = '#23282d'; g.fillRect(0, 420, 1024, 156);
    [['#4c7396', 20], ['#5d8a6a', 60], ['#b0835a', 100]].forEach(([cl, y], i) => { let x = 30; while (x < 1000) { const w = 60 + ((x * 7 + i * 13) % 150); g.fillStyle = cl; g.fillRect(x, 430 + y, w, 30); x += w + 10; } });
    g.fillStyle = '#e8574a'; g.fillRect(470, 424, 3, 150);
  } else {
    g.fillStyle = '#f7f8f9'; g.fillRect(0, 0, 1024, 576);
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, 1024, 48); g.fillStyle = '#e4e7ea'; g.fillRect(0, 48, 1024, 2);
    g.fillStyle = '#2f4a66'; g.beginPath(); g.arc(80, 118, 44, 0, 6.283); g.fill();
    g.fillStyle = '#f2f5f7'; g.font = `700 38px ${FONT_GOTHIC}`; g.textAlign = 'center'; g.fillText('AI', 80, 131); g.textAlign = 'left';
    g.fillStyle = '#1f2a33'; g.font = `700 34px ${FONT_GOTHIC}`; g.fillText('まさやん【AIギルドch】', 144, 110);
    g.fillStyle = '#56636d'; g.font = `500 24px ${FONT_GOTHIC}`; g.fillText('チャンネル登録者 3,462人', 144, 146);
    g.fillStyle = '#1f2a33'; g.fillRect(820, 92, 160, 50); g.fillStyle = '#f7f8f9'; g.font = `700 24px ${FONT_GOTHIC}`; g.fillText('登録済み', 852, 125);
    const titles = ['Claude Code', 'MCPサーバー', 'AI導入の相談', '自動化の設計', 'API開発', '仕事の効率化', 'デモの準備', 'ライブ配信'];
    const cols = ['#34597a', '#3f6b5a', '#6a4a3a', '#44506a', '#2f4a66', '#5a6a3a', '#6a3a4a', '#3a5a6a'];
    titles.forEach((tt, i) => {
      const x = 40 + (i % 4) * 244, y = 196 + Math.floor(i / 4) * 188;
      g.fillStyle = cols[i]; g.fillRect(x, y, 224, 126);
      g.fillStyle = '#f5f7f8'; g.font = `700 26px ${FONT_GOTHIC}`; g.fillText(tt, x + 14, y + 72);
      g.fillStyle = '#1f2a33'; g.fillRect(x, y + 136, 190, 12); g.fillStyle = '#9aa7b1'; g.fillRect(x, y + 156, 120, 10);
    });
  }
  return tex(c, { repeat: false });
}
function outsideTex(mode) {
  const dusk = mode !== 'day', night = mode === 'night';
  const c = makeCanvas(512, 384), g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 384);
  if (night) { gr.addColorStop(0, '#070b16'); gr.addColorStop(0.7, '#1a2340'); gr.addColorStop(1, '#2a3050'); }
  else if (dusk) { gr.addColorStop(0, '#2c3a60'); gr.addColorStop(0.55, '#c9786a'); gr.addColorStop(1, '#f0a878'); }
  else { gr.addColorStop(0, '#8fb2cc'); gr.addColorStop(0.7, '#dce7ee'); gr.addColorStop(1, '#eef2f3'); }
  g.fillStyle = gr; g.fillRect(0, 0, 512, 384);
  seed = 77;
  for (let layer = 0; layer < 2; layer++) {
    let x = -10;
    while (x < 520) {
      const w = rr(30, 70), hh = layer ? rr(80, 190) : rr(140, 260);
      g.fillStyle = night ? (layer ? '#0d0f18' : '#161a26') : dusk ? (layer ? '#2a2b3a' : '#3b3a4c') : (layer ? '#7d8e9a' : '#a4b3bd');
      g.fillRect(x, 384 - hh, w, hh);
      for (let yy = 384 - hh + 10; yy < 380; yy += 14) for (let xx = x + 6; xx < x + w - 6; xx += 12) if (rnd() < (night ? 0.55 : dusk ? 0.45 : 0.25)) { g.fillStyle = dusk ? 'rgba(255,196,120,0.9)' : 'rgba(230,238,244,0.6)'; g.fillRect(xx, yy, 5, 6); }
      x += w + rr(2, 10);
    }
  }
  return tex(c, { repeat: false });
}
function paperTex(lines) {
  const c = makeCanvas(384, 288), g = c.getContext('2d');
  g.fillStyle = '#fbfbf8'; g.fillRect(0, 0, c.width, c.height);
  g.strokeStyle = 'rgba(80,110,140,0.18)'; g.lineWidth = 2;
  for (let y = 60; y < c.height; y += 44) { g.beginPath(); g.moveTo(16, y); g.lineTo(c.width - 16, y); g.stroke(); }
  g.fillStyle = '#23303a'; g.textAlign = 'center'; g.textBaseline = 'middle';
  lines.forEach(([t, size, y]) => { g.font = `600 ${size}px ${FONT_HAND}`; g.fillText(t, c.width / 2, y); });
  return tex(c, { repeat: false });
}
function calendarTex() {
  const c = makeCanvas(384, 480), g = c.getContext('2d');
  g.fillStyle = '#fdfdfc'; g.fillRect(0, 0, 384, 480);
  g.fillStyle = '#2f4a66'; g.fillRect(0, 0, 384, 70);
  g.fillStyle = '#f2f5f7'; g.font = `700 40px ${FONT_MINCHO}`; g.textAlign = 'center'; g.fillText('9月', 192, 48);
  g.fillStyle = '#56636d'; g.font = `500 20px ${FONT_GOTHIC}`;
  let d = 1;
  for (let r = 0; r < 5; r++) for (let k = 0; k < 7; k++) { const idx = r * 7 + k; if (idx < 1 || d > 30) continue; g.fillText(String(d++), 30 + k * 54, 112 + r * 52); }
  g.save(); g.translate(210, 330); g.rotate(-0.06);
  g.fillStyle = '#cfe3f0'; g.fillRect(-96, -58, 192, 116);
  g.fillStyle = '#1f2a33'; g.font = `600 30px ${FONT_HAND}`; g.fillText('デモ準備', 0, -16); g.fillText('4時間 → 20分', 0, 28);
  g.restore();
  return tex(c, { repeat: false });
}

// ---------- scene helpers ----------
let world;
const std = (o) => new THREE.MeshStandardMaterial(o);
const matCache = new Map();
const cached = (key, make) => { if (!matCache.has(key)) matCache.set(key, make()); return matCache.get(key); };
const pmat = (color, o = {}) => cached('p' + color + JSON.stringify(o), () => std(Object.assign({ color: C(color), roughness: 0.7 }, o)));
const G = {
  box: new THREE.BoxGeometry(1, 1, 1),
  cyl: new THREE.CylinderGeometry(0.5, 0.5, 1, 14),
  sphere: new THREE.SphereGeometry(0.5, 14, 10),
  cone: new THREE.ConeGeometry(0.5, 1, 16, 1, true),
};
function boxUV(w, h, d) {
  const g = new THREE.BoxGeometry(w, h, d), uv = g.attributes.uv;
  const dims = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]];
  for (let f = 0; f < 6; f++) for (let i = 0; i < 4; i++) { const k = f * 4 + i; uv.setXY(k, uv.getX(k) * dims[f][0], uv.getY(k) * dims[f][1]); }
  return g;
}
function mesh(geo, mat, par, x = 0, y = 0, z = 0) { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; (par || world).add(m); return m; }
function box(mat, x, y, z, w, h, d, par, ry = 0) { const m = mesh(G.box, mat, par, x, y, z); m.scale.set(w, h, d); m.rotation.y = ry; return m; }
function cyl(mat, x, y, z, r, h, par) { const m = mesh(G.cyl, mat, par, x, y, z); m.scale.set(r * 2, h, r * 2); return m; }
function sph(mat, x, y, z, r, par) { const m = mesh(G.sphere, mat, par, x, y, z); m.scale.set(r * 2, r * 2, r * 2); return m; }
function cone(mat, x, y, z, r, h, par) { const m = mesh(G.cone, mat, par, x, y, z); m.scale.set(r * 2, h, r * 2); return m; }
function group(x, y, z, ry = 0, par) { const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; (par || world).add(g); return g; }
const _up = new V3(0, 1, 0);
function segment(a, b, r, mat, par) {
  const dir = new V3().subVectors(b, a), len = dir.length();
  const m = mesh(G.cyl, mat, par); m.scale.set(r * 2, len, r * 2);
  m.position.copy(a).addScaledVector(dir, 0.5); m.quaternion.setFromUnitVectors(_up, dir.normalize()); return m;
}
function blobGeo(seedOff) {
  const geo = new THREE.SphereGeometry(1, 30, 20), pos = geo.attributes.position, cols = new Float32Array(pos.count * 3), v = new V3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    const n1 = vnoise3(v.x * 1.8 + seedOff, v.y * 1.8, v.z * 1.8), n2 = vnoise3(v.x * 5 + seedOff, v.y * 5, v.z * 5), n3 = vnoise3(v.x * 13, v.y * 13 + seedOff, v.z * 13);
    const r = 0.8 + 0.3 * n1 + 0.14 * n2 + 0.1 * n3;
    v.multiplyScalar(r); pos.setXYZ(i, v.x, v.y, v.z);
    const ao = 0.4 + 0.6 * smoothstep(-1.1, 0.8, v.y), k = ao * (0.72 + 0.45 * (r - 0.8) + 0.15 * n3);
    cols[i * 3] = k * 0.96; cols[i * 3 + 1] = k; cols[i * 3 + 2] = k * 0.9;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(cols, 3)); geo.computeVertexNormals(); return geo;
}
let blobs;
function blob(color, x, y, z, sx, sy, sz, par) { const m = mesh(pick(blobs), cached('fo' + color, () => std({ vertexColors: true, color: C(color), roughness: 0.9 })), par, x, y, z); m.scale.set(sx, sy, sz); m.rotation.y = rr(0, 6.28); return m; }

// glow registry: emissive surfaces that brighten after dark
const glows = [];
function glow(m, d, n) { const e = { m, d, n }; glows.push(e); return e; }
const lights = [];
function nightLight(x, y, z, color, max, dist) { const l = new THREE.PointLight(C(color), 0, dist, 2); l.position.set(x, y, z); world.add(l); lights.push({ l, max }); }

// ---------- the study ----------
const W = 16, D = 12, BASE_Y = -0.35;
let outM, outViews, monitorGroup;
function buildStudy() {
  const timberTex = tex(woodCan(24, 28, 34)), hinokiTex = tex(woodCan(34, 42, 66)); hinokiTex.repeat.set(0.25, 1);
  const plasterTex = tex(pixels(256, 256, (x, y) => { const n = fbm(x / 32, y / 32, 5, 8), s = fbm(x / 64 + 3, y / 14, 3, 4); const v = 226 + (n - 0.5) * 26 - Math.max(0, s - 0.6) * 80; return [v, v * 0.99, v * 0.975]; }));
  plasterTex.repeat.set(0.8, 0.8);
  const plankTex = tex(planks()); plankTex.repeat.set(1.2, 1.2);
  const M = {
    timber: std({ color: C('#4a3a2e'), map: timberTex, roughness: 0.85 }),
    hinoki: std({ map: hinokiTex, roughness: 0.6 }),
    plinth: std({ color: C('#1d2226'), roughness: 0.35, metalness: 0.1 }),
    iron: std({ color: C('#25272b'), roughness: 0.45, metalness: 0.7 }),
    rubber: std({ color: C('#1a1a1a'), roughness: 0.9 }),
    dark: std({ color: C('#23201e'), roughness: 0.8 }),
    lamp: std({ color: C('#f4ecd8'), roughness: 0.3, emissive: C('#ffcf8a'), emissiveIntensity: 0.1, side: THREE.DoubleSide }),
  };
  glow(M.lamp, 0.1, 5.0);
  const plaster = (color) => cached('pl' + color, () => std({ map: plasterTex, color: C(color), roughness: 0.93 }));

  // floor and display base
  box(M.plinth, 0, -0.175, 0, W, 0.35, D);
  const fl = new THREE.PlaneGeometry(W, D); fl.rotateX(-PI / 2);
  mesh(fl, std({ map: plankTex, roughness: 0.55 }), null, 0, 0.002, 0);
  mesh(boxUV(W, 0.1, D), M.plinth, null, 0, BASE_Y - 0.05, 0);
  mesh(boxUV(W + 0.5, 0.22, D + 0.5), M.hinoki, null, 0, BASE_Y - 0.11, 0);
  mesh(boxUV(W + 1.3, 1.2, D + 1.3), M.plinth, null, 0, BASE_Y - 0.82, 0);
  mesh(boxUV(W - 2, 40, D - 2), M.plinth, null, 0, BASE_Y - 21.4, 0);
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(4.8, 0.62), std({ map: textPlate('Miyabiya Studio ・ 縮尺 1/12', 1122, 145, '#b8904a', '#2a2014', `600 60px ${FONT_MINCHO}`), roughness: 0.35, metalness: 0.9 }));
  plate.position.set(0, BASE_Y - 0.82, D / 2 + 0.66); world.add(plate);

  // walls: back wall with a window, left wall
  const wallM = plaster('#ece8e1'), cap = pmat('#cbbfa8', { roughness: 0.9 }), trim = pmat('#e6e1d8', { roughness: 0.6 });
  const WH = 7.6, bz = -D / 2 + 0.15, lx = -W / 2 + 0.15;
  const wall = (x, y, z, w, h, d) => mesh(boxUV(w, h, d), wallM, null, x, y, z);
  wall(-3.8, WH / 2, bz, 8.4, WH, 0.3); wall(6.3, WH / 2, bz, 3.4, WH, 0.3);
  wall(2.5, 1.45, bz, 4.2, 2.9, 0.3); wall(2.5, 6.9, bz, 4.2, 1.4, 0.3);
  wall(lx, WH / 2, 0.15, 0.3, WH, D - 0.3);
  box(cap, 0, WH + 0.01, bz, W, 0.02, 0.3); box(cap, lx, WH + 0.01, 0.15, 0.3, 0.02, D - 0.3);
  box(trim, 0, 0.15, bz + 0.17, W - 0.3, 0.3, 0.04); box(trim, lx + 0.17, 0.15, 0.15, 0.04, 0.3, D - 0.3);
  const fr = pmat('#e8e4dc', { roughness: 0.5 });
  box(fr, 2.5, 2.9, bz + 0.1, 4.4, 0.1, 0.5); box(fr, 2.5, 6.2, bz, 4.4, 0.1, 0.34);
  box(fr, 0.4, 4.55, bz, 0.1, 3.4, 0.34); box(fr, 4.6, 4.55, bz, 0.1, 3.4, 0.34); box(fr, 2.5, 4.55, bz, 0.08, 3.3, 0.2);
  outViews = { day: outsideTex('day'), dusk: outsideTex('dusk'), night: outsideTex('night') };
  outM = new THREE.MeshBasicMaterial({ map: outViews.day });
  const op = new THREE.Mesh(new THREE.PlaneGeometry(4.3, 3.4), outM); op.position.set(2.5, 4.55, bz - 0.6); world.add(op);
  for (const [x, y, w, h] of [[2.5, 6.3, 4.6, 0.1], [2.5, 2.8, 4.6, 0.1], [0.25, 4.55, 0.1, 3.6], [4.75, 4.55, 0.1, 3.6]]) box(wallM, x, y, bz - 0.35, w, h, 0.5);

  // rug
  const rc = makeCanvas(512, 340), rg = rc.getContext('2d');
  rg.fillStyle = '#5f7182'; rg.fillRect(0, 0, 512, 340); rg.strokeStyle = '#d8dde2'; rg.lineWidth = 6; rg.strokeRect(24, 24, 464, 292); rg.strokeStyle = '#46576a'; rg.lineWidth = 3; rg.strokeRect(40, 40, 432, 260);
  const rgGeo = new THREE.PlaneGeometry(6.4, 4.2); rgGeo.rotateX(-PI / 2); mesh(rgGeo, std({ map: tex(rc, { repeat: false }), roughness: 0.95 }), null, 2.0, 0.012, -1.8);

  // desk
  const deskM = pmat('#8a6a4e', { roughness: 0.55 }), deskTop = std({ map: timberTex, color: C('#c9a882'), roughness: 0.5 });
  box(deskTop, 2.5, 2.4, -4.55, 5.6, 0.12, 2.1);
  for (const x of [-0.25, 5.25]) box(deskM, x, 1.17, -4.55, 0.1, 2.34, 1.9);
  box(deskM, 4.4, 1.4, -4.55, 1.5, 1.6, 1.8); for (const y of [1.9, 1.2]) box(M.iron, 4.4, y, -3.64, 0.4, 0.04, 0.04);

  // monitors (click opens the channel)
  monitorGroup = group(0, 0, 0);
  [['editor', 1.35, 0.14], ['channel', 3.7, -0.14]].forEach(([k, x, ry]) => {
    const g = group(x, 3.5, -5.05, ry, monitorGroup);
    box(M.iron, 0, 0, -0.03, 2.12, 1.26, 0.08, g);
    const t = screenTex(k), sm = std({ map: t, emissive: C('#ffffff'), emissiveMap: t, roughness: 0.3 });
    glow(sm, 0.55, 0.9);
    const s = new THREE.Mesh(new THREE.PlaneGeometry(2.02, 1.14), sm); s.position.z = 0.015; g.add(s);
    box(M.iron, 0, -0.85, -0.1, 0.12, 0.6, 0.08, g); box(M.iron, 0, -1.08, -0.05, 0.6, 0.03, 0.4, g);
  });
  const light = pmat('#d7dadd', { roughness: 0.5 });
  box(light, 2.5, 2.49, -3.95, 1.4, 0.05, 0.46); box(light, 3.6, 2.49, -3.9, 0.16, 0.05, 0.26);
  const cup = pmat('#f1efe9', { roughness: 0.4 });
  cyl(cup, 4.7, 2.62, -3.95, 0.12, 0.26); const mh = mesh(new THREE.TorusGeometry(0.07, 0.02, 6, 12), cup, null, 4.84, 2.62, -3.95); mh.rotation.y = PI / 2;
  { const base = new V3(0.2, 2.46, -4.9), j1 = new V3(0.2, 3.35, -4.75), j2 = new V3(1.0, 3.05, -3.95);
    cyl(M.iron, 0.2, 2.5, -4.9, 0.1, 0.08); segment(base, j1, 0.03, M.iron); segment(j1, j2, 0.03, M.iron);
    const mic = cyl(pmat('#2b2e33', { roughness: 0.3, metalness: 0.6 }), 1.05, 2.95, -3.9, 0.1, 0.36); mic.rotation.x = 0.4; }

  // chair
  { const g = group(2.4, 0, -2.3, 0.2), fab = pmat('#3b4450', { roughness: 0.85 });
    for (let k = 0; k < 5; k++) { const a = k / 5 * PI * 2, leg = box(M.iron, Math.sin(a) * 0.45, 0.1, Math.cos(a) * 0.45, 0.1, 0.06, 0.9, g); leg.rotation.y = a; sph(M.rubber, Math.sin(a) * 0.85, 0.06, Math.cos(a) * 0.85, 0.06, g); }
    cyl(M.iron, 0, 0.8, 0, 0.06, 1.3, g); box(fab, 0, 1.55, 0, 1.5, 0.22, 1.45, g); box(fab, 0, 2.75, 0.75, 1.4, 1.9, 0.2, g);
    for (const sx of [-0.8, 0.8]) { box(M.iron, sx, 1.85, 0.1, 0.06, 0.5, 0.06, g); box(fab, sx, 2.1, 0.05, 0.14, 0.06, 0.8, g); } }

  // bookshelf
  { const g = group(-7.15, 0, -1.0), shM = pmat('#6a5240', { roughness: 0.6 }), Hs = 6.2, Ls = 5;
    for (const z of [-Ls / 2, Ls / 2]) box(shM, 0, Hs / 2, z, 1.0, Hs, 0.1, g);
    box(shM, -0.47, Hs / 2, 0, 0.06, Hs, Ls, g);
    const bookCols = ['#34597a', '#6b2a24', '#2e4a3a', '#8a7a64', '#d8d2c4', '#44506a', '#5a3e30', '#9aa7b1'];
    for (let s = 0; s < 5; s++) {
      const y = 0.08 + s * 1.2; box(shM, 0, y, 0, 1.0, 0.08, Ls, g);
      if (s === 4) continue;
      let z = -Ls / 2 + 0.1;
      while (z < Ls / 2 - 0.25) { const bw = rr(0.12, 0.24), bh = rr(0.6, 1.0); if (rnd() < 0.08) { z += 0.4; continue; } box(pmat(pick(bookCols), { roughness: 0.8 }), 0.05, y + 0.04 + bh / 2, z + bw / 2, rr(0.6, 0.8), bh, bw - 0.01, g); z += bw; }
    }
    cyl(pmat('#8a5a3c'), 0.1, 5.15, 1.6, 0.14, 0.3, g); blob('#3f6b35', 0.1, 5.5, 1.6, 0.3, 0.26, 0.3, g); }

  // pegboard with speaker badges
  { const g = group(-4.0, 4.55, bz + 0.17);
    box(pmat('#b89a74', { roughness: 0.95 }), 0, 0, 0, 3.2, 1.7, 0.04, g);
    ['#2f4a66', '#6b2a24', '#2e4a3a', '#44506a', '#8a6628'].forEach((bc, i) => {
      const x = -1.3 + i * 0.65, cv = makeCanvas(160, 220), cg = cv.getContext('2d');
      cg.fillStyle = '#fbfbf8'; cg.fillRect(0, 0, 160, 220); cg.fillStyle = bc; cg.fillRect(0, 0, 160, 54);
      cg.fillStyle = '#1f2a33'; cg.font = `700 34px ${FONT_GOTHIC}`; cg.textAlign = 'center'; cg.fillText('登壇者', 80, 130);
      cg.fillStyle = '#9aa7b1'; cg.fillRect(30, 160, 100, 8); cg.fillRect(44, 180, 72, 8);
      box(pmat(bc, { roughness: 0.8 }), x, 0.35, 0.04, 0.04, 0.5, 0.01, g);
      const pl = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.6), std({ map: tex(cv, { repeat: false }), roughness: 0.4 }));
      pl.position.set(x, -0.2, 0.05); pl.rotation.z = rr(-0.08, 0.08); pl.castShadow = true; g.add(pl);
    }); }

  // note and calendar
  { const g = group(-1.1, 4.85, bz + 0.17); const pl = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.05), std({ map: paperTex([['登録者', 44, 96], ['3,462', 86, 190]]), roughness: 0.9 }));
    pl.rotation.z = 0.05; pl.castShadow = true; g.add(pl); box(pmat('#cfe3f0', { roughness: 0.6 }), 0, 0.5, 0.01, 0.4, 0.1, 0.01, g); }
  { const g = group(6.4, 4.6, bz + 0.17); const pl = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.88), std({ map: calendarTex(), roughness: 0.85 }));
    pl.castShadow = true; g.add(pl); cyl(M.iron, 0, 1.0, 0.01, 0.03, 0.05, g); }

  // plant, floor lamp, camera, softbox
  cyl(pmat('#9a6a4a', { roughness: 0.8 }), 6.9, 0.45, -4.6, 0.45, 0.9); blob('#3a6a3a', 6.9, 1.8, -4.6, 0.8, 0.95, 0.8); blob('#467a40', 6.6, 2.5, -4.4, 0.5, 0.55, 0.5);
  { cyl(M.iron, -5.8, 0.04, -4.6, 0.35, 0.08); cyl(M.iron, -5.8, 2.5, -4.6, 0.03, 5); const shade = cone(M.lamp, -5.8, 5.1, -4.6, 0.5, 0.6); shade.castShadow = false; }
  { const g = group(2.3, 0, 1.9, PI);
    for (let k = 0; k < 3; k++) { const a = k / 3 * PI * 2; segment(new V3(Math.sin(a) * 0.7, 0, Math.cos(a) * 0.7), new V3(0, 3.1, 0), 0.03, M.iron, g); }
    box(pmat('#23262b', { roughness: 0.4 }), 0, 3.35, 0, 0.6, 0.42, 0.36, g); const lens = cyl(pmat('#1a1c20', { roughness: 0.2, metalness: 0.5 }), 0, 3.35, 0.32, 0.14, 0.3, g); lens.rotation.x = PI / 2; }
  { const g = group(6.0, 0, -1.4, -0.9), sb = std({ color: C('#f4f4f2'), emissive: C('#ffffff'), roughness: 0.9 }); glow(sb, 0.25, 1.0);
    cyl(M.iron, 0, 2.2, 0, 0.03, 4.4, g); for (let k = 0; k < 3; k++) { const a = k / 3 * PI * 2; segment(new V3(0, 0.8, 0), new V3(Math.sin(a) * 0.6, 0, Math.cos(a) * 0.6), 0.025, M.iron, g); }
    const s = box(sb, 0, 4.4, 0.3, 1.1, 0.9, 0.12, g); s.rotation.x = -0.3; box(M.dark, 0, 4.45, 0.12, 1.2, 1.0, 0.3, g).rotation.x = -0.3; }

  nightLight(-5.8, 4.6, -4.6, '#ffc98a', 60, 14); nightLight(2.5, 4.2, -3.6, '#ffe2c0', 30, 10); nightLight(5.8, 4.2, -1.0, '#f4f4ff', 14, 9);
}

// ---------- renderer, sky, light cycle, post ----------
const skyVert = `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`;
const skyFrag = `
  varying vec3 vDir; uniform vec3 top; uniform vec3 mid; uniform vec3 bot; uniform float time; uniform float cloud;
  float h(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
  float n(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x), mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x), f.y); }
  float fbm(vec2 p){ float s=0.0, a=0.5; for(int i=0;i<5;i++){ s+=a*n(p); p*=2.03; a*=0.5; } return s; }
  void main(){
    vec3 d = normalize(vDir);
    vec3 c = d.y > 0.0 ? mix(mid, top, pow(d.y, 0.5)) : mix(mid, bot, pow(-d.y, 0.45));
    vec2 uv = d.xz / (abs(d.y) + 0.22) * 0.9 + vec2(time * 0.003, 0.0);
    float cl = fbm(uv * vec2(1.0, 3.0));
    c = mix(c, c * 1.12 + 0.03, smoothstep(0.5, 0.85, cl) * cloud);
    gl_FragColor = vec4(c, 1.0);
  }`;
const postFrag = `
  uniform sampler2D tDiffuse; uniform vec2 res; uniform float focusY; uniform float blur; uniform float exposure; uniform float time;
  varying vec2 vUv;
  vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14), 0.0, 1.0); }
  void main(){
    float r = smoothstep(0.1, 0.52, abs(vUv.y - focusY)) * blur;
    vec3 col = texture2D(tDiffuse, vUv).rgb; float wsum = 1.0; vec3 glow = vec3(0.0);
    for (int i = 0; i < 24; i++) {
      float fi = float(i), a = fi * 2.39996, rad = sqrt(fi + 0.5) / sqrt(24.0);
      vec2 dir = vec2(cos(a), sin(a));
      col += texture2D(tDiffuse, vUv + dir * rad * r / res).rgb; wsum += 1.0;
      glow += max(texture2D(tDiffuse, vUv + dir * rad * (10.0 + 0.012 * res.y) / res).rgb - 1.1, 0.0);
    }
    col /= wsum; col += glow / 24.0 * 0.9; col *= exposure; col = aces(col);
    float l = dot(col, vec3(0.2126, 0.7152, 0.0722)); col = mix(vec3(l), col, 1.05);
    vec2 q = vUv - 0.5; col *= 1.0 - dot(q, q) * 0.45;
    col = pow(col, vec3(1.0 / 2.2));
    col += (fract(sin(dot(vUv * res + time, vec2(12.9898, 78.233))) * 43758.5453) - 0.5) * 0.012;
    gl_FragColor = vec4(col, 1.0);
  }`;

// k: 0 = 昼, 1 = 夕暮れ・朝焼け, 2 = 夜。旧来の光量単位から物理単位へは π 倍で合わせる。
const KEYS = [
  { sun: C('#fff4e6'), sunI: 2.7, hemiS: C('#d6e4f0'), hemiG: C('#7c7a70'), hemiI: 0.5, top: C('#86a6be'), mid: C('#dbe3e5'), bot: C('#8b9aa0'), fog: C('#cdd8dc'), exp: 1.0, env: 0.8 },
  { sun: C('#ff8a50'), sunI: 2.0, hemiS: C('#6a6f9e'), hemiG: C('#3a2e2c'), hemiI: 0.35, top: C('#3a4872'), mid: C('#e89a72'), bot: C('#4e4448'), fog: C('#b58a80'), exp: 1.15, env: 0.55 },
  { sun: C('#9fb4e0'), sunI: 0.5, hemiS: C('#3a4a70'), hemiG: C('#15161c'), hemiI: 0.22, top: C('#0c1322'), mid: C('#26304a'), bot: C('#15161c'), fog: C('#232a3a'), exp: 1.3, env: 0.28 },
];
const CYCLE = 48;   // 秒。昼 → 日没 → 夜 → 日の出 → 昼
function cycleK(c) {
  const seg = (a, b, k0, k1) => c >= a && c < b ? k0 + (k1 - k0) * fade((c - a) / (b - a)) : null;
  return seg(16, 24, 0, 1) ?? seg(24, 28, 1, 2) ?? seg(28, 34, 2, 2) ?? seg(34, 38, 2, 1) ?? seg(38, 44, 1, 0) ?? 0;
}
const SUN_ARC = [new V3(45, 5, -25), new V3(24, 42, 18), new V3(6, 5, 45)];
const moonPos = new V3(-12, 40, 22), _sp = new V3(), _mp = new V3();
function sunOnArc(c) {
  let u = ((c - 36 + CYCLE) % CYCLE) / 36;   // 日の出 c=36 → 日没 c=24
  if (u > 1) u = c < 30 ? 1 : 0;
  const [R, N, S] = SUN_ARC;
  return _sp.set(0, 0, 0).addScaledVector(R, (1 - u) * (1 - u)).addScaledVector(N, 2 * u * (1 - u)).addScaledVector(S, u * u);
}

// camera sway: stays on the open side of the room
const HOME_TARGET = new V3(0.3, 2.6, -1.8), HOME_DIR = new V3(14.5, 11.4, 19.8).normalize();
const SWAY = { c: 0.66, a: 0.46, w: 0.09 };

let renderer, scene, camera, sun, hemi, skyU, envs, rt, postU, postScene, postCam, stdMats = [];
let width = 1, height = 1, raf = 0, previous = 0, visible = true, disposed = false, cyc = 6, K = 0, swayT = 0, baseDist = 26;
const _off = new V3(), _sph = new THREE.Spherical();

function applyTime(k, c) {
  const i = k < 1 ? 0 : 1, f = k - i, A = KEYS[i], B = KEYS[i + 1], L = (a, b) => a + (b - a) * f;
  sun.color.lerpColors(A.sun, B.sun, f); sun.intensity = L(A.sunI, B.sunI) * PI;
  sun.position.lerpVectors(sunOnArc(c), _mp.copy(moonPos), clamp01(k - 1)).setLength(55);
  hemi.color.lerpColors(A.hemiS, B.hemiS, f); hemi.groundColor.lerpColors(A.hemiG, B.hemiG, f); hemi.intensity = L(A.hemiI, B.hemiI) * PI;
  skyU.top.value.lerpColors(A.top, B.top, f); skyU.mid.value.lerpColors(A.mid, B.mid, f); skyU.bot.value.lerpColors(A.bot, B.bot, f);
  scene.fog.color.lerpColors(A.fog, B.fog, f);
  scene.environment = k < 0.5 ? envs.day : k < 1.5 ? envs.dusk : envs.night;
  const e = L(A.env, B.env);
  stdMats.forEach(m => { m.envMapIntensity = e; });
  postU.exposure.value = L(A.exp, B.exp);
  const lit = Math.min(1, k);
  glows.forEach(g => { g.m.emissiveIntensity = g.d + (g.n - g.d) * lit; });
  lights.forEach(o => { o.l.intensity = o.max * lit; });
  const want = k < 0.5 ? outViews.day : k < 1.5 ? outViews.dusk : outViews.night;
  if (outM.map !== want) { outM.map = want; outM.needsUpdate = true; }
}
function place(theta) {
  _sph.setFromVector3(HOME_DIR); _sph.radius = baseDist; _sph.theta = theta;
  _off.setFromSpherical(_sph); camera.position.copy(HOME_TARGET).add(_off); camera.lookAt(HOME_TARGET);
}
function render(t) {
  applyTime(K, cyc);
  skyU.time.value = t; postU.time.value = t % 100;
  renderer.setRenderTarget(rt); renderer.render(scene, camera);
  renderer.setRenderTarget(null); renderer.render(postScene, postCam);
  canvas.dataset.rendered = 'true';
}
function schedule() { if (!raf && !document.hidden && visible && !disposed) raf = requestAnimationFrame(tick); }
function tick(now) {
  raf = 0;
  const dt = previous ? Math.min(0.05, (now - previous) / 1000) : 0; previous = now;
  if (!reduce.matches) {
    cyc = (cyc + dt) % CYCLE; K = cycleK(cyc);
    swayT += dt; place(SWAY.c + SWAY.a * Math.sin(swayT * SWAY.w));
  }
  render(now / 1000);
  if (!reduce.matches) schedule();
}
function resize() {
  width = wrap.clientWidth; height = wrap.clientHeight; if (!width || !height) return;
  const dpr = Math.min(devicePixelRatio || 1, width < 700 ? 1.4 : 1.6);
  renderer.setPixelRatio(dpr); renderer.setSize(width, height, false);
  const aspect = width / height; camera.aspect = aspect;
  // wide screens: the copy sits on the left, so move the room right. Phones: the room sits in the middle band.
  const fit = (w) => w / (Math.tan(15 * PI / 180) * aspect);   // distance at which a room w units wide fills the width
  if (width > 1000) { baseDist = Math.max(34, fit(15)); camera.setViewOffset(width, height, -width * 0.2, height * 0.02, width, height); }
  else if (width > 700) { baseDist = Math.max(36, fit(17)); camera.setViewOffset(width, height, -width * 0.1, -height * 0.02, width, height); }
  else { baseDist = Math.max(40, fit(10.5)); camera.setViewOffset(width, height, 0, -height * 0.13, width, height); }
  camera.updateProjectionMatrix();
  rt.setSize(Math.floor(width * dpr), Math.floor(height * dpr)); postU.res.value.set(Math.floor(width * dpr), Math.floor(height * dpr)); postU.blur.value = 0.009 * height * dpr;
  place(reduce.matches ? SWAY.c : SWAY.c + SWAY.a * Math.sin(swayT * SWAY.w));
  if (reduce.matches) render(0); else schedule();
}

try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance' });
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  ANISO = renderer.capabilities.getMaxAnisotropy();
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(30, 1, 0.3, 900);
  world = new THREE.Group(); scene.add(world);
  blobs = [blobGeo(0), blobGeo(11.3), blobGeo(27.1)];
  buildStudy();

  sun = new THREE.DirectionalLight(0xffffff, 2.5);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.025;
  Object.assign(sun.shadow.camera, { left: -13, right: 13, top: 13, bottom: -13, near: 1, far: 120 });
  scene.add(sun, sun.target);
  hemi = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.5); scene.add(hemi);
  skyU = { top: { value: C('#86a6be') }, mid: { value: C('#dbe3e5') }, bot: { value: C('#8b9aa0') }, time: { value: 0 }, cloud: { value: 0.8 } };
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(500, 48, 24), new THREE.ShaderMaterial({ uniforms: skyU, vertexShader: skyVert, fragmentShader: skyFrag, side: THREE.BackSide, depthWrite: false, fog: false })));
  scene.fog = new THREE.Fog(C('#cdd8dc'), 55, 150);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const buildEnv = (t, m, bo) => {
    const es = new THREE.Scene(), u = { top: { value: t }, mid: { value: m }, bot: { value: bo }, time: { value: 0 }, cloud: { value: 0.3 } };
    es.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.ShaderMaterial({ uniforms: u, vertexShader: skyVert, fragmentShader: skyFrag, side: THREE.BackSide })));
    return pmrem.fromScene(es, 0.04).texture;
  };
  envs = { day: buildEnv(C('#a9c6dc'), C('#eef2f2'), C('#7d8a8e')), dusk: buildEnv(C('#3c4a78'), C('#f0a07a'), C('#3e3638')), night: buildEnv(C('#0e1526'), C('#2a3452'), C('#15161c')) };
  pmrem.dispose();
  scene.traverse(o => { const m = o.material; if (m && m.isMeshStandardMaterial && !stdMats.includes(m)) stdMats.push(m); });

  rt = new THREE.WebGLRenderTarget(2, 2, { type: THREE.HalfFloatType, samples: 4 });
  postU = { tDiffuse: { value: rt.texture }, res: { value: new THREE.Vector2(2, 2) }, focusY: { value: 0.45 }, blur: { value: 8 }, exposure: { value: 1 }, time: { value: 0 } };
  const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ uniforms: postU, depthTest: false, depthWrite: false, vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }', fragmentShader: postFrag }));
  post.frustumCulled = false;
  postScene = new THREE.Scene(); postScene.add(post);
  postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  try { const c0 = parseFloat(new URLSearchParams(location.search).get('c')); if (c0 >= 0) cyc = c0 % CYCLE; } catch (e) { /* no override */ }
  K = reduce.matches ? 0 : cycleK(cyc);
  resize();
  host.classList.add('ready');
  new ResizeObserver(resize).observe(wrap);
  new IntersectionObserver(en => { visible = en[0].isIntersecting; previous = 0; if (visible) schedule(); else { cancelAnimationFrame(raf); raf = 0; } }, { threshold: 0 }).observe(host);

  // the monitors open the YouTube channel
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  const overMonitor = (e) => {
    const r = canvas.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    return ray.intersectObject(monitorGroup, true).length > 0;
  };
  canvas.addEventListener('pointermove', (e) => { canvas.style.cursor = overMonitor(e) ? 'pointer' : ''; });
  canvas.addEventListener('click', (e) => { if (overMonitor(e)) window.open(CHANNEL_URL, '_blank', 'noopener'); });
} catch (e) {
  canvas.dataset.error = e.message;
  const l = host.querySelector('.loading'); if (l) l.textContent = '3Dを表示できませんでした。再読み込みしてお試しください。';
  console.error(e);
}
reduce.addEventListener('change', () => { previous = 0; if (reduce.matches) { K = 0; cancelAnimationFrame(raf); raf = 0; resize(); } else schedule(); });
document.addEventListener('visibilitychange', () => { previous = 0; if (document.hidden) { cancelAnimationFrame(raf); raf = 0; } else schedule(); });
window.addEventListener('pagehide', () => {
  disposed = true; cancelAnimationFrame(raf);
  scene?.traverse(o => { o.geometry?.dispose(); for (const m of Array.isArray(o.material) ? o.material : [o.material]) { m?.map?.dispose(); m?.dispose(); } });
  Object.values(envs || {}).forEach(t => t.dispose()); rt?.dispose(); renderer?.dispose();
});
