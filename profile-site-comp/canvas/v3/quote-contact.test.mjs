import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
import {HANDOFF_KEY,HANDOFF_TTL,CONTACT_PATH,contactText,saveHandoff,takeHandoff,receiveHandoff,installQuoteContact} from './quote-contact.mjs';
import {quote,summary,defaultItems} from './pricing-model.mjs';

const origin='https://studio.msyn.me';
const storage=()=>{const data=new Map();return {getItem:key=>data.get(key)??null,setItem:(key,value)=>data.set(key,value),removeItem:key=>data.delete(key)};};
const data={...JSON.parse(readFileSync(new URL('./pricing-rates/4d2a90817527.json',import.meta.url))),rateVersion:'4d2a90817527'};
const state={media:['main','short','x'],items:defaultItems(data),revisions:2,revisionCounts:{main:3,short:4,x:5},shortMode:'clip',custom:[],notes:''};
const inquiry=summary(data,state);
const formDoc=(body='')=>{
  const form={elements:{body:{value:body},kind:{value:''}}},status={textContent:''};
  return {form,status,getElementById:id=>id==='inquiry-form'?form:id==='quote-handoff-status'?status:null};
};

test('all seven quote summaries reach the form without recalculating rates or taking URL amounts',()=>{
  for(const media of [['x'],['short'],['short','x'],['main'],['main','x'],['main','short'],['main','short','x']]) {
    const current={...state,media},text=summary(data,current),before=quote(data,current),store=storage();
    saveHandoff(store,origin,text,1000);
    const doc=formDoc();
    const address=new URL(CONTACT_PATH,origin);address.searchParams.set('total','1');
    assert.equal(receiveHandoff(doc,address.href,store,1100),true);
    assert.equal(doc.form.elements.body.value,text);
    assert.equal(doc.form.elements.kind.value,'PR・タイアップのご依頼');
    assert.deepEqual(quote(data,current),before);
    assert.equal(store.getItem(HANDOFF_KEY),null);
    assert.ok(doc.status.textContent.includes('確認して送信'));
  }
});

test('records are origin bound, expire after thirty minutes, and are consumed once',()=>{
  for(const change of [r=>r.origin='https://other.example',r=>r.createdAt=-HANDOFF_TTL,r=>r.createdAt=10000000,r=>r.body='',r=>r.body='x'.repeat(5001),r=>r.version=2,r=>r.omittedQuoteUrl='false']) {
    const store=storage(),record=saveHandoff(store,origin,inquiry,1000000);
    change(record);store.setItem(HANDOFF_KEY,JSON.stringify(record));
    assert.equal(takeHandoff(store,origin,1000001),null);
    assert.equal(store.getItem(HANDOFF_KEY),null);
  }
  const store=storage();saveHandoff(store,origin,inquiry,1000);
  assert.equal(takeHandoff(store,origin,1000+HANDOFF_TTL).body,inquiry);
  assert.equal(takeHandoff(store,origin,1000+HANDOFF_TTL),null);
  saveHandoff(store,origin,inquiry,1000);assert.equal(takeHandoff(store,origin,1001+HANDOFF_TTL),null);
  store.setItem(HANDOFF_KEY,'{broken');assert.equal(takeHandoff(store,origin,2000),null);
});

test('only an explicit contact handoff is applied, without overwriting existing text',()=>{
  const store=storage();saveHandoff(store,origin,inquiry,1000);
  const doc=formDoc('入力中の内容');
  assert.equal(receiveHandoff(doc,origin+'/contact/?type=pr&total=1',store,1100),false);
  assert.ok(store.getItem(HANDOFF_KEY));
  assert.equal(receiveHandoff(doc,origin+CONTACT_PATH,store,1100),false);
  assert.equal(doc.form.elements.body.value,'入力中の内容');
  assert.ok(doc.status.textContent.includes('保持'));
  assert.equal(store.getItem(HANDOFF_KEY),null);
});

test('long encoded links are omitted only when needed, preserving amounts and the full request',()=>{
  const request='あ'.repeat(1000),text=summary(data,{...state,notes:request});
  assert.ok(text.length>5000);
  const prepared=contactText(text);
  assert.equal(prepared.omittedQuoteUrl,true);
  assert.ok(prepared.body.length<=5000);
  assert.ok(prepared.body.includes(request));
  assert.ok(prepared.body.includes('69,600円'));
  assert.ok(prepared.body.includes('要相談'));
  assert.throws(()=>contactText('x'.repeat(5001)));
  assert.throws(()=>contactText('x'.repeat(5001)+'\nhttps://evil.example/pricing/'));
});

test('click handoff finishes storage synchronously; copy has a manual fallback',async()=>{
  const handlers=new Map(),store=storage(),field={value:inquiry,hidden:true,focus(){this.focused=true},select(){this.selected=true}},status={textContent:''},fallback={hidden:true};
  const host={querySelector:s=>s==='[data-quote-text]'?field:s==='[data-quote-status]'?status:fallback};
  let mode='inquiry';
  const control={closest:()=>host,hasAttribute:name=>name===(mode==='inquiry'?'data-quote-inquiry':'data-quote-copy')};
  const doc={readyState:'complete',addEventListener:(name,fn)=>handlers.set(name,fn),getElementById:()=>null};
  const win={location:new URL(origin+'/pricing/'),sessionStorage:store,navigator:{clipboard:{writeText:async()=>{throw new Error('denied')}}}};
  installQuoteContact(doc,win);
  let prevented=false;const event={target:{closest:()=>control},preventDefault:()=>prevented=true};
  const pending=handlers.get('click')(event);
  assert.equal(JSON.parse(store.getItem(HANDOFF_KEY)).body,inquiry);
  assert.equal(prevented,false);await pending;
  mode='copy';await handlers.get('click')(event);
  assert.equal(field.hidden,false);assert.equal(field.focused,true);assert.equal(field.selected,true);
  assert.ok(status.textContent.includes('コピー'));
  mode='inquiry';win.sessionStorage={setItem(){throw new Error('blocked')}};
  prevented=false;await handlers.get('click')(event);
  assert.equal(prevented,true);assert.equal(fallback.hidden,false);
});

test('analytics count successful inquiries only and do not include input text or URL queries',()=>{
  const source=execFileSync('python3',['-c',"import ast,json,pathlib; p=ast.parse(pathlib.Path('canvas/v3/build_public.py').read_text()); a=next(n for n in p.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GA4' for t in n.targets)); print(json.dumps(eval(compile(ast.Expression(a.value),'<ga>','eval'),{'GA4_ID':'test'})))"],{cwd:new URL('../..',import.meta.url),encoding:'utf8'});
  const html=JSON.parse(source),script=html.match(/<script>([\s\S]*)<\/script>/)[1],handlers=new Map();
  const context={window:{},document:{addEventListener:(name,fn)=>handlers.set(name,fn)},location:new URL(origin+'/contact/?notes=PRIVATE&total=1'),URL,WeakSet};
  context.window=context;context.dataLayer=[];vm.runInNewContext(script,context);
  const events=()=>context.dataLayer.map(args=>Array.from(args)).filter(row=>row[0]==='event');
  assert.equal(handlers.has('submit'),false);
  const body={name:'body',closest:()=>form};
  const form={elements:{kind:{value:'PR・タイアップのご依頼'},body:{value:'PRIVATE request'}}};
  handlers.get('input')({target:body});handlers.get('input')({target:body});
  assert.equal(events().filter(row=>row[1]==='inquiry_start').length,1);
  assert.equal(events().filter(row=>row[1]==='generate_lead').length,0);
  handlers.get('site:inquiry-sent')({detail:{kind:'PR・タイアップのご依頼'}});
  handlers.get('site:inquiry-sent')({detail:{kind:'PRIVATE request'}});
  handlers.get('site:inquiry-sent')({detail:{kind:'__proto__'}});
  assert.equal(events().filter(row=>row[1]==='generate_lead').length,1);
  handlers.get('site:pricing-complete')({detail:{mode:'wizard',notes:'PRIVATE request'}});
  const action={id:'',href:origin+'/contact/?body=PRIVATE&total=1',hostname:'studio.msyn.me',matches:()=>true,hasAttribute:()=>false,closest:()=>null};
  handlers.get('click')({target:{closest:()=>action}});
  assert.equal(events().find(row=>row[1]==='cta_click')[2].action,'contact');
  action.id='wizard-open';handlers.get('click')({target:{closest:()=>action}});
  assert.equal(events().filter(row=>row[1]==='pricing_start').length,1);
  const encoded=JSON.stringify(events());
  assert.equal(encoded.includes('PRIVATE'),false);assert.equal(encoded.includes('total=1'),false);
});
