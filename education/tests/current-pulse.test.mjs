import test from 'node:test';
import assert from 'node:assert/strict';
import {ELBOW} from '../web/elbow.mjs';
import {SERIES} from '../web/series.mjs';
import {SPATIAL} from '../web/spatial.mjs';
import {AdvancedView} from '../web/advanced.mjs';

globalThis.cancelAnimationFrame=()=>{};
globalThis.requestAnimationFrame=()=>1; // Scheduling only; step the real solver below.
globalThis.IntersectionObserver=class {observe(){}};
globalThis.document={querySelectorAll:()=>[],querySelector:()=>null,addEventListener(){},createElement:()=>({append(){},textContent:''})};
const {Lab}=await import('../web/app.mjs');
function fixture(kind){
 const actions=new Map(),elements=new Map();
 const root={dataset:kind==='spatial'?{advanced:kind}:{demo:kind},querySelectorAll:()=>[],querySelector(selector){
  if(!elements.has(selector))elements.set(selector,{addEventListener:(_,fn)=>actions.set(selector,fn),replaceChildren(){},focus(){},select(){}});
  return elements.get(selector);
 }};
 const lab=kind==='spatial'?new AdvancedView(root,()=>{}):new Lab(root);
 // Browser startup is separately exercised with the production bundle/WebGL.
 lab.start=()=>{root.dataset.sceneState='ready';};
 return {lab,actions,root};
}
for(const kind of ['elbow','series','spatial'])test(`${kind} pulse retains selected inputs and evolved physical state; releases relative to current time`,()=>{
 const {lab,actions,root}=fixture(kind);
 const defaults=kind==='spatial'?SPATIAL:kind==='series'?SERIES:ELBOW;
 lab.params={...lab.params,load:8,excitation:.35,angle:45,dt:.01,mode:'prescribed'};
 if(kind==='spatial')lab.params={...lab.params,skin:'off',activeShape:'off',sweeps:80};
 lab.state=lab.initialFn?lab.initialFn(lab.params):{...lab.state,q:Math.PI/4};
 lab.initialEnergy=lab.resultFn?.(lab.state,lab.params).energy;
 for(let i=0;i<40;i++)lab.step();
 const state=structuredClone(lab.state),params=structuredClone(lab.params),index=lab.index,history=structuredClone(lab.history);
 actions.get(kind==='spatial'?'[data-action=pulse]':'[data-action="pulse"]')();
 lab.pause();assert.deepEqual(lab.state,state);assert.deepEqual(lab.params,params);
 assert.equal(lab.index,index);assert.deepEqual(lab.history,history);assert.equal(root.dataset.runDisplay,'live');
 assert.ok(Math.abs(lab.pulse.releaseTime-state.time-.3)<1e-12);
 for(let i=0;i<30;i++)lab.step();
 assert.equal(lab.params.excitation,.35,'no early release even when original time exceeds .3');
 const beforeRelease=structuredClone(lab.state);lab.step();
 assert.equal(lab.params.excitation,0);assert.ok(lab.state.a>0&&lab.state.a<beforeRelease.a);
 assert.equal(lab.state.q,state.q,'prescribed mode retained');assert.equal(lab.state.w,0);
 assert.ok(lab.state.time>beforeRelease.time);assert.equal(lab.state.dissipation,state.dissipation);
 if(kind==='elbow')assert.equal(lab.state.work,0);
 if(kind==='series')assert.ok(lab.history.at(-1).fiberSpeed>0&&lab.history.at(-1).activePower<0,'active fiber lengthens after release');
 lab.reset();assert.deepEqual(lab.params,defaults);assert.equal(lab.state.time,0);assert.equal(lab.state.a,0);assert.equal(lab.index,0);assert.equal(lab.pulse,false);
});
test('failed 3D startup labels numerical-only stepping and does not retry every step',()=>{
 const {lab,actions,root}=fixture('force');let starts=0;
 lab.start=()=>{starts++;root.dataset.sceneState='error';};
 const action=actions.get('[data-action="step"]');action();action();
 assert.equal(starts,1);assert.equal(root.dataset.runDisplay,'numerical-only');
 assert.equal(lab.params.time,.1);assert.ok(lab.result.position>0);
 assert.match(root.querySelector('.scene-notice').textContent,/static reference diagram does not move/);
});
