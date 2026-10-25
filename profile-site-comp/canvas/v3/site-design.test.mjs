import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const here=fileURLToPath(new URL('.',import.meta.url));
function python(code){return execFileSync('python3',['-c',code],{cwd:here,encoding:'utf8'});}

test('legacy action variants become complete primary or secondary components at every depth',()=>{
  const samples=JSON.parse(python(`import json,site_journeys
samples=['v3-secondary','v3-primary','v3-primary v3-secondary','btn btn-p','btn btn-g','btn btn-w','business-cta']
print(json.dumps([site_journeys.normalize_actions('<details><div><a class="'+s+'" href="/contact/">相談する</a></div></details>') for s in samples]))`));
  for(const [i,html] of samples.entries()){
    assert.match(html,/class="site-action site-action-(primary|secondary)"/);
    assert.match(html,/href="\/contact\/"/);
    assert.equal(html.includes('site-action-secondary'),[0,2,4,5].includes(i));
  }
});

test('public price examples use the live quote model and do not include a standalone X partner price',()=>{
  const rows=JSON.parse(execFileSync('node',['build_pricing_examples.mjs'],{cwd:here,encoding:'utf8'}));
  assert.deepEqual(rows.map(r=>[r.label,r.total]),[['YouTube本編1本',53000],['ショート1本',10000]]);
  const html=python('import build_pricing;print(build_pricing.media_summary())');
  assert.match(html,/53,000円/);assert.match(html,/10,000円/);
  assert.match(html,/Xのみの製品PR.*個別にお見積もり/);
  assert.match(html,/<details class="ratecard-terms">/);
  for(const fee of ['5,500円','3,300円','1,000円'])assert.ok(html.includes(fee));
  assert.equal((html.match(/data-site-action=/g)||[]).length,2);
});
