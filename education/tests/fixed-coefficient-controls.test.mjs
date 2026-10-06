import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {axialSource,matchedPrism,prepareControl,evaluateControl,diagnoseControl,frozenHeadSupports,maximum,dot} from '../tools/fixed-coefficient-fixtures.mjs';
import {prepareApparatus} from '../web/anatomical-apparatus.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url)));
const geometry=read('generated/arm-reference.json'),fits=read('audit/modal-fixed-end-results.json'),source=geometry.muscles.find(m=>m.element_id==='FJ1512'),material={...MUSCLE_FIXTURE,sigma0:fits.records.find(r=>r.elementId===source.element_id).match.sigma0Pa};
const near=(a,b,tolerance=1e-8)=>assert.ok(Math.abs(a-b)<=tolerance,`${a} versus ${b}`);
test('matched prism preserves input, topology, volume and length',()=>{
 const before=JSON.stringify(source),p=matchedPrism(source);assert.equal(JSON.stringify(source),before);assert.deepEqual(p.elements_ten_node,source.elements_ten_node);assert.deepEqual(p.distal_nodes,source.distal_nodes);assert.deepEqual(p.proximal_nodes,source.proximal_nodes);
 near(p.reference_volume_m3/source.reference_volume_m3,1,1e-12);assert.deepEqual(p.belly_interval_m,source.belly_interval_m);assert.equal(p.nodes_m.length,source.nodes_m.length);
});
test('uniform prism carries analytic active force without compression or free forces',()=>{
 const p=matchedPrism(source),f=prepareControl(p,{depth:1}),x=new Float64Array(63),a=.3,r=evaluateControl(f,x,a,material,{hessian:false}),d=diagnoseControl(f,x,a,material),analytic=a*material.sigma0*p.reference_volume_m3/(p.belly_interval_m[1]-p.belly_interval_m[0]);
 assert.ok(maximum(f.free.map(i=>r.gradient[i]))<1e-4);assert.ok(d.independentReducedResidualN<1e-4);assert.ok(d.maximumFreeNodalComponentN<1e-4);near(d.globalVolumeRatio,1,1e-11);near(d.minimumCornerJ,1,1e-11);near(d.reactions.active.directDistalN,analytic,1e-7);near(d.reactions.active.axialVirtualForceN,analytic,1e-7);
});
test('independent nodal body, sheet and frozen support forces project and differentiate',()=>{
 const model=prepareApparatus(geometry,read('config/attachments-apparatus.json'),fits,{routingRecipe:read('config/apparatus-routing.json')}),supports=frozenHeadSupports(model,source.element_id),f=prepareControl(axialSource(source),{kind:'attachment',sheets:true,supports,depth:0});assert.ok(supports.branches.length>0&&supports.interfaces.length>0);
 const x=Float64Array.from({length:63},(_,i)=>1e-5*Math.sin(i+1)),v=Float64Array.from({length:63},(_,i)=>Math.cos(2*i+1)),a=.03,r=evaluateControl(f,x,a,material),d=diagnoseControl(f,x,a,material);assert.ok(maximum(d.projectedGradientN.map((g,i)=>g-r.gradient[i]))<2e-6);
 const h=2e-8,plus=evaluateControl(f,x.map((q,i)=>q+h*v[i]),a,material,{hessian:false}),minus=evaluateControl(f,x.map((q,i)=>q-h*v[i]),a,material,{hessian:false});near((plus.energy-minus.energy)/(2*h),dot(r.gradient,v),1e-4);
 const Hv=Array.from({length:63},(_,i)=>dot(Array.from(r.hessian.slice(63*i,63*i+63)),v)),finite=plus.gradient.map((g,i)=>(g-minus.gradient[i])/(2*h)),error=maximum(finite.map((g,i)=>g-Hv[i]));assert.ok(error/Math.max(1,maximum(Hv))<1e-5,`Hessian relative error ${error/maximum(Hv)}`);
});
