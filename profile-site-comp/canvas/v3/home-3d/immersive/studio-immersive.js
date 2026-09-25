import * as T from 'three';
import {RectAreaLightUniformsLib} from 'three/examples/jsm/lights/RectAreaLightUniformsLib.js';

// These changes belong to the local hero proposal, not the public studio model.
export function immerseStudio(scene,camera,renderer,key,wrap){
 RectAreaLightUniformsLib.init();
 scene.background=new T.Color(0x151b21);
 scene.environmentIntensity=.34;
 renderer.toneMappingExposure=.94;
 scene.traverse(o=>{
  if(o.isGroup&&o.children.some(c=>c.geometry?.type==='LatheGeometry'))o.position.set(6.05,3.42,-.65);
  if(o.isHemisphereLight)o.intensity=.22;
  if(o.isDirectionalLight&&o!==key){o.intensity=1.5;o.color.setHex(0xd8e9ff)}
  if(o.isSpotLight){o.intensity=65;o.color.setHex(0xe8f0ff)}
  if(!o.isMesh||!o.material.color)return;
  const hex=o.material.color.getHex();
  if(hex===0xb5bec8){o.material.anisotropy=0;o.material.roughness=.46;o.material.envMapIntensity=.7}
  if(o.position.z<-5&&hex===0xeff1f3)o.material.color.setHex(0x56616c);
  if(o.position.z<-5&&hex===0x103771)o.material.color.setHex(0x111e2c);
  if(o.position.z<-5&&hex===0x133f8f)o.material.color.setHex(0x243e59);
  if(hex===0xe2e6eb)o.material.color.setHex(0x38434d);
  if(hex===0xe7e9ec){o.material.color.setHex(0xc2c9cd);o.material.roughness=.3;o.material.clearcoat=.25}
  if(hex===0xf4f3ef){o.material.roughness=.3;o.material.clearcoatRoughness=.25}
  if(o.geometry.parameters?.width===.009&&o.geometry.parameters?.height===.08){o.material=o.material.clone();o.material.roughness=.7;o.material.envMapIntensity=.45;o.castShadow=false}
 });
 key.intensity=4.1;key.color.setHex(0xfff4e4);key.position.set(-7,12,3);
 key.target.position.set(.5,3.5,-1);
 key.shadow.mapSize.set(3072,3072);key.shadow.radius=3;
 renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=true;
 const fill=new T.RectAreaLight(0xd5e6ff,4.2,6,2.5);
 fill.position.set(.1,5.6,-1.63);fill.lookAt(.1,3.4,1.6);scene.add(fill);
 const portraitLight=new T.RectAreaLight(0xccddf5,2.8,2,3.6);
 portraitLight.position.set(-4.5,5.5,-1.48);portraitLight.lookAt(-3.5,3.4,1.5);scene.add(portraitLight);
 const softbox=new T.RectAreaLight(0xf8f9ff,6,10,3);
 softbox.position.set(0,10,1.5);softbox.lookAt(0,3.2,-1);scene.add(softbox);
 // A real wall wash, with narrow strips and their shadows instead of a screen glow.
 const wash=new T.SpotLight(0xf1f6ff,160,25,.58,.75,1.6);
 wash.position.set(8.5,9,-3.5);wash.target.position.set(6,5,-6);scene.add(wash,wash.target);

 const desktopPath=new T.CatmullRomCurve3([
  [4.7,4.04,3.8],[3.2,5.2,6.5],[.6,7.3,11.2],[-3.6,8.8,14.1]
 ].map(v=>new T.Vector3(...v)),false,'catmullrom',.3);
 const mobilePath=new T.CatmullRomCurve3([
  [2.4,4.8,4.8],[1.2,6.1,8],[-.2,7.6,12],[-.8,8.1,15.5]
 ].map(v=>new T.Vector3(...v)),false,'catmullrom',.3);
 const narrowPath=new T.CatmullRomCurve3([
  [4.7,4.04,3.8],[4.5,5.7,7.1],[3.9,7.2,11],[3.2,8.1,14.2]
 ].map(v=>new T.Vector3(...v)),false,'catmullrom',.3);
 const pos=new T.Vector3(),aim=new T.Vector3(),p=new T.Vector2();
 const enterPos=new T.Vector3(),enterAim=new T.Vector3();
 let blend=0,prev=0,lastPhase='';
 function update(t,pointer,active,moving,reduce){
  const w=wrap.clientWidth,h=wrap.clientHeight,mobile=w<700,narrow=w/h<1.15;
  const dt=Math.min(.08,Math.max(0,t-prev));prev=t;
  const progress=reduce?1:T.MathUtils.clamp(t/6.4,0,1);
  const u=1-Math.pow(1-progress,2.5);
  const phase=progress<1?'arrival':'settled';
  if(phase!==lastPhase){wrap.closest(".immersive-hero").dataset.studioPhase=phase;lastPhase=phase}
  p.lerp(new T.Vector2(pointer.x,pointer.y),moving?1-Math.exp(-dt*3.2):1);
  const path=mobile?mobilePath:narrow?narrowPath:desktopPath;
  path.getPoint(u,pos);
  const drift=Math.max(0,t-6.4);
  if(!mobile&&!narrow){
   pos.x+=Math.sin(drift*.08)*1.45*u;pos.z+=(Math.cos(drift*.08)-1)*.5*u;
   pos.y+=Math.sin(drift*.10)*.13*u;
   aim.set(T.MathUtils.lerp(-.4,1.0,u),T.MathUtils.lerp(4.9,6.6,u),-1.0);
  }else if(narrow&&!mobile){
   pos.x+=Math.sin(drift*.10)*.5*u;aim.set(-.6,T.MathUtils.lerp(4.85,6.7,u),-1.1);
  }else{
   pos.x+=Math.sin(drift*.11)*.32*u;aim.set(.1,T.MathUtils.lerp(4.9,6.9,u),-1.1);
  }
  pos.x+=p.x*.95;pos.y-=p.y*.3;
  aim.x+=p.x*.36;aim.y-=p.y*.16;
  const desired=active?1:0;
  blend=moving?T.MathUtils.damp(blend,desired,2.2,dt):desired;
  if(Math.abs(blend-desired)<.001)blend=desired;
  enterPos.set(.45+p.x*3.4,7.65-p.y*.6,mobile||narrow?14.8:10.7);
  enterAim.set(.5+p.x*5.8,6.65-p.y*1.8,-1.7);
  pos.lerp(enterPos,blend);aim.lerp(enterAim,blend);
  camera.clearViewOffset();
  camera.fov=T.MathUtils.lerp(mobile?57:narrow?58:48,mobile?66:68,blend);
  camera.position.copy(pos);camera.lookAt(aim);camera.aspect=w/h;camera.updateProjectionMatrix();
  const ox=(mobile?0:narrow?-.06:-.12)*(1-blend);
  const oy=(mobile?-.07:narrow?-.10:-.055)*(1-blend);
  camera.setViewOffset(w,h,w*ox,h*oy,w,h);
  wrap.dataset.camera=pos.toArray().map(n=>n.toFixed(2)).join(',');
  wrap.dataset.arrival=progress.toFixed(3);wrap.dataset.immersion=blend.toFixed(3);
 }
 return {update};
}
