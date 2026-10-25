import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote,summary,quotePresentation,comparisonQuotes,alternativeQuotes,estimateUrl,stateFromUrl,loadSharedRates} from './pricing-model.mjs';
const data={...JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url))),rateVersion:'abcdef123456'};
const previous=JSON.parse(readFileSync(new URL('./pricing-rates/17268bfca1d6.json',import.meta.url)));

test('approved fixed work uses the previous upper amounts and preserves tax treatment and pending media conditions',()=>{
  for(const line of data.checklistItems) {
    const old=previous.checklistItems.find(item=>item.id===line.id);
    assert.equal(line.min,old.max);assert.equal(line.max,old.max);
    assert.equal(line.taxInclusive,old.taxInclusive);assert.equal(line.fixed,old.fixed);
  }
  assert.equal(data.rateMode,'fixed');assert.equal(data.taxRate,previous.taxRate);
  assert.equal(data.revisionFee,previous.revisionFee);
  assert.deepEqual(data.mediaRates,previous.mediaRates);
  for(const row of comparisonQuotes(data)) {
    const main=row.state.media.includes('main'),bundle=row.state.media.length===3;
    const expected=main?(bundle?58500:53000):null;
    assert.deepEqual([row.result.totalMin,row.result.totalMax],[expected,expected]);
    assert.ok(!/[〜～]/.test(row.view.totalText));
    if(row.state.media.join(',')==='main')assert.equal(row.result.quotedTotal,53000);
    else {assert.ok(row.result.pending.length);assert.equal(row.result.quotedTotal,null);}
    const state={...row.state,revisions:3,notes:'準備物の分担を相談したい'};
    const result=quote(data,state),view=quotePresentation(data,state,result);
    assert.equal(result.totalMin,expected==null?null:expected+5500);
    assert.equal(result.totalMax,result.totalMin);
    assert.ok(summary(data,state).includes(view.totalText));
    assert.ok(summary(data,state).includes(state.notes));
    assert.deepEqual(quote(data,stateFromUrl(data,estimateUrl(data,state))),result);
    for(const alternative of alternativeQuotes(data,state))assert.deepEqual(alternative.result,quote(data,alternative.state));
  }
  for(const [items,total] of [[[],37000],[['thumbnail'],42000],[['materials'],48000],[['materials','thumbnail'],53000]]) {
    const result=quote(data,{media:['main'],items});
    assert.deepEqual([result.totalMin,result.totalMax],[total,total]);
    assert.equal(result.min+result.taxMin,total);
  }
});

test('versioned and unversioned historical links preserve their original ranges after fixed pricing is adopted',async()=>{
  for(const suffix of ['?items=materials,thumbnail','?items=materials,thumbnail&v=17268bfca1d6','?items=materials,thumbnail&v=17268bfca1d6&media=main']) {
    const url='https://studio.msyn.me/pricing/'+suffix;
    const restored=await loadSharedRates(data,url,async version=>{assert.equal(version,previous.rateVersion);return previous;});
    const result=quote(restored,stateFromUrl(restored,url));
    assert.deepEqual([result.totalMin,result.totalMax],[45300,53000]);
    assert.equal(new URL(estimateUrl(restored,stateFromUrl(restored,url))).searchParams.get('v'),previous.rateVersion);
  }
  for(const suffix of ['', '?media=main&items=materials,thumbnail','?media=main&items=materials,thumbnail&v=abcdef123456']) {
    const url='https://studio.msyn.me/pricing/'+suffix;
    const restored=await loadSharedRates(data,url,async()=>{throw new Error('A new quote must use current data');});
    assert.equal(restored,data);
  }
});

test('approved fixed main work and private reference conditions remain consistent without publishing private prices',{skip:!process.env.PRICING_PRIVATE_FIXTURE},()=>{
  const fixture=JSON.parse(readFileSync(process.env.PRICING_PRIVATE_FIXTURE));
  const reference=structuredClone(data);Object.assign(reference.mediaRates,fixture.overrides);
  for(const [media,min,max] of fixture.expected) {
    const result=quote(reference,{media,items:['materials','thumbnail']});
    assert.deepEqual([result.totalMin,result.totalMax,result.pending],[media.includes('main')?max:min,max,[]]);
    assert.ok(result.lines.filter(line=>line.id==='research').length<=1);
    assert.ok(result.lines.filter(line=>line.id==='shooting').length<=1);
  }
});
