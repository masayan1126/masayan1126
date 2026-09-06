import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {PDFDocument,PDFString,PDFName,rgb} from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import {createEstimatePdf} from './pricing-pdf.mjs';
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
    assert.equal(document.getPageCount(),1);
    assert.equal(document.getTitle(),'PR動画制作 概算お見積書');
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
  assert.ok((await PDFDocument.load(bytes)).getPageCount()>=1);
  assert.equal(archived.rateVersion,'5bf426700870');
});

test('invalid quantities and unsupported recipient text do not produce misleading PDFs',async()=>{
  await assert.rejects(createEstimatePdf(data,{revisions:-1},options),/修正回数/);
  await assert.rejects(createEstimatePdf(data,{}, {...options,recipient:'あ'.repeat(81)}),/80文字/);
  await assert.rejects(createEstimatePdf(data,{}, {...options,recipient:'会社😀'}),/使用できない文字/);
});
