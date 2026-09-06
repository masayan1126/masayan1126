import {quote, taxIncluded, estimateUrl} from './pricing-model.mjs';

const money = (min, max) => min == null ? '要相談' :
  (min === max ? min.toLocaleString('ja-JP') : min.toLocaleString('ja-JP') + '〜' + max.toLocaleString('ja-JP')) + '円';

// The same quote calculation powers the screen, shared links, and exported PDF.
export async function createEstimatePdf(data, state, options) {
  const {PDFDocument, PDFString, rgb, fontkit, fontBytes, recipient = '', honorific = '御中', date = new Date()} = options;
  const result = quote(data, state);
  if (result.status === 'invalid') throw new Error(result.error);
  const document = await PDFDocument.create();
  document.registerFontkit(fontkit);
  // Keep the Japanese font intact: fontkit subsetting can omit visible glyphs.
  const font = await document.embedFont(fontBytes, {subset:false});
  const latinFont = await document.embedFont('Helvetica');
  const name = recipient.trim().replace(/\s+/gu, ' ');
  if ([...name].length > 80) throw new Error('宛名は80文字以内で入力してください。');
  const supported = new Set(font.getCharacterSet());
  if ([...name].some(char => !supported.has(char.codePointAt(0)))) {
    throw new Error('宛名にPDFで使用できない文字が含まれています。絵文字や特殊文字を変更してください。');
  }
  const issued = new Intl.DateTimeFormat('ja-JP', {timeZone:'Asia/Tokyo',year:'numeric',month:'long',day:'numeric'}).format(date);
  document.setTitle('PR動画制作 概算お見積書');
  document.setAuthor('Miyabiya Studio / Masaya Nishigaki');
  document.setSubject('PR動画制作の概算見積もり');
  document.setCreationDate(date);
  const W = 595.28, H = 841.89, left = 44, right = W - 44;
  const ink = rgb(.13,.16,.20), muted = rgb(.36,.40,.46), blue = rgb(.075,.247,.561), border = rgb(.82,.85,.89);
  let page, y;
  const text = (value, x, top, size=10, color=ink) => page.drawText(String(value), {x,y:H-top-size,size,font,color});
  const aligned = (value, end, top, size=10, color=ink) => text(value,end-font.widthOfTextAtSize(value,size),top,size,color);
  const line = top => page.drawLine({start:{x:left,y:H-top},end:{x:right,y:H-top},thickness:.6,color:border});
  const wrap = (value, width, size, face=font) => {
    const lines = [];
    for (const paragraph of String(value).split('\n')) {
      let part = '';
      for (const char of paragraph) {
        if (part && face.widthOfTextAtSize(part+char,size)>width) { lines.push(part); part=''; }
        part += char;
      }
      lines.push(part);
    }
    return lines;
  };
  const addPage = (continuation=false) => {
    page = document.addPage([W,H]); y=44;
    if (continuation) {text('PR動画制作 概算お見積書（続き）',left,y,12,blue);y+=34;}
  };
  const room = height => {if(y+height>758) addPage(true);};
  const paragraph = (value, size=9, color=muted) => {
    const lines = wrap(value,right-left,size);
    room(lines.length*(size+5)+5);
    for(const value of lines) {text(value,left,y,size,color);y+=size+5;}
    y+=5;
  };
  addPage();
  const title='御見積書';
  text(title,(W-font.widthOfTextAtSize(title,25))/2,42,25,blue);
  const subtitle='概算';
  text(subtitle,(W-font.widthOfTextAtSize(subtitle,10))/2,78,10,muted);
  aligned('発行日：'+issued,right,104,9,muted);
  const addressee = name ? name + (/\s*(御中|様)$/u.test(name) ? '' : ' '+(honorific==='様'?'様':'御中')) : 'お客様';
  const recipientLines=wrap(addressee,275,12);
  recipientLines.forEach((value,index)=>text(value,left,128+index*18,12));
  const senderX=354;
  text('Miyabiya Studio',senderX,135,13,blue);
  text('Masaya Nishigaki',senderX,158,10);
  text('contact@msyn.me',senderX,177,9,muted);
  y=Math.max(207,128+recipientLines.length*18+14);
  text('件名：PR動画制作',left,y,11);y+=26;
  page.drawRectangle({x:left,y:H-y-52,width:right-left,height:52,color:rgb(.95,.97,.99)});
  text(result.pending.length?'金額を算出できる項目の小計（税込）':'概算合計（税込）',left+14,y+9,9,muted);
  aligned(money(result.totalMin,result.totalMax),right-14,y+20,21,blue);y+=69;
  const cols=[left,286,325,438,right];
  const tableHeader=()=>{
    page.drawRectangle({x:left,y:H-y-26,width:right-left,height:26,color:rgb(.94,.95,.97)});
    text('品目・作業内容',left+9,y+7,9);
    text('数量',cols[1]+9,y+7,9);
    aligned('単価（税込）',cols[3]-10,y+7,9);
    aligned('金額（税込）',right-10,y+7,9);y+=26;
  };
  tableHeader();
  for(const item of result.lines) {
    const labels=wrap(item.label,cols[1]-left-20,10);
    const details=item.description?wrap(item.description,cols[1]-left-20,8):[];
    const height=Math.max(35,labels.length*15+details.length*12+14);
    if(y+height>720) {addPage(true);tableHeader();}
    labels.forEach((value,index)=>text(value,left+9,y+8+index*15,10));
    details.forEach((value,index)=>text(value,left+9,y+8+labels.length*15+index*12,8,muted));
    const amount=money(taxIncluded(item.min,data.taxRate,item.taxInclusive),taxIncluded(item.max,data.taxRate,item.taxInclusive));
    text('1式',cols[1]+9,y+10,9,muted);
    aligned(amount,cols[3]-10,y+10,9);
    aligned(amount,right-10,y+10,9);y+=height;line(y);
  }
  y+=12;room(83);
  for(const [label,value,bold] of [
    ['税抜小計',money(result.min,result.max),false],
    ['消費税（'+Number((data.taxRate*100).toFixed(2))+'%）',money(result.taxMin,result.taxMax),false],
    [result.pending.length?'小計（税込）':'概算合計（税込）',money(result.totalMin,result.totalMax),true]
  ]) {
    text(label,320,y,9,bold?blue:muted);aligned(value,right-9,y,bold?12:10,bold?blue:ink);y+=23;
  }
  y+=7;
  paragraph('※こちらの金額はあくまで概算になります。正式な料金は動画内容や尺により変動します。');
  if(result.pending.length) paragraph('要相談：'+result.pending.map(item=>item.label).join('、')+'。上記の小計には含まれません。');
  paragraph('公開時期：ご発注の確定から2〜3週間（お客様に内容をご確認いただく期間を含みます）');
  paragraph('お支払い：原則、動画公開月の月末締め・翌月末払い');
  paragraph('その他の条件は、下記の見積もりページでご確認ください。');
  const url=estimateUrl(data,state,'https://studio.msyn.me/pricing/');
  const pdfPages=document.getPages();
  pdfPages.forEach((target,index)=>{
    page=target;line(778);
    text('料金表：'+data.updated,left,786,8,muted);
    aligned((index+1)+' / '+pdfPages.length,right,786,8,muted);
    wrap(url,right-left,7,latinFont).forEach((value,i)=>page.drawText(value,{x:left,y:H-808-i*10,size:7,font:latinFont,color:muted}));
    const link=document.context.register(document.context.obj({
      Type:'Annot',Subtype:'Link',Rect:[left,12,right,43],Border:[0,0,0],
      A:{Type:'Action',S:'URI',URI:PDFString.of(url)},
    }));
    page.node.addAnnot(link);
  });
  return document.save();
}

let resources;
export async function downloadEstimatePdf(data,state,recipient,honorific) {
  if(!resources) resources=Promise.all([
    import('./pdf-vendor/pdf-lib-1.17.1.mjs'),
    import('./pdf-vendor/fontkit-1.1.1.mjs'),
    fetch(new URL('./pdf-assets/NotoSansJP-Regular.ttf',import.meta.url)).then(response=>{
      if(!response.ok) throw new Error('PDF用フォントを読み込めませんでした。');
      return response.arrayBuffer();
    })
  ]).catch(error=>{resources=undefined;throw error;});
  const [library,fontkit,fontBytes]=await resources;
  const date=new Date();
  const bytes=await createEstimatePdf(data,state,{...library,fontkit:fontkit.default,fontBytes,recipient,honorific,date});
  const url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));
  const anchor=document.createElement('a');
  const stamp=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'}).format(date);
  anchor.href=url;anchor.download='Miyabiya-Studio_PR動画制作_概算見積書_'+stamp+'.pdf';
  document.body.append(anchor);anchor.click();anchor.remove();
  setTimeout(()=>URL.revokeObjectURL(url),60000);
}
