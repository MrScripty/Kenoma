import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {CONTROLS,parameters,lessonState,validateScene,projectedSamples} from '../web/chapter-models.mjs';
import {LatestWorker} from '../../browser/embedded/latest-worker.js';
import {springStep,DEFAULTS} from '../web/mechanics.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url)));
const registry=read('../book/examples/registry.json');
const atlas=read('../data/elbow-v1/data/bodyparts3d_right_arm_m.json');
const apparatus={geometry:read('../data/anatomical-arm-v1/generated/arm-geometry.json'),trajectory:read('../data/anatomical-arm-v1/audit/arm-trajectory-results.json')};
const coupling=read('../data/anatomical-arm-v1/audit/coupling-results.json');
function asset(kind,p){return kind==='atlas'||(['research','coverage'].includes(kind)&&p.layer==='atlas')?atlas:kind==='apparatus'||(kind==='research'&&p.layer==='apparatus')?apparatus:kind==='coupled'?coupling:null;}
test('one scoped example per canonical chapter, in book order',()=>{
 assert.deepEqual(registry.examples.map(e=>e.chapter),read('../book/book.json').chapters);
 assert.equal(new Set(registry.examples.map(e=>e.id)).size,27);
 for(const e of registry.examples){assert.ok(CONTROLS[e.kind]);assert.ok(e.limits&&e.evidenceClass&&e.task);}
});
for(const kind of Object.keys(CONTROLS))test(`${kind}: finite indexed geometry at every control endpoint`,()=>{
 const variants=[parameters(kind)];
 for(const c of CONTROLS[kind])for(const value of c.type==='choice'?c.options:[c.min,c.max])variants.push(parameters(kind,{[c.key]:value}));
 for(const p of variants){const s=lessonState(kind,p,asset(kind,p));assert.equal(validateScene(s),s);assert.equal(s.kind,kind);assert.ok(s.metrics.every(([k,v])=>k&&!/NaN|Infinity|undefined/.test(v)));}
});
test('velocity glyph follows oscillator axis and original integrator',()=>{
 const p={method:'verlet',steps:30},q={...DEFAULTS.energy,method:p.method};let state={x:q.x,v:q.v};for(let i=0;i<p.steps;i++)state=springStep(state,q);
 const s=lessonState('energy',p);assert.deepEqual(s.objects.find(o=>o.type==='arrow').vector,[state.v*.1,0,0]);
});
test('atlas filtering preserves source coordinates, provenance, and part color',()=>{
 const all=lessonState('atlas',{},atlas),one=lessonState('atlas',{part:'3'},atlas);
 assert.deepEqual(one.objects[0],all.objects[3]);assert.deepEqual(one.objects[0].vertices[0],[atlas.parts[3].vertices_m[0][0],atlas.parts[3].vertices_m[0][2],-atlas.parts[3].vertices_m[0][1]]);
});
test('weighted projection retains the orthogonal energy identity at each space size',()=>{
 for(const n of [1,2,4]){const s=projectedSamples(n);assert.ok(Math.abs(s.full-s.condensed-s.gap)<1e-12);assert.ok(Math.abs(s.residual.reduce((a,v,i)=>a+v*s.projected[i]*s.weights[i],0))<1e-12);}
 assert.equal(projectedSamples(4).gap,0);assert.throws(()=>projectedSamples(3));
});
test('invalid or out-of-domain model input is rejected',()=>{
 for(const input of [{force:NaN},{force:Infinity},{force:9},{force:.11},{unknown:1},[]])assert.throws(()=>parameters('force',input));
 assert.throws(()=>parameters('missing'));assert.throws(()=>parameters('energy',{method:'unknown'}));
});
test('scene validation rejects sparse, unsupported and out-of-bounds objects',()=>{
 const check=o=>validateScene({version:1,objects:[o]});
 for(const o of [{type:'unknown'},{type:'arrow',origin:Array(3),vector:[1,2,3]},{type:'sphere',center:[0,0,0],radius:-1},{type:'mesh',vertices:[[0,0,0]],faces:[[0,1,2]]},{type:'mesh',vertices:[[0,0,0]],faces:[Array(3)]},{type:'line',points:Array(2)}])assert.throws(()=>check(o));
});
test('latest worker bounds queue, rejects stale results and terminates once',()=>{
 const posted=[],results=[],errors=[];let terminated=0;const w={postMessage:x=>posted.push(x),terminate:()=>terminated++};const bridge=new LatestWorker(w,x=>results.push(x),e=>errors.push(e));
 bridge.request({value:1});bridge.request({value:2});bridge.request({value:3});assert.equal(posted.length,1);
 w.onmessage({data:{id:1,ok:true,state:'stale'}});assert.deepEqual(results,[]);assert.equal(posted.length,2);assert.equal(posted[1].value,3);
 w.onmessage({data:{id:3,ok:true,state:'latest'}});assert.deepEqual(results,['latest']);
 bridge.request({value:4});w.onmessage({data:{id:4,ok:false,error:'domain'}});assert.equal(errors[0].message,'domain');
 bridge.dispose();bridge.dispose();assert.equal(terminated,1);assert.throws(()=>bridge.request({}));w.onmessage({data:{id:4,ok:true,state:'late'}});assert.deepEqual(results,['latest']);
});
