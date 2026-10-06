import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {quadraticRingFixture,liftAffineCoordinates,diagnoseQuadratic} from '../tools/fixed-coefficient-quadratic-space.mjs';
import {axialSource,matchedPrism,prepareControl,maximum,dot} from '../tools/fixed-coefficient-fixtures.mjs';
import {modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url))),g=read('generated/arm-reference.json'),source=axialSource(g.muscles.find(m=>m.element_id==='FJ1512')),baseline=read('audit/fixed-coefficient-taper.json'),material=baseline.material;
test('quadratic ring space embeds the original field exactly and fixes cap traces',()=>{
 const old=prepareControl(source,{depth:0}),next=quadraticRingFixture(source,0),x=Float64Array.from(baseline.accepted[1].coordinatesM),q=liftAffineCoordinates(x),A=modalPositions(old.body,x),B=modalPositions(next.body,q);assert.equal(next.free.length,90);assert.ok(maximum(A.flatMap((v,n)=>v.map((a,d)=>a-B[n][d])))<1e-12);
 const a=evaluateModalBody(old.body,x,.01,{material,hessian:false}),b=evaluateModalBody(next.body,q,.01,{material,hessian:false});assert.ok(Math.abs(a.energy-b.energy)<1e-8);assert.ok(maximum(a.gradient.map((v,i)=>v-b.gradient[Math.floor(i/9)*18+i%9]))<2e-6);
 const d=diagnoseQuadratic(next,q,.01,material);assert.ok(d.maximumHeldDisplacementM<=1e-12);assert.ok(maximum(d.projectedGradientN.map((v,i)=>v-b.gradient[i]))<2e-6);
});
test('enriched prism still has the analytic undeformed solution',()=>{
 const p=matchedPrism(source),f=quadraticRingFixture(p,0),x=new Float64Array(126),r=evaluateModalBody(f.body,x,.01,{material,hessian:false}),d=diagnoseQuadratic(f,x,.01,material);assert.ok(maximum(f.free.map(i=>r.gradient[i]))<1e-4);assert.ok(d.independentReducedResidualN<1e-4);assert.ok(d.maximumFreeNodalComponentN<1e-4);assert.ok(Math.abs(d.reactions.active.directDistalN-.01*material.sigma0*p.reference_volume_m3/(p.belly_interval_m[1]-p.belly_interval_m[0]))<1e-7);
});
test('new quadratic modes have independently projected and differentiated forces',()=>{
 const f=quadraticRingFixture(source,0),x=new Float64Array(126),v=new Float64Array(126);for(const i of f.free){x[i]=1e-6*Math.sin(i);if(i%18>=9)v[i]=Math.cos(i);}
 const r=evaluateModalBody(f.body,x,.01,{material}),d=diagnoseQuadratic(f,x,.01,material),h=2e-8,plus=evaluateModalBody(f.body,x.map((a,i)=>a+h*v[i]),.01,{material,hessian:false}),minus=evaluateModalBody(f.body,x.map((a,i)=>a-h*v[i]),.01,{material,hessian:false});assert.ok(maximum(d.projectedGradientN.map((a,i)=>a-r.gradient[i]))<2e-6);assert.ok(Math.abs((plus.energy-minus.energy)/(2*h)-dot(r.gradient,v))<1e-4);
 const Hv=Array.from({length:126},(_,i)=>dot(Array.from(r.hessian.slice(126*i,126*i+126)),v)),finite=plus.gradient.map((a,i)=>(a-minus.gradient[i])/(2*h));assert.ok(maximum(finite.map((a,i)=>a-Hv[i]))/Math.max(1,maximum(Hv))<1e-5);
});
