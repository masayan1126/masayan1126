import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const required=['README.md','PRACTICES.md','index.html','deck-template.html','slides.css','icons.svg','manifest.json','tokens/colors.css','tokens/typography.css','tokens/layout.css'];
for(const file of required)await fs.access(path.join(root,file));
const [colors,slides,deck,practices,manifestText,index]=await Promise.all(['tokens/colors.css','slides.css','deck-template.html','PRACTICES.md','manifest.json','index.html'].map(f=>fs.readFile(path.join(root,f),'utf8')));
const manifest=JSON.parse(manifestText);
const allowed=new Set(Object.values(manifest.inheritedColors).map(v=>v.toUpperCase()));
const hexes=[...new Set((colors.match(/#[0-9A-Fa-f]{6}/g)||[]).map(v=>v.toUpperCase()))];
const unexpected=hexes.filter(hex=>{const r=hex.slice(1,3),g=hex.slice(3,5),b=hex.slice(5,7);return !(r===g&&g===b)&&!allowed.has(hex)});
if(unexpected.length)throw Error('Unexpected chromatic colors: '+unexpected.join(','));
const practiceCount=(practices.match(/^- \*\*(.+?)\*\*（/gm)||[]).length;if(practiceCount!==46)throw Error('Practice count: '+practiceCount);
const slideCount=(deck.match(/<section class=\"slide/g)||[]).length;if(slideCount!==8)throw Error('Slide count: '+slideCount);
const noteCount=(deck.match(/class=\"speaker-notes\"/g)||[]).length;if(noteCount!==slideCount)throw Error('Speaker notes: '+noteCount);
const claimCount=(deck.match(/data-claim=/g)||[]).length;if(claimCount!==slideCount)throw Error('Claim titles: '+claimCount);
const titles=[...deck.matchAll(/data-claim=\"([^\"]+)/g)].map(m=>m[1]);if(new Set(titles).size!==titles.length)throw Error('Duplicate claims');
if(!deck.includes('bar-value')||!deck.includes('例示値。実データではありません'))throw Error('Chart labels/source missing');
if(!slides.includes('--type-body: 28px')&&!index.includes('本文 28px'))throw Error('Body type contract missing');
const forbidden=/DotGothic|Zen Kaku|pixelated|hero-cat|happy-sit|RPG|ギルドランク/i;for(const [name,text] of [['slides.css',slides],['deck-template.html',deck]])if(forbidden.test(text))throw Error('Legacy expression in '+name);
for(const term of ['linear-gradient','radial-gradient','box-shadow:'])for(const [name,text] of [['slides.css',slides],['index.html',index]])if(text.includes(term))throw Error('Decorative effect in '+name+': '+term);
function lum(hex){const rgb=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4));return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]}
function contrast(a,b){const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
const pairs=[['#2F5D50','#FFFFFF','white on primary'],['#171717','#FFFFFF','strong text'],['#5F5F5F','#FFFFFF','muted text'],['#171717','#E6EDE9','text on soft green']];for(const [a,b,label] of pairs){const ratio=contrast(a,b);if(ratio<4.5)throw Error(label+' contrast '+ratio.toFixed(2));}
console.log(JSON.stringify({status:'PASS',files:required.length,practices:practiceCount,slides:slideCount,notes:noteCount,claims:claimCount,chromaticColors:allowed.size,contrastPairs:pairs.length},null,2));
