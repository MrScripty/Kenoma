import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULTS,springTrace,exactSpring} from '../web/mechanics.mjs';
import {ENERGY_DURATION_S,ENERGY_BATCH_STEPS,energyStepLimit} from '../web/energy-run.mjs';

let frames=new Map(),nextFrame=1;
globalThis.cancelAnimationFrame=id=>frames.delete(id);
globalThis.requestAnimationFrame=fn=>{const id=nextFrame++;frames.set(id,fn);return id;};
globalThis.IntersectionObserver=class {observe(){}};
globalThis.document={querySelectorAll:()=>[],querySelector:()=>null,addEventListener(){},createElement:()=>({append(){},textContent:''})};
const {Lab}=await import('../web/app.mjs');
function fixture(dt,method){
 frames.clear();const elements=new Map();
 const root={dataset:{demo:'energy'},querySelectorAll:()=>[],querySelector(selector){
  if(selector==='.energy-chart')return null;
  if(!elements.has(selector))elements.set(selector,{addEventListener(){},replaceChildren(){},focus(){},select(){},setAttribute(){}});
  return elements.get(selector);
 }};
 const lab=new Lab(root);lab.start=()=>{root.dataset.sceneState='ready';};lab.plot=()=>{};
 lab.params={...DEFAULTS.energy,dt,method};lab.state={x:lab.params.x,v:lab.params.v};lab.history=[];lab.update();
 let renders=0;const update=lab.update.bind(lab);lab.update=()=>{renders++;update();};
 return {lab,renders:()=>renders};
}
function frame(timestamp){const [id,fn]=frames.entries().next().value;frames.delete(id);fn(timestamp);}
for(const dt of [.005,.01,.02,.05,.1])for(const method of ['explicit','symplectic','verlet'])test(`${method} h=${dt} actual controller reaches 12s, preserves every sample and measured maximum`,()=>{
 const {lab,renders}=fixture(dt,method),limit=energyStepLimit(dt),reference=springTrace(lab.params,limit);
 lab.playEnergy(true);let calls=0;
 while(lab.running){const before=lab.index;frame(calls++*16);assert.ok(lab.index-before<=ENERGY_BATCH_STEPS);}
 assert.equal(lab.index,limit);assert.equal(lab.energyRun().timeS,ENERGY_DURATION_S);
 assert.equal(lab.history.length,limit+1);assert.deepEqual(lab.history,reference);
 assert.deepEqual(lab.state,{x:reference.at(-1).x,v:reference.at(-1).v});
 const e0=reference[0].energy,max=Math.max(...reference.map(row=>Math.abs(row.energy/e0-1)));
 assert.equal(lab.energyRun().maxAbsoluteRelativeEnergyDeviation,max);
 assert.equal(lab.energyRun().absolutePositionErrorM,Math.abs(lab.state.x-exactSpring(12,lab.params).x));
 assert.equal(renders(),Math.ceil(limit/ENERGY_BATCH_STEPS));
 const end=structuredClone(lab.history);lab.step();lab.playEnergy(true);assert.equal(lab.running,false);assert.deepEqual(lab.history,end);
});
test('batch pause/resume and single steps retain current trajectory; edit/reset start new trajectories',()=>{
 const {lab}=fixture(.005,'verlet');lab.playEnergy(true);frame(0);assert.equal(lab.index,64);
 lab.pause();assert.equal(frames.size,0);const state=structuredClone(lab.state);assert.equal(lab.history.length,65);
 lab.step();assert.equal(lab.index,65);assert.notDeepEqual(lab.state,state);lab.playEnergy(true);frame(16);assert.equal(lab.index,129);lab.pause();
 lab.change({dataset:{param:'dt'},tagName:'SELECT',value:'.01'});assert.equal(lab.index,0);assert.equal(lab.history.length,1);assert.deepEqual(lab.state,{x:.2,v:0});assert.equal(lab.energyRun().stepLimit,1200);
 lab.playEnergy(true);frame(0);lab.reset();assert.equal(frames.size,0);assert.equal(lab.running,false);assert.deepEqual(lab.params,DEFAULTS.energy);assert.equal(lab.index,0);assert.equal(lab.maxRelativeEnergyDeviation,0);
});
test('paced Play uses chosen fixed h and bounded catch-up, with one redraw per frame',()=>{
 const {lab,renders}=fixture(.005,'symplectic');const summary=lab.status.textContent;lab.play();frame(0);assert.equal(lab.index,0);frame(16);assert.equal(lab.index,3);frame(1016);assert.equal(lab.index,53);
 assert.equal(renders(),2);assert.deepEqual(lab.history,springTrace(lab.params,53));lab.pause();assert.equal(frames.size,0);assert.equal(lab.status.textContent,summary);
});
test('duration bounds reject unsupported fractional, excessive or invalid step budgets',()=>{
 for(const dt of [0,-1,NaN,Infinity,.001,.07])assert.throws(()=>energyStepLimit(dt),RangeError);
});
