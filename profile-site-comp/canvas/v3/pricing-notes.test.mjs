// Preserve regression coverage for the published range-price snapshot.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote,quotePresentation,extrasPresentation,summary,estimateUrl,stateFromUrl,normalizeNotes} from './pricing-model.mjs';
const data={...JSON.parse(readFileSync(new URL('./pricing-rates/17268bfca1d6.json',import.meta.url))),rateVersion:'17268bfca1d6'};
const notes='準備物や作業の分担を相談したい\n目安より大幅に長い動画を依頼したい';
const base={media:['main'],items:['materials','thumbnail'],revisions:3,custom:[]};

test('free-form requests stay pending without changing work prices, tax, or revision charges in all seven offers',()=>{
  for(const media of [['x'],['short'],['short','x'],['main'],['main','x'],['main','short'],['main','short','x']]) {
    const state={...base,media,notes},result=quote(data,state),before=quote(data,{...state,notes:''});
    for(const key of ['lines','totalMin','totalMax','min','max','taxMin','taxMax','extra'])assert.deepEqual(result[key],before[key],key);
    assert.equal(result.quotedTotal,null);
    assert.equal(result.status,'custom');
    assert.equal(result.pending.find(item=>item.id==='notes').label,'追加のご希望：'+notes);
    assert.ok(summary(data,state).includes(notes));
    assert.ok(summary(data,state).includes('要相談の項目を含みません'));
    assert.equal(quotePresentation(data,state).totalText,quotePresentation(data,{...state,notes:''}).totalText);
    const extras=extrasPresentation(data,state);
    assert.equal(extras.baselineText,extrasPresentation(data,{...state,notes:''}).baselineText);
    assert.ok(extras.consultations.some(item=>item.label.includes(notes)));
  }
});

test('sharing restores multiline text and old custom requests without interpreting amounts or markup',()=>{
  const text=notes+'\n& <確認> ? # notes=別の内容 total=1';
  const state={...base,custom:['reuse'],notes:text};
  const url=estimateUrl(data,state);
  assert.equal(new URL(url).searchParams.get('notes'),text);
  const restored=stateFromUrl(data,url);
  assert.equal(restored.notes,text);
  assert.deepEqual(restored.custom,['reuse']);
  assert.deepEqual(quote(data,restored),quote(data,state));
  assert.equal(quote(data,stateFromUrl(data,url+'&price=1&total=1')).totalMin,50800);
  const old=stateFromUrl(data,'https://studio.msyn.me/pricing/?items=materials,thumbnail&v=17268bfca1d6&custom=reuse');
  assert.equal(old.media,undefined);
  assert.deepEqual(old.custom,['reuse']);
  assert.equal(old.notes,undefined);
  assert.equal(quote(data,old).totalMin,45300);
});

test('empty requests preserve existing quotes and URLs; text has a consistent length and newline limit',()=>{
  assert.deepEqual(quote(data,{...base,notes:' \r\n\t '}),quote(data,base));
  assert.equal(estimateUrl(data,{...base,notes:'   '}),estimateUrl(data,base));
  assert.equal(normalizeNotes('  分担\r\n\u0000長尺\r希望  '),'分担\n長尺\n希望');
  assert.equal(normalizeNotes('あ'.repeat(1200)).length,1000);
  assert.equal(stateFromUrl(data,estimateUrl(data,{...base,notes:'あ'.repeat(1200)})).notes.length,1000);
  assert.equal(normalizeNotes({notes}), '');
  assert.equal(quote(data,{...base,media:[],notes}).status,'empty');
  assert.equal(quote(data,{...base,revisions:-1,notes}).status,'invalid');
});
