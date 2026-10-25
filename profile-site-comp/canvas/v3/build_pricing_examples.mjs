// Representative public scenarios use the same model as the live simulator.
import {readFileSync} from 'node:fs';
import {quote,quotePresentation,defaultItems} from './pricing-model.mjs';
const data=JSON.parse(readFileSync(new URL('./pricing-data.json',import.meta.url),'utf8'));
const scenarios=[['YouTube本編1本',['main']],['ショート1本',['short']]];
console.log(JSON.stringify(scenarios.map(([label,media])=>{
  const state={media,items:defaultItems(data),shortMode:'clip',revisionCounts:{main:2,short:2,x:2},notes:''};
  const result=quote(data,state),view=quotePresentation(data,state,result);
  return {label,totalText:view.totalText,total:result.totalMin};
})));
