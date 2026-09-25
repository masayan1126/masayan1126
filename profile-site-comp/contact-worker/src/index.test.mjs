import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
// cloudflare:email exists only in Workers; test a copy of the module with a stub in its place.
const source = readFileSync(new URL('./index.js', import.meta.url), 'utf8').replace("import { EmailMessage } from 'cloudflare:email';", 'const EmailMessage = class {};');
const copy = new URL('./.index.under-test.mjs', import.meta.url);
writeFileSync(copy, source);
const { validate, mime } = await import(copy.href);
rmSync(copy);

const form = values => ({ get: key => values[key] ?? null });
const ok = { kind: 'PR・タイアップのご依頼', name: '山田 太郎', org: '株式会社サンプル', email: 'taro@example.com', body: 'テスト\n2行目' };

test('valid input passes and trims', () => {
  assert.deepEqual(validate(form({ ...ok, name: '  山田 太郎 ' })).data.name, '山田 太郎');
});
test('rejects unknown kind, missing fields, bad email, header injection and long text', () => {
  assert.ok(validate(form({ ...ok, kind: 'x' })).error);
  assert.ok(validate(form({ ...ok, body: '' })).error);
  assert.ok(validate(form({ ...ok, email: 'nope' })).error);
  assert.ok(validate(form({ ...ok, name: 'a\r\nBcc: x@y.z' })).error);
  assert.ok(validate(form({ ...ok, body: 'a'.repeat(5001) })).error);
});
test('builds a UTF-8 message with reply-to and an encoded subject', () => {
  const raw = mime(ok, 'owner@example.com', new Date('2026-09-25T00:00:00Z'), 'id');
  assert.match(raw, /^From: =\?UTF-8\?B\?.+\?= <form@msyn\.me>\r\n/);
  assert.match(raw, /\r\nReply-To: taro@example\.com\r\n/);
  const subject = raw.match(/Subject: =\?UTF-8\?B\?(.+)\?=/)[1];
  assert.equal(Buffer.from(subject, 'base64').toString(), '【PR・タイアップのご依頼】山田 太郎（株式会社サンプル） 様からのお問い合わせ');
  const body = Buffer.from(raw.split('\r\n\r\n')[1].replace(/\r\n/g, ''), 'base64').toString();
  assert.match(body, /ご相談内容：\nテスト\n2行目/);
});
