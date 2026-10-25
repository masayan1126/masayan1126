import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

test('contact form rejects invalid input before network activity and restores the button after valid submission', async()=>{
  const html=execFileSync('python3',['-c',"import runpy,sys;print(runpy.run_path(sys.argv[1])['render_contact_form']())",fileURLToPath(new URL('./build_sections.py',import.meta.url))],{encoding:'utf8'});
  const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes("const f=document.getElementById('inquiry-form')"));
  let valid=false,submit,requests=0,resets=0;
  const status={},button={disabled:false};
  let successEvents=0;
  const form={querySelector:s=>s==='.form-status'?status:button,elements:{kind:{value:'PR・タイアップのご依頼'}},reportValidity:()=>valid,reset:()=>resets++,addEventListener:(name,fn)=>{if(name==='submit')submit=fn;}};
  vm.runInNewContext(script,{document:{getElementById:()=>form,dispatchEvent:e=>{if(e.type==='site:inquiry-sent')successEvents++;}},CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},location:{search:''},URLSearchParams,FormData:class {},fetch:async()=>{requests++;return {ok:true,json:async()=>({ok:true})};}});
  await submit({preventDefault(){}});
  assert.equal(requests,0);
  assert.equal(successEvents,0);
  assert.equal(button.disabled,false);
  valid=true;
  await submit({preventDefault(){}});
  assert.equal(requests,1);
  assert.equal(resets,1);
  assert.equal(successEvents,1);
  assert.equal(button.disabled,false);
  assert.match(status.textContent,/2営業日/);
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
