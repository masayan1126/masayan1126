import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {alternativeQuotes,comparisonQuotes,quote,summary,estimateUrl,stateFromUrl} from './pricing-model.mjs';

const data={...JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url))),rateVersion:'123456abcdef'};

test('all seven selections generate six alternatives with preserved answers, amounts and restoring URLs',()=>{
  for(const selection of comparisonQuotes(data)) {
    const state={...selection.state,items:['thumbnail'],notes:'準備物の分担を相談したい\n二次利用も希望',revisions:3,custom:[]};
    const before=structuredClone(state),rows=alternativeQuotes(data,state);
    assert.equal(rows.length,6);
    assert.equal(new Set(rows.map(row=>row.state.media.join(','))).size,6);
    for(const row of rows) {
      assert.notDeepEqual(new Set(row.state.media),new Set(state.media));
      assert.deepEqual(row.state.items,state.items);
      assert.equal(row.state.notes,state.notes);
      assert.equal(row.state.revisions,3);
      assert.deepEqual(row.result,quote(data,row.state));
      assert.deepEqual(quote(data,stateFromUrl(data,estimateUrl(data,row.state))),row.result);
      const text=summary(data,row.state,row.result);
      assert.ok(text.includes(row.view.totalText));
      assert.ok(text.includes(state.notes));
      assert.ok(row.result.lines.filter(line=>line.id==='research').length<=1);
      assert.ok(row.result.lines.filter(line=>line.id==='shooting').length<=1);
      assert.equal(row.knownDelta,null);
    }
    assert.deepEqual(state,before);
    for(let i=1;i<rows.length;i++) {
      assert.ok((rows[i-1].result.totalMin??Infinity)<=(rows[i].result.totalMin??Infinity));
      if(rows[i-1].result.totalMin===rows[i].result.totalMin)assert.ok(rows[i-1].state.media.length<=rows[i].state.media.length);
    }
  }
});

test('unpriced X announcements and standalone offers remain pending rather than being advertised as free',()=>{
  const rows=alternativeQuotes(data,{media:['main'],items:['materials','thumbnail'],revisions:2});
  const x=rows.find(row=>row.state.media.join(',')==='main,x');
  assert.equal(x.label,'公開動画をXでも告知する場合');
  assert.equal(x.knownDelta,null);
  assert.ok(x.result.pending.some(item=>item.id==='videoAnnouncement'));
  assert.equal(x.result.lines.find(line=>line.id==='videoAnnouncement').min,null);
  for(const media of ['x','short','short,x']) {
    const row=rows.find(row=>row.state.media.join(',')===media);
    assert.equal(row.result.totalMin,null);
    assert.equal(row.view.totalText,'要相談');
    assert.ok(!row.result.lines.some(line=>['research','shooting','editing'].includes(line.id)));
  }
  assert.deepEqual(alternativeQuotes(data,{media:[]}),[]);
  assert.deepEqual(alternativeQuotes(data,{media:['main'],revisions:-1}),[]);
  assert.deepEqual(alternativeQuotes(data,{items:[]}),[]);
});

test('alternative quotes calculate from the supplied historical rate snapshot',()=>{
  for(const filename of readdirSync(new URL('./pricing-rates/',import.meta.url))) {
    const archived=JSON.parse(readFileSync(new URL('./pricing-rates/'+filename,import.meta.url)));
    if(!archived.mediaSchema)continue;
    for(const row of alternativeQuotes(archived,{media:['main'],items:[],revisions:2})) {
      assert.deepEqual(row.result,quote(archived,row.state));
      assert.equal(new URL(estimateUrl(archived,row.state)).searchParams.get('v'),archived.rateVersion);
    }
  }
});
