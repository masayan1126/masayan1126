// Owner-only prototypes. The public build never imports these files.
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {build} from 'esbuild';
const here = new URL('./', import.meta.url);
const out = new URL('../../output/3d-mode/', here);
const page = readFileSync(new URL('site/pricing/index.html', here), 'utf8');
const match = page.match(/<script id="pricing-data" type="application\/json">([\s\S]*?)<\/script>/);
if (!match) throw new Error('Run the existing site build before building the review.');
const data = JSON.parse(match[1]);
const script = await build({entryPoints:[new URL('pricing-flows.mjs', here).pathname], bundle:true,
  write:false, format:'iife', target:'es2022', external:['/pricing-pdf.mjs'],
  define:{REVIEW_PRICING_DATA:JSON.stringify(data)}, logLevel:'silent'});
const html = readFileSync(new URL('pricing-flows.html', here),'utf8')
  .replace('%%STYLE%%', readFileSync(new URL('pricing-flows.css',here),'utf8'))
  .replace('%%SCRIPT%%', script.outputFiles[0].text.replaceAll('</script','<\\/script'));
mkdirSync(out,{recursive:true});
writeFileSync(new URL('pricing-flows.html',out),html);
console.log(new URL('pricing-flows.html',out).pathname);
