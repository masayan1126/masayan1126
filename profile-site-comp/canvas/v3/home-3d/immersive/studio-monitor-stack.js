import * as T from 'three';
import {RoundedBoxGeometry} from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import {createAgentScreens} from '../agent-screens.js';

// Extend the proposal without changing the model used by the public homepage.
export function createMonitorStack(scene,wrap){
 const lower=[];
 scene.traverse(o=>{
  if(o.geometry?.type==='PlaneGeometry'&&o.material.map?.image?.getContext){
   const {width,height}=o.material.map.image;
   if((width===1920&&height===840)||(width===900&&height===1500)||(width===1440&&height===900))lower.push(o);
  }
 });
 if(lower.length!==3)throw new Error('The three lower monitor screens must be present');
 const texture=(w,h,draw)=>{const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;return t};
 const screens=createAgentScreens(texture);
 const metal=new T.MeshPhysicalMaterial({color:0x8b959f,metalness:.86,roughness:.38,envMapIntensity:.65});
 const graphite=new T.MeshStandardMaterial({color:0x1b222a,metalness:.65,roughness:.46});
 const cable=new T.MeshStandardMaterial({color:0x15191f,roughness:.83});
 function add(parent,geometry,material,pos){const m=new T.Mesh(geometry,material);m.position.fromArray(pos);m.castShadow=m.receiveShadow=true;parent.add(m);return m}
 function box(parent,w,h,d,material,pos,r=.025){return add(parent,new RoundedBoxGeometry(w,h,d,3,Math.min(r,w/2,h/2,d/2)),material,pos)}
 function cylinder(parent,r,h,material,pos){return add(parent,new T.CylinderGeometry(r,r,h,32),material,pos)}
 function arm(parent,a,b,r=.067){const delta=b.clone().sub(a);const m=cylinder(parent,r,delta.length(),graphite,a.clone().add(b).multiplyScalar(.5).toArray());m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize());return m}
 const upper=[];
 for(const source of lower){
  const base=source.parent,desk=base.parent,{width:w,height:h}=source.geometry.parameters;
  const portrait=h>w,wide=w>5,materialMap=portrait?screens.portrait:wide?screens.main:screens.work;
  const g=new T.Group();g.name='upper-monitor-'+(portrait?'portrait':wide?'main':'work');desk.add(g);
  g.position.copy(base.position);g.position.y+=h+(wide?.35:.26);g.rotation.y=base.rotation.y;g.rotation.x=.055;
  // Reuse the exact enclosure and printed bezel, excluding the lower stand/cable.
  for(const child of base.children){
   if(child.geometry?.type==='TubeGeometry')continue;
   if(child.position.z<-.105)continue;
   const copy=child.clone();
   if(child===source){copy.material=child.material.clone();copy.material.map=materialMap;copy.name='upper-screen';upper.push(copy)}
   g.add(copy);
  }
  // The lower side-monitor bases sit inside their groups, unlike the main base.
  for(const child of [...g.children])if(child.position.y < -h/2-.12)g.remove(child);
  box(g,.64,.64,.06,graphite,[0,0,-.145]);
  for(const x of [-.24,.24])for(const y of [-.24,.24]){const screw=cylinder(g,.032,.018,metal,[x,y,-.184]);screw.rotation.x=Math.PI/2}
  const mount=new T.Group();mount.name='dual-monitor-arm';desk.add(mount);
  mount.position.set(base.position.x,0,base.position.z-.55);mount.rotation.y=base.rotation.y;
  const top=g.position.y+.32;
  cylinder(mount,.086,top-3.42,graphite,[0,(top+3.42)/2,0]);
  cylinder(mount,.091,.08,metal,[0,top,0]);
  box(mount,.54,.1,.72,graphite,[0,3.46,-.12],.03);
  box(mount,.14,.36,.66,graphite,[0,3.23,-.2],.025);
  box(mount,.52,.08,.56,graphite,[0,3.015,-.14],.02);
  cylinder(mount,.051,.35,metal,[0,3.13,-.23]);
  for(const y of [base.position.y,g.position.y]){
   cylinder(mount,.14,.24,metal,[0,y,0]);
   arm(mount,new T.Vector3(0,y,.06),new T.Vector3(.08,y-.08,.38));
   const hinge=cylinder(mount,.12,.29,graphite,[.08,y-.08,.39]);hinge.rotation.z=Math.PI/2;
  }
  const route=new T.CatmullRomCurve3([
   [.23,g.position.y-.18,.38],[.3,g.position.y-.5,.06],[.16,g.position.y-1,-.12],
   [.14,4.1,-.12],[.21,3.48,-.27],[.54,3.39,-.55]
  ].map(p=>new T.Vector3(...p)));
  add(mount,new T.TubeGeometry(route,64,.024,8,false),cable,[0,0,0]);
  for(let y=4.1;y<top-.5;y+=1.35)box(mount,.23,.075,.23,cable,[0,y,0],.015);
 }
 const all=[...lower,...upper],projected=new T.Vector3();
 wrap.dataset.monitorCount=String(all.length);wrap.dataset.monitorRows='3 lower / 3 upper';
 let last=-1;
 function update(t,camera){
  screens.update(t+17);
  wrap.dataset.monitors='4 landscape / 2 portrait';wrap.dataset.upperScreenFrame=String(screens.state.frame);
  const frame=[Math.floor(t*2),wrap.clientWidth,wrap.clientHeight,wrap.dataset.immersion].join('/');
  if(frame!==last){last=frame;scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);wrap.dataset.monitorCenters=JSON.stringify(all.map(s=>{s.getWorldPosition(projected);projected.project(camera);return [projected.x,projected.y,projected.z].map(n=>Number(n.toFixed(3)))}))}
 }
 return {update};
}
