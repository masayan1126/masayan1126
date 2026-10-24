import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote} from './pricing-model.mjs';
import {fixedReviewRates,relatedQuotes,reviewSummary,combinations} from './pricing-flows-model.mjs';
const source=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
const state={media:['main'],items:['materials','thumbnail'],revisions:2,custom:[],notes:''};

test('fixed-price proposals use existing upper amounts without changing published data or unknown media rates',()=>{
  const before=JSON.stringify(source),data=fixedReviewRates(source);
  assert.equal(quote(data,state).totalMin,53000);
  assert.equal(quote(data,state).totalMax,53000);
  assert.equal(quote(data,{...state,revisions:3}).totalMin,58500);
  assert.equal(quote(data,{...state,items:[]}).totalMin,37000);
  for(const line of data.checklistItems)assert.equal(line.min,line.max);
  assert.deepEqual(data.mediaRates,source.mediaRates);
  assert.equal(quote(data,{media:['x']}).totalMin,null);
  assert.equal(quote(data,{media:['short']}).totalMin,null);
  assert.equal(JSON.stringify(source),before);
  assert.equal(quote(fixedReviewRates(source,'min'),state).totalMin,45300);
  assert.throws(()=>fixedReviewRates(source,'arbitrary'));
});

test('every selection generates six distinct alternatives with shared details and no free-X assumption',()=>{
  const data=fixedReviewRates(source);
  for(const media of combinations){
    const current={...state,media,notes:'準備物の分担を相談したい',revisions:3};
    const alternatives=relatedQuotes(data,current);
    assert.equal(alternatives.length,6);
    assert.equal(new Set(alternatives.map(item=>item.state.media.join(','))).size,6);
    for(const item of alternatives){
      assert.notDeepEqual(new Set(item.state.media),new Set(media));
      assert.equal(item.state.notes,current.notes);
      assert.equal(item.state.revisions,3);
      assert.deepEqual(item.state.items,current.items);
      assert.deepEqual(item.result,quote(data,item.state));
      assert.equal(item.knownDelta,null);
      assert.ok(!/\d円[〜～]/.test(item.view.totalText));
    }
  }
  const extraX=relatedQuotes(data,state).find(item=>item.state.media.join(',')==='main,x');
  assert.match(extraX.label,/動画をXでも告知/);
  assert.ok(extraX.result.pending.some(item=>item.id==='videoAnnouncement'));
  assert.equal(extraX.knownDelta,null);
  assert.equal(relatedQuotes(data,{...state,media:['x','main']}).length,6);
  assert.deepEqual(relatedQuotes(data,{...state,media:[]}),[]);
});

test('prototype summaries carry fixed amounts and requests without creating a conflicting public share link',()=>{
  const data=fixedReviewRates(source);
  for(const media of combinations){
    const text=reviewSummary(data,{...state,media,notes:'掲載期間の相談'});
    assert.ok(text.includes('未承認'));
    assert.ok(text.includes('掲載期間の相談'));
    assert.ok(!text.includes('https://studio.msyn.me/pricing/'));
    assert.ok(!/\d円[〜～]/.test(text));
  }
  assert.equal(reviewSummary(data,{media:[]}), '');
});
