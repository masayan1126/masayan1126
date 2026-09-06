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
  // Localized digit substitutions lack Unicode mappings in this embedded font.
  const font = await document.embedFont(fontBytes, {subset:false,features:{locl:false}});
  const name = recipient.trim().replace(/\s+/gu, ' ');
  if ([...name].length > 80) throw new Error('宛名は80文字以内で入力してください。');
  const supported = new Set(font.getCharacterSet());
  if ([...name].some(char => !supported.has(char.codePointAt(0)))) {
    throw new Error('宛名にPDFで使用できない文字が含まれています。絵文字や特殊文字を変更してください。');
  }
  const issued = new Intl.DateTimeFormat('ja-JP', {timeZone:'Asia/Tokyo',year:'numeric',month:'long',day:'numeric'}).format(date);
  document.setTitle('PR動画制作 概算見積書');
  document.setAuthor('Miyabiya Studio / Masaya Nishigaki');
  document.setSubject('PR動画制作の概算見積もり');
  document.setCreationDate(date);
  const W = 595.28, H = 841.89, left = 44, right = W - 44;
  const ink = rgb(0,0,0), border = rgb(.82,.82,.82);
  let page, y;
  const text = (value, x, top, size=10) => page.drawText(String(value), {x,y:H-top-size,size,font,color:ink});
  const aligned = (value, end, top, size=10) => text(value,end-font.widthOfTextAtSize(value,size),top,size);
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
    if (continuation) {text('PR動画制作 概算見積書（続き）',left,y,12);y+=34;}
  };
  const room = height => {if(y+height>758) addPage(true);};
  addPage();
  const title='概算見積書';
  text(title,(W-font.widthOfTextAtSize(title,25))/2,42,25);
  aligned('見積日：'+issued,right,88,9);
  const addressee = name ? name + (/\s*(御中|様)$/u.test(name) ? '' : ' '+(honorific==='様'?'様':'御中')) : 'お客様';
  const recipientLines=wrap(addressee,275,12);
  text('宛先（お客様）',left,111,9);
  recipientLines.forEach((value,index)=>text(value,left,129+index*18,12));
  const senderX=354;
  text('発行者',senderX,111,9);
  text('Miyabiya Studio',senderX,129,13);
  text('Masaya Nishigaki',senderX,152,10);
  text('contact@msyn.me',senderX,170,9);
  y=Math.max(197,129+recipientLines.length*18+14);
  text('件名：PR動画制作',left,y,11);y+=26;
  page.drawRectangle({x:left,y:H-y-52,width:right-left,height:52,color:rgb(.97,.97,.97)});
  text(result.pending.length?'金額を算出できる項目の小計（税込）':'概算合計（税込）',left+14,y+9,9);
  aligned(money(result.totalMin,result.totalMax),right-14,y+20,21);y+=63;
  const cols=[left,286,325,438,right];
  const tableHeader=()=>{
    page.drawRectangle({x:left,y:H-y-26,width:right-left,height:26,color:rgb(.94,.94,.94)});
    text('品目・作業内容',left+9,y+7,9);
    text('数量',cols[1]+9,y+7,9);
    aligned('単価（税込）',cols[3]-10,y+7,9);
    aligned('金額（税込）',right-10,y+7,9);y+=26;
  };
  tableHeader();
  for(const item of result.lines) {
    const labels=wrap(item.label,cols[1]-left-20,10);
    const details=item.description?wrap(item.description,cols[1]-left-20,8):[];
    const height=Math.max(33,labels.length*15+details.length*12+14);
    if(y+height>720) {addPage(true);tableHeader();}
    labels.forEach((value,index)=>text(value,left+9,y+8+index*15,10));
    details.forEach((value,index)=>text(value,left+9,y+8+labels.length*15+index*12,8));
    const amount=money(taxIncluded(item.min,data.taxRate,item.taxInclusive),taxIncluded(item.max,data.taxRate,item.taxInclusive));
    text('1式',cols[1]+9,y+10,9);
    aligned(amount,cols[3]-10,y+10,9);
    aligned(amount,right-10,y+10,9);y+=height;line(y);
  }
  y+=10;room(50);
  for(const [label,value,bold] of [
    [result.pending.length?'小計（税込）':'概算合計（税込）',money(result.totalMin,result.totalMax),true],
    ['うち消費税相当額（'+Number((data.taxRate*100).toFixed(2))+'%）',money(result.taxMin,result.taxMax),false]
  ]) {
    text(label,286,y,9);aligned(value,right-9,y,bold?12:10);y+=20;
  }
  // Keep the price page brief; the attached page records the agreed service terms.
  const conditions=[
    ['対象動画','本編1本（10〜20分程度）の制作と、当チャンネルへの掲載を見積額に含みます。\n掲載先：https://www.youtube.com/@masayan-ai-hack'],
    ['登録状況','適格請求書発行事業者には登録しておりません。'],
    ['備考','※こちらの金額はあくまで概算になります。正式な料金は動画内容や尺により変動します。\n有効期限は、正式見積もり時にご提示いたします。'],
    ...(result.pending.length ? [['要相談',result.pending.map(item=>item.label).join('、')+'。上記の小計には含まれません。']] : []),
  ].map(([label,value])=>({label,lines:wrap(value,right-left-102,8.5)}));
  const notesHeight=28+conditions.reduce((height,row)=>height+row.lines.length*13+5,0);
  y+=3;room(notesHeight);
  page.drawRectangle({x:left,y:H-y-notesHeight,width:right-left,height:notesHeight,borderWidth:.6,borderColor:border});
  text('ご確認事項',left+10,y+8,9);y+=27;
  for(const row of conditions) {
    text(row.label,left+10,y,8.5);
    for(const value of row.lines) {text(value,left+87,y,8.5);y+=13;}
    y+=5;
  }
  const included=new Set(result.lines.map(item=>item.id));
  const revisionFee=money(taxIncluded(data.revisionFee,data.taxRate),taxIncluded(data.revisionFee,data.taxRate));
  const termSections=[
    ['公開時期・お支払い',[
      '正式なお見積もりと取引条件へのご承諾をもって、ご発注の確定といたします。メールでのご承諾も承ります。',
      'お客様に内容をご確認いただく期間を含め、ご発注の確定から公開までは2〜3週間を目安としております。',
      'アカウントのご提供やご確認が予定より遅れる場合は、公開日を調整いたします。',
      '原則、お支払いは動画公開月の月末締め・翌月末払いでお願いいたします。',
    ]],
    ['修正・追加料金',[
      '当チャンネルで通常公開している動画と同水準の編集を行います。モーショングラフィックスやアニメーションなどの高度な編集は対象外です。',
      '公開前の軽微修正は、2回まで追加料金なしで承ります。テロップの誤字修正・不要な部分のカット・事実関係の訂正が対象です。',
      '3回目以降の修正は、1回につき'+revisionFee+'（税込）を頂戴いたします。',
      '30分を超える動画や撮り直しの料金は、要相談とさせていただきます。',
    ]],
    ['事前検証・レポート',[
      'PRするサービスの検証用アカウントをご用意いただくようお願いいたします。',
      '検証用アカウントは本件の制作にのみ使用し、ログイン情報を第三者に開示いたしません。',
      ...(included.has('research')?['サービスの事前検証では、機能や操作手順を確認し、動画で紹介する内容を検証します。']:[]),
      ...(included.has('publishing')?[
        '公開30日後に、動画の再生数・視聴維持率をまとめたレポートをお渡しいたします。',
        'お客様に計測用リンクをご用意いただける場合は、動画の概要欄に掲載いたします。',
      ]:[]),
    ]],
    ['PR表記・成果について',[
      '動画もしくは概要欄に「PR」「プロモーションを含む」などの表記を入れます。',
      '動画公開によるサービス利用者数・有料プランの契約数・売上の増加は、保証しておりません。',
    ]],
    ['著作権・二次利用',[
      '動画・資料の著作権は、個別のご契約で取り決めます。',
      '自社サイト・SNS・広告などでの二次利用については、利用範囲を含めて要相談とさせていただきます。',
    ]],
    ['掲載期間',[
      '公開後の動画は、原則として継続して掲載いたします。ただし、サービスの終了や大幅な仕様変更、YouTubeの規約への対応に伴い、非公開または削除する場合がございます。',
      '掲載期間のご指定や、複数本の制作・継続契約は要相談とさせていただきます。',
    ]],
    ['キャンセル料',[
      '着手後〜撮影前：正式に確定したお見積もり総額（税込）の30%',
      '撮影後：正式に確定したお見積もり総額（税込）の50%',
      '編集完了後：正式に確定したお見積もり総額（税込）の100%',
    ]],
  ];
  addPage();
  text('取引条件・作業範囲',left,y,20);y+=35;
  text('PR動画制作 / Miyabiya Studio',left,y,10);
  aligned('見積日：'+issued,right,y,9);y+=32;
  for(const [heading,values] of termSections) {
    const rows=values.map(value=>wrap(value,right-left-18,9.5));
    const height=22+rows.reduce((sum,row)=>sum+row.length*14+3,0);
    room(height);
    text(heading,left,y,11);y+=18;
    for(const row of rows) {
      text('・',left,y,9.5);
      for(const value of row) {text(value,left+12,y,9.5);y+=14;}
      y+=3;
    }
    y+=4;
  }
  const url=estimateUrl(data,state,'https://studio.msyn.me/pricing/');
  const pdfPages=document.getPages();
  pdfPages.forEach((target,index)=>{
    page=target;line(778);
    text('選択した見積内容をWebで確認する',left,786,8);
    text('https://studio.msyn.me/pricing/',left,800,7.5);
    aligned((index+1)+' / '+pdfPages.length,right,786,8);
    const link=document.context.register(document.context.obj({
      Type:'Annot',Subtype:'Link',Rect:[left,H-823,right,H-784],Border:[0,0,0],
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
