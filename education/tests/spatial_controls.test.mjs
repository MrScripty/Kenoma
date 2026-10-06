import test from 'node:test';
import assert from 'node:assert/strict';
import {AdvancedView} from '../web/advanced.mjs';
import {SPATIAL,SPATIAL_MESH as mesh,skinPoint,spatialInitial,spatialStep} from '../web/spatial.mjs';

// Use the real controller and solver; only DOM/rendering services are stubs.
globalThis.cancelAnimationFrame=()=>{};
globalThis.document={createElement:()=>({append(){},textContent:''})};
function fixture(){
 const elements=new Map(),actions=new Map();
 const root={dataset:{advanced:'spatial'},querySelectorAll:()=>[],querySelector(selector){
  if(!elements.has(selector))elements.set(selector,{addEventListener:(_,fn)=>actions.set(selector,fn),replaceChildren(){},focus(){},select(){}});
  return elements.get(selector);
 }};
 const lab=new AdvancedView(root,()=>{});
 return {lab,actions,change:(key,value)=>lab.change({dataset:{param:key},value:String(value),min:'',max:'',removeAttribute(){},setAttribute(){}})};
}
const snapshot=lab=>structuredClone({state:lab.state,index:lab.index});
function invariant(lab){
 const r=lab.result.shape;
 assert.equal(r.q,lab.state.q);assert.equal(r.a,lab.state.a);
 assert.ok(r.x.flat().every(Number.isFinite));assert.ok(r.volumeRatios.every(J=>J>.01));
 assert.ok(r.acceptedEnergy.every((E,i,A)=>i===0||E<=A[i-1]+1e-13));
 assert.deepEqual(r.baseline,mesh.rest.map(X=>skinPoint(X,lab.state.q)));
 mesh.fixed.forEach((fixed,i)=>{if(fixed)assert.deepEqual(r.x[i],r.baseline[i]);});
 assert.ok(Number.isFinite(r.freeResidualN));
}
test('compression control ablations preserve activation/pose and produce the named physical effect',()=>{
 const {lab,actions,change}=fixture();actions.get('[data-action=compression]')();
 const before=snapshot(lab),full=structuredClone(lab.result);
 assert.equal(lab.state.a,.6);assert.equal(lab.state.q,Math.PI/2);invariant(lab);
 for(const [key,value] of [['skin','off'],['boneContact','off'],['volumeK',2500],['activeShape','off'],['sweeps',80],['tendon','rigid'],['load',7],['dt',.01]]){
  lab.reset();actions.get('[data-action=compression]')();
  change(key,value);assert.deepEqual(snapshot(lab),before,key);invariant(lab);
  assert.equal(lab.history.length,1);assert.equal(lab.history[0].activation,.6);
  const r=lab.result.shape;
  if(key==='skin'){assert.equal(r.energy.skin,0);assert.equal(r.energy.fascia,0);}
  if(key==='boneContact'){assert.equal(r.contactNormalSumN,0);assert.ok(r.maxPenetrationM>10*full.shape.maxPenetrationM);}
  if(key==='volumeK')assert.ok(r.minJ<full.shape.minJ-.1);
  if(key==='activeShape'){
   assert.equal(r.energy.active,0);assert.ok(full.shape.energy.active>0);
   assert.deepEqual(lab.result.hinge,full.hinge,'shape ablation leaves the line actuator unchanged');
   const displacement=Math.max(...r.x.map((X,i)=>Math.hypot(...X.map((v,d)=>v-full.shape.x[i][d]))));
   assert.ok(displacement>.001,'same-activation shape comparison moves the visible mesh');
   change('activeShape','on');assert.deepEqual(lab.result,full,'fresh deterministic solve restores paired geometry');
  }
 }
});
test('parameter edits preserve evolved state, halt, accounting and counters; pose/hold edits enforce kinematics',()=>{
 const {lab,change}=fixture();
 for(let i=0;i<60;i++)lab.state=spatialStep(lab.state,lab.params);
 lab.index=60;lab.update();const before=snapshot(lab);
 assert.ok(before.state.a>.59&&before.state.w>0&&before.state.work>0);
 change('skin','off');assert.deepEqual(snapshot(lab),before);assert.equal(lab.history[0].step,60);invariant(lab);
 lab.running=true;lab.pulse=true;change('dt',.01);assert.deepEqual(snapshot(lab),before);assert.equal(lab.running,false);assert.equal(lab.pulse,false);
 lab.state.halted=true;change('volumeK',2500);assert.equal(lab.state.halted,true);
 change('angle',75);assert.deepEqual(lab.state,{...before.state,q:75*Math.PI/180,w:0,halted:false});invariant(lab);
 lab.state.w=2;change('mode','prescribed');assert.deepEqual(lab.state,{...before.state,q:75*Math.PI/180,w:0,halted:false});
 assert.equal(lab.params.angle,lab.state.q*180/Math.PI);
 const held=snapshot(lab);lab.step();assert.equal(lab.state.q,held.state.q);assert.equal(lab.state.w,0);
 assert.equal(lab.state.dissipation,held.state.dissipation);assert.ok(lab.state.time>held.state.time);
 lab.reset();assert.deepEqual(lab.state,spatialInitial(SPATIAL));assert.equal(lab.index,0);assert.equal(lab.history.length,1);
});
