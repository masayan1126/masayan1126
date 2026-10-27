import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const contactHtml=execFileSync('python3',['-c',"import runpy,sys;print(runpy.run_path(sys.argv[1])['render_contact_form']())",fileURLToPath(new URL('./build_sections.py',import.meta.url))],{encoding:'utf8'});
const contactScript=[...contactHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes("const f=document.getElementById('inquiry-form')"));
function contactHarness({valid=true,search='',kind='PR・タイアップのご依頼',request=async()=>({ok:true,json:async()=>({ok:true})})}={}) {
  const handlers={},windowHandlers={},documentHandlers={},attrs={};
  const field=value=>({value,customError:'',setCustomValidity(message){this.customError=message;}});
  const elements={kind:field(kind),name:field('テスト担当'),org:field(''),email:field('test@example.com'),body:field('ご相談の本文'),website:field('')};
  const status={focus(){this.focused=true;}},hint={},count={};
  const button={disabled:false,innerHTML:'相談内容を送信する<span>→</span>',setAttribute:(k,v)=>{attrs[k]=v;},removeAttribute:k=>{delete attrs[k];}};
  let requests=0,resets=0,successEvents=0;
  const form={elements,querySelector:s=>s==='.form-status'?status:button,reportValidity:()=>valid&&!Object.values(elements).some(f=>f.customError),reset:()=>{resets++;for(const f of Object.values(elements))f.value='';},addEventListener:(name,fn)=>{handlers[name]=fn;}};
  const nodes={'inquiry-form':form,'inquiry-body-hint':hint,'inquiry-body-count':count};
  vm.runInNewContext(contactScript,{document:{getElementById:id=>nodes[id],addEventListener:(k,fn)=>{documentHandlers[k]=fn;},dispatchEvent:e=>{if(e.type==='site:inquiry-sent')successEvents++;}},window:{addEventListener:(k,fn)=>{windowHandlers[k]=fn;}},CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},location:{search},URLSearchParams,FormData:class {},fetch:async()=>{requests++;return request();}});
  return {elements,status,button,hint,count,attrs,handlers,windowHandlers,documentHandlers,submit:()=>handlers.submit({preventDefault(){}}),result:()=>({requests,resets,successEvents})};
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
  assert.match(valid.button.innerHTML,/相談内容を送信する/);
  assert.match(valid.status.textContent,/2営業日/);
  assert.equal(valid.status.focused,true);
  assert.equal(valid.count.textContent,'0 / 5,000文字');
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

test('edits made while sending remain unsent and are not erased on success',async()=>{
  let resolve;
  const h=contactHarness({request:()=>new Promise(r=>{resolve=r;})});
  const pending=h.submit();
  h.elements.body.value+='\n送信中の追記';
  h.elements.kind.value='登壇のご依頼';
  resolve({ok:true,json:async()=>({ok:true})});await pending;
  assert.equal(h.result().resets,0);
  assert.match(h.elements.body.value,/送信中の追記/);
  assert.match(h.status.textContent,/未送信/);
  assert.match(h.hint.textContent,/イベント名/);
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
