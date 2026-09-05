import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {quote, summary, mailto, amountText, taxIncluded, selectedFromUrl, estimateUrl, loadSharedRates} from './pricing-model.mjs';
const data=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
const source=JSON.parse(readFileSync(new URL('./pricing-proposal.json',import.meta.url)));
const optional=data.checklistItems.filter(x=>!x.fixed&&x.min!=null).map(x=>x.id);
test('source rates are preserved except the two user-specified tax-inclusive prices',()=>{
  for(const work of data.checklistItems.filter(x=>x.sourceLabel)){
    const rates=source.items.find(x=>x.label===work.sourceLabel).amounts.filter(n=>n>0);
    assert.equal(work.min,Math.min(...rates)); assert.equal(work.max,Math.max(...rates));
  }
  for(const [id,price] of [['editing',15000],['thumbnail',5000]]){
    const item=data.checklistItems.find(x=>x.id===id); assert.equal(item.min,price);assert.equal(item.max,price);assert.equal(item.taxInclusive,true);
  }
  for(const id of ['placement','script','comparison']){
    assert.ok(!data.checklistItems.some(item=>item.id===id));
    assert.ok(data.checklistGroups.every(group=>!group.items.includes(id)));
  }
  assert.deepEqual(quote(data,{items:['script','comparison','placement']}),quote(data));
});
test('shooting, editing, thumbnail and publishing are always included in the minimum',()=>{
  for(const [items,min,max] of [[[],31000,33200],[['editing'],31000,33200],[['thumbnail'],31000,33200],[['editing','thumbnail'],31000,33200]]){
    const r=quote(data,{items});assert.equal(r.totalMin,min);assert.equal(r.totalMax,max);
    assert.equal(r.min+r.taxMin,min);assert.equal(r.max+r.taxMax,max);
    assert.equal(r.quotedTotal,null);
    assert.equal(r.preparation.includes('サムネイルの制作'),false);
    assert.equal(r.preparation.includes('撮影素材の編集・完成データの提供'),false);
    assert.deepEqual(r.lines.map(x=>x.id),['shooting','editing','thumbnail','publishing']);
  }
});
test('all work sums to 58,500–77,200 including tax; third revision adds 5,500',()=>{
  const full=quote(data,{items:optional}),third=quote(data,{items:optional,revisions:3});
  assert.deepEqual([full.totalMin,full.totalMax],[58500,77200]);
  assert.deepEqual([third.totalMin,third.totalMax],[64000,82700]);
  assert.equal(third.extra,5000);assert.equal(third.lines.at(-1).label,'追加修正（1回）');
  assert.equal(third.min,58182);assert.equal(third.taxMin,5818);
});
test('all eight optional combinations stay above the minimum without double taxation',()=>{
  let count=0;
  for(let mask=0;mask<2**optional.length;mask++){
    const items=optional.filter((id,i)=>mask&(1<<i)),r=quote(data,{items});count++;
    assert.ok(r.totalMin>=31000);assert.ok(r.totalMax>=33200);
    const lines=data.checklistItems.filter(x=>x.fixed||items.includes(x.id));
    for(const edge of ['min','max']){
      const sum=lines.reduce((n,x)=>n+(x.taxInclusive?x[edge]:x[edge]+Math.round(x[edge]*.1)),0);
      assert.equal(edge==='min'?r.totalMin:r.totalMax,sum);
    }
    assert.deepEqual(quote(data,{items:[...items,...items]}),r);
    for(const id of optional.filter(x=>!items.includes(x))){
      const next=quote(data,{items:[...items,id]});assert.ok(next.totalMin>=r.totalMin);assert.ok(next.totalMax>=r.totalMax);
    }
  }
  assert.equal(count,8);
});
test('research and materials have separate prices and preparation responsibilities',()=>{
  const base=quote(data),research=quote(data,{items:['research']}),materials=quote(data,{items:['materials']});
  assert.deepEqual([research.totalMin,research.totalMax],[42000,55200]);
  assert.deepEqual([materials.totalMin,materials.totalMax],[42000,49700]);
  assert.ok(base.preparation.includes('紹介する機能・操作手順の検証結果'));
  assert.ok(!research.preparation.includes('紹介する機能・操作手順の検証結果'));
  assert.ok(research.preparation.includes('台本'));
  assert.ok(!materials.preparation.includes('台本'));
  assert.deepEqual(quote(data,{items:optional}).preparation,['検証用アカウント']);
});
test('unpriced conditions preserve a known subtotal rather than a complete quote',()=>{
  for(const custom of data.custom.map(x=>[x.id]))for(const items of [[],optional]){
    const r=quote(data,{items,custom,revisions:3});assert.equal(r.status,'custom');assert.equal(r.quotedTotal,null);assert.equal(r.pending.length,custom.length);
    assert.equal(r.totalMin,quote(data,{items,revisions:3}).totalMin);
    const text=summary(data,{items,custom,revisions:3});assert.ok(text.includes('小計'));assert.ok(text.includes('要相談の項目の金額を含みません'));assert.ok(!text.includes('概算合計：'));
  }
});
test('revision inputs reject empty, fractional, negative and unsafe values',()=>{
  for(const revisions of ['',-1,'1.5','abc',NaN,Infinity,'1e3','9007199254740991'])assert.equal(quote(data,{revisions}).status,'invalid',String(revisions));
  for(const revisions of [0,1,2,'2'])assert.equal(quote(data,{revisions}).extra,0);
  for(const revisions of [3,4,10])assert.equal(quote(data,{revisions}).extra,(revisions-2)*5000);
});
test('inquiry keeps the separate work, responsibilities and correct gross and net values',()=>{
  for(const state of [{},{items:['editing']},{items:['thumbnail']},{items:optional},{items:optional,custom:data.custom.map(x=>x.id),revisions:4}]){
    const r=quote(data,state),text=summary(data,state);
    assert.ok(r.preparation.includes('検証用アカウント'));
    assert.ok(text.includes('10〜20分程度（30分を超える場合は要相談）'));
    assert.ok(text.includes('概算料金（税込）'));assert.ok(text.includes(amountText(r.totalMin,r.totalMax)+'（税込）'));assert.ok(text.includes('税抜：'+amountText(r.min,r.max)));
    for(const removed of ['掲載費','台本の作成','他ツールとの比較検証','動画編集・サムネイル制作','説明用資料の作成','リサーチ・事前検証'])assert.ok(!text.includes(removed));
    if(state.items?.includes('materials'))assert.ok(text.includes('動画で使用する資料の作成'));
    if(state.items?.includes('editing'))assert.ok(text.includes('動画編集：15,000円'));
    if(state.items?.includes('thumbnail'))assert.ok(text.includes('サムネイル制作：5,000円'));
    if(state.revisions===4)assert.ok(text.includes('追加修正（2回）：11,000円'));
    for(const line of r.lines)assert.ok(text.includes(line.label+'：'+amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive))));
    for(const item of r.pending)assert.ok(text.includes(item.label));
    for(const item of r.preparation)assert.ok(text.includes(item));
    const link=new URL(mailto(text));assert.equal(link.pathname,'contact@msyn.me');assert.equal(link.searchParams.get('body'),text);
  }
  assert.equal(quote(data,{}).totalMin,31000);assert.equal(summary(data,{revisions:-1}),'');
});

const versionedData = {...data,rateVersion:'123456abcdef'};
test('shared URLs reproduce all eight selections, itemized prices and totals',()=>{
  for(let mask=0;mask<2**optional.length;mask++) {
    const state={items:optional.filter((id,index)=>mask&(1<<index))};
    const url=estimateUrl(versionedData,state);
    const restored={items:selectedFromUrl(versionedData,url)};
    assert.deepEqual(quote(versionedData,restored),quote(versionedData,state));
    assert.equal(new URL(url).searchParams.get('v'),versionedData.rateVersion);
    assert.equal(new URL(url).origin,'https://studio.msyn.me');
  }
});
test('URLs ignore unknown items, fixed rows, duplicates and supplied amounts',()=>{
  const url='https://studio.msyn.me/pricing/?items=thumbnail,editing,editing,shooting,script,unknown&items=materials&total=1&taxRate=0';
  assert.deepEqual(selectedFromUrl(versionedData,url),['materials']);
  assert.equal(quote(versionedData,{items:selectedFromUrl(versionedData,url)}).totalMin,42000);
  assert.deepEqual(selectedFromUrl(versionedData,'https://studio.msyn.me/pricing/'),[]);
  assert.deepEqual(selectedFromUrl(versionedData,estimateUrl(versionedData,{items:[]})),[]);
});
test('archived rates preserve shared amounts after a later price change',async()=>{
  const previous=structuredClone(versionedData);
  const newer=structuredClone(versionedData);newer.rateVersion='abcdef123456';
  newer.checklistItems.find(item=>item.id==='editing').min=20000;
  newer.checklistItems.find(item=>item.id==='editing').max=20000;
  const state={items:['editing','thumbnail']},url=estimateUrl(previous,state);
  const restored=await loadSharedRates(newer,url,async version=>{assert.equal(version,previous.rateVersion);return previous;});
  assert.equal(quote(newer,state).totalMin,36000);
  assert.equal(quote(restored,{items:selectedFromUrl(restored,url)}).totalMin,31000);
  assert.ok(summary(restored,state).includes(url));
});
test('existing shared links preserve their optional editing and thumbnail and old minimum',async()=>{
  const old=JSON.parse(readFileSync(new URL('./pricing-rates/0da10cd790a7.json',import.meta.url)));
  for (let mask=0;mask<16;mask++) {
    const ids=['materials','editing','thumbnail','shorts'].filter((id,index)=>mask&(1<<index));
    const url=estimateUrl(old,{items:ids});
    const restored=await loadSharedRates(versionedData,url,async()=>old);
    const result=quote(restored,{items:selectedFromUrl(restored,url)});
    assert.equal(result.totalMin,11000+(ids.includes('materials')?11000:0)+(ids.includes('editing')?15000:0)+(ids.includes('thumbnail')?5000:0)+(ids.includes('shorts')?5500:0));
    assert.equal(result.preparation.includes('撮影素材の編集・完成データの提供'),!ids.includes('editing'));
    assert.equal(result.preparation.includes('サムネイルの制作'),!ids.includes('thumbnail'));
    assert.ok(!result.preparation.includes('紹介する機能・操作手順の検証結果'));
  }
});
test('missing or invalid rate archives fail instead of showing a different price',async()=>{
  for(const version of ['../secrets','bad','','123456abcdef']){
    const current={...data,rateVersion:'abcdef123456'};
    await assert.rejects(loadSharedRates(current,'https://studio.msyn.me/pricing/?v='+encodeURIComponent(version),async()=>{throw new Error('Not found');}));
  }
  await assert.rejects(loadSharedRates(versionedData,'https://studio.msyn.me/pricing/?v=abcdef123456',async()=>versionedData));
  for(const url of ['https://studio.msyn.me/pricing/','https://studio.msyn.me/pricing/?v=123456abcdef']){
    assert.equal(await loadSharedRates(versionedData,url,async()=>{throw new Error('Should not fetch');}),versionedData);
  }
});
