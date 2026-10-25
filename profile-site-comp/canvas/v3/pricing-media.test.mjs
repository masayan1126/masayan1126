// Preserve regression coverage for the published range-price snapshot.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote,summary,estimateUrl,stateFromUrl,loadSharedRates,comparisonQuotes,amountText,taxIncluded,quotePresentation} from './pricing-model.mjs';
const data={...JSON.parse(readFileSync(new URL('./pricing-rates/17268bfca1d6.json',import.meta.url))),rateVersion:'123456abcdef'};
const combinations=[['x'],['short'],['short','x'],['main'],['main','x'],['main','short'],['main','short','x']];
test('public offers preserve main work and keep unapproved amounts and conditions pending',()=>{
  for (const media of combinations) {
    const state={media,items:['materials','thumbnail']},r=quote(data,state);
    assert.equal(r.media.includes('main'),media.includes('main'));
    for (const id of ['research','materials','shooting','editing','thumbnail','publishing']) assert.equal(r.lines.some(line=>line.id===id),media.includes('main'));
    if (media.length===1 && media[0]==='main') assert.deepEqual([r.totalMin,r.totalMax,r.status],[45300,53000,'range']);
    else {assert.equal(r.status,'custom');assert.equal(r.quotedTotal,null);assert.ok(r.pending.length);}
    if (!media.includes('main')) {assert.equal(r.totalMin,null);assert.equal(r.totalMax,null);assert.ok(!summary(data,state).includes('0円'));}
    assert.ok(!r.lines.some(line=>line.id==='xPr'&&media.length>1));
    assert.equal(r.lines.filter(line=>line.id==='videoAnnouncement').length,media.includes('x')&&media.length===2?1:0);
    if(media.includes('main')&&media.includes('short')) assert.ok(r.pending.some(item=>item.id==='shortCount'));
  }
  assert.equal(quote(data,{media:['main'],items:[]}).totalMin,31500);
});
test('new URLs restore media, optional work, revisions and custom conditions without accepting prices',()=>{
  for (const media of [[],...combinations]) for(const items of [[],['materials','thumbnail']]) {
    const state={media,items,revisions:4,custom:['reuse','period']};
    const url=estimateUrl(data,state);
    assert.deepEqual(quote(data,stateFromUrl(data,url)),quote(data,state));
    assert.equal(estimateUrl(data,stateFromUrl(data,url)),url);
    const tampered=url+'&total=1&taxRate=0&standaloneShort=1&media=x&custom=unknown';
    const restored=stateFromUrl(data,tampered);
    assert.deepEqual(quote(data,restored),quote(data,{...state,media:[...media,'x']}));
  }
  const old='https://studio.msyn.me/pricing/?items=materials,thumbnail';
  assert.deepEqual([quote(data,stateFromUrl(data,old)).totalMin,quote(data,stateFromUrl(data,old)).totalMax],[45300,53000]);
  assert.equal(quote(data,stateFromUrl(data,'https://studio.msyn.me/pricing/')).status,'empty');
  assert.equal(summary(data,{media:[]}), '');
  const legacy={items:['materials','thumbnail'],revisions:4,custom:['reuse']};
  assert.deepEqual(quote(data,stateFromUrl(data,estimateUrl(data,legacy))),quote(data,legacy));
});
test('unknown selections, stale main options and repeated media never create extra charges',()=>{
  for(const media of combinations){
    const state={media,items:['materials','thumbnail']};
    assert.deepEqual(quote(data,{...state,media:[...media,...media,'unknown'],items:[...state.items,'shorts','shooting','unknown']}),quote(data,state));
  }
  for(const revisions of ['',-1,'1.5','1e3',Number.MAX_SAFE_INTEGER])assert.equal(quote(data,{media:['x'],revisions}).status,'invalid');
  const x=quote(data,{media:['x'],revisions:4});
  assert.ok(!x.lines.some(line=>line.id==='revisions'));
  assert.ok(!x.scope.join('\n').includes('本編'));
  assert.ok(!x.preparation.includes('サムネイルの制作'));
  assert.ok(x.revisionNotes.join('\n').includes('要相談'));
});
test('new archived snapshots and every historical snapshot preserve their rules',async()=>{
  const newer={...structuredClone(data),rateVersion:'abcdef123456'};
  newer.mediaRates.standaloneShort={min:99999,max:99999};
  for(const media of combinations){
    const state={media,items:['materials','thumbnail'],revisions:3,custom:['reuse']};
    const url=estimateUrl(data,state);
    const restored=await loadSharedRates(newer,url,async()=>structuredClone(data));
    assert.deepEqual(quote(restored,stateFromUrl(restored,url)),quote(data,state));
  }
  for (const version of ['0da10cd790a7','46dd15855eab','59b492c82f8a','5bf426700870','7056daa746d4','a4a327e3b849','ae1bfffee985','bda428420609','d5e35c70d01c','e59497ebf5cc']) {
    const old=JSON.parse(readFileSync(new URL('./pricing-rates/'+version+'.json',import.meta.url)));
    const state={items:old.checklistItems.filter(item=>!item.fixed).map(item=>item.id)};
    const url=estimateUrl(old,state),restored=await loadSharedRates(data,url,async()=>old);
    assert.deepEqual(quote(restored,stateFromUrl(restored,url)),quote(restored,state));
    assert.throws(()=>stateFromUrl(restored,url+'&media=x'));
  }
});
test('screen presentation and inquiry share amounts, pending conditions, scope and responsibilities',()=>{
  for (const media of combinations) {
    const state={media,items:['materials','thumbnail'],revisions:3,custom:['reuse']};
    const r=quote(data,state),view=quotePresentation(data,state,r),body=summary(data,state,r);
    assert.ok(body.includes(view.mediaLabel));assert.ok(body.includes(view.totalLabel+'：'+view.totalText));
    for (const line of r.lines) assert.ok(body.includes(line.label+'：'+amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive))));
    for (const value of [...view.scope,...view.revisionNotes,...view.preparation]) assert.ok(body.includes(value));
    for (const item of r.pending) assert.ok(body.includes(item.label));
    assert.ok(body.includes(estimateUrl(data,state,'https://studio.msyn.me/pricing/#estimate-result')));
  }
  const sorted=comparisonQuotes(data).filter(row=>row.result.totalMin!=null);
  assert.deepEqual(sorted.map(row=>row.result.totalMin),sorted.map(row=>row.result.totalMin).sort((a,b)=>a-b));
});
