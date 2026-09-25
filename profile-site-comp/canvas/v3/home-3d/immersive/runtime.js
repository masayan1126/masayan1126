import * as T from 'three';
import {RoundedBoxGeometry} from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/examples/jsm/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/examples/jsm/postprocessing/RenderPass.js';
import {SSAOPass} from 'three/examples/jsm/postprocessing/SSAOPass.js';
import {BokehPass} from 'three/examples/jsm/postprocessing/BokehPass.js';
import {OutputPass} from 'three/examples/jsm/postprocessing/OutputPass.js';
import {HDRLoader} from 'three/examples/jsm/loaders/HDRLoader.js';
import {createStudioScene} from '../studio-scene.js';
import {immerseStudio} from './studio-immersive.js';
import {createStudioInputs} from './studio-inputs.js';
import {createMonitorStack} from './studio-monitor-stack.js';
const host=document.querySelector('.immersive-hero');
const canvas=host.querySelector('#scene'),wrap=host.querySelector('.world');
const variant=1,reduce=matchMedia('(prefers-reduced-motion: reduce)');
const INTRO_END=6.4,INTRO_SECONDS=4;
const scene=new T.Scene(),camera=new T.PerspectiveCamera(38,1,.1,160),pointer={x:0,y:0};let renderer,composer,view,env,raf=0,previous=0,t=reduce.matches?INTRO_END:0,paused=reduce.matches,width=1,height=1,ready=false,disposed=false,visible=true;
let studio,inputs,monitorStack,depthOfField;
const focusPoint=new T.Vector3(.1,5.66,-1.8),focusDirection=new T.Vector3();
function render(){if(!ready||disposed)return;view.update(t,pointer,!paused);studio?.update(t,pointer,false,!paused,reduce.matches);inputs?.update(t);monitorStack?.update(t,camera);if(depthOfField){depthOfField.enabled=width>=700;camera.getWorldDirection(focusDirection);depthOfField.uniforms.focus.value=focusPoint.clone().sub(camera.position).dot(focusDirection);depthOfField.uniforms.aperture.value=.00065}composer.render();canvas.dataset.paused=String(paused);canvas.dataset.time=t.toFixed(2);canvas.dataset.rendered='true';canvas.dataset.frame=String(Number(canvas.dataset.frame||0)+1)}
function schedule(){if(!raf&&!document.hidden&&visible&&!disposed&&ready)raf=requestAnimationFrame(tick)}
function tick(now){
 raf=0;
 const dt=previous?Math.max(0,(now-previous)/1000):0;
 previous=now;
 if(!paused){t=Math.min(INTRO_END,t+dt*INTRO_END/INTRO_SECONDS);paused=t>=INTRO_END}
 render();
 if(!paused)schedule()
}
function resize(){if(!ready)return;width=wrap.clientWidth;height=wrap.clientHeight;const dpr=Math.min(devicePixelRatio,width<700?1.4:1.6);renderer.setPixelRatio(dpr);renderer.setSize(width,height,false);composer.setPixelRatio(dpr);composer.setSize(width,height);camera.aspect=width/height;camera.updateProjectionMatrix();if(variant===1)view.resize(camera.aspect);else view.resize(width,height);canvas.dataset.viewport=width+'x'+height;schedule()}
try{
 renderer=new T.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.04;renderer.shadowMap.enabled=variant!==5;renderer.shadowMap.type=T.PCFSoftShadowMap;
 const pmrem=new T.PMREMGenerator(renderer),room=new RoomEnvironment();env=pmrem.fromScene(room,.035);scene.environment=env.texture;room.dispose();pmrem.dispose();
 const key=new T.DirectionalLight(0xfffaf1,3);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.radius=3;scene.add(key,key.target);scene.add(new T.HemisphereLight(0xf9fbff,0x959faa,1.2));const rim=new T.DirectionalLight(0xcddfed,2);rim.position.set(10,8,-8);scene.add(rim);
 if(variant===1){const box=(w,h,d,m,r=.025)=>{const o=new T.Mesh(new RoundedBoxGeometry(w,h,d,3,Math.min(r,w/2,h/2,d/2)),m);o.castShadow=o.receiveShadow=true;return o};view=createStudioScene(T,scene,camera,wrap,{renderer,keyLight:key,requestRender:schedule,box});studio=immerseStudio(scene,camera,renderer,key,wrap);inputs=createStudioInputs(scene,renderer,wrap);monitorStack=createMonitorStack(scene,wrap)}
 renderer.toneMappingExposure=1.13;scene.environmentIntensity=.48;key.intensity=4.9;
 const target=new T.WebGLRenderTarget(1,1,{type:T.HalfFloatType,samples:4});composer=new EffectComposer(renderer,target);composer.addPass(new RenderPass(scene,camera));if(variant<4){const ao=new SSAOPass(scene,camera,512,512,12);ao.kernelRadius=variant===1?.15:.3;ao.minDistance=.0001;ao.maxDistance=.025;composer.addPass(ao)}if(variant===1){depthOfField=new BokehPass(scene,camera,{focus:10,aperture:.00065,maxblur:.008});composer.addPass(depthOfField)}composer.addPass(new OutputPass());
 ready=true;resize();render();host.classList.add('ready');schedule();
 if(variant===1&&canvas.dataset.hdr)new HDRLoader().loadAsync(canvas.dataset.hdr).then(source=>{if(disposed){source.dispose();return}const pm=new T.PMREMGenerator(renderer),next=pm.fromEquirectangular(source);source.dispose();pm.dispose();env.dispose();env=next;scene.environment=env.texture;schedule()}).catch(()=>{});
 new ResizeObserver(resize).observe(wrap);
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;canvas.dataset.offscreen=String(!visible);previous=0;if(visible)schedule();else{cancelAnimationFrame(raf);raf=0}},{threshold:0}).observe(host);
}catch(e){canvas.dataset.error=e.message;host.querySelector('.loading').textContent='3Dを表示できませんでした。再読み込みしてお試しください。';console.error(e)}
reduce.addEventListener('change',()=>{if(reduce.matches){t=INTRO_END;paused=true}previous=0;schedule()});
document.addEventListener('visibilitychange',()=>{previous=0;if(document.hidden){cancelAnimationFrame(raf);raf=0}else schedule()});

window.addEventListener('pagehide',()=>{disposed=true;cancelAnimationFrame(raf);scene.traverse(o=>{o.geometry?.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material]){m?.map?.dispose();m?.dispose()}});for(const pass of composer?.passes||[])pass.dispose?.();composer?.dispose();env?.dispose();renderer?.dispose()});
