import {loadSharedRates,stateFromUrl} from './pricing-model.mjs';
import {startWizard} from './pricing-wizard.mjs';

const current=JSON.parse(document.getElementById('pricing-data').textContent);
const wizard=document.getElementById('pricing-wizard');
const legacy=document.getElementById('legacy-estimate');
try {
  const data=await loadSharedRates(current,location.href,async version=>{
    const response=await fetch('/pricing-rates/'+version+'.json');
    if(!response.ok)throw new Error('Rate snapshot unavailable');
    return response.json();
  });
  const state=stateFromUrl(data,location.href);
  if(Array.isArray(state.media)) {
    document.getElementById('base-scope-hint').hidden=true;
    document.getElementById('estimate-result').id='legacy-estimate-result';
    startWizard(data,state,current);
  } else {
    wizard.hidden=true;legacy.hidden=false;
    await import('./pricing-legacy.mjs');
  }
} catch {
  wizard.hidden=true;legacy.hidden=true;
  document.getElementById('share-load-error').hidden=false;
}
