import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote,quotePresentation,summary,estimateUrl,stateFromUrl,loadSharedRates,alternativeQuotes,comparisonQuotes,extrasPresentation,defaultItems,mediaRevisionDetails,taxIncluded} from './pricing-model.mjs';
const data={...JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url))),rateVersion:'123456abcdef'};
const items=defaultItems(data);

test('each selected medium includes two revisions and bills only its own additional rounds',()=>{
  const gross={main:5500,short:3300,x:1000};
  for(const [id,config] of Object.entries(data.mediaRevisionRates)) {
    assert.equal(config.included,2);
    assert.equal(taxIncluded(config.fee.min,data.taxRate,config.fee.taxInclusive),gross[id]);
  }
  for(const combination of comparisonQuotes(data))for(const counts of [{main:0,short:1,x:2},{main:2,short:2,x:2},{main:3,short:4,x:5},{main:5,short:3,x:0}]) {
    const state={...combination.state,revisionCounts:counts};
    const baseline=quote(data,{...state,revisionCounts:{main:2,short:2,x:2}}),result=quote(data,state);
    const additional=state.media.reduce((sum,id)=>sum+Math.max(0,counts[id]-2)*gross[id],0);
    assert.equal(result.totalMin,baseline.totalMin==null?(additional||null):baseline.totalMin+additional);
    assert.equal(result.pending.some(row=>['shortRevisions','xRevisions'].includes(row.id)),false);
    for(const row of result.revisionDetails)assert.equal(row.count,counts[row.id]);
    if(result.totalMin!=null)assert.equal(result.min+result.taxMin,result.totalMin);
    for(const id of ['main','short','x'])if(!state.media.includes(id))assert.ok(!result.lines.some(row=>row.id===(id==='main'?'revisions':id+'Revisions')));
  }
});

test('independent counts, fees, summaries, alternatives and shared URLs agree without URL-supplied prices',()=>{
  const state={media:['main','short','x'],items,revisionCounts:{main:3,short:4,x:5},notes:''};
  const result=quote(data,state),url=estimateUrl(data,state),restored=stateFromUrl(data,url+'&shortRevisionFee=0&xRevisionFee=0&revisionFee=0');
  assert.equal(result.totalMin,69600);
  assert.deepEqual(quote(data,restored),result);
  assert.deepEqual(restored.revisionCounts,{main:'3',short:'4',x:'5'});
  for(const note of quotePresentation(data,state).revisionNotes)assert.ok(summary(data,state).includes(note));
  const extras=extrasPresentation(data,state);
  assert.equal(extras.baselineText,'54,500円');assert.equal(extras.totalText,'69,600円');
  assert.deepEqual(extras.revisionEffects.map(row=>row.effect),['＋5,500円（1回分・税込）','＋6,600円（2回分・税込）','＋3,000円（3回分・税込）']);
  for(const row of alternativeQuotes(data,state)) {
    assert.deepEqual(row.state.revisionCounts,state.revisionCounts);
    assert.deepEqual(quote(data,stateFromUrl(data,estimateUrl(data,row.state))),row.result);
  }
});

test('invalid counts are rejected per selected medium and unknown fees never become zero',()=>{
  for(const id of ['main','short','x'])for(const invalid of ['',-1,1.5,'1e3','abc',Number.MAX_SAFE_INTEGER+1]) {
    const result=quote(data,{media:[id],items,revisionCounts:{[id]:invalid}});
    assert.equal(result.status,'invalid');assert.equal(result.invalidRevisionMedia,id);
  }
  assert.equal(quote(data,{media:['short'],revisionCounts:{main:-1,short:2,x:'bad'}}).status,'estimate');
  const alternatives=alternativeQuotes(data,{media:['short'],revisionCounts:{main:-1,short:2,x:'bad'}});
  assert.equal(alternatives.length,6);
  for(const row of alternatives) {
    assert.notEqual(row.result.status,'invalid');
    assert.equal(row.state.revisionCounts.main,2);assert.equal(row.state.revisionCounts.x,2);
    assert.ok(row.knownDelta==null||Number.isFinite(row.knownDelta));
  }
  const unknown=structuredClone(data);unknown.mediaRevisionRates.short.fee.min=null;unknown.mediaRevisionRates.short.fee.max=null;
  const state={media:['short'],revisionCounts:{short:3}},result=quote(unknown,state);
  assert.equal(result.totalMin,10000);assert.equal(result.quotedTotal,null);
  assert.ok(result.pending.some(row=>row.id==='shortRevisions'));
  assert.ok(mediaRevisionDetails(unknown,state)[0].condition.includes('個別にお見積もり'));
});

test('published URLs retain the global count and pending conditions of their own rate version',async()=>{
  const old=JSON.parse(readFileSync(new URL('./pricing-rates/2707d85bdbdd.json',import.meta.url)));
  const state={media:['main','short','x'],items,revisions:3},url=estimateUrl(old,state);
  const loaded=await loadSharedRates(data,url,async()=>old),restored=stateFromUrl(loaded,url+'&shortRevisions=9&xRevisions=9');
  assert.equal(quote(loaded,restored).totalMin,60000);
  assert.equal(restored.revisionCounts,undefined);
  assert.ok(quote(loaded,restored).pending.some(row=>row.id==='shortRevisions'));
  const migrated=stateFromUrl(data,estimateUrl(data,state));
  assert.deepEqual(migrated.revisionCounts,{main:'3',short:'3',x:'3'});
  assert.equal(quote(data,migrated).totalMin,64300);
});
