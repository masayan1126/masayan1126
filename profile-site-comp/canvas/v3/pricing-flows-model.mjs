// Review-only fixed-price examples. Never import from a public entry point.
import {quote,quotePresentation,amountText,taxIncluded} from './pricing-model.mjs';
export const combinations=[['x'],['short'],['short','x'],['main'],['main','x'],['main','short'],['main','short','x']];
export function fixedReviewRates(source,basis='max') {
  if(!['min','max'].includes(basis))throw new Error('Unknown review rate basis');
  const data=structuredClone(source);
  data.checklistItems=data.checklistItems.map(item=>({...item,min:item[basis],max:item[basis]}));
  // No speculative public Short or X rate is introduced for the prototype.
  return data;
}
export function relatedQuotes(data,state) {
  if(!state.media.length)return [];
  const selected=new Set(state.media);
  return combinations.filter(media=>!(media.length===selected.size&&media.every(id=>selected.has(id)))).map(media=>{
    const next={...state,media:[...media]},result=quote(data,next),view=quotePresentation(data,next,result);
    const added=media.filter(id=>!selected.has(id)),removed=state.media.filter(id=>!media.includes(id));
    const changeCount=added.length+removed.length;
    const label=added.length===1&&!removed.length
      ? added[0]==='x'?'公開動画をXでも告知する場合':added[0]==='short'?'ショート動画でも紹介する場合':'本編でも詳しく紹介する場合'
      : view.mediaLabel+'の場合';
    const before=quote(data,state);
    const knownDelta=!before.pending.length&&!result.pending.length?result.totalMin-before.totalMin:null;
    return {state:next,result,view,label,added,removed,changeCount,knownDelta};
  }).sort((a,b)=>(a.removed.length?1:0)-(b.removed.length?1:0)||a.changeCount-b.changeCount||(a.result.totalMin??Infinity)-(b.result.totalMin??Infinity)||a.state.media.length-b.state.media.length);
}
export function reviewSummary(data,state) {
  const result=quote(data,state),view=quotePresentation(data,state,result);
  if(['invalid','empty'].includes(result.status))return '';
  return ['画面比較用の見積もり',view.subject,
    ...result.lines.map(item=>item.label+'：'+amountText(taxIncluded(item.min,data.taxRate,item.taxInclusive),taxIncluded(item.max,data.taxRate,item.taxInclusive))),
    view.totalLabel+'：'+view.totalText,
    ...view.revisionNotes,
    ...(result.pending.length?['要相談：',...result.pending.map(item=>item.label),'要相談の料金は小計に含みません。']:[]),
    'この見積書は操作画面の比較用です。正式見積もりではありません。'].join('\n');
}
