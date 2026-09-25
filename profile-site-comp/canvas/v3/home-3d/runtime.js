import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { SSAOPass } from 'three/examples/jsm/postprocessing/SSAOPass.js';
import { BokehPass } from 'three/examples/jsm/postprocessing/BokehPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { HDRLoader } from 'three/examples/jsm/loaders/HDRLoader.js';
import { createStudioScene } from './studio-scene.js';

const canvas=document.querySelector('#scene'),wrap=canvas.parentElement;
const mode=document.querySelector('#mode-toggle'),motion=document.querySelector('#motion-toggle'),detail=document.querySelector('#view-detail');
const state=document.querySelector('#render-state'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(42,1,.1,180);
let renderer,composer,ao,bokeh,view,environment,raf=0,previous=0,elapsed=reduced.matches?18:0,paused=reduced.matches,enabled=true,visible=true,ready=false,disposed=false,failed=false;
const pointer={x:0,y:0},smoothPointer={x:0,y:0};let resizeObserver,intersectionObserver;
function sync(){
 document.body.classList.toggle('three-off',!enabled);document.body.classList.toggle('motion-paused',paused);
 mode.textContent=enabled?'3D ON':'3D OFF';mode.setAttribute('aria-pressed',String(enabled));mode.setAttribute('aria-label',enabled?'3D表示をオフにする':'3D表示をオンにする');mode.disabled=failed||!ready;
 motion.textContent=reduced.matches?'動きを抑えて表示中':paused?'動きを再開':'動きを停止';motion.setAttribute('aria-pressed',String(!paused));motion.disabled=reduced.matches||!enabled||!ready;
 document.querySelectorAll('[data-camera-control]').forEach(b=>b.disabled=!ready||failed||!enabled);
}
function schedule(){if(!raf&&enabled&&visible&&!document.hidden&&!disposed&&ready)raf=requestAnimationFrame(draw)}
function render(){bokeh.enabled=document.body.classList.contains('immersed')&&wrap.clientWidth>=760;bokeh.uniforms.focus.value=view.getFocus();composer.render();canvas.dataset.rendered='true';canvas.dataset.elapsed=elapsed.toFixed(3);canvas.dataset.camera=camera.position.toArray().map(n=>n.toFixed(2)).join(',')}
function draw(now){
 raf=0;if(!enabled||!visible||document.hidden||disposed)return;
 const dt=previous?Math.min((now-previous)/1000,.15):0;previous=now;if(!paused)elapsed+=dt;
 smoothPointer.x+=(pointer.x-smoothPointer.x)*.055;smoothPointer.y+=(pointer.y-smoothPointer.y)*.055;
 view.update(elapsed,smoothPointer,!paused);render();if(!paused)schedule();
}
function resize(){
 const width=wrap.clientWidth,height=wrap.clientHeight;if(!width||!height||!ready)return;
 const dpr=Math.min(devicePixelRatio,width<760?1.5:1.75);renderer.setPixelRatio(dpr);renderer.setSize(width,height,false);composer.setPixelRatio(dpr);composer.setSize(width,height);ao.setSize(Math.round(width*dpr*.7),Math.round(height*dpr*.7));camera.aspect=width/height;camera.updateProjectionMatrix();view.resize(camera.aspect);canvas.dataset.viewport=width+'x'+height;schedule();
}
async function lighting(){
 try{const source=await new HDRLoader().loadAsync(canvas.dataset.environment);if(disposed){source.dispose();return}const pmrem=new THREE.PMREMGenerator(renderer),next=pmrem.fromEquirectangular(source);source.dispose();pmrem.dispose();environment.dispose();environment=next;scene.environment=environment.texture;scene.environmentRotation.y=.6;schedule()}catch{/* The local room environment remains a complete lighting fallback. */}
}
function fail(error){console.error('Studio scene could not start:',error);failed=true;enabled=false;ready=false;state.textContent='3Dを表示できないため、プロフィール写真を表示しています。';sync()}
function start(){
 try{
  renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=true;
  canvas.dataset.engine='Three.js WebGLRenderer';canvas.dataset.renderer=renderer.getContext().getParameter(renderer.getContext().VERSION);
  const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();environment=pmrem.fromScene(room,.035);scene.environment=environment.texture;room.dispose();pmrem.dispose();
  const key=new THREE.DirectionalLight(0xffffff,2.3);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.radius=4;scene.add(key,key.target);scene.add(new THREE.HemisphereLight(0xffffff,0xa3a9b0,.85));const fill=new THREE.DirectionalLight(0xe8efff,.65);fill.position.set(12,6,-9);scene.add(fill);
  const box=(w,h,d,m,r=.025)=>{const mesh=new THREE.Mesh(new RoundedBoxGeometry(w,h,d,3,Math.min(r,w/2,h/2,d/2)),m);mesh.castShadow=mesh.receiveShadow=true;return mesh};
  view=createStudioScene(THREE,scene,camera,wrap,{box,renderer,keyLight:key,requestRender:schedule});
  // The apparatus does not move; cache its shadow map while the camera travels.
  key.shadow.mapSize.set(wrap.clientWidth<760?2048:4096,wrap.clientWidth<760?2048:4096);
  const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:4});composer=new EffectComposer(renderer,target);composer.addPass(new RenderPass(scene,camera));ao=new SSAOPass(scene,camera,512,512,16);ao.kernelRadius=.16;ao.minDistance=.0001;ao.maxDistance=.018;composer.addPass(ao);bokeh=new BokehPass(scene,camera,{focus:14,aperture:.0003,maxblur:.002});bokeh.enabled=false;composer.addPass(bokeh);composer.addPass(new OutputPass());
  ready=true;resize();view.update(elapsed,smoothPointer,!paused);render();document.body.classList.add('scene-ready');sync();lighting();
  resizeObserver=new ResizeObserver(resize);resizeObserver.observe(wrap);
  intersectionObserver=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;previous=0;if(visible)schedule();else{cancelAnimationFrame(raf);raf=0}},{threshold:.01});intersectionObserver.observe(wrap);schedule();
 }catch(error){fail(error)}
}
mode.addEventListener('click',()=>{enabled=!enabled;previous=0;if(!enabled){cancelAnimationFrame(raf);raf=0;state.textContent='プロフィール写真を表示しています。'}else{state.textContent='3Dの作業場を表示しています。';schedule()}sync()});
motion.addEventListener('click',()=>{if(reduced.matches)return;paused=!paused;previous=0;sync();schedule()});
detail.addEventListener('click',()=>{requestAnimationFrame(()=>{document.querySelector('.studio-frame').scrollIntoView({block:'start',behavior:reduced.matches?'instant':'smooth'})})});
reduced.addEventListener('change',()=>{paused=reduced.matches;previous=0;sync();schedule()});
document.addEventListener('visibilitychange',()=>{previous=0;if(document.hidden){cancelAnimationFrame(raf);raf=0}else schedule()});
wrap.addEventListener('pointermove',e=>{if(paused||e.pointerType==='touch')return;const r=wrap.getBoundingClientRect();pointer.x=(e.clientX-r.left)/r.width-.5;pointer.y=(e.clientY-r.top)/r.height-.5},{passive:true});wrap.addEventListener('pointerleave',()=>{pointer.x=pointer.y=0},{passive:true});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fail(new Error('WebGL context lost'))});
window.addEventListener('pagehide',event=>{cancelAnimationFrame(raf);raf=0;previous=0;if(event.persisted)return;disposed=true;resizeObserver?.disconnect();intersectionObserver?.disconnect();const geometries=new Set(),materials=new Set(),textures=new Set();scene.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m))});materials.forEach(m=>{Object.values(m).forEach(v=>{if(v?.isTexture)textures.add(v)});m.dispose()});geometries.forEach(g=>g.dispose());textures.forEach(t=>t.dispose());view?.dispose();ao?.dispose();bokeh?.dispose();composer?.dispose();environment?.dispose();renderer?.dispose()});
window.addEventListener('pageshow',e=>{if(e.persisted){previous=0;schedule()}});
// Preserve text and portrait until the scene has rendered its first frame.
start();
