// Three sizes shared by desktop and mobile, including captions.
export const adoptedPreset = 'a';
export const roles = [
  {id:'large',label:'大',hint:'ページタイトル・成果や料金の数字',min:22,max:40,selector:'h1:not(#a-title),.focus-result,.focus-metrics dd,.price-examples dd,.grand-total strong,.chosen-estimate strong,.alternative-total,.launch-summary strong,.aside-price,.extras-current dd,.result-amount strong,#result-range'},
  {id:'medium',label:'中',hint:'見出し・名前・屋号・項目名・入力欄',min:16,max:22,selector:'h2,h3,h4,h5,h6,#a-title,.editorial-brand,.choice-title,.pr-history legend,.asset-options-title,.media-revisions legend,.estimate-group legend,.media-option b,.focus-person .focus-result,input:not([type="checkbox"]):not([type="radio"]),select,textarea'},
  {id:'small',label:'小',hint:'自己紹介・本文・補足・メニュー・ボタン',min:14,max:16,selector:'p,li,small,button,summary,label,th,td,dt,dd,.editorial-nav a,.editorial-contact-link,.editorial-button,.button,.plain-link,.text-button,.site-action-primary,.site-action-secondary,.estimate-button,.estimate-copy-button,.answer-value,.choice-description,.choice-price,.sheet-note,.rev-note,.paper-sender,.paper-subject,.document-foot,.document-details,.completed-answers small,.grand-total span'}
];
export const presets = {
  a:{label:'A',description:'24・18・14pxで全ページを統一します。',values:[24,18,14]},
  b:{label:'B',description:'28・20・16pxで比較します。',values:[28,20,16]},
  c:{label:'C',description:'32・22・16pxで比較します。',values:[32,22,16]}
};
export function typographyCss({values}){
  const scope='body.site-renewal.editorial.compact-local';
  const size=index=>`${values[index]/16}rem`;
  // A local layer keeps legacy font shorthands and important declarations from
  // adding sizes. Descendants inherit their role, including nested link text.
  const reset=`${scope}{font-family:var(--font-ui)!important;font-size:${size(2)}!important;font-weight:400!important;}\n${scope} :where(*),${scope} ::before,${scope} ::after,${scope} ::marker{font-family:inherit!important;font-size:inherit!important;font-weight:inherit!important;}`;
  const rules=[2,0,1].map(i=>`${scope} :where(${roles[i].selector}){font-size:${size(i)}!important;}`).join('\n');
  const emphasis=`${scope} :where(h1,h2,h3,h4,h5,h6,strong,b,button,summary,legend,.editorial-brand,.choice-title,.site-action,.pr-estimate-link,.detail-link,.req){font-weight:700!important;}`;
  return `@layer local-typography {\n${reset}\n${rules}\n${emphasis}\n}`;
}
