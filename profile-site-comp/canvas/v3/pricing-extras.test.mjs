// Preserve regression coverage for the published range-price snapshot.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote,extrasPresentation} from './pricing-model.mjs';
const data=JSON.parse(readFileSync(new URL('./pricing-rates/17268bfca1d6.json',import.meta.url)));
const base={media:['main'],items:['materials','thumbnail'],revisions:2,custom:[]};

test('each consultation request stays outside the priced subtotal and is identified explicitly',()=>{
  for(const custom of [...data.custom.map(item=>[item.id]),data.custom.map(item=>item.id)]) {
    const state={...base,custom},view=extrasPresentation(data,state),result=quote(data,state);
    assert.equal(view.baselineText,'45,300円〜53,000円');
    assert.equal(view.totalText,'45,300円〜53,000円');
    assert.equal(view.totalLabel,'現在の小計（税込）');
    assert.deepEqual(view.consultations.map(item=>item.id),custom);
    assert.equal(result.quotedTotal,null);
    assert.match(view.note,/この小計に含みません/);
  }
});
test('main-video revision effects agree with the existing inclusive-tax calculation',()=>{
  for(const [revisions,fee,total] of [[0,'2回まで料金内',45300],[1,'2回まで料金内',45300],[2,'2回まで料金内',45300],[3,'＋5,500円（1回分・税込）',50800],[4,'＋11,000円（2回分・税込）',56300]]) {
    const state={...base,revisions,custom:['reuse']},view=extrasPresentation(data,state),result=quote(data,state);
    assert.equal(result.totalMin,total);
    assert.equal(view.baselineText,'45,300円〜53,000円');
    assert.equal(view.totalText,result.totalMin.toLocaleString('ja-JP')+'円〜'+result.totalMax.toLocaleString('ja-JP')+'円');
    assert.equal(view.revisionEffects[0].effect,fee);
    assert.deepEqual(view.consultations.map(item=>item.id),['reuse']);
  }
});
test('unpriced short and X revisions stay pending and invalid inputs do not show a total',()=>{
  for(const media of [['short'],['x'],['short','x'],['main','short','x']]) {
    const state={...base,media,revisions:3,custom:['period']},view=extrasPresentation(data,state);
    assert.match(view.baselineLabel,/小計/);
    for(const item of view.revisionEffects.filter(item=>item.id!=='main'))assert.equal(item.effect,'料金・無料回数は要相談');
    if(!media.includes('main')) {
      assert.equal(view.baselineText,'要相談');assert.equal(view.totalText,'要相談');
      assert.ok(!JSON.stringify(view).includes('0円'));
    }
  }
  assert.equal(extrasPresentation(data,{...base,media:[]}).status,'empty');
  for(const revisions of ['',-1,1.5]){
    const view=extrasPresentation(data,{...base,revisions});
    assert.equal(view.status,'invalid');assert.equal(view.totalText,undefined);
  }
});
