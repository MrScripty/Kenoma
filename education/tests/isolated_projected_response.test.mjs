import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareModalBody} from '../web/anatomical-modal.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
import {prepareResponseBody,addResponseDirection,responsePositions,evaluateResponse,cholesky,solveCholesky} from '../tools/isolated-projected-response.mjs';
import {evaluateCompressionBody} from '../tools/anatomical-compression-quadrature.mjs';
import {meshPartition,originalFreeColumns,cartesianColumns,dot,maxAbs} from '../tools/isolated-displacement-family.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url)));
const full=read('generated/arm-reference.json').muscles.find(m=>m.element_id==='FJ1486'),fit=read('audit/modal-fixed-end-results.json').records.find(r=>r.elementId==='FJ1486'),modal=prepareModalBody(full),source={...full,elements_ten_node:[full.elements_ten_node[150]],reference_fibres:[full.reference_fibres[150]]},material={...MUSCLE_FIXTURE,sigma0:fit.match.sigma0Pa};
const body=prepareResponseBody(source,modal,material,32),z=Float64Array.from(fit.match.coordinatesM.slice(9,54)),partition=meshPartition(full),columns=cartesianColumns(originalFreeColumns(full,modal.nodeModes,partition).columns);
const direction=full.nodes_m.map(()=>[0,0,0]);partition.free.forEach((n,i)=>{direction[n]=[0,1,2].map(d=>Math.sin((3*i+d)*.17));});const norm=Math.hypot(...direction.flat());direction.forEach(v=>v.forEach((x,d)=>v[d]=x/norm));
const near=(a,b,t)=>assert.ok(Math.abs(a-b)<=t,`${a} vs ${b}`);
test('45-column body projection agrees with independent existing full nodal assembly',()=>{
 const r=evaluateResponse(body,z),fullResult=evaluateCompressionBody(body.prepared,responsePositions(body,z),1,material),g=partition.free.flatMap(n=>fullResult.nodalGradientN[n]);
 near(r.energyJ,fullResult.energyJ,1e-12);columns.forEach((c,k)=>near(dot(c,g),r.gradientN[k],1e-9));
 for(let i=0;i<45;i++)for(let j=0;j<45;j++)near(r.hessianNPerM[45*i+j],r.hessianNPerM[45*j+i],1e-9);
});
test('one general vector direction preserves original coordinates and passes energy and tangent differences',()=>{
 const before=responsePositions(body,z);addResponseDirection(body,direction);const x=Float64Array.from([...z,0]);assert.deepEqual(responsePositions(body,x),before);
 const r=evaluateResponse(body,x),v=Float64Array.from({length:46},(_,i)=>Math.cos(.19*i)),nv=Math.hypot(...v);v.forEach((s,i)=>v[i]=s/nv);
 for(const h of [1e-7,5e-8]){
  const A=evaluateResponse(body,x.map((s,k)=>s+h*v[k]),{hessian:false}),B=evaluateResponse(body,x.map((s,k)=>s-h*v[k]),{hessian:false});
  near((A.energyJ-B.energyJ)/(2*h),dot(r.gradientN,v),1e-6);
  const exact=Float64Array.from({length:46},(_,i)=>v.reduce((s,w,k)=>s+w*r.hessianNPerM[46*i+k],0));
  assert.ok(maxAbs(exact.map((s,k)=>s-(A.gradientN[k]-B.gradientN[k])/(2*h)))<.05);
 }
 assert.throws(()=>addResponseDirection(body,direction),/frozen once/);
});
test('unqualified tangent and nonzero cap direction are refused without regularizing the law',()=>{
 assert.throws(()=>cholesky([1,0,0,-1],2),/Nonpositive/);const H=[4,1,1,3],b=[1,2],x=solveCholesky(cholesky(H,2),b);near(4*x[0]+x[1],1,1e-14);near(x[0]+3*x[1],2,1e-14);
 const damaged=direction.map(v=>v.slice());damaged[full.distal_nodes[0]][0]=1e-15;const other=prepareResponseBody(source,modal,material,32);assert.throws(()=>addResponseDirection(other,damaged),/nonzero cap/);
});
