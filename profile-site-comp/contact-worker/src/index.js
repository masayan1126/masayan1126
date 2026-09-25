// 問い合わせフォームの受け口。入力を検証し、Email Routing 経由で受信アドレス (env.TO) へ送る。
import { EmailMessage } from 'cloudflare:email';

const FROM = 'form@msyn.me';
const ORIGINS = ['https://studio.msyn.me', 'https://miyabiya-studio.pages.dev'];
const KINDS = ['開発・AI導入のご依頼', 'PR・タイアップのご依頼', '登壇のご依頼', '動画編集のご依頼', '採用・業務委託のご相談', 'その他'];
const LIMITS = { name: 100, org: 150, email: 254, body: 5000 };

const b64 = text => btoa(String.fromCharCode(...new TextEncoder().encode(text)));
const header = text => `=?UTF-8?B?${b64(text)}?=`;
const wrap = text => text.replace(/.{1,76}/g, '$&\r\n');

function cors(origin) {
  return ORIGINS.includes(origin)
    ? { 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', Vary: 'Origin' }
    : {};
}
const reply = (status, body, origin) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors(origin) } });

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

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });
    if (request.method !== 'POST') return reply(405, { ok: false, error: 'Method Not Allowed' }, origin);
    if (!ORIGINS.includes(origin)) return reply(403, { ok: false, error: 'Forbidden' }, origin);
    let form;
    try { form = await request.formData(); } catch { return reply(400, { ok: false, error: '入力を確認してください。' }, origin); }
    if (String(form.get('website') ?? '')) return reply(200, { ok: true }, origin);   // honeypot: bots fill the hidden field
    const { data, error } = validate(form);
    if (error) return reply(400, { ok: false, error }, origin);
    try {
      await env.MAILER.send(new EmailMessage(FROM, env.TO, mime(data, env.TO)));
    } catch (e) {
      console.error('send failed', e);
      return reply(502, { ok: false, error: '送信できませんでした。お手数ですがメールでお送りください。' }, origin);
    }
    return reply(200, { ok: true }, origin);
  },
};
