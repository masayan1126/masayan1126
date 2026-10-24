// Run with PRICING_PRIVATE_FIXTURE pointing at a local, ignored offer fixture.
// Individual-contract amounts deliberately do not appear in tracked test data.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote,summary,estimateUrl,stateFromUrl,comparisonQuotes} from './pricing-model.mjs';
test('private reference conditions reproduce all seven offers without double tax or shared-work charges',{skip:!process.env.PRICING_PRIVATE_FIXTURE},()=>{
  const fixture=JSON.parse(readFileSync(process.env.PRICING_PRIVATE_FIXTURE));
  const data=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
  data.rateVersion='123456abcdef';Object.assign(data.mediaRates,fixture.overrides);
  for(const [media,min,max] of fixture.expected){
    const state={media,items:['materials','thumbnail']},r=quote(data,state);
    assert.deepEqual([r.totalMin,r.totalMax,r.pending],[min,max,[]],media.join(','));
    assert.deepEqual(quote(data,stateFromUrl(data,estimateUrl(data,state))),r);
    assert.ok(summary(data,state).includes(min.toLocaleString('ja-JP')+'円'));
    assert.ok(r.lines.filter(line=>line.id==='research').length<=1);
    assert.ok(r.lines.filter(line=>line.id==='shooting').length<=1);
  }
  assert.deepEqual(comparisonQuotes(data).map(row=>row.state.media),fixture.expected.map(([media])=>media));
});
