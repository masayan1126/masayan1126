// 問い合わせフォームの受け口。入力を検証し、Email Routing 経由で受信アドレス (env.TO) へ送る。
import { EmailMessage } from 'cloudflare:email';

const FROM = 'form@msyn.me';
const ORIGINS = ['https://studio.msyn.me'];
const KINDS = ['開発・AI導入のご依頼', 'PR・タイアップのご依頼', '登壇のご依頼', '動画編集のご依頼', '採用・業務委託のご相談', 'その他'];
const MAX_REQUEST_BYTES = 64 * 1024;
const TOKEN_FIELD = 'cf-turnstile-response';
const ALLOWED_FIELDS = new Set(['kind', 'name', 'org', 'email', 'body', 'website', TOKEN_FIELD]);
const LIMITS = { name: 100, org: 150, email: 254, body: 5000 };

const b64 = text => btoa(String.fromCharCode(...new TextEncoder().encode(text)));
const header = text => `=?UTF-8?B?${b64(text)}?=`;
const wrap = text => text.replace(/.{1,76}/g, '$&\r\n');

function cors(origin) {
  return ORIGINS.includes(origin)
    ? { 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', Vary: 'Origin' }
    : {};
}
const reply = (status, body, origin, extraHeaders = {}) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors(origin), 'Cache-Control': 'no-store', ...extraHeaders } });

export function validate(form) {
  const value = key => String(form.get(key) ?? '').trim();
  const data = { kind: value('kind'), name: value('name'), org: value('org'), email: value('email'), body: value('body') };
  if (!KINDS.includes(data.kind)) return { error: 'ご相談の種類を選んでください。' };
  if (!data.name || !data.email || !data.body) return { error: '必須の項目を入力してください。' };
  if (!/^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]+$/.test(data.email)) return { error: 'メールアドレスの形式を確認してください。' };
  for (const [key, max] of Object.entries(LIMITS)) if (data[key].length > max) return { error: '入力が長すぎます。' };
  if (/[\r\n]/.test(data.name + data.org + data.email)) return { error: '入力を確認してください。' };
  return { data };
}

export function mime({ kind, name, org, email, body }, to, now = new Date(), id = crypto.randomUUID()) {
  const text = [`ご相談の種類：${kind}`, `お名前：${name}`, `会社名・団体名：${org || '（なし）'}`, `メールアドレス：${email}`, '', 'ご相談内容：', body, '', '— studio.msyn.me の問い合わせフォームから送信'].join('\n');
  return [
    `From: ${header('Miyabiya Studio フォーム')} <${FROM}>`,
    `To: ${to}`,
    `Reply-To: ${email}`,
    `Subject: ${header(`【${kind}】${name}${org ? `（${org}）` : ''} 様からのお問い合わせ`)}`,
    `Message-ID: <${id}@msyn.me>`,
    `Date: ${now.toUTCString()}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    wrap(b64(text)),
  ].join('\r\n');
}

// Cap the actual stream too: Content-Length can be absent or dishonest.
async function readForm(request) {
  if (Number(request.headers.get('Content-Length')) > MAX_REQUEST_BYTES) throw 413;
  const reader = request.body?.getReader();
  if (!reader) throw 400;
  const chunks = []; let size = 0;
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_REQUEST_BYTES) { await reader.cancel(); throw 413; }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return new Response(bytes, { headers: { 'Content-Type': request.headers.get('Content-Type') } }).formData();
}

async function verifyToken(token, ip, secret) {
  try {
    const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body: new URLSearchParams({ secret, response: token, remoteip: ip }),
      signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) return 'unavailable';
    const result = await response.json();
    if (result.success === true && result.hostname === 'studio.msyn.me' && result.action === 'contact') return 'verified';
    if (result['error-codes']?.some(code => ['internal-error', 'missing-input-secret', 'invalid-input-secret'].includes(code))) return 'unavailable';
    return 'rejected';
  } catch { return 'unavailable'; }
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });
    if (request.method !== 'POST') return reply(405, { ok: false, error: 'Method Not Allowed' }, origin, { Allow: 'POST, OPTIONS' });
    if (!ORIGINS.includes(origin)) return reply(403, { ok: false, error: 'Forbidden' }, origin);
    const type = (request.headers.get('Content-Type') || '').split(';')[0].trim().toLowerCase();
    if (!['multipart/form-data', 'application/x-www-form-urlencoded'].includes(type)) return reply(415, { ok: false, error: '入力形式を確認してください。' }, origin);
    if (!env.TURNSTILE_SECRET_KEY || !env.CONTACT_RATE_LIMITER?.limit) return reply(503, { ok: false, error: '現在送信できません。時間をおいてお試しください。' }, origin);
    const ip = request.headers.get('CF-Connecting-IP');
    if (!ip) return reply(403, { ok: false, error: '送信元を確認できませんでした。' }, origin);
    try {
      const { success } = await env.CONTACT_RATE_LIMITER.limit({ key: `contact:${ip}` });
      if (!success) return reply(429, { ok: false, error: '送信回数が多いため、1分ほど待ってからお試しください。' }, origin, { 'Retry-After': '60' });
    } catch { return reply(503, { ok: false, error: '現在送信できません。時間をおいてお試しください。' }, origin); }
    let form;
    try { form = await readForm(request); }
    catch (error) { return reply(error === 413 ? 413 : 400, { ok: false, error: error === 413 ? '入力が長すぎます。' : '入力を確認してください。' }, origin); }
    for (const key of form.keys()) {
      if (!ALLOWED_FIELDS.has(key) || form.getAll(key).length !== 1 || typeof form.get(key) !== 'string') return reply(400, { ok: false, error: '入力を確認してください。' }, origin);
    }
    if (form.get('website')) return reply(200, { ok: true }, origin); // No mail, including when the token is absent.
    const token = (form.get(TOKEN_FIELD) || '').trim();
    if (!token || token.length > 2048) return reply(400, { ok: false, code: 'BOT_CHECK_REQUIRED', error: '確認が完了していません。ページを再読み込みしてお試しください。' }, origin);
    const { data, error } = validate(form);
    if (error) return reply(400, { ok: false, error }, origin);
    const verification = await verifyToken(token, ip, env.TURNSTILE_SECRET_KEY);
    if (verification !== 'verified') return reply(verification === 'unavailable' ? 503 : 400, { ok: false, code: 'BOT_CHECK_FAILED', error: verification === 'unavailable' ? '自動確認に接続できません。時間をおいてお試しください。' : '確認の有効期限が切れたか、確認できませんでした。もう一度お試しください。' }, origin);
    try {
      await env.MAILER.send(new EmailMessage(FROM, env.TO, mime(data, env.TO)));
    } catch {
      console.error('Contact mail delivery failed');
      return reply(502, { ok: false, error: '送信できませんでした。お手数ですがメールでお送りください。' }, origin);
    }
    return reply(200, { ok: true }, origin);
  },
};
