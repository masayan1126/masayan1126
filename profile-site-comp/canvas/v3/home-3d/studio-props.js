// Purpose-built, physically proportioned equipment for the immersive studio.
export function studioProps(T, api) {
 const {box,renderer}=api;
 const M=(color,roughness=.4,metalness=0,extra={})=>new T.MeshPhysicalMaterial({color,roughness,metalness,...extra});
 const mesh=(g,m,p)=>{const o=new T.Mesh(g,m);o.castShadow=o.receiveShadow=true;p?.add(o);return o};
 const at=(o,x,y,z,rx=0,ry=0,rz=0)=>{o.position.set(x,y,z);o.rotation.set(rx,ry,rz);return o};
 const add=(p,w,h,d,m,x,y,z,r=.025)=>{const o=box(w,h,d,m,r);p.add(o);return at(o,x,y,z)};
 const cyl=(p,r1,r2,h,m,x=0,y=0,z=0,rx=0)=>at(mesh(new T.CylinderGeometry(r1,r2,h,80),m,p),x,y,z,rx);
 const tex=(w,h,fn)=>{const c=document.createElement('canvas');c.width=w;c.height=h;fn(c.getContext('2d'),w,h);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return t};
 let seed=701;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 const grain=tex(512,512,(c,w,h)=>{c.fillStyle='#e4e4e4';c.fillRect(0,0,w,h);for(let i=0;i<75000;i++){const n=210+rand()*45;c.fillStyle=`rgb(${n},${n},${n})`;c.fillRect(rand()*w,rand()*h,1+rand(),1+rand())}});grain.colorSpace=T.NoColorSpace;grain.wrapS=grain.wrapT=T.RepeatWrapping;grain.repeat.set(6,6);
 const leather=grain.clone();leather.repeat.set(2.5,2.5);leather.needsUpdate=true;
 const alu=M(0xb5bec8,.39,1,{roughnessMap:grain,anisotropy:.4});
 const dark=M(0x20242b,.58,.25,{roughnessMap:grain});
 const rubber=M(0x15191c,.88,0,{bumpMap:leather,bumpScale:.012});
 const white=M(0xe9ebed,.43,.12,{roughnessMap:grain});
 const blue=M(0x133f8f,.3,.35,{clearcoat:.35,clearcoatRoughness:.28});
 const black=M(0x070b0e,.48,.12);
 const textPlane=(p,text,w,h,x,y,z,color='#a9b1bb',font=32)=>{
  const t=tex(512,128,(c)=>{c.fillStyle=color;c.font=`500 ${font}px Arial`;c.textAlign='center';c.textBaseline='middle';c.fillText(text,256,64)});
  const o=mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:t,transparent:true,depthWrite:false,toneMapped:false}),p);return at(o,x,y,z);
 };
 const ring=(p,r,t,m,z)=>at(mesh(new T.TorusGeometry(r,t,10,96),m,p),0,0,z);
 function keyboard(){
  const p=new T.Group();add(p,4.55,.16,1.65,alu,0,0,0,.06);add(p,4.43,.06,1.53,black,0,.087,0,.04);
  const rows=[['esc','1','2','3','4','5','6','7','8','9','0','−','=','delete'],['tab','Q','W','E','R','T','Y','U','I','O','P','[',']','\\'],['caps','A','S','D','F','G','H','J','K','L',';',"'",'return'],['shift','Z','X','C','V','B','N','M',',','.','/','shift'],['ctrl','opt','cmd','space','cmd','opt','←','↓','↑','→']];
  const widths=[[1,...Array(12).fill(1),1.65],[1.65,...Array(13).fill(1)],[1.85,...Array(11).fill(1),1.8],[2.25,...Array(10).fill(1),2.4],[1.2,1.2,1.2,6.05,1.2,1.2,.7,.7,.7,.7]];
  const atlas=tex(1024,512,c=>{c.fillStyle='#e4e9ef';c.textAlign='center';c.textBaseline='middle';rows.flat().forEach((s,i)=>{c.font=(s.length>1?'15':'25')+'px Arial';c.fillText(s==='space'?'':s,(i%16)*64+32,Math.floor(i/16)*80+40)})});
  const keymat=M(0x263342,.52,.12),legendmat=new T.MeshBasicMaterial({map:atlas,transparent:true,depthWrite:false,toneMapped:false});let idx=0;
  rows.forEach((row,r)=>{let x=-2.1;row.forEach((s,k)=>{const units=widths[r][k],w=units*.29-.022,cx=x+w/2,z=-.64+r*.303;add(p,w,.12,.271,s==='esc'?blue:keymat,cx,.174,z,.023);const g=new T.PlaneGeometry(Math.min(w-.025,.29),.21);const uv=g.attributes.uv;for(let j=0;j<uv.count;j++)uv.setXY(j,(idx%16+uv.getX(j))/16,(512-(Math.floor(idx/16)+1)*80+uv.getY(j)*80)/512);at(mesh(g,legendmat,p),cx,.237,z,-Math.PI/2);x+=units*.29;idx++})});
  const cable=new T.CatmullRomCurve3([new T.Vector3(-1.8,0,-.81),new T.Vector3(-1.8,-.015,-1.1),new T.Vector3(-1.3,-.04,-1.4)]);mesh(new T.TubeGeometry(cable,28,.021,8,false),rubber,p);return p;
 }
 function microphone(){
  const p=new T.Group();
  const mic=new T.Group();p.add(mic);at(mic,0,0,0,Math.PI/2-.14,0,-.16);
  cyl(mic,.26,.28,1.15,dark);cyl(mic,.284,.284,.11,alu,0,-.55,0);
  const foamTex=grain.clone();foamTex.repeat.set(1,1);foamTex.needsUpdate=true;
  const foam=M(0x1f2327,.98,0,{bumpMap:foamTex,bumpScale:.015});
  cyl(mic,.292,.292,.68,foam,0,.64,0);const top=mesh(new T.SphereGeometry(.292,48,28,0,Math.PI*2,0,Math.PI/2),foam,mic);top.position.y=.98;
  textPlane(mic,'STUDIO / 01',.23,.063,0,-.15,.286,'#b2bcc9',26);
  add(mic,.085,.94,.15,dark,-.4,-.23,0,.04);add(mic,.085,.94,.15,dark,.4,-.23,0,.04);add(mic,.87,.085,.15,dark,0,-.66,0,.04);
  [-.4,.4].forEach(x=>{const o=cyl(mic,.12,.12,.11,alu,x,.12,0);o.rotation.z=Math.PI/2});
  return p;
 }
 return {M,mesh,at,add,cyl,tex,textPlane,alu,dark,rubber,white,blue,black,grain,keyboard,microphone};
}
