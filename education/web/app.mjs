import * as THREE from 'three';
import './property-labs.mjs';
import './material-lab.mjs';
import {formatReadout} from './readout.mjs';
import {SceneStatus} from './scene-status.mjs';
import {currentPulse,pulseDue} from './pulse.mjs';
import {DEFAULTS,forceState,leverState,springStep,springEnergy} from './mechanics.mjs';
import {ELBOW,elbowInitial,elbowResults,elbowStep} from './elbow.mjs';
import {SERIES,seriesInitial,seriesResults,seriesStep} from './series.mjs';
import {TISSUE,lbsPoint} from './tissue.mjs';
import {EvidenceView} from './evidence.mjs';
import {AdvancedView} from './advanced.mjs';
const defaultsFor=kind=>kind==='series'?SERIES:kind==='elbow'?ELBOW:DEFAULTS[kind];

const fmt=(v,d=3)=>Math.abs(v)<1e-12?'0':Math.abs(v)>1e5?v.toExponential(3):v.toFixed(d);
let active=null;
export class Lab {
  constructor(root) {
    this.root=root; this.kind=root.dataset.demo; this.running=false; this.index=0; this.view='front';
    this.articulated=['elbow','series'].includes(this.kind);
    this.initialFn=this.kind==='series'?seriesInitial:elbowInitial;
    this.resultFn=this.kind==='series'?seriesResults:elbowResults;
    this.readout=root.querySelector('.readout'); this.sceneHost=root.querySelector('.scene-host');
    this.params={...defaultsFor(this.kind)}; this.history=[]; this.status=root.querySelector('.announce');
    root.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>this.change(input)));
    root.querySelector('[data-action="reset"]').addEventListener('click',()=>this.reset());
    root.querySelector('[data-action="start"]').addEventListener('click',()=>this.start());
    root.querySelector('[data-action="view"]').addEventListener('click',()=>{
      this.view=this.view==='front'?'oblique':'front'; this.draw();
      this.status.textContent=`Camera ${this.view}; physics state unchanged.`;
    });
    root.querySelector('[data-action="summary"]').addEventListener('click',()=>{this.status.textContent=formatReadout(this.readout);});
    root.querySelector('[data-action="copy"]').addEventListener('click',async()=>{
      const text=JSON.stringify({schema:1,scene:this.kind,parameters:this.params,step:this.index,state:this.state,initialEnergy:this.initialEnergy,view:this.view,pulse:this.pulse||null,display:this.root.dataset.runDisplay},null,2);
      const preset=root.querySelector('.preset'); preset.hidden=false; preset.value=text;
      preset.focus(); preset.select();
      this.status.textContent='Reproducible state shown below. Copy the selected text.';
    });
    const step=root.querySelector('[data-action="step"]');
    if(step)step.addEventListener('click',()=>{this.sceneStatus.run(()=>this.start());this.pause();this.step();});
    const play=root.querySelector('[data-action="play"]');
    if(play)play.addEventListener('click',()=>this.running?this.pause():this.play());
    root.querySelector('[data-action="release"]')?.addEventListener('click',()=>{this.pulse=false;this.params.excitation=0;this.sync();this.update();this.status.textContent='Excitation released. Activation and velocity continue from the current state.';});
    root.querySelector('[data-action="pulse"]')?.addEventListener('click',()=>this.pulseCurrent());
    root.querySelector('[data-action="export"]')?.addEventListener('click',()=>{
      const blob=new Blob([JSON.stringify({schema:1,model:this.kind==='series'?'series-force-length-affine-tissue-v2':'schematic-elbow-v1',units:'SI, angle radians',tracePolicy:'One row per step; current row refreshed after same-time input changes. Its excitation applies to the next step; time, state and accumulated work do not advance.',parameters:this.params,initialEnergy:this.initialEnergy,pulse:this.pulse||null,trace:this.history},null,2)],{type:'application/json'});
      const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=this.kind==='series'?'kenoma-series-trace.json':'kenoma-elbow-trace.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
      this.status.textContent='Downloaded the current trace with model parameters and energy accounting.';
    });
    this.sceneStatus=new SceneStatus(root,()=>this.stopRenderer());
    this.reset();
  }
  change(input) {
    const key=input.dataset.param;
    let value=['method','mode','tendon','contact'].includes(key)?input.value:Number(input.value);
    if(input.tagName!=='SELECT') {
      if(input.value==='' || !Number.isFinite(value) || value<Number(input.min)||value>Number(input.max)){input.setAttribute('aria-invalid','true');this.status.textContent='Enter a finite number within the displayed control limits.';return;}
      input.removeAttribute('aria-invalid');
    }
    this.params[key]=value;
    this.root.querySelectorAll(`[data-param="${key}"]`).forEach(el=>{if(el!==input)el.value=value;});
    if(this.articulated && key==='excitation'){this.pulse=false;this.update();return;}
    this.pause(); this.index=0; this.history=[]; this.state={x:this.params.x,v:this.params.v};
    if(this.articulated){this.pulse=false;this.state=this.initialFn(this.params);this.initialEnergy=this.resultFn(this.state,this.params).energy;}
    if(this.kind==='force' && key!=='time') {this.params.time=0;this.sync();}
    this.update();
  }
  sync(){this.root.querySelectorAll('[data-param]').forEach(el=>{el.value=this.params[el.dataset.param];el.removeAttribute('aria-invalid');});}
  reset(){
    this.pause();this.params={...defaultsFor(this.kind)};this.index=0;this.history=[];this.pulse=false;
    this.state={x:this.params.x,v:this.params.v};this.view='front';this.sync();this.update();
    this.status.textContent='Reset to the documented default state; playback paused.';
  }
  pause(){
    this.running=false;cancelAnimationFrame(this.frame);
    const button=this.root.querySelector('[data-action="play"]');if(button)button.textContent='Play';
  }
  play(){
    if(this.articulated && (this.index>=1200||this.state.halted))return;
    if(this.kind==='energy' && this.index>=600)return;
    if(this.kind==='force' && this.params.time>=2)return;
    this.sceneStatus.run(()=>this.start());
    if(active && active!==this)active.pause();
    this.running=true;this.last=0;this.accumulator=0;
    this.root.querySelector('[data-action="play"]').textContent='Pause';
    const tick=timestamp=>{
      if(!this.running)return;
      if(this.last)this.accumulator+=Math.min((timestamp-this.last)/1000,0.25);
      this.last=timestamp;
      // One physics step per 1/30 s of playback. h remains the chosen simulation step.
      while(this.accumulator>=1/30 && this.running){this.step();this.accumulator-=1/30;}
      if(this.running)this.frame=requestAnimationFrame(tick);
    };
    this.frame=requestAnimationFrame(tick);
  }
  pulseCurrent(){
    if(this.state.halted||this.index>=1200){this.status.textContent='Pulse unavailable at the domain/step limit. Reset defaults or set a new experiment before running.';return;}
    this.pulse=currentPulse(this.state.time,this.params.excitation);this.play();
    this.status.textContent=`Current-state pulse: selected excitation ${this.params.excitation} for 0.30 additional simulated seconds, released at the first step boundary at or after ${this.pulse.releaseTime.toFixed(3)} s. Selected parameters and hold mode retained.`;
  }
  step(){
    if(this.kind==='force') {
      if(this.params.time>=2){this.pause();return;}
      this.params.time=Math.min(2,Math.round((this.params.time+0.05)*100)/100);this.index++;
      this.sync();if(this.params.time>=2)this.pause();
    } else if(this.kind==='energy') {
      if(this.index>=600){this.pause();return;}
      this.state=springStep(this.state,this.params);this.index++;
      if(this.index>=600)this.pause();
    } else if(this.articulated) {
      if(this.index>=1200||this.state.halted){this.pause();return;}
      if(pulseDue(this.pulse,this.state.time)){this.pulse=false;this.params.excitation=0;this.sync();this.update();}
      this.state=(this.kind==='series'?seriesStep:elbowStep)(this.state,this.params);
      if(this.state.halted){this.pause();this.status.textContent='Paused at the last admissible state: a trial left the angle/fiber teaching domain. Joint-stop impact is not modeled.';}
      else this.index++;
      if(this.index>=1200)this.pause();
    }
    this.update();
  }
  update(){
    this.root.querySelector(".preset").hidden=true;
    let values;
    if(this.kind==='force') {
      this.result=forceState(this.params);
      const s=this.result;
      values=[['Time',`${fmt(this.params.time,2)} s`],['Acceleration',`${fmt(s.acceleration)} m/s²`],
        ['Position',`${fmt(s.position)} m`],['Velocity',`${fmt(s.velocity)} m/s`],
        ['Work',`${fmt(s.work)} J`],['Kinetic energy',`${fmt(s.kinetic)} J`],
        ['Position scale',`${fmt(.5/(1.7/Math.max(4,Math.abs(forceState({...this.params,time:2}).position))))} m per grid interval; fixed over 0–2 s for this mass/force`]];
    } else if(this.kind==='torque') {
      this.result=leverState(this.params);const s=this.result;
      values=[['Load force y',`${fmt(s.force[1])} N`],['Torque z',`${fmt(s.torque)} N m`],
        ['Moment arm magnitude',`${fmt(s.momentArm)} m`],['Potential energy',`${fmt(s.potential)} J`]];
    } else if(this.articulated) {
      if(this.index===0 && !Number.isFinite(this.state.q)){this.state=this.initialFn(this.params);this.initialEnergy=this.resultFn(this.state,this.params).energy;}
      this.result=this.resultFn(this.state,this.params);const s=this.state,r=this.result;
      const residual=r.energy-this.initialEnergy-s.work+s.dissipation;
      const row={step:this.index,...s,excitation:this.params.excitation,...r,balanceResidual:residual};
      const existing=this.history.findIndex(h=>h.step===this.index);
      if(existing<0)this.history.push(row);else this.history[existing]=row;
      values=[['Mode',this.params.mode==='forward'?'Force-driven hinge':'Prescribed static hold'],['Time',`${fmt(s.time,3)} s`],['Flexion q',`${fmt(s.q*180/Math.PI,2)}°`],
        ['Excitation u',fmt(this.params.excitation,3)],['Activation a',fmt(s.a,3)],['Angular velocity',`${fmt(s.w)} rad/s`],['Fiber length',`${fmt(r.fiber,4)} m`],
        ['Fiber velocity',`${fmt(r.fiberSpeed,4)} m/s`],['Moment arm',`${fmt(r.momentArm,4)} m`],['Active tension',`${fmt(r.active,2)} N`],['Passive tension',`${fmt(r.passive,2)} N`],
        ['Muscle moment',`${fmt(r.activeTorque+r.passiveTorque)} N m`],['Gravity moment',`${fmt(r.gravityTorque)} N m`],['External hold moment',`${fmt(r.motorTorque)} N m`],
        ['Active work',`${fmt(s.work,4)} J`],['Dissipated energy',`${fmt(s.dissipation,4)} J`],['Energy balance residual',`${fmt(residual,7)} J`],['Fiber motion',Math.abs(r.fiberSpeed)<1e-6?'Isometric':r.fiberSpeed<0?'Shortening':'Lengthening']];
      if(Math.abs(r.momentArm)<1e-12)values.push(['Actuator leverage','Dead centre: zero moment arm at q = 0°. Activation and tension cannot turn this straight-path hinge; no angle is nudged.']);
      if(this.kind==='series')values.push(['Tendon length',`${fmt(r.tendon,5)} m`],['Tendon stretch',`${fmt((r.tendon-this.params.tendonLength)*1000,3)} mm`],
       ['Tendon energy',`${fmt(r.tendonEnergy,5)} J`],['Passive fiber energy',`${fmt(r.fiberEnergy,5)} J`],['Force equilibrium residual',`${fmt(r.forceResidual,8)} N`],
       ['Active fiber power',`${fmt(r.activePower,4)} W`],['Muscle power at hinge',`${fmt(r.hingeMusclePower,4)} W`],
       ['Tissue volume ratio J',fmt(r.tissue.volumeRatio,5)],['LBS volume ratio',fmt(r.tissue.skinVolumeRatio,5)],['Tissue normal force',`${fmt(r.tissue.normal,4)} N`],
       ['Model plate pressure',`${fmt(r.tissue.pressure,2)} Pa`],['Tissue resisting moment',`${fmt(r.tissue.torque,5)} N m`],['Tissue elastic energy',`${fmt(r.tissue.energy,6)} J`],
       ['Plate gap',`${fmt(r.tissue.gap*1000,3)} mm`],['Tissue penetration',`${fmt(r.tissue.penetration*1000,3)} mm`],['LBS clearance',`${fmt(r.tissue.skinClearance*1000,3)} mm`],
       ['Free-side stress residual',`${fmt(r.tissue.lateralStressResidual,8)} Pa`],['Complementarity residual',`${fmt(r.tissue.complementarity,8)} N m`],['Event subdivisions',String(s.eventSplits)],['LBS force / pressure','Not modeled']);
    } else {
      const energy=springEnergy(this.state,this.params),e0=springEnergy(this.params,this.params);
      this.result={...this.state,energy};
      if(!this.history.some(s=>s.step===this.index))this.history.push({step:this.index,energy});
      values=[['Step',String(this.index)],['Time',`${fmt(this.index*this.params.dt,2)} s`],
        ['Extension',`${fmt(this.state.x)} m`],['Velocity',`${fmt(this.state.v)} m/s`],
        ['Energy',`${fmt(energy,5)} J`],['Relative energy change',`${fmt(100*(energy/e0-1),2)} %`]];
      this.plot();
    }
    this.readout.replaceChildren(...values.map(([label,value])=>{
      const div=document.createElement('div');const dt=document.createElement('dt');dt.textContent=label;
      const dd=document.createElement('dd');dd.textContent=value;div.append(dt,dd);return div;
    }));
    this.draw();
  }
  plot(){
    const svg=this.root.querySelector('.energy-chart');if(!svg)return;
    const e0=springEnergy(this.params,this.params),max=Math.max(e0*1.2,...this.history.map(s=>s.energy));
    const points=this.history.map(s=>`${40+s.step/600*500},${160-s.energy/max*130}`).join(' ');
    svg.querySelector('.trace').setAttribute('points',points);
    svg.querySelector('.reference').setAttribute('y1',160-e0/max*130);
    svg.querySelector('.reference').setAttribute('y2',160-e0/max*130);
    svg.querySelector('.scale').textContent=`Energy range 0 to ${fmt(max)} J`;
    svg.querySelector('title').textContent=`Energy plot after ${this.index} steps. Current ${fmt(this.result.energy)} J; reference ${fmt(e0)} J. Vertical range 0 to ${fmt(max)} J.`;
  }
  start(){
    if(active && active!==this)active.stopRenderer();
    active=this;
    this.sceneStatus.begin();
    if(!this.renderer){
      try {
        this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.5));
        this.renderer.setClearColor(0x101d2c);
        const canvas=this.renderer.domElement;canvas.setAttribute('role','img');
        canvas.setAttribute('aria-label',`${this.kind} schematic 3D scene; equivalent results and description follow.`);
        this.sceneHost.replaceChildren(canvas);this.scene=new THREE.Scene();
        this.camera=new THREE.PerspectiveCamera(40,1,0.01,100);
        this.sceneStatus.watch(this.renderer);
        this.observer=new ResizeObserver(()=>this.draw());this.observer.observe(this.sceneHost);
      }catch(error){
        this.sceneStatus.fail(error,'initialization');this.status.textContent='3D rendering unavailable. Static figure, controls and numerical results remain available.';return;
      }
    }
    this.root.classList.add('active-scene');
    if(this.draw())try{this.sceneStatus.ready(this.renderer);}catch(error){this.sceneStatus.fail(error,'first-frame');}
  }
  stopRenderer(){
    this.pause();if(!this.renderer&&this.root.dataset.sceneState==='error')return;
    this.sceneStatus.idle();this.observer?.disconnect();
    this.scene?.traverse(obj=>{obj.geometry?.dispose();if(obj.material)obj.material.dispose();});
    this.renderer?.dispose();this.renderer?.forceContextLoss();this.renderer=null;
    this.sceneHost.replaceChildren();this.root.classList.remove('active-scene');
  }
  draw(){if(!this.renderer)return false;return this.sceneStatus.draw(()=>this.renderScene());}
  renderScene(){
    if(!this.renderer)return;
    this.scene.traverse(obj=>{obj.geometry?.dispose();if(obj.material)obj.material.dispose();});this.scene.clear();
    this.scene.add(new THREE.AmbientLight(0xffffff,2));
    const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(1,3,5);this.scene.add(light);
    const line=(a,b,color=0x70e0cc)=>{
      const geo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]);
      this.scene.add(new THREE.Line(geo,new THREE.LineBasicMaterial({color})));
    };
    const sphere=(position,radius,color)=>{
      const obj=new THREE.Mesh(new THREE.SphereGeometry(radius,24,16),new THREE.MeshStandardMaterial({color,roughness:0.6}));
      obj.position.set(...position);this.scene.add(obj);return obj;
    };
    const arrow=(position,vector,color)=>{
      const v=new THREE.Vector3(...vector);if(v.length()<1e-8)return;
      this.scene.add(new THREE.ArrowHelper(v.clone().normalize(),new THREE.Vector3(...position),v.length(),color,0.15,0.08));
    };
    const rod=(a,b)=>{
      const start=new THREE.Vector3(...a),end=new THREE.Vector3(...b),delta=end.clone().sub(start);
      const obj=new THREE.Mesh(new THREE.CylinderGeometry(0.045,0.045,delta.length(),20),new THREE.MeshStandardMaterial({color:0xa2bdcf}));
      obj.position.copy(start.add(end).multiplyScalar(0.5));obj.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());this.scene.add(obj);
    };
    for(let i=-4;i<=4;i++){line([i/2,-1.8,-0.1],[i/2,1.8,-0.1],0x263d50);line([-2,i/2,-0.1],[2,i/2,-0.1],0x263d50);}
    arrow([-1.8,-1.5,0],[0.45,0,0],0xffffff);arrow([-1.8,-1.5,0],[0,0.45,0],0xffffff);
    if(this.kind==='force') {
      // Fit the whole allowed trajectory, so changing time never rescales position.
      const x=this.result.position,end=forceState({...this.params,time:2}),scale=1.7/Math.max(4,Math.abs(end.position));
      sphere([x*scale,0,0],0.13,0x70e0cc);line([0,0,0],[x*scale,0,0]);
      arrow([x*scale,0,0],[this.params.force/8*0.65,0,0],0xffc66d);
      arrow([x*scale,0.28,0],[this.result.velocity/Math.max(8,Math.abs(end.velocity))*0.55,0,0],0xd7a3ff);
    } else if(this.kind==='torque') {
      const [x,y]=this.result.r.map(v=>v*5);
      rod([0,0,0],[x,y,0]);sphere([0,0,0],0.12,0xa2bdcf);sphere([x,y,0],0.15,0x70e0cc);
      arrow([x,y-0.17,0],[0,-this.params.mass/10*0.9,0],0xffc66d);line([0,0,0.09],[x,0,0.09],0xffffff);
    } else if(this.kind==='series') {
      const p=this.params,r=this.result,q=this.state.q,mid=q/2;
      const box=(position,size,color,rotation=0,wireframe=false)=>{
        const object=new THREE.Mesh(new THREE.BoxGeometry(...size),new THREE.MeshStandardMaterial({color,roughness:.65,wireframe,transparent:!wireframe,opacity:.8}));
        object.position.set(...position);object.rotation.z=rotation;this.scene.add(object);return object;
      };
      for(const offset of [-.95,.95]){
        const scale=2.7,base=[offset,.2,0],end=[offset+p.length*Math.sin(q)*scale,.2-p.length*Math.cos(q)*scale,0];
        rod([offset,1.15,0],base);rod(base,end);sphere(base,.08,0xa2bdcf);
        rod([end[0]-.14,end[1],0],[end[0]+.14,end[1],0]);sphere([end[0]-.14,end[1],0],.09,0x71818b);sphere([end[0]+.14,end[1],0],.09,0x71818b);
        if(offset<0){
          const origin=new THREE.Vector3(offset,.2+p.origin*scale,.1),insertion=new THREE.Vector3(offset+r.point[0]*scale,.2+r.point[1]*scale,.1);
          const direction=insertion.clone().sub(origin).normalize(),junction=origin.clone().addScaledVector(direction,r.fiber*scale);
          line(origin.toArray(),junction.toArray(),0xff876f);line(junction.toArray(),insertion.toArray(),0xffc66d);sphere(junction.toArray(),.035,0xffc66d);
        }
        const magnify=8,center=[offset,-1.2,.15];
        if(offset<0)box(center,[TISSUE.width*r.tissue.lateralStretch*magnify,r.tissue.height*magnify,TISSUE.depth*r.tissue.lateralStretch*magnify],0x70e0cc,mid);
        else {
          // Apply the actual 50/50 transform to every bind-space vertex; no second pose.
          const geo=new THREE.BoxGeometry(TISSUE.width*magnify,TISSUE.height*magnify,TISSUE.depth*magnify),vertices=geo.attributes.position;
          for(let i=0;i<vertices.count;i++){const v=lbsPoint([vertices.getX(i),vertices.getY(i),vertices.getZ(i)],q);vertices.setXYZ(i,...v);}
          geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:0x9bafff,wireframe:true}));mesh.position.set(...center);this.scene.add(mesh);
        }
        for(const sign of [-1,1]){
          const localY=sign*r.tissue.gap*magnify/2;
          box([center[0]-Math.sin(mid)*localY,center[1]+Math.cos(mid)*localY,.15],[TISSUE.width*1.5*magnify,.025,TISSUE.depth*1.6*magnify],0xe8cf9b,mid);
        }
      }
    } else if(this.kind==='elbow') {
      const q=this.state.q,scale=4.5,p=this.params;
      const end=[p.length*Math.sin(q)*scale,-p.length*Math.cos(q)*scale,0];
      rod([0,1.45,0],[0,0,0]);rod([0,0,0],end);sphere([0,0,0],.11,0xa2bdcf);
      rod([end[0]-.22,end[1],0],[end[0]+.22,end[1],0]);sphere([end[0]-.22,end[1],0],.14,0x71818b);sphere([end[0]+.22,end[1],0],.14,0x71818b);
      const origin=[0,p.origin*scale,.15],insert=[...this.result.point.map(v=>v*scale),.15];
      line(origin,insert,0xff876f);sphere(origin,.045,0xffc66d);sphere(insert,.045,0xffc66d);
      const v=new THREE.Vector3(...insert).sub(new THREE.Vector3(...origin));
      const belly=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),new THREE.MeshStandardMaterial({color:new THREE.Color().setHSL(.02,.65,.35+.2*this.state.a),roughness:.6}));
      const radius=.075*Math.sqrt(.2/this.result.fiber);belly.scale.set(radius,v.length()*.31,radius);
      belly.position.copy(new THREE.Vector3(...origin).addScaledVector(v,.44));belly.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),v.normalize());this.scene.add(belly);
      arrow([end[0],end[1]-.2,0],[0,-p.load*.075,0],0xffc66d);
    } else {
      const x=this.state.x,scale=3/Math.max(1,Math.abs(x));const tip=0.6+x*scale;
      const points=[];for(let i=0;i<=120;i++)points.push(new THREE.Vector3(-1.4+(tip+1.4)*i/120,i===0||i===120?0:0.1*Math.sin(i/120*Math.PI*20),0.1*Math.cos(i/120*Math.PI*20)));
      this.scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:0xa2bdcf})));
      sphere([tip,0,0],0.14,0x70e0cc);line([0.6,-0.4,0],[tip,-0.4,0],0xffffff);
    }
    const width=Math.max(200,this.sceneHost.clientWidth),height=300;
    this.renderer.setSize(width,height,false);this.camera.aspect=width/height;
    this.camera.position.set(...(this.view==='front'?[0,0,6]:[2,1.5,6]));this.camera.lookAt(0,0,0);this.camera.updateProjectionMatrix();
    this.renderer.render(this.scene,this.camera);
  }
}
const labs=[...document.querySelectorAll('[data-demo]')].map(root=>new Lab(root));
const advanced=[...document.querySelectorAll('[data-advanced]')].map(root=>new AdvancedView(root,view=>{if(active&&active!==view)active.stopRenderer();active=view;}));
const evidenceRoot=document.querySelector('#evidence-viewer');
if(evidenceRoot)new EvidenceView(evidenceRoot,view=>{if(active&&active!==view)active.stopRenderer();active=view;});
document.addEventListener('visibilitychange',()=>{if(document.hidden)[...labs,...advanced].forEach(lab=>lab.pause());});
const offscreen=new IntersectionObserver(entries=>{for(const entry of entries)if(!entry.isIntersecting)[...labs,...advanced].find(lab=>lab.root===entry.target)?.pause();});
[...labs,...advanced].forEach(lab=>offscreen.observe(lab.root));
