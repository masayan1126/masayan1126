// Local owner review only. Never included in the public export.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {quote,quotePresentation,comparisonQuotes,defaultItems,amountText} from './pricing-model.mjs';
const root=new URL('../../',import.meta.url),out=new URL('output/3d-mode/',root);
const data=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url)));
const fixture=JSON.parse(readFileSync(new URL('docs/pricing/private/media-reference.json',root)));
const historical=JSON.parse(readFileSync(new URL('./pricing-rates/17268bfca1d6.json',import.meta.url)));
Object.assign(historical.mediaRates,fixture.overrides);
const esc=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const rate=key=>amountText(data.mediaRates[key]?.min,data.mediaRates[key]?.max);
const cards=[
  ['軽微修正を媒体ごとに指定できます','本編・ショート・Xは各2回まで料金内です。3回目以降は1回あたり本編5,500円、ショート3,300円、X1,000円（税込）で計算します。Xは本人指定の「1,000円以下」の上限額です。画面・共有URL・PDF・問い合わせ文で同じ回数と追加料金を使います。'],
  ['同じサービス・製品のPR依頼歴を確認します','以前にも当方へPRを依頼したことが「ある」場合は事前検証費用0円、「ない」場合は税込8,800円です。2択で回答でき、選び直すと金額も切り替わります。'],
  ['公開30日後のレポートは削除しました','新しい見積もりの選択肢・明細・納品条件から、レポート提出を削除しました。YouTubeへの公開作業は税込2,200円を維持します。'],
  ['「動画の企画・台本作成」に変えました','紹介内容・構成・話す内容をまとめた企画書と台本を作成します。お客様に台本や構成案をご用意いただける場合は、選択を外せます。税込11,000円の単価は維持します。'],
  ['ショートの制作方法とXシェアを分けました','本編素材からの切り抜きショート1本は追加0円です。別撮影・大幅な内容変更は税込10,000円です。Xでの動画シェアは別の選択肢とし、1回税込1,500円です。X単独の製品PR投稿は別の料金として要相談を維持します。'],
];
const rows=comparisonQuotes(data).map(({state,result,view})=>{
  const repeat=quote(data,{...state,items:defaultItems(data).filter(id=>id!=='research')});
  const dedicated=quote(data,{...state,shortMode:'dedicated'});
  return `<tr><th scope="row">${esc(view.mediaLabel)}</th><td>${esc(view.totalText)}${result.pending.length?'<small>金額が分かる項目の小計</small>':''}</td><td>${esc(amountText(repeat.totalMin,repeat.totalMax))}</td><td>${state.media.includes('main')&&state.media.includes('short')?esc(amountText(dedicated.totalMin,dedicated.totalMax)):'対象外'}</td></tr>`;
}).join('');
const history=comparisonQuotes(historical).map(({view})=>`<li>${esc(view.mediaLabel)}：${esc(view.totalText)}</li>`).join('');
mkdirSync(out,{recursive:true});
writeFileSync(new URL('pricing-review.html',out),`<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>PR制作の料金・条件の確認</title><style>:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f7f7f7;color:#252c33;font:15px/1.8 'Noto Sans JP','Hiragino Sans',sans-serif}main{max-width:1100px;margin:auto;padding:28px 24px 64px}h1{font-size:26px;line-height:1.5}h2{font-size:21px;margin:32px 0 12px}p{margin:8px 0 16px}.notice{background:#fff6e6;border-left:4px solid #a66a11;padding:18px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.grid article{padding:20px;background:#fff;border:1px solid #e1e1e1}.grid h2{font-size:18px;margin:0 0 10px}.grid p{margin:0}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:14px;text-align:left;border-bottom:1px solid #e1e1e1}thead th{background:#efefef}td small{display:block;font-size:12px}details{padding:16px;background:#fff}summary{cursor:pointer;min-height:44px;font-weight:600}summary:focus-visible{outline:3px solid #133f8f}@media(max-width:600px){main{padding:20px 14px 48px}.grid{grid-template-columns:1fr}h1{font-size:22px}table{min-width:740px}}</style></head><body><main><h1>必要な作業と公開後の対応を、別々に選べるようにしました</h1><p>「採用した見積もり」タブで、質問への回答・選び直し・見積書・PDFを確認できます。単独ショートは税込10,000円を維持します。</p><div class="grid">${cards.map(([title,body])=>`<article><h2>${title}</h2><p>${body}</p></article>`).join('')}</div><h2>7構成の料金を比べる</h2><p>本編は10〜20分程度、ショートは60秒程度を各1本。企画・台本とサムネイルを依頼する場合です。本編とショートの組み合わせでは、切り抜き型を基準にしています。</p><p class="notice">未確定の料金・修正条件は要相談です。表示した小計は、未確定の料金を含む総額ではありません。Xのみの個別契約の金額は、一般向けの公開データに含めていません。</p><div class="scroll"><table><thead><tr><th>制作物</th><th>事前検証あり（税込）</th><th>事前検証なし（税込）</th><th>別撮影型のショート（税込）</th></tr></thead><tbody>${rows}</tbody></table></div><h2>共有時の料金を保ちます</h2><p>旧URLでは、共有時の事前検証・レポート・ショートとXのセット条件を再現します。新URLでは、事前検証の有無とショートの制作方法も保存します。</p><details><summary>当初の非公開参考条件を見る</summary><p>過去の検算に使った仮価格と個別契約の条件です。現在の公開料金とは分けて管理します。</p><ul>${history}</ul></details></main></body></html>`);
console.log(new URL('pricing-review.html',out).pathname);
