import test from 'node:test';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {PDFDocument,PDFString,PDFName,rgb} from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import {createEstimatePdf,createEstimateNumber} from './pricing-pdf.mjs';
import {loadSharedRates} from './pricing-model.mjs';

const source=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
const data={...source,rateVersion:createHash('sha256').update(JSON.stringify(source)).digest('hex').slice(0,12)};
const options={PDFDocument,PDFString,rgb,fontkit,fontBytes:readFileSync(new URL('./pdf-assets/NotoSansJP-Regular.ttf',import.meta.url)),date:new Date('2026-09-06T00:00:00Z')};

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
  const bytes=await createEstimatePdf(data,{items:['materials','thumbnail']},options);
  const extracted=spawnSync('pdftotext',['-f','1','-l','1','-','-'],{input:Buffer.from(bytes),encoding:'utf8'});
  if(extracted.error) throw extracted.error;
  assert.equal(extracted.status,0,extracted.stderr);
  const text=extracted.stdout;
  assert.ok(text.includes('動画で使用する資料の作成\n説明内容と順番をまとめた動画用資料'));
  assert.ok(text.includes('動画編集\nカット、テロップ、BGM、効果音'));
  const ordered=['サービスの事前検証','動画で使用する資料の作成','動画撮影','動画編集','サムネイル制作','公開作業および公開30日後のレポート提出'];
  let last=-1;
  for(const label of ordered) {
    const offset=text.indexOf(label);
    assert.ok(offset>last,'Item reading order: '+label);
    last=offset;
  }
});
