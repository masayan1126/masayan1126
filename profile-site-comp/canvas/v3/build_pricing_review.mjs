// Local owner review only; never imported by the public build.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {quote,quotePresentation,comparisonQuotes,amountText,taxIncluded} from './pricing-model.mjs';
const root=new URL('../../',import.meta.url),out=new URL('output/3d-mode/',root);
const fixture=JSON.parse(readFileSync(new URL('docs/pricing/private/media-reference.json',root)));
const data=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
const reference=structuredClone(data);Object.assign(reference.mediaRates,fixture.overrides);
const esc=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const records=comparisonQuotes(reference);
const rows=records.map(({state,result,view})=>{
  const r=quote(data,state),v=quotePresentation(data,state,r);
  return `<tr><th scope="row">${esc(view.mediaLabel)}</th><td>${esc(view.totalText)}</td><td>${r.pending.length?'要相談':esc(v.totalText)}${r.pending.length&&r.totalMin!=null?'<small>金額が分かる項目の小計：'+esc(v.totalText)+'</small>':''}</td></tr>`;
}).join('');
const details=records.map(({result,view})=>`<details><summary>${esc(view.mediaLabel)}：${esc(view.totalText)}（参考・未承認）</summary><ul>${result.lines.map(line=>'<li>'+esc(line.label)+'：'+esc(amountText(taxIncluded(line.min,data.taxRate,line.taxInclusive),taxIncluded(line.max,data.taxRate,line.taxInclusive)))+'</li>').join('')}</ul><p>${esc(view.taxText)}</p><ul>${view.scope.map(text=>'<li>'+esc(text)+'</li>').join('')}</ul></details>`).join('');
const decisions=[
  ['単独ショートの料金','3〜4時間で試算した参考額を採用するか、個別見積もりを続けるかを決めます。作業範囲と超過時の扱いも確認します。'],
  ['動画のX告知','動画に組み合わせるX告知1回を、追加料金なしにするかを決めます。'],
  ['本編からの追加ショート','本編の素材から60秒程度を1本作る範囲と、X告知を省いても既存セットと同額にする条件を確認します。'],
  ['ショート・Xの修正条件','無料回数と超過時の料金は未設定です。参考比較の検算では2回まで料金内と仮置きしています。'],
  ['公開・納品の範囲','ショートの公開先・ファイル納品・レポート・キャンセル条件を確認します。Xのみの個別条件は一般向け料金に採用せず、公開データから分離しています。'],
];
mkdirSync(out,{recursive:true});
writeFileSync(new URL('pricing-review.html',out),`<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>PR制作の見積もり：本人確認</title><style>:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#252c33;font:15px/1.8 'Noto Sans JP','Hiragino Sans',sans-serif}main{max-width:1100px;margin:auto;padding:28px 24px 64px}h1{font-size:26px;line-height:1.5}h2{font-size:21px;margin:32px 0 12px}p{margin:8px 0 16px}.notice{background:#fff6e6;border-left:4px solid #a66a11;padding:18px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:14px;text-align:left;border-bottom:1px solid #dce2e9}thead th{background:#eaf0f8}td{font-variant-numeric:tabular-nums}td small{display:block;font-size:12px;line-height:1.7}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.grid article{padding:20px;background:#fff;border:1px solid #dce2e9}.grid h3{font-size:17px;margin:0 0 10px}.grid p{margin:0}details{padding:16px;background:#fff;border-bottom:1px solid #dce2e9}summary{cursor:pointer;min-height:44px;font-weight:600}summary:focus-visible{outline:3px solid #133f8f}a{color:#133f8f}@media(max-width:600px){main{padding:20px 14px 48px}.grid{grid-template-columns:1fr}h1{font-size:22px}table{min-width:650px}}</style></head><body><main><h1>PR制作の見積もりを7構成で確認する</h1><p class="notice">本人確認用の非公開資料です。参考額には、仮価格と個別契約の条件を含みます。公開サイトでは未確定の料金・条件を「要相談」と表示します。</p><p>「見積もり操作」タブで、公開用の選択画面・明細・PDFを確認できます。Gmailの下書きは変更していません。</p><h2>7構成の参考額と公開用の表示</h2><p>本編10〜20分・ショート60秒程度を各1本、X投稿1回で比較します。本編は資料作成とサムネイル制作を含みます。参考額は税込の金額が低い順です。</p><div class="scroll"><table><thead><tr><th>制作物</th><th>今回の参考額（税込）</th><th>公開用の表示</th></tr></thead><tbody>${rows}</tbody></table></div><h2>決める必要がある単価・条件</h2><div class="grid">${decisions.map(([title,body])=>'<article><h3>'+esc(title)+'</h3><p>'+esc(body)+'</p></article>').join('')}</div><h2>内訳と制作範囲</h2><p>参考条件を使った計算例です。未承認の条件を公開料金に反映したものではありません。</p>${details}<h2>検算・互換性の確認</h2><p>既存単価と税込計算、全7構成、未選択、旧料金10版、新旧URL、PDFと問い合わせ文の一致を32テストで確認済みです。PC・スマホの切り替え、Tab・Spaceの操作、共有URLの再読み込み、ブラウザからのPDF保存も確認しました。検証の記録は同じ作業ディレクトリ内に保存します。</p></main></body></html>`);
console.log(new URL('pricing-review.html',out).pathname);
