import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {quote,quotePresentation,summary,estimateUrl,stateFromUrl,loadSharedRates,comparisonQuotes,alternativeQuotes,defaultItems} from './pricing-model.mjs';
const data={...JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url))),rateVersion:'123456abcdef'};
const items=defaultItems(data);

test('repeat PR requests may omit research while keeping every other work rate and tax rule',()=>{
  const previous=JSON.parse(readFileSync(new URL('./pricing-rates/04da1a7ceffd.json',import.meta.url)));
  assert.equal(data.mediaSchema,2);
  for(const item of data.checklistItems) {
    const old=previous.checklistItems.find(row=>row.id===item.id);
    assert.deepEqual([item.min,item.max,item.taxInclusive],[old.min,old.max,old.taxInclusive]);
  }
  assert.equal(data.checklistItems.find(row=>row.id==='research').fixed,false);
  assert.equal(data.checklistItems.find(row=>row.id==='materials').label,'動画の企画・台本作成');
  assert.equal(quote(data,{media:['main'],items}).totalMin,53000);
  const repeat=quote(data,{media:['main'],items:['materials','thumbnail']});
  assert.equal(repeat.totalMin,44200);
  assert.ok(!repeat.lines.some(row=>row.id==='research'));
  assert.ok(repeat.preparation.some(text=>text.includes('前回のPR動画URL')));
  assert.ok(repeat.scope.some(text=>text.includes('着手日・キャンセル条件')));
  assert.equal(quote(data,{media:['main'],items:[]}).totalMin,28200);
});

test('clip shorts cost zero, dedicated shorts cost 10,000 inclusive, and X is always a separate line',()=>{
  for(const x of [false,true])for(const mode of ['clip','dedicated']) {
    const state={media:['main','short',...(x?['x']:[])],items,shortMode:mode};
    const result=quote(data,state),short=result.lines.find(row=>row.id===(mode==='clip'?'additionalShortClip':'additionalShortDedicated'));
    assert.equal(short.min,mode==='clip'?0:10000);
    assert.equal(short.taxInclusive,true);
    assert.equal(result.totalMin,(mode==='clip'?53000:63000)+(x?1500:0));
    assert.equal(result.totalMin,result.min+result.taxMin);
    for(const id of ['research','shooting','editing'])assert.equal(result.lines.filter(row=>row.id===id).length,1);
    assert.ok(!result.lines.some(row=>['xPr','shorts','additionalShort'].includes(row.id)));
    assert.equal(result.lines.some(row=>row.id==='videoAnnouncement'),x);
    assert.ok(!result.pending.some(row=>row.id==='shortCount'));
  }
  assert.equal(quote(data,{media:['short'],items,shortMode:'clip'}).totalMin,10000);
});

test('reporting is removed and cannot be reintroduced through a state or URL flag',()=>{
  const base={media:['main'],items};
  const without=quote(data,base),withReport=quote(data,{...base,report:true});
  assert.ok(!without.lines.some(row=>row.id==='report'));
  assert.equal(data.mediaRates.report,undefined);
  assert.deepEqual(withReport,without);
  assert.ok(!JSON.stringify(without).includes('レポート'));
  const url=estimateUrl(data,{...base,report:true});
  assert.equal(new URL(url).searchParams.has('report'),false);
  assert.equal(stateFromUrl(data,url+'&report=1').report,undefined);
  const xOnly=quote(data,{media:['x'],report:true,items});
  assert.ok(!xOnly.lines.some(row=>['report','research','additionalShortClip'].includes(row.id)));
});

test('all options, six alternatives, totals and inquiry details survive shared links without URL-supplied prices',()=>{
  for(const row of comparisonQuotes(data))for(let mask=0;mask<8;mask++)for(const shortMode of ['clip','dedicated'])for(const report of [false,true]) {
    const state={media:row.state.media,items:items.filter((_,i)=>mask&(1<<i)),shortMode,report,revisions:3,notes:'前回と同じサービスです。\n変更点を紹介したい'};
    const result=quote(data,state),view=quotePresentation(data,state,result);
    const url=estimateUrl(data,state);
    const restored=stateFromUrl(data,url+'&total=1&taxRate=0&additionalShortDedicated=0&reportFee=0');
    assert.deepEqual(quote(data,restored),result);
    assert.equal(restored.shortMode,shortMode);assert.equal(restored.report,undefined);
    assert.deepEqual(restored.items,state.items);
    assert.ok(summary(data,state,result).includes(view.totalText));
    const alternatives=alternativeQuotes(data,state);
    assert.equal(alternatives.length,6);
    for(const alternative of alternatives) {
      assert.equal(alternative.state.shortMode,shortMode);assert.equal(alternative.state.report,report);
      assert.deepEqual(alternative.state.items,state.items);
      assert.deepEqual(quote(data,stateFromUrl(data,estimateUrl(data,alternative.state))),alternative.result);
    }
  }
  const invalid=stateFromUrl(data,'https://studio.msyn.me/pricing/?media=main,short&shortMode=free&report=yes');
  assert.equal(invalid.shortMode,'clip');assert.equal(invalid.report,undefined);
  assert.equal(quote(data,{media:[]}).status,'empty');
});

test('all archived rules remain intact, including bundled shorts, mandatory research and included reporting',async()=>{
  for(const filename of readdirSync(new URL('./pricing-rates/',import.meta.url))) {
    const archived=JSON.parse(readFileSync(new URL('./pricing-rates/'+filename,import.meta.url)));
    if(archived.mediaSchema>=2)continue;
    const before=structuredClone(archived);
    const state={...(archived.mediaSchema?{media:['main','short','x']}:{}),items:['materials','thumbnail']};
    const url=estimateUrl(archived,state);
    const restored=await loadSharedRates(data,url,async()=>archived);
    assert.deepEqual(quote(restored,stateFromUrl(restored,url)),quote(archived,stateFromUrl(archived,url)));
    assert.deepEqual(restored.checklistItems,archived.checklistItems);
    assert.deepEqual(archived,before);
  }
});
