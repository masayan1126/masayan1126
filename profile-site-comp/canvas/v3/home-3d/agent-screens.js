// Three synchronized, locally rendered screen animations. No external jobs run.
export function createAgentScreens(tex){
 const main=tex(1920,840,()=>{}),portrait=tex(900,1500,()=>{}),work=tex(1440,900,()=>{});
 const tasks=[['RESEARCH','Sources & references'],['FRONTEND','Studio website'],['API','Content endpoints'],['TEST','Integration suite'],['DESIGN','Layout & typography'],['VIDEO','Composition render'],['AUDIO','Voice & waveform'],['CONTENT','Technical script'],['REVIEW','Code inspection'],['DATA','Content indexing'],['BUILD','Preview compilation'],['VERIFY','Browser validation']];
 const c0=main.image.getContext('2d'),c1=portrait.image.getContext('2d'),c2=work.image.getContext('2d');
 const palette={bg:'#101925',panel:'#182434',line:'#2c3d52',muted:'#8196af',text:'#ced9e7',blue:'#79a8d6',green:'#8cc3b2'};
 function text(c,s,x,y,size=18,col=palette.text,font='Arial'){c.fillStyle=col;c.font=`${size}px ${font}`;c.fillText(s,x,y)}
 function rect(c,x,y,w,h,col){c.fillStyle=col;c.fillRect(x,y,w,h)}
 function dot(c,x,y,col,r=4){c.fillStyle=col;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill()}
 function header(c,w,title){rect(c,0,0,w,56,'#1d2b3e');text(c,title,25,35,18);dot(c,w-116,28,'#8cb7a8');text(c,'WORKSPACE',w-101,33,11,palette.muted)}
 const logs=['spawn worker','read project context','search references','inspect dependencies','write component','check API schema','compile preview','run integration tests','render composition','compare output','prepare review'];
 const code=['import { orchestrate } from "./agents"','', 'const studio = orchestrate({','  concurrency: 36,','  workspace: "miyabiya-studio",','  tasks: [','    research({ sources: "verified" }),','    develop({ target: "website" }),','    compose({ format: "video" }),','    review({ checks: "all" }),','  ],','})','','await studio.run()','','// Each worker returns a reviewable result.'];
 let last=-1;const state={count:1,review:0,frame:0};
 function update(t){
  if(last===Math.floor(t*8))return;last=Math.floor(t*8);const cycle=t%48;
  const count=cycle<10?Math.min(36,1+Math.floor(cycle*3.5)):36;
  const progressOf=id=>Math.min(1,Math.max(0,(cycle-id*.19-2)/(8+(id%7)))%1.16);
  const done=Array.from({length:count},(_,id)=>progressOf(id)).filter(p=>p>=1).length;
  Object.assign(state,{count,review:done,frame:last});
  rect(c0,0,0,1920,840,palette.bg);header(c0,1920,'MIYABIYA / AGENT WORKSPACE');
  rect(c0,0,56,240,784,'#142030');text(c0,'WORKSPACES',25,99,13,palette.muted);text(c0,'Studio production',25,140,20);text(c0,'Development',25,183,16,palette.muted);text(c0,'Research',25,218,16,palette.muted);text(c0,'Media creation',25,253,16,palette.muted);rect(c0,20,284,200,1,palette.line);
  text(c0,String(count).padStart(2,'0'),24,375,68,'#e1ebf7');text(c0,'AGENTS CONNECTED',26,407,12,palette.muted);
  [['Running',Math.max(1,count-done)],['Ready for review',done],['Work streams',12]].forEach(([s,n],i)=>{text(c0,s,25,462+i*46,14,palette.muted);text(c0,String(n).padStart(2,'0'),185,462+i*46,17)});
  text(c0,'studio / orchestrator',26,731,13);text(c0,'Parallel execution',26,760,12,palette.muted);
  text(c0,'One workspace. Many hands.',272,107,27);text(c0,'Research, build, create and verify — in parallel',272,138,15,palette.muted);
  // A parent connects to four teams. Activity moves through the actual branches.
  const parentX=363,branchY=190;rect(c0,parentX-91,branchY-20,182,42,'#234169');text(c0,'ORCHESTRATOR',parentX-68,branchY+7,15);
  for(let g=0;g<4;g++){const x=665+g*338;c0.strokeStyle=palette.line;c0.lineWidth=2;c0.beginPath();c0.moveTo(parentX+91,branchY);c0.lineTo(x-109,branchY);c0.stroke();rect(c0,x-108,branchY-19,215,40,'#1d3049');text(c0,['RESEARCH','DEVELOPMENT','PRODUCTION','REVIEW'][g],x-82,branchY+7,14);const u=(t*.65+g*.21)%1;dot(c0,parentX+94+(x-205-parentX)*u,branchY,palette.blue,3)}
  tasks.forEach(([name,sub],i)=>{const col=i%4,row=Math.floor(i/4),x=273+col*404,y=254+row*170;
   rect(c0,x,y,386,153,palette.panel);rect(c0,x,y,386,2,i*3<count?'#5980ab':palette.line);text(c0,String(i+1).padStart(2,'0')+' / '+name,x+17,y+28,15);text(c0,sub+' / '+['reading','working','checking'][Math.floor(t*.45+i)%3],x+17,y+51,12,palette.muted);
   for(let j=0;j<3;j++){const id=i*3+j,active=id<count,progress=active?progressOf(id):0;
    dot(c0,x+20,y+77+j*23,progress>=1?palette.green:active?palette.blue:'#425166',3);
    text(c0,'agent-'+String(id+1).padStart(2,'0'),x+32,y+82+j*23,12,active?palette.text:palette.muted,'monospace');
    rect(c0,x+135,y+74+j*23,147,5,'#2b3b50');rect(c0,x+135,y+74+j*23,147*progress,5,progress>=1?'#83b5a5':'#719dcc');
    text(c0,progress>=1?'REVIEW':active?'RUNNING':'QUEUED',x+297,y+81+j*23,9,progress>=1?palette.green:palette.muted);
   }
  });
  rect(c0,0,806,1920,34,'#173652');text(c0,'studio-main  /  36 workers  /  12 parallel streams',20,829,13);text(c0,'Review before release',1724,829,12);

  rect(c1,0,0,900,1500,'#101924');header(c1,900,'AGENT ACTIVITY');
  text(c1,'Execution log',32,113,29);text(c1,'studio-main / worker events',33,150,17,palette.muted);rect(c1,32,178,836,1,palette.line);
  text(c1,String(count).padStart(2,'0'),35,242,56,'#dce9f6');text(c1,'connected',125,238,18,palette.muted);text(c1,String(done).padStart(2,'0'),475,242,56,palette.green);text(c1,'in review',565,238,18,palette.muted);
  const seq=Math.floor(t*3.4),fraction=(t*3.4)%1;
  c1.save();c1.beginPath();c1.rect(20,285,860,1030);c1.clip();
  for(let row=0;row<21;row++){const n=Math.max(0,seq-19+row),id=n*7%36,action=n%logs.length,y=304+row*50-fraction*50;
   text(c1,String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0'),31,y,15,'#657f9d','monospace');
   text(c1,'agent-'+String(id+1).padStart(2,'0'),116,y,16,palette.blue,'monospace');
   text(c1,logs[action],262,y,17,action>8?palette.green:palette.text,'monospace');
   text(c1,tasks[Math.floor(id/3)][0].toLowerCase()+' / '+['read','execute','write','verify'][n%4],263,y+21,12,palette.muted,'monospace');
  }c1.restore();
  rect(c1,20,1321,860,144,palette.panel);text(c1,'NEXT / REVIEW QUEUE',39,1356,15,palette.muted);text(c1,'Website preview',40,1393,18);text(c1,'Video composition',40,1430,18);text(c1,done>0?'READY':'PROCESSING',668,1393,15,palette.green);text(c1,done>2?'READY':'PROCESSING',668,1430,15,palette.green);

  rect(c2,0,0,1440,900,palette.bg);header(c2,1440,'BUILD / PREVIEW / RENDER');
  rect(c2,18,76,748,510,'#131e2e');text(c2,'studio.ts   ×',35,111,16);rect(c2,20,127,744,1,palette.line);
  const typed=Math.floor(cycle*23)%code.join('\n').length;let chars=0;
  code.forEach((line,i)=>{text(c2,String(i+1).padStart(2,' '),34,160+i*24,13,palette.muted,'monospace');const shown=line.slice(0,Math.max(0,typed-chars));text(c2,shown,77,160+i*24,14,line.startsWith('//')?palette.muted:i%3===0?palette.blue:palette.text,'monospace');if(typed>=chars&&typed<=chars+line.length&&Math.floor(t*2)%2===0)rect(c2,77+shown.length*8.5,146+i*24,2,17,palette.blue);chars+=line.length+1});
  // The generated browser preview fills out while the workers run.
  rect(c2,790,76,628,510,'#f1f4f8');rect(c2,790,76,628,36,'#d9e1e9');text(c2,'studio.local / preview',820,100,13,'#526780');
  text(c2,'Miyabiya Studio',817,157,23,'#133f8f');text(c2,'ABOUT     WORKS     CONTACT',1154,154,9,'#42638e');
  text(c2,'Build useful things.',819,238,34,'#133f8f');text(c2,'Share what works.',819,281,34,'#133f8f');
  rect(c2,820,319,565,1,'#cad6e4');
  for(let i=0;i<3;i++){const x=820+i*190;rect(c2,x,344,175,162,cycle>4+i*3?'#dde7f3':'#e7ecf2');if(cycle>4+i*3){rect(c2,x,344,175,85,['#164587','#2e5b92','#5077a7'][i]);text(c2,['01 / DEVELOPMENT','02 / AUTOMATION','03 / MEDIA'][i],x+12,452,10,'#133f8f');text(c2,['Web & API','Agent workflows','Content creation'][i],x+12,482,13,'#133f8f')}}
  text(c2,cycle>17?'Preview ready for review':'Updating preview…',821,557,14,'#43638b');
  rect(c2,18,608,1400,270,palette.panel);text(c2,'VIDEO COMPOSITION',37,641,16);text(c2,'Render workers / 08',1191,640,13,palette.muted);
  for(let j=0;j<3;j++){text(c2,['VIDEO','AUDIO','CAPTIONS'][j],37,688+j*51,11,palette.muted);for(let i=0;i<10;i++){const x=150+i*124,y=664+j*51;rect(c2,x,y,115,36,['#315e91','#376e7d','#4a668b'][j]);text(c2,(j?'track-':'scene-')+String(i+1).padStart(2,'0'),x+10,y+23,10,'#cbdfed');if(j===1){c2.strokeStyle='#8fbcc9';c2.beginPath();for(let u=0;u<94;u+=3){const yy=y+18+Math.sin(u*.4)*Math.sin(u*.17)*11;u?c2.lineTo(x+10+u,yy):c2.moveTo(x+10+u,yy)}c2.stroke()}}}
  rect(c2,150+(t*37)%1230,655,2,166,'#d4e5f5');const pct=Math.min(100,Math.floor(cycle/38*100));text(c2,'Encoding frames',37,856,13,palette.muted);rect(c2,211,846,980,5,'#30465d');rect(c2,211,846,980*pct/100,5,palette.blue);text(c2,String(pct)+'%',1286,856,15);
  main.needsUpdate=portrait.needsUpdate=work.needsUpdate=true;
 }
 update(0);return{main,portrait,work,update,state};
}
