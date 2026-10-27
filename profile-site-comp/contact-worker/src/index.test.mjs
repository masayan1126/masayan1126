import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
// cloudflare:email exists only in Workers; test a copy of the module with a stub in its place.
const source = readFileSync(new URL('./index.js', import.meta.url), 'utf8').replace("import { EmailMessage } from 'cloudflare:email';", 'const EmailMessage = class {};');
const copy = new URL('./.index.under-test.mjs', import.meta.url);
writeFileSync(copy, source);
const { default: worker, validate, mime } = await import(copy.href);
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


function apiHarness({verify={success:true,hostname:'studio.msyn.me',action:'contact'},rate=true,secret='test-only-secret',verifyThrows=false,mailThrows=false}={}) {
  let mail=0,verification=0,limits=0;
  const env={TO:'owner@example.com',TURNSTILE_SECRET_KEY:secret,CONTACT_RATE_LIMITER:{limit:async()=>{limits++;return {success:rate};}},MAILER:{send:async()=>{mail++;if(mailThrows)throw new Error('mail');}}};
  const original=globalThis.fetch;
  globalThis.fetch=async(url,options)=>{verification++;assert.equal(url,'https://challenges.cloudflare.com/turnstile/v0/siteverify');assert.equal(options.body.get('response'),'test-token');assert.equal(options.body.get('remoteip'),'192.0.2.42');if(verifyThrows)throw new Error('offline');return verify instanceof Response?verify:Response.json(verify);};
  return {env,counts:()=>({mail,verification,limits}),close:()=>{globalThis.fetch=original;}};
}
function request(values={},headers={},method='POST') {
  return new Request('https://studio.msyn.me/api/contact',{method,headers:{Origin:'https://studio.msyn.me','CF-Connecting-IP':'192.0.2.42',...headers},...(method==='POST'?{body:new URLSearchParams({...ok,'cf-turnstile-response':'test-token',...values})}:{})});
}
async function runApi(options,req=request()) {
  const h=apiHarness(options);try{const response=await worker.fetch(req,h.env);return {response,body:await response.json(),counts:h.counts()};}finally{h.close();}
}
test('API accepts exactly one verified inquiry; rejects missing, expired, reused and unrelated tokens without mail',async()=>{
  const accepted=await runApi({});assert.equal(accepted.response.status,200);assert.equal(accepted.counts.mail,1);assert.equal(accepted.counts.verification,1);
  for(const token of ['', 'x'.repeat(2049)]) {const r=await runApi({},request({'cf-turnstile-response':token}));assert.equal(r.response.status,400);assert.equal(r.body.code,'BOT_CHECK_REQUIRED');assert.equal(r.counts.mail,0);assert.equal(r.counts.verification,0);}
  for(const verify of [{success:false,'error-codes':['invalid-input-response']},{success:false,'error-codes':['timeout-or-duplicate']},{success:true,hostname:'other.example',action:'contact'},{success:true,hostname:'studio.msyn.me',action:'login'},null]) {const r=await runApi({verify});assert.equal(r.response.status,verify===null?503:400);assert.equal(r.counts.mail,0);}
});
test('API fails closed on missing configuration, rate rejection and verification outages',async()=>{
  for(const options of [{secret:''},{rate:false},{verifyThrows:true},{verify:new Response('not json')},{verify:new Response('',{status:500})},{verify:{success:false,'error-codes':['invalid-input-secret']}},{verify:{success:false,'error-codes':['internal-error']}}]) {
    const r=await runApi(options);assert.equal(r.response.status,options.rate===false?429:503);assert.equal(r.counts.mail,0);
    if(options.rate===false){assert.equal(r.response.headers.get('Retry-After'),'60');assert.equal(r.counts.verification,0);}
  }
  const h=apiHarness();try{delete h.env.CONTACT_RATE_LIMITER;const r=await worker.fetch(request(),h.env);assert.equal(r.status,503);assert.equal(h.counts().mail,0);}finally{h.close();}
});
test('API rejects forged origins, wrong methods/types, duplicates, files and oversized streams',async()=>{
  const duplicate=new URLSearchParams({...ok,'cf-turnstile-response':'test-token'});duplicate.append('email','second@example.com');
  const file=new FormData();for(const [key,value]of Object.entries(ok))file.set(key,value);file.set('cf-turnstile-response','test-token');file.set('org',new Blob(['file']),'file.txt');
  const bad=[
    [request({}, {Origin:'https://evil.example'}),403],
    [request({}, {},'GET'),405],
    [request({}, {'Content-Type':'application/json'}),415],
    [request({}, {'CF-Connecting-IP':''}),403],
    [new Request(request(),{body:duplicate}),400],
    [new Request('https://studio.msyn.me/api/contact',{method:'POST',headers:{Origin:'https://studio.msyn.me','CF-Connecting-IP':'192.0.2.42'},body:file}),400],
    [request({unknown:'value'}),400],
    [request({}, {'Content-Length':'65537'}),413],
    [request({body:'a'.repeat(65537)}),413],
    [request({body:'a'.repeat(65537)}, {'Content-Length':'10'}),413],
    [request({body:'a'.repeat(5001)}),400],
  ];
  for(const [req,status]of bad){const r=await runApi({},req);assert.equal(r.response.status,status);assert.equal(r.counts.mail,0);assert.equal(r.counts.verification,0);}
});
test('honeypot and preflight never verify or send; mail failures do not disclose internal errors',async()=>{
  const trap=await runApi({},request({website:'https://bot.example','cf-turnstile-response':''}));assert.equal(trap.response.status,200);assert.equal(trap.counts.mail,0);assert.equal(trap.counts.verification,0);
  const h=apiHarness();try{const r=await worker.fetch(request({}, {},'OPTIONS'),h.env);assert.equal(r.status,204);assert.deepEqual(h.counts(),{mail:0,verification:0,limits:0});}finally{h.close();}
  const failed=await runApi({mailThrows:true});assert.equal(failed.response.status,502);assert.equal(failed.counts.mail,1);assert.doesNotMatch(failed.body.error,/Error/);
});
