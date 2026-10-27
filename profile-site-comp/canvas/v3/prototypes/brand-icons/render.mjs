// Export a contact sheet and transparent PNGs from the original vector proposals.
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const require=createRequire(import.meta.url);
const sharp=require('sharp');
const {createCanvas,loadImage}=require('@napi-rs/canvas');
const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(here,'../../../../output/brand-icon-options');
await mkdir(out,{recursive:true});
const {options}=JSON.parse(await readFile(path.join(here,'options.json'),'utf8'));
const canvas=createCanvas(1080,784),ctx=canvas.getContext('2d');
ctx.fillStyle='#fff';ctx.fillRect(0,0,1080,784);
ctx.fillStyle='#202020';ctx.font='700 24px "Hiragino Sans", sans-serif';
ctx.fillText('Miyabiya Studio — アイコン5案',40,44);
ctx.font='14px "Hiragino Sans", sans-serif';ctx.fillStyle='#606060';
ctx.fillText('左：拡大表示　右：屋号と並べた表示',40,72);
for(const [index,option] of options.entries()){
  const svg=(await readFile(path.join(here,'marks',`${option.id}.svg`),'utf8')).replace('<svg ','<svg color="#202020" ');
  const png=await sharp(Buffer.from(svg)).resize(256,256).png().toBuffer();
  await writeFile(path.join(out,`${option.id}.png`),png);
  const image=await loadImage(png),x=40+(index%2)*520,y=112+Math.floor(index/2)*208;
  ctx.fillStyle='#202020';ctx.font='700 18px "Hiragino Sans", sans-serif';
  ctx.fillText(`${option.id.toUpperCase()}｜${option.label}`,x,y);
  ctx.drawImage(image,x+4,y+32,64,64);
  ctx.drawImage(image,x+112,y+54,24,24);
  ctx.font='700 18px "Hiragino Sans", sans-serif';ctx.fillText('Miyabiya Studio',x+144,y+73);
  ctx.font='14px "Hiragino Sans", sans-serif';ctx.fillStyle='#606060';
  ctx.fillText(option.note,x,y+132);
}
await writeFile(path.join(out,'five-options.png'),canvas.toBuffer('image/png'));
console.log(path.join(out,'five-options.png'));
