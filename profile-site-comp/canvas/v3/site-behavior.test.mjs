import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const contactHtml=execFileSync('python3',['-c',"import runpy,sys;print(runpy.run_path(sys.argv[1])['render_contact_form']())",fileURLToPath(new URL('./build_sections.py',import.meta.url))],{encoding:'utf8'});
const contactScript=[...contactHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes("const f=document.getElementById('inquiry-form')"));
function contactHarness({verified=true,valid=true,search='',kind='PR・タイアップのご依頼',resetDefaults={},handoffText='',request=async()=>({ok:true,json:async()=>({ok:true})})}={}) {
  const handlers={},windowHandlers={},documentHandlers={},attrs={};
  const field=value=>({value,customError:'',setCustomValidity(message){this.customError=message;}});
  const elements={kind:field(kind),name:field('テスト担当'),org:field(''),email:field('test@example.com'),body:field('ご相談の本文'),website:field('')};
  const status={focus(){this.focused=true;}},handoffStatus={textContent:handoffText},hint={},count={},check={focus(){this.focused=true;}},tokenField={value:''},retry={addEventListener:(k,fn)=>{handlers['retry:'+k]=fn;}};
  let widgetOptions,checkResets=0;const loader={addEventListener:(k,fn)=>{handlers['loader:'+k]=fn;},remove(){}};
  const browser={addEventListener:(k,fn)=>{windowHandlers[k]=fn;},turnstile:{render:(_selector,options)=>{widgetOptions=options;return 'widget';},reset:()=>{checkResets++;}}};
  const button={disabled:false,innerHTML:'送信する<span>→</span>',setAttribute:(k,v)=>{attrs[k]=v;},removeAttribute:k=>{delete attrs[k];}};
  let requests=0,resets=0,successEvents=0;
  const form={elements,querySelector:s=>s==='.form-status'?status:button,reportValidity:()=>valid&&!Object.values(elements).some(f=>f.customError),reset:()=>{resets++;for(const [key,field] of Object.entries(elements))field.value=resetDefaults[key]??'';},addEventListener:(name,fn)=>{handlers[name]=fn;}};
  const nodes={'inquiry-form':form,'inquiry-body-hint':hint,'inquiry-body-count':count,'inquiry-security-status':check,'inquiry-security-retry':retry,'inquiry-security-token':tokenField,'quote-handoff-status':handoffStatus};
  vm.runInNewContext(contactScript,{document:{head:{append(){}},createElement:()=>loader,getElementById:id=>nodes[id],addEventListener:(k,fn)=>{documentHandlers[k]=fn;},dispatchEvent:e=>{if(e.type==='site:inquiry-sent')successEvents++;}},window:browser,CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},location:{search},URLSearchParams,FormData:class {},fetch:async()=>{requests++;return request();}});
  browser.onContactTurnstileReady();if(verified)widgetOptions.callback('verified-test-token');
  return {check,tokenField,retry,widgetOptions,checkResets:()=>checkResets,elements,status,handoffStatus,button,hint,count,attrs,handlers,windowHandlers,documentHandlers,submit:()=>handlers.submit({preventDefault(){}}),result:()=>({requests,resets,successEvents})};
}

test('contact form rejects invalid input before network activity and restores the button after valid submission', async()=>{
  const invalid=contactHarness({valid:false});
  await invalid.submit();
  assert.equal(invalid.result().requests,0);
  assert.equal(invalid.button.disabled,false);
  const valid=contactHarness();
  await valid.submit();
  assert.deepEqual(valid.result(),{requests:1,resets:1,successEvents:1});
  assert.equal(valid.button.disabled,false);
  assert.equal(valid.attrs['aria-busy'],undefined);
  assert.match(valid.button.innerHTML,/送信する/);
  assert.match(valid.status.textContent,/2営業日/);
  assert.equal(valid.status.focused,true);
  assert.equal(valid.count.textContent,'0 / 5,000文字');
  for(const key of ['kind','name','org','email','body'])assert.equal(valid.elements[key].value,'');
});

test('successful inquiries clear sent values even when native reset restores nonempty defaults',async()=>{
  const h=contactHarness({resetDefaults:{kind:'PR・タイアップのご依頼',name:'初期のお名前',org:'初期の会社名',email:'initial@example.com',body:'初期の見積もり本文'},handoffText:'見積もりを入力しました。'});
  await h.submit();
  for(const key of ['kind','name','org','email','body'])assert.equal(h.elements[key].value,'');
  assert.equal(h.handoffStatus.textContent,'');
  assert.equal(h.count.textContent,'0 / 5,000文字');
  assert.equal(h.hint.textContent,'ご相談の概要・希望時期・ご予算など');
  assert.equal(h.elements.body.placeholder,'決まっている範囲でご記入ください。');
  assert.match(h.status.textContent,/送信しました/);
});

test('bot verification blocks unverified submits, supports retry, and clears used or expired tokens',async()=>{
  const h=contactHarness({verified:false});const original=h.elements.body.value;
  await h.submit();assert.equal(h.result().requests,0);assert.equal(h.check.focused,true);assert.equal(h.elements.body.value,original);
  h.widgetOptions['before-interactive-callback']();assert.match(h.check.textContent,/チェック/);await h.submit();assert.match(h.status.textContent,/チェック/);
  h.widgetOptions['error-callback']();assert.equal(h.retry.hidden,false);
  h.handlers['retry:click']();assert.equal(h.checkResets(),1);assert.equal(h.retry.hidden,true);
  h.widgetOptions.callback('new-token');assert.equal(h.tokenField.value,'new-token');assert.equal(h.check.textContent,'');
  h.widgetOptions['expired-callback']();assert.equal(h.tokenField.value,'');
  await h.submit();assert.equal(h.result().requests,0);
  h.widgetOptions.callback('fresh-token');await h.submit();assert.equal(h.result().requests,1);assert.equal(h.tokenField.value,'');
  assert.equal(h.checkResets(),2);await h.submit();assert.equal(h.result().requests,1);
  const cached=contactHarness();cached.windowHandlers.pageshow({persisted:true});assert.equal(cached.tokenField.value,'');
});

test('pages.dev contact pages move to the canonical host before loading verification',()=>{
  let redirected;
  vm.runInNewContext(contactScript,{document:{getElementById:()=>({})},location:{hostname:'release.miyabiya-studio.pages.dev',search:'?type=pr',hash:'#contact-form',replace:url=>{redirected=url;}}});
  assert.equal(redirected,'https://studio.msyn.me/contact/?type=pr#contact-form');
});

test('verification script failure keeps the form editable and offers a keyboard-accessible retry',async()=>{
  const h=contactHarness({verified:false});h.handlers['loader:error']();
  assert.equal(h.retry.hidden,false);assert.match(h.check.textContent,/再試行/);
  await h.submit();assert.equal(h.result().requests,0);assert.equal(h.button.disabled,false);
  assert.equal(h.elements.email.value,'test@example.com');
});

test('changing inquiry suggestions and restoring a quote never replaces the entered body',()=>{
  const h=contactHarness();
  const quote='本編＋ショート＋X\n税込54,500円';
  h.elements.body.value=quote;
  h.elements.kind.value='登壇のご依頼';
  h.handlers.change({target:h.elements.kind});
  assert.match(h.hint.textContent,/イベント名/);
  assert.equal(h.elements.body.value,quote);
  assert.equal(h.count.textContent,`${quote.length} / 5,000文字`);
  h.elements.body.value+='\n追加のご希望';
  h.windowHandlers.pageshow();
  assert.equal(h.count.textContent,`${h.elements.body.value.length} / 5,000文字`);
  const restored=contactHarness({kind:'登壇のご依頼',search:'?type=pr'});
  assert.equal(restored.elements.kind.value,'登壇のご依頼');
  assert.match(restored.hint.textContent,/イベント名/);
});

test('whitespace-only required text uses native validity and clears when edited',async()=>{
  const h=contactHarness();h.elements.body.value='　 \n';
  await h.submit();
  assert.equal(h.result().requests,0);
  assert.match(h.elements.body.customError,/ご相談内容/);
  h.elements.body.value='ご相談';h.handlers.input({target:h.elements.body});
  assert.equal(h.elements.body.customError,'');
  await h.submit();assert.equal(h.result().requests,1);
});

test('pending inquiries cannot be sent twice and failed requests retain all input',async()=>{
  let resolve;
  const h=contactHarness({request:()=>new Promise(r=>{resolve=r;})});
  const text=h.elements.body.value,first=h.submit();
  assert.equal(h.button.disabled,true);
  assert.equal(h.attrs['aria-busy'],'true');
  assert.equal(h.button.textContent,'送信中…');
  await h.submit();assert.equal(h.result().requests,1);
  resolve({ok:false,json:async()=>({error:'メールアドレスの形式を確認してください。'})});await first;
  assert.deepEqual(h.result(),{requests:1,resets:0,successEvents:0});
  assert.equal(h.elements.body.value,text);
  assert.equal(h.button.disabled,false);
  assert.equal(h.status.focused,true);
  assert.match(h.status.textContent,/メールアドレスの形式/);
  const disconnected=contactHarness({request:async()=>{throw new Error('offline');}});
  await disconnected.submit();
  assert.equal(disconnected.result().resets,0);
  assert.equal(disconnected.elements.email.value,'test@example.com');
  assert.equal(disconnected.button.disabled,false);
  assert.equal(disconnected.attrs['aria-busy'],undefined);
});

test('success clears sent fields while preserving only fields edited during the request',async()=>{
  let resolve;
  const h=contactHarness({handoffText:'見積もりを入力しました。',request:()=>new Promise(r=>{resolve=r;})});
  const pending=h.submit();
  assert.equal(h.elements.name.value,'テスト担当');
  h.elements.body.value+='\n送信中の追記';
  h.elements.kind.value='登壇のご依頼';
  resolve({ok:true,json:async()=>({ok:true})});await pending;
  assert.equal(h.result().resets,0);
  assert.match(h.elements.body.value,/送信中の追記/);
  for(const key of ['name','org','email'])assert.equal(h.elements[key].value,'');
  assert.equal(h.elements.kind.value,'登壇のご依頼');
  assert.equal(h.count.textContent,`${h.elements.body.value.length} / 5,000文字`);
  assert.equal(h.handoffStatus.textContent,'');
  assert.match(h.status.textContent,/未送信/);
  assert.match(h.hint.textContent,/イベント名/);
});

test('application errors and unreadable responses keep every field and the quote notice',async()=>{
  for(const request of [async()=>({ok:true,json:async()=>({ok:false,error:'確認できませんでした。'})}),async()=>({ok:true,json:async()=>{throw new Error('invalid json');}})]){
    const h=contactHarness({handoffText:'見積もりを入力しました。',request});
    h.elements.org.value='テスト会社';
    const before=Object.fromEntries(Object.entries(h.elements).map(([key,field])=>[key,field.value]));
    await h.submit();
    assert.deepEqual(Object.fromEntries(Object.entries(h.elements).map(([key,field])=>[key,field.value])),before);
    assert.equal(h.handoffStatus.textContent,'見積もりを入力しました。');
    assert.equal(h.result().successEvents,0);
    assert.equal(h.status.className,'form-status ng');
    assert.equal(h.button.disabled,false);
  }
});

test('background motion follows visibility and reduced-motion preferences without a manual control',()=>{
  const source=readFileSync(new URL('./home-3d/diorama/video-hero.js',import.meta.url),'utf8');
  const handlers={},videoHandlers={};let intersection,preferenceChange;
  const preference={matches:false,addEventListener:(_,fn)=>{preferenceChange=fn;}};
  const video={dataset:{sets:JSON.stringify({webm:'scene.webm',hevc:'scene.mp4',poster:'scene.webp',w:100,h:80}),track:'track.json'},paused:true,append(){},addEventListener:(name,fn)=>{videoHandlers[name]=fn;},play(){this.paused=false;return Promise.resolve();},pause(){this.paused=true;},load(){}};
  const host={querySelector:s=>({'#scene':video,'.world':{style:{setProperty(){}}},'.monitor-link':{}})[s],classList:{add(){}}};
  const document={hidden:false,querySelector:()=>host,createElement:()=>({}),addEventListener:(name,fn)=>{handlers[name]=fn;}};
  vm.runInNewContext(source,{document,navigator:{userAgent:'Chrome'},matchMedia:()=>preference,IntersectionObserver:class{constructor(fn){intersection=fn;}observe(){}},fetch:()=>new Promise(()=>{}),requestAnimationFrame:()=>1});
  assert.equal(video.paused,false);
  intersection([{isIntersecting:false}]);assert.equal(video.paused,true);
  preference.matches=true;preferenceChange();assert.equal(video.paused,true);
  preference.matches=false;preferenceChange();assert.equal(video.paused,true);
  preference.matches=true;preferenceChange();assert.equal(video.paused,true);
  intersection([{isIntersecting:true}]);assert.equal(video.paused,true);
  preference.matches=false;preferenceChange();assert.equal(video.paused,false);
  document.hidden=true;handlers.visibilitychange();assert.equal(video.paused,true);
  intersection([{isIntersecting:false}]);intersection([{isIntersecting:true}]);assert.equal(video.paused,true);
  document.hidden=false;handlers.visibilitychange();assert.equal(video.paused,false);
});
