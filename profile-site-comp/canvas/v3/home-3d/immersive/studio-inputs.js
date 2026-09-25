import * as T from 'three';

const rows=[['esc','1','2','3','4','5','6','7','8','9','0','−','=','delete'],['tab','Q','W','E','R','T','Y','U','I','O','P','[',']','\\'],['caps','A','S','D','F','G','H','J','K','L',';',"'",'return'],['shift','Z','X','C','V','B','N','M',',','.','/','shift'],['ctrl','opt','cmd','space','cmd','opt','←','↓','↑','→']];
const duration=24;
const phrases=[
 [1.35,6.55,'const agents = await studio.spawn(36)\n'],
 [8.15,10.9,'await agents.run(tasks)\n'],
 [15.2,20.65,'await verify.outputs()\nawait studio.preview()\n']
];
const events=[];
let text='';
for(const [start,end,line] of phrases){
 const weights=[...line].map((c,i)=>c==='\n'?2.4:c===' '?1.15:[.78,1.08,.86,1.32,.74,1.04,.94][i%7]);
 const total=weights.reduce((a,b)=>a+b,0);let offset=0;
 [...line].forEach((char,i)=>{text+=char;events.push({at:start+(end-start)*offset/total,char,text});offset+=weights[i]});
}
const motion=[
 [0,405,190,-.14],[1.1,512,230,-.29],
 [6.45,512,230,-.29],[7.65,1043,550,.09],
 [10.95,1043,550,.09],[11.7,520,691,-.08],
 [13,870,691,.12],[14.7,437,319,-.20],
 [20.7,437,319,-.20],[21.55,1130,550,.04],
 [22.5,1130,550,.04],[24,405,190,-.14]
];
const ease=n=>n*n*(3-2*n);
function press(age){if(age<0||age>.17)return 0;if(age<.038)return ease(age/.038);if(age<.065)return 1;return 1-ease((age-.065)/.105)}
function keyFor(char){
 if(char===' ')return ['space'];if(char==='\n')return ['return'];
 const shifted={'(':'9',')':'0','_':'−','{':'[','}':']',':':';','"':"'"};
 if(shifted[char])return ['shift',shifted[char]];
 return [char==='-'?'−':char.toUpperCase()];
}

// Attach motion to the existing model; the public site's model stays untouched.
export function createStudioInputs(scene,renderer,wrap){
 let keyboard,mouse,screen;
 scene.traverse(o=>{
  if(o.isGroup&&o.children.filter(c=>c.geometry?.parameters?.height===.12&&Math.abs(c.position.y-.174)<.0001).length>50)keyboard=o;
  if(o.isGroup&&Math.abs(o.position.x-2.75)<.001&&o.children.some(c=>c.geometry?.type==='SphereGeometry'))mouse=o;
  if(o.isMesh&&o.material.map?.image?.width===1440&&o.material.map?.image?.height===900)screen=o.material.map;
 });
 if(!keyboard||!mouse||!screen)throw new Error('Studio input model could not be found');
 const caps=keyboard.children.filter(o=>o.geometry?.parameters?.height===.12&&Math.abs(o.position.y-.174)<.0001);
 const legends=keyboard.children.filter(o=>o.geometry?.type==='PlaneGeometry'&&Math.abs(o.position.y-.237)<.0001);
 const labels=rows.flat(),keys=caps.map((mesh,i)=>({mesh,legend:legends[i],label:labels[i],y:mesh.position.y,ly:legends[i]?.position.y}));
 if(caps.length!==labels.length||legends.length!==caps.length)throw new Error('Studio keycaps and legends must match');

 // Keep the lower shell grounded; only the independent front buttons pivot.
 const old=mouse.children.find(o=>o.geometry?.type==='SphereGeometry');
 const shellMaterial=old.material,scale=old.scale.clone();mouse.remove(old);old.geometry.dispose();
 const theta=1.03;
 function shell(phi,length,start,span,parent=mouse){
  const m=new T.Mesh(new T.SphereGeometry(.5,48,28,phi,length,start,span),shellMaterial);
  m.scale.copy(scale);m.castShadow=m.receiveShadow=true;parent.add(m);return m;
 }
 shell(0,Math.PI*2,theta,Math.PI/2-theta);shell(0,Math.PI,0,theta);
 function button(phi){const g=new T.Group();g.position.set(0,.16,.06);mouse.add(g);const m=shell(phi,Math.PI/2,0,theta,g);m.position.set(0,-.16,-.06);return g}
 const left=button(Math.PI*1.5),right=button(Math.PI);
 const wheel=mouse.children.find(o=>o.geometry?.type==='CylinderGeometry');
 mouse.position.y=3.434;
 const source=screen.image,context=source.getContext('2d'),backing=document.createElement('canvas');
 backing.width=source.width;backing.height=source.height;const base=backing.getContext('2d');
 let baseFrame=-1,paintFrame=-1,shadowFrame=-1;
 const prefix='import { studio, verify } from "./workspace"\n\nconst tasks = ["research", "build", "review"]\n\n';
 function drawCode(typed,t){
  context.fillStyle='#131e2e';context.fillRect(18,76,748,510);
  context.fillStyle='#ced9e7';context.font='16px Arial';context.fillText('workspace.ts   ×',35,111);
  context.fillStyle='#2c3d52';context.fillRect(20,127,744,1);
  const lines=(prefix+typed).split('\n');
  lines.forEach((line,i)=>{
   context.font='13px monospace';context.fillStyle='#8196af';context.fillText(String(i+1).padStart(2,' '),34,160+i*24);
   context.font='14px monospace';context.fillStyle=line.startsWith('await')?'#8cc3b2':'#ced9e7';context.fillText(line,77,160+i*24);
  });
  if(Math.floor(t*2)%2===0){const line=lines[lines.length-1];context.font='14px monospace';context.fillStyle='#bfd8ef';context.fillRect(77+context.measureText(line).width,146+(lines.length-1)*24,2,17)}
 }
 function drawCursor(x,y,clicked,dragging){
  context.save();context.translate(x,y);context.lineJoin='round';context.shadowColor='#000a';context.shadowBlur=5;
  context.beginPath();context.moveTo(0,0);context.lineTo(1,27);context.lineTo(8,20);context.lineTo(14,33);context.lineTo(20,30);context.lineTo(14,18);context.lineTo(24,17);context.closePath();
  context.fillStyle=clicked||dragging?'#94bcde':'#f5f7fa';context.strokeStyle='#152131';context.lineWidth=1.8;context.fill();context.stroke();context.restore();
 }
 function update(t){
  const cycle=((t%duration)+duration)%duration;
  let typed='',active=[];
  const depths=new Map();
  for(const event of events){
   const age=cycle-event.at;if(age>=.035)typed=event.text;
   const depth=press(age);if(!depth)continue;
   for(const label of keyFor(event.char)){depths.set(label,Math.max(depths.get(label)||0,depth));if(!active.includes(label))active.push(label)}
  }
  for(const key of keys){const depth=(depths.get(key.label)||0)*.047;key.mesh.position.y=key.y-depth;if(key.legend)key.legend.position.y=key.ly-depth}
  let index=0;while(index<motion.length-2&&cycle>=motion[index+1][0])index++;
  const a=motion[index],b=motion[index+1],u=ease((cycle-a[0])/(b[0]-a[0]));
  const interpolate=i=>T.MathUtils.lerp(a[i],b[i],u);
  const cursorX=interpolate(1),cursorY=interpolate(2),dragging=cycle>=11.68&&cycle<=13.04;
  mouse.position.x=2.2+(cursorX-405)/850;mouse.position.z=.57+(cursorY-190)/600;mouse.rotation.y=interpolate(3);
  const click=Math.max(press(cycle-1.12),press(cycle-7.78),press(cycle-21.66));
  const dragDown=cycle>=11.68&&cycle<=13.16?Math.min(ease(T.MathUtils.clamp((cycle-11.68)/.08,0,1)),1-ease(T.MathUtils.clamp((cycle-13.04)/.12,0,1))):0;
  left.rotation.x=-.067*Math.max(click,dragDown);right.rotation.x=0;
  if(wheel)wheel.rotation.x=cycle>13.3&&cycle<14.2?(cycle-13.3)*1.8:0;
  // Both keycaps and the mouse use the same time as the displayed code and cursor.
  const now=Number(wrap.dataset.screenFrame),newBase=now!==baseFrame;
  if(newBase){baseFrame=now;base.clearRect(0,0,1440,900);base.drawImage(source,0,0)}
  const frame=Math.floor(t*30);
  if(newBase||frame!==paintFrame){
   paintFrame=frame;context.clearRect(0,0,1440,900);context.drawImage(backing,0,0);drawCode(typed,t);
   if(dragging){context.strokeStyle='#c0dbf1';context.lineWidth=2;context.strokeRect(cursorX-48,662,115,40)}
   drawCursor(cursorX,cursorY,click>.3,dragging);screen.needsUpdate=true;
  }
  const shadow=Math.floor(t*24);if(shadow!==shadowFrame){shadowFrame=shadow;renderer.shadowMap.needsUpdate=true}
  wrap.dataset.mousePosition=[mouse.position.x,mouse.position.y,mouse.position.z].map(v=>v.toFixed(3)).join(',');
  wrap.dataset.screenCursor=[cursorX,cursorY].map(v=>v.toFixed(1)).join(',');wrap.dataset.mouseButton=left.rotation.x.toFixed(4);
  wrap.dataset.pressedKeys=active.join(',');wrap.dataset.typedCharacters=String(typed.length);
  wrap.dataset.keyTravel=Math.max(...keys.map(k=>k.y-k.mesh.position.y)).toFixed(4);
  wrap.dataset.mouseAction=dragging?'drag':click>.3?'click':Math.abs(b[1]-a[1])>.01?'move':active.length?'typing':'rest';
  wrap.dataset.keyboardKeys=String(keys.length);
 }
 return {update};
}
