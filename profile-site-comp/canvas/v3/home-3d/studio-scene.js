import { studioProps } from './studio-props.js';
import { createAgentScreens } from './agent-screens.js';

export function createStudioScene(T,scene,camera,wrap,api){
 const {renderer,requestRender,keyLight}=api;
 const {M,mesh,at,add,cyl,tex,textPlane,alu,dark,rubber,white,blue,black,grain,keyboard,microphone}=studioProps(T,api);
 const root=new T.Group();scene.add(root);const screens=createAgentScreens(tex);
 scene.background=new T.Color(0xf1f4f8);scene.environmentIntensity=.65;renderer.toneMappingExposure=1.03;
 keyLight.intensity=2.3;keyLight.position.set(-8,13,6);keyLight.target.position.set(0,3,0);keyLight.shadow.mapSize.set(4096,4096);Object.assign(keyLight.shadow.camera,{left:-11,right:11,top:11,bottom:-11,near:.1,far:45});keyLight.shadow.normalBias=.008;keyLight.shadow.bias=-.00002;
 const plaster=M(0xeff1f3,.89,0,{bumpMap:grain,bumpScale:.006});
 at(mesh(new T.PlaneGeometry(100,100),M(0xe2e6eb,.78,0,{roughnessMap:grain}),root),0,0,0,-Math.PI/2);
 add(root,40,19,.25,plaster,0,8,-6.4,.02);add(root,10,18,.22,M(0x103771,.95),7.8,8,-6.17,.02);
 const felt=M(0x133f8f,.93,0,{bumpMap:grain,bumpScale:.01});for(let i=0;i<12;i++)add(root,.73,15,.08,felt,3.2+i*.83,7.7,-6.0,.016);
 add(root,40,.1,.2,alu,0,.2,-6.15,.02);
 const windowGlass=M(0xe7eff8,.17,.15,{emissive:0xd7e6f8,emissiveIntensity:.17,clearcoat:.9});add(root,.22,16,14,plaster,-12,7,-1,.025);
 for(let i=0;i<3;i++){add(root,.025,8,3.4,windowGlass,-11.86,7,-4+i*3.55,.01);add(root,.16,8.5,.065,alu,-11.75,7,-5.76+i*3.55,.012)}
 add(root,.22,.07,11,alu,-11.73,3,-2,.01);
 const wallLight=new T.SpotLight(0xedf4ff,90,40,.65,.6,1);wallLight.position.set(-9,11,4);wallLight.target.position.set(3,5,-6);scene.add(wallLight,wallLight.target);
 const desk=new T.Group();root.add(desk);const tabletop=M(0xe7e9ec,.36,.08,{roughnessMap:grain,clearcoat:.17,clearcoatRoughness:.32});
 add(desk,14,.24,6.2,tabletop,0,3.28,0,.065);add(desk,13.96,.07,6.16,alu,0,3.13,0,.025);
 for(const x of [-5.3,5.3]){add(desk,.38,2.75,.65,white,x,1.6,-.25,.045);add(desk,.3,1.6,.56,alu,x,2.3,-.25,.025);add(desk,.6,.18,4.5,white,x,.14,0,.05);for(const z of [-1.9,1.9])add(desk,.52,.05,.4,rubber,x,.025,z,.02)}
 add(desk,10.6,.25,.48,white,0,2.95,-.25,.04);
 const textile=tex(512,512,(c,w,h)=>{c.fillStyle='#213e66';c.fillRect(0,0,w,h);c.lineWidth=1;for(let n=0;n<512;n+=3){c.strokeStyle=n%2?'#29486f':'#1c3558';c.beginPath();c.moveTo(n,0);c.lineTo(n,512);c.stroke();c.beginPath();c.moveTo(0,n);c.lineTo(512,n);c.stroke()}});textile.wrapS=textile.wrapT=T.RepeatWrapping;textile.repeat.set(5,3);
 add(desk,7,.028,2.62,M(0xffffff,.93,0,{map:textile,bumpMap:textile,bumpScale:.006}),.1,3.417,.93,.1);
 const kb=keyboard();desk.add(kb);at(kb,-.48,3.522,.9,0,-.035,0);
 const mouse=new T.Group();desk.add(mouse);at(mouse,2.75,3.47,.94,0,-.14,0);const shell=mesh(new T.SphereGeometry(.5,56,32,0,Math.PI*2,0,Math.PI/2),white,mouse);shell.scale.set(.65,.45,1.1);add(mouse,.018,.012,.43,dark,0,.204,-.19,.004);const wheel=cyl(mouse,.09,.09,.058,rubber,0,.208,-.14);wheel.rotation.z=Math.PI/2;
 const mon=new T.Group();desk.add(mon);at(mon,.1,5.66,-1.9);add(mon,6.7,2.91,.16,dark,0,0,0,.09);add(mon,6.66,2.87,.035,alu,0,0,-.098,.07);add(mon,6.57,2.78,.018,black,0,0,.091,.035);
 const screenMaterial=new T.MeshBasicMaterial({map:screens.main,toneMapped:false});at(mesh(new T.PlaneGeometry(6.47,2.68),screenMaterial,mon),0,.015,.103);
 cyl(mon,.016,.016,.008,M(0x779bbb,.22,0,{emissive:0x3c6288,emissiveIntensity:.5}),3.13,-1.375,.1,Math.PI/2);textPlane(mon,'MIYABIYA',.34,.04,0,-1.397,.107,'#8392a2',30);
 add(desk,.26,.87,.22,alu,.1,3.88,-2.02,.04);cyl(desk,.12,.12,.6,alu,.1,4.32,-1.92).rotation.z=Math.PI/2;add(desk,2.14,.085,1.13,alu,.1,3.445,-1.8,.07);add(desk,.4,.65,.22,alu,.1,4.64,-2.04,.035);
 const monitorCable=new T.CatmullRomCurve3([new T.Vector3(.45,4.95,-2.04),new T.Vector3(.49,4.2,-2.25),new T.Vector3(.8,3.48,-2.3),new T.Vector3(1.8,3.46,-2.8)]);mesh(new T.TubeGeometry(monitorCable,40,.026,8,false),rubber,desk);
 // Each screen has its own bezel, back shell, hinge, grounded stand and cable.
 function extraMonitor(texture,w,h,x,y,z,yaw){
  const g=new T.Group();desk.add(g);at(g,x,y,z,0,yaw,0);
  add(g,w+.15,h+.15,.15,dark,0,0,0,.075);add(g,w+.1,h+.1,.028,alu,0,0,-.093,.06);add(g,w+.035,h+.035,.016,black,0,0,.084,.018);
  at(mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:texture,toneMapped:false}),g),0,0,.096);
  textPlane(g,'MIYABIYA',.29,.034,0,-h/2-.04,.098,'#8090a0',30);
  const base=3.445-y,top=-h/2+.46;
  add(g,.27,top-base,.21,alu,0,(top+base)/2,-.11,.035);
  add(g,1.65,.085,1.02,alu,0,base,.15,.06);
  const wire=new T.CatmullRomCurve3([new T.Vector3(.36,-h/2+.5,-.11),new T.Vector3(.4,base+.55,-.19),new T.Vector3(.7,base+.04,-.33),new T.Vector3(1.1,base+.025,-.65)]);
  mesh(new T.TubeGeometry(wire,32,.022,8,false),rubber,g);return g;
 }
 extraMonitor(screens.portrait,2.34,3.94,-4.55,5.72,-1.75,.2);
 extraMonitor(screens.work,4.38,2.74,5.68,5.57,-1.32,-.44);
 const mic=microphone();desk.add(mic);at(mic,-5.4,4.68,.16,0,-.25,0);
 mic.updateMatrixWorld(true);const attachment=mic.children[0].localToWorld(new T.Vector3(0,-.7,0));
 const boomPoints=[new T.Vector3(-5.65,3.52,-2.4),new T.Vector3(-5.65,4.05,-2.4),new T.Vector3(-5.9,4.2,-.25),attachment];
 for(let i=0;i<boomPoints.length-1;i++){const a=boomPoints[i],b=boomPoints[i+1],d=b.clone().sub(a),o=add(desk,.17,d.length(),.21,dark,0,0,0,.045);o.position.copy(a).add(b).multiplyScalar(.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());const j=cyl(desk,.16,.16,.23,alu,b.x,b.y,b.z);j.rotation.z=Math.PI/2}
 add(desk,.35,.5,.56,dark,-5.65,3.34,-2.78,.04);const micCable=new T.CatmullRomCurve3([...boomPoints.map(p=>p.clone().add(new T.Vector3(0,.09,.12))),attachment.clone().add(new T.Vector3(.1,.25,-.15)),new T.Vector3(-5.4,4.63,-.44)]);mesh(new T.TubeGeometry(micCable,70,.021,8,false),rubber,desk);
 const audio=new T.Group();desk.add(audio);at(audio,4.5,3.62,1.47,0,-.13,0);add(audio,1.55,.36,1.1,alu,0,0,0,.075);add(audio,1.42,.29,.025,dark,0,0,.564,.018);
 for(const x of [-.45,-.06]){cyl(audio,.124,.124,.035,alu,x,-.035,.59,Math.PI/2);cyl(audio,.083,.083,.04,black,x,-.035,.617,Math.PI/2);for(let i=0;i<3;i++){const a=i*2.094;cyl(audio,.012,.012,.007,alu,x+Math.cos(a)*.04,-.035+Math.sin(a)*.04,.64,Math.PI/2)}}
 cyl(audio,.23,.23,.095,dark,.34,.225,-.05);cyl(audio,.21,.21,.012,alu,.34,.28,-.05);for(let i=0;i<48;i++){const a=i/48*Math.PI*2;add(audio,.009,.08,.012,alu,.34+Math.cos(a)*.233,.227,-.05+Math.sin(a)*.233,.002)}add(audio,.018,.008,.07,blue,.34,.29,-.17,.002);
 const meters=[];for(let j=0;j<2;j++)for(let i=0;i<8;i++){const material=M(0x749dbc,.3,0,{emissive:0x4786bd,emissiveIntensity:.2});meters.push(add(audio,.041,.005,.047,material,-.5+i*.06,.187,-.1+j*.13,.002))}
 add(desk,1.6,.075,2.05,blue,-5.38,3.449,.95,.03);add(desk,1.5,.06,1.97,white,-5.4,3.507,.95,.017);add(desk,1.6,.035,2.05,blue,-5.38,3.553,.95,.022);const pen=cyl(desk,.027,.027,1.35,alu,-5.38,3.595,.95);pen.rotation.x=Math.PI/2;pen.rotation.z=-.16;
 const cup=new T.Group();desk.add(cup);at(cup,5.85,3.42,.6);const ceramic=M(0xf4f3ef,.19,0,{clearcoat:.35});const cupProfile=[[.28,0],[.33,.035],[.36,.6],[.347,.63],[.323,.625],[.308,.11],[.28,.09]].map(([r,y])=>new T.Vector2(r,y));mesh(new T.LatheGeometry(cupProfile,80),ceramic,cup);cyl(cup,.318,.318,.014,M(0x2b1d18,.16),0,.49,0);const handle=mesh(new T.TorusGeometry(.17,.045,12,48),ceramic,cup);at(handle,.42,.36,0);
 let aspect=1,narrow=false,detail=false,selected='tour',time=0,lastFrame=-1,initialized=false,transition=1;let currentPos=new T.Vector3(),currentAim=new T.Vector3(),fromPos=new T.Vector3(),fromAim=new T.Vector3();const focus=new T.Vector3(),desiredPos=new T.Vector3(),desiredAim=new T.Vector3();
 const status=document.querySelector('#scene-status'),detailButton=document.querySelector('#view-detail'),shotButtons=[...document.querySelectorAll('[data-shot]')];const names={tour:'作業場を巡る',develop:'開発の手元へ',create:'撮影と発信へ'};const shots={develop:{pos:[-.9,6.1,8.2],aim:[-.3,5,-1]},create:{pos:[8.4,6.6,8.6],aim:[3.6,5,-.9]}};
 function switchShot(id){selected=id;fromPos.copy(currentPos);fromAim.copy(currentAim);transition=0;shotButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.shot===id)));if(status)status.textContent=names[id];requestRender()}
 shotButtons.forEach(b=>b.addEventListener('click',()=>switchShot(b.dataset.shot)));detailButton?.addEventListener('click',()=>{detail=!detail;detailButton.setAttribute('aria-pressed',String(detail));detailButton.textContent=detail?'全景へ戻る':'中へ入る';document.body.classList.toggle('immersed',detail);switchShot(detail?'develop':'tour')});
 const tourPos=new T.CatmullRomCurve3([[6.3,7.1,15],[2.7,6.7,13.5],[-2.5,6.5,13],[-3.8,6.7,13.7],[2,7,14.2],[6,6.8,14.3]].map(v=>new T.Vector3(...v)),true,'catmullrom',.25);const tourAim=new T.CatmullRomCurve3([[.7,4.85,-.2],[.65,4.85,-.2],[.6,4.85,-.3],[.6,4.85,-.3],[.7,4.85,-.2],[.8,4.85,-.15]].map(v=>new T.Vector3(...v)),true,'catmullrom',.2);
 function frame(t,p,moving){
  const dt=Math.max(0,Math.min(t-time,.15));time=t;const mobile=narrow;if(lastFrame!==Math.floor(t*10)){lastFrame=Math.floor(t*10);screens.update(t);meters.forEach((m,i)=>m.material.emissiveIntensity=.08+(Math.sin(t*6+i*.77)>.05?1.6:.05))}
  if(selected==='tour'){tourPos.getPoint((t/52)%1,desiredPos);tourAim.getPoint((t/52)%1,desiredAim)}else{desiredPos.fromArray(shots[selected].pos);desiredAim.fromArray(shots[selected].aim);desiredPos.x+=Math.sin(t*.11)*.36;desiredPos.z+=Math.cos(t*.095)*.23}
  if(detail){desiredPos.sub(desiredAim).multiplyScalar(.84).add(desiredAim);desiredAim.y+=.16}if(mobile){if(selected==='tour'){desiredAim.set(1.05,4.9,-1);desiredPos.set(1.45+Math.sin(t*.09)*.7,3.2,23.4).normalize().multiplyScalar(15.6/(.84895*aspect)).add(desiredAim)}else{const delta=desiredPos.clone().sub(desiredAim).multiplyScalar(1.35);desiredPos.copy(desiredAim).add(delta);desiredAim.y+=.18}camera.fov=46}else camera.fov=42;camera.updateProjectionMatrix();desiredPos.x+=p.x*.3;desiredPos.y-=p.y*.12;
  if(!initialized){currentPos.copy(desiredPos);currentAim.copy(desiredAim);initialized=true}if(!moving)transition=1;else transition=Math.min(1,transition+dt/1.65);const ease=transition*transition*(3-2*transition);currentPos.lerpVectors(fromPos,desiredPos,ease);currentAim.lerpVectors(fromAim,desiredAim,ease);camera.position.copy(currentPos);camera.lookAt(currentAim);focus.copy(currentAim);
  wrap.dataset.shot=selected;wrap.dataset.motionPhase=t.toFixed(3);wrap.dataset.focusDistance=camera.position.distanceTo(focus).toFixed(3);wrap.dataset.agentCount=screens.state.count;wrap.dataset.screenFrame=screens.state.frame;wrap.dataset.monitors='2 landscape / 1 portrait';const progress=document.querySelector('.tour-progress');if(progress)progress.style.transform=`scaleX(${(t%52)/52})`;
 }
 return{resize(r){aspect=r;narrow=typeof wrap.clientWidth==='number'?wrap.clientWidth<760:r<1.15},update:frame,getFocus:()=>camera.position.distanceTo(focus),dispose(){}};
}
