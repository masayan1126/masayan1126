import test from 'node:test';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {PDFDocument,PDFString,PDFName,rgb} from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import {createEstimatePdf,createEstimateNumber} from './pricing-pdf.mjs';
import {loadSharedRates,quote,quotePresentation,amountText,taxIncluded,stateFromUrl} from './pricing-model.mjs';

const source=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
const data={...source,rateVersion:createHash('sha256').update(JSON.stringify(source)).digest('hex').slice(0,12)};
const options={PDFDocument,PDFString,rgb,fontkit,fontBytes:readFileSync(new URL('./pdf-assets/NotoSansJP-Regular.ttf',import.meta.url)),date:new Date('2026-09-06T00:00:00Z')};

test('PDF range explanations match fixed, historical and unpriced work',async()=>{
  const previous=JSON.parse(readFileSync(new URL('./pricing-rates/17268bfca1d6.json',import.meta.url)));
  for(const [rates,media,hasRange] of [[data,['main'],false],[previous,['main'],true],[data,['short'],false]]) {
    const bytes=await createEstimatePdf(rates,{media,items:['materials','thumbnail']},options);
    const extracted=spawnSync('pdftotext',['-layout','-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
    assert.equal(extracted.status,0,extracted.stderr);
    assert.equal(extracted.stdout.includes('料金に幅がある項目は'),hasRange);
  }
});

test('all current selections export as readable A4 PDF documents',async()=>{
  const optional=data.checklistItems.filter(item=>!item.fixed).map(item=>item.id);
  for(let mask=0;mask<2**optional.length;mask++) {
    const items=optional.filter((_,index)=>mask&(1<<index));
    const before=JSON.stringify(data);
    const bytes=await createEstimatePdf(data,{items},{...options,recipient:'株式会社サンプル'});
    const document=await PDFDocument.load(bytes);
    assert.equal(document.getPageCount(),3);
    assert.equal(document.getTitle(),'PR動画制作 概算見積書');
    assert.equal(document.getAuthor(),'Miyabiya Studio / 西垣雅矢 (Masaya Nishigaki)');
    assert.ok(Math.abs(document.getPage(0).getWidth()-595.28)<.01);
    const annotation=document.context.lookup(document.getPage(0).node.Annots().get(0));
    const action=annotation.lookup(PDFName.of('A'));
    const link=new URL(action.get(PDFName.of('URI')).decodeText());
    assert.equal(link.searchParams.get('v'),data.rateVersion);
    assert.deepEqual(link.searchParams.get('items').split(',').filter(Boolean),items);
    assert.equal(JSON.stringify(data),before);
  }
});

test('an archived quote with a long recipient remains exportable',async()=>{
  const archived=await loadSharedRates(data,'https://studio.msyn.me/pricing/?items=materials&v=5bf426700870',async version=>JSON.parse(readFileSync(new URL('./pricing-rates/'+version+'.json',import.meta.url))));
  const bytes=await createEstimatePdf(archived,{items:['materials']},{...options,recipient:'株式会社'+ '企業向けサービス事業部'.repeat(5),honorific:'御中'});
  assert.equal((await PDFDocument.load(bytes)).getPageCount(),3);
  assert.equal(archived.rateVersion,'5bf426700870');
});

test('invalid quantities and unsupported recipient text do not produce misleading PDFs',async()=>{
  await assert.rejects(createEstimatePdf(data,{revisions:-1},options),/修正回数/);
  await assert.rejects(createEstimatePdf(data,{}, {...options,recipient:'あ'.repeat(81)}),/80文字/);
  await assert.rejects(createEstimatePdf(data,{}, {...options,recipient:'会社😀'}),/使用できない文字/);
});


test('estimate references use the issue date in Japan and differ between exports',()=>{
  const date=new Date('2026-09-06T15:00:00Z');
  const first=createEstimateNumber(date),second=createEstimateNumber(date);
  assert.match(first,/^MS-20260907-[0-9A-F]{12}$/);
  assert.match(second,/^MS-20260907-[0-9A-F]{12}$/);
  assert.notEqual(first,second);
});

test('a supplied export reference is retained in PDF metadata and malformed references are rejected',async()=>{
  const estimateNumber='MS-20260906-A1B2C3D4E5F6';
  const bytes=await createEstimatePdf(data,{items:[]},{...options,estimateNumber});
  const document=await PDFDocument.load(bytes);
  assert.equal(document.getSubject(),'PR動画制作（サービス紹介動画1本・AIギルドch掲載） / '+estimateNumber);
  assert.equal(document.getKeywords(),estimateNumber);
  assert.equal(document.getPageCount(),3);
  await assert.rejects(createEstimatePdf(data,{}, {...options,estimateNumber:'bad-reference'}),/見積番号/);
});


test('item names and descriptions remain together in extracted PDF text',async()=>{
  const bytes=await createEstimatePdf(data,{items:['research','materials','thumbnail']},options);
  const extracted=spawnSync('pdftotext',['-f','1','-l','1','-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
  if(extracted.error) throw extracted.error;
  assert.equal(extracted.status,0,extracted.stderr);
  const text=extracted.stdout;
  assert.ok(text.replace(/\s+/gu,'').includes('動画の企画・台本作成紹介内容・構成・話す内容を整理した企画書と台本'));
  assert.ok(text.includes('動画編集\nカット、テロップ、BGM、効果音'));
  const ordered=['サービスの事前検証','動画の企画・台本作成','動画撮影','動画編集','サムネイル制作','YouTubeへの公開作業'];
  let last=-1;
  for(const label of ordered) {
    const offset=text.indexOf(label);
    assert.ok(offset>last,'Item reading order: '+label);
    last=offset;
  }
});

test('all seven media offers have matching PDF amounts, conditions and restoring links',async()=>{
  for(const media of [['x'],['short'],['short','x'],['main'],['main','x'],['main','short'],['main','short','x']]) {
    const state={media,items:['materials','thumbnail'],revisions:2,custom:['reuse'],notes:'準備物や作業の分担を相談したい\n目安より大幅に長い動画を依頼したい'};
    const r=quote(data,state),view=quotePresentation(data,state,r);
    const bytes=await createEstimatePdf(data,state,options);
    const document=await PDFDocument.load(bytes);
    const extracted=spawnSync('pdftotext',['-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
    assert.equal(extracted.status,0,extracted.stderr);
    const text=extracted.stdout.replace(/\s+/gu,'');
    const compact=value=>value.replace(/\s+/gu,'');
    assert.ok(text.includes(compact(view.subject)));
    assert.ok(text.includes(compact(view.totalLabel)));
    assert.ok(text.includes(compact(view.totalText).replaceAll('円〜','〜')));
    assert.ok(text.includes('小計（税抜）'));
    assert.ok(text.includes(compact(amountText(r.min,r.max)).replaceAll('円〜','〜')));
    for(const item of r.pending)assert.ok(text.includes(compact(item.label)),item.label);
    for(const line of r.lines){
      assert.ok(text.includes(compact(line.label)),line.label);
      assert.ok(text.includes(compact(amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive))).replaceAll('円〜','〜')));
    }
    if (!media.includes('main')){
      assert.ok(!text.includes('サービス紹介動画1本'));
      assert.ok(!text.includes('本編動画はYouTube'));
      assert.ok(!text.includes('撮影開始時点'));
      if(r.lines.some(line=>line.min==null))assert.ok(text.includes('要相談'));
    }
    const annotation=document.context.lookup(document.getPage(0).node.Annots().get(0));
    const link=annotation.lookup(PDFName.of('A')).get(PDFName.of('URI')).decodeText();
    assert.deepEqual(quote(data,stateFromUrl(data,link)),r);
  }
  await assert.rejects(createEstimatePdf(data,{media:[]},options),/制作物/);
});

test('production options agree in PDF prices, scope, removed reports and restoring links',async()=>{
  for(const state of [
    {media:['main','short'],items:['materials','thumbnail'],shortMode:'clip',report:false},
    {media:['main','short','x'],items:['research','materials','thumbnail'],shortMode:'dedicated',report:true},
    {media:['short'],items:[],report:true},
  ]) {
    const result=quote(data,state),view=quotePresentation(data,state,result);
    const bytes=await createEstimatePdf(data,state,options),doc=await PDFDocument.load(bytes);
    const extracted=spawnSync('pdftotext',['-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
    assert.equal(extracted.status,0,extracted.stderr);
    const text=extracted.stdout.replace(/\s+/gu,'');
    assert.ok(text.includes(view.totalText));
    for(const line of result.lines)assert.ok(text.includes(line.label.replace(/\s+/gu,'')),line.label);
    for(const scope of view.scope)assert.ok(text.includes(scope.replace(/\s+/gu,'')),scope);
    assert.ok(!text.includes('公開30日後'));
    if(!state.items.includes('research'))assert.ok(!text.includes('サービスの事前検証を開始した時点を「着手」といたします。'));
    const annotation=doc.context.lookup(doc.getPage(0).node.Annots().get(0));
    const link=annotation.lookup(PDFName.of('A')).get(PDFName.of('URI')).decodeText();
    assert.deepEqual(quote(data,stateFromUrl(data,link)),result);
  }
});

test('long multiline requests continue onto new PDF pages and retain their restoring link',async()=>{
  const notes='確認事項\n'.repeat(190)+'最後の希望';
  const state={media:['main'],items:['materials','thumbnail'],revisions:3,notes};
  const bytes=await createEstimatePdf(data,state,options),document=await PDFDocument.load(bytes);
  assert.ok(document.getPageCount()>3);
  const extracted=spawnSync('pdftotext',['-bbox','-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
  assert.equal(extracted.status,0,extracted.stderr);
  assert.ok(extracted.stdout.includes('最後の希望'));
  for(const match of extracted.stdout.matchAll(/yMax="([\d.]+)"/g))assert.ok(Number(match[1])<824,'Text must stay within the PDF page');
  const annotation=document.context.lookup(document.getPage(0).node.Annots().get(0));
  const link=annotation.lookup(PDFName.of('A')).get(PDFName.of('URI')).decodeText();
  assert.equal(stateFromUrl(data,link).notes,notes);
});

test('independent revision counts and each medium fee match the PDF and its restoring link',async()=>{
  const state={media:['main','short','x'],items:['research','materials','thumbnail'],revisionCounts:{main:3,short:4,x:5}};
  const result=quote(data,state),view=quotePresentation(data,state,result);
  const bytes=await createEstimatePdf(data,state,options),doc=await PDFDocument.load(bytes);
  const extracted=spawnSync('pdftotext',['-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
  assert.equal(extracted.status,0,extracted.stderr);
  const text=extracted.stdout.replace(/\s+/gu,'');
  assert.equal(result.totalMin,69600);assert.ok(text.includes('69,600円'));
  for(const note of view.revisionNotes)assert.ok(text.includes(note.replace(/\s+/gu,'')),note);
  for(const line of result.lines)assert.ok(text.includes(line.label.replace(/\s+/gu,'')),line.label);
  assert.ok(!text.includes('ショートの修正回数・追加料金'));
  assert.ok(!text.includes('X投稿の修正回数・追加料金'));
  const annotation=doc.context.lookup(doc.getPage(0).node.Annots().get(0));
  const link=annotation.lookup(PDFName.of('A')).get(PDFName.of('URI')).decodeText();
  assert.deepEqual(quote(data,stateFromUrl(data,link)),result);
});
