import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {decomposeVector,hashBytes,validateFrozenInputs,nodalSheets,projectLegacy,freeResolution,constitutiveComponents,componentNodalGradients,maxAbs} from '../tools/isolated-calibration-diagnostic.mjs';
import {midpointNodes} from '../web/anatomical-element.mjs';
import {muscleMaterial,MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from '../tools/anatomical-compression-quadrature.mjs';
import {prepareFurtherBody} from '../tools/anatomical-integration-refinement.mjs';
import {prepareModalBody,modalPositions} from '../web/anatomical-modal.mjs';
import {prepareIntramuscularAponeuroses,evaluateIntramuscularAponeuroses} from '../web/anatomical-aponeurosis.mjs';

const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} versus ${b}; tolerance ${t}`);
const vectorNear=(a,b,t)=>{assert.equal(a.length,b.length);a.forEach((v,k)=>near(v,b[k],t));};
const nodes=midpointNodes([[0,0,0],[.03,0,0],[0,.02,0],[0,0,.01]]);
const source={nodes_m:nodes,elements_ten_node:[[0,1,2,3,4,5,6,7,8,9]],reference_fibres:[[1,0,0]]},modes=nodes.map(()=>[]);
const mv=(F,X)=>[0,1,2].map(d=>[0,1,2].reduce((s,k)=>s+F[3*d+k]*X[k],0));

test('unit-direction decomposition resolves a known omitted force and rank without modal scaling bias',()=>{
 const r=decomposeVector([0,1,2],[[1,1,0],[2,2,0]]);
 assert.equal(r.rank,1);vectorNear(r.retained,[.5,.5,0],1e-14);vectorNear(r.omitted,[-.5,.5,2],1e-14);
 near(r.omittedSquaredNormFraction,.9,1e-14);
 const rescaled=decomposeVector([0,1,2],[[.003,.003,0]]);
 vectorNear(r.omitted,rescaled.omitted,1e-14);
 assert.throws(()=>decomposeVector([1,2],[[1]]),/dimensions/);
});

test('freeze checks reject damaged input bytes and a changed physical acceptance gate',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'kenoma-calibration-freeze-'))+'/';
 try{
  fs.writeFileSync(dir+'fixture','historical bytes');
  const m={stationarity_tolerance_N:1e-4,activation:1,quadrature_points_per_element:[32,256,2048],inputs:{fixture:hashBytes(fs.readFileSync(dir+'fixture'))}};
  validateFrozenInputs(dir,m);
  assert.throws(()=>validateFrozenInputs(dir,{...m,stationarity_tolerance_N:1e-3}),/contract changed/);
  fs.appendFileSync(dir+'fixture','damage');assert.throws(()=>validateFrozenInputs(dir,m),/Frozen input changed/);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('matched affine control preserves exact volume, energy and nodal force across all three quadratures',()=>{
 const F=[.85,.1,0,0,1.07,0,0,0,.98],a=.04,positions=nodes.map(X=>mv(F,X)),expected=muscleMaterial(F,[1,0,0],a);
 const bodies=[prepareCompressionBody(source,modes,1),prepareCompressionBody(source,modes,2),prepareFurtherBody(source,modes)];
 const evaluations=bodies.map(b=>evaluateCompressionBody(b,positions,a,MUSCLE_FIXTURE));
 for(const [k,r] of evaluations.entries()){
  near(bodies[k].referenceVolumeM3,1e-6,1e-18);near(r.energyJ,expected.solvePotential*1e-6,1e-12);near(r.minimumCornerJ,expected.J,1e-12);
  vectorNear(r.nodalGradientN.flat(),evaluations[0].nodalGradientN.flat(),1e-10);
  for(let d=0;d<3;d++)near(r.nodalGradientN.reduce((s,g)=>s+g[d],0),0,1e-10);
 }
});

test('rigid rotation and translation preserve energy and rotate the full assembled gradient',()=>{
 const theta=.63,Q=[Math.cos(theta),-Math.sin(theta),0,Math.sin(theta),Math.cos(theta),0,0,0,1];
 const positions=nodes.map(X=>mv([.85,.1,0,0,1.07,0,0,0,.98],X)),transformed=positions.map(X=>mv(Q,X).map((v,d)=>v+[.014,-.011,.007][d]));
 const body=prepareCompressionBody(source,modes,2),a=.04,A=evaluateCompressionBody(body,positions,a,MUSCLE_FIXTURE),B=evaluateCompressionBody(body,transformed,a,MUSCLE_FIXTURE);
 near(A.energyJ,B.energyJ,1e-12);near(A.minimumJ,B.minimumJ,1e-12);
 vectorNear(B.nodalGradientN.flat(),A.nodalGradientN.map(g=>mv(Q,g)).flat(),1e-9);
});

test('independent stress components and assembly agree with energy derivatives in a compressed control',()=>{
 const F=[.75,.07,0,0,1.02,.02,0,0,.97],a=.4,material={...MUSCLE_FIXTURE,sigma0:8e6},split=constitutiveComponents(F,[1,0,0],a,material);
 for(const [key,P] of Object.entries(split.stressesPa)){
  const energyKey={matrix:'matrix',bulk:'volume',passiveFibre:'passiveFiber',active:'activePotential'}[key];
  for(let i=0;i<9;i++){
   const h=1e-6,A=F.slice(),B=F.slice();A[i]+=h;B[i]-=h;
   near((muscleMaterial(A,[1,0,0],a,material).energy[energyKey]-muscleMaterial(B,[1,0,0],a,material).energy[energyKey])/(2*h),P[i],.001);
  }
 }
 const body=prepareCompressionBody(source,modes,2),positions=nodes.map(X=>mv(F,X)),parts=componentNodalGradients(body,positions,a,material),full=evaluateCompressionBody(body,positions,a,material);
 const sum=full.nodalGradientN.map((_,n)=>[0,1,2].map(d=>Object.values(parts).reduce((s,g)=>s+g[n][d],0)));
 vectorNear(sum.flat(),full.nodalGradientN.flat(),1e-9);
});

test('actual frozen short-biceps sheets retain exact reference embedding and explicit cap constraints',()=>{
 const geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),fit=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json').records.find(r=>r.elementId==='FJ1512');
 const s=geometry.muscles.find(m=>m.element_id===fit.elementId),body=prepareModalBody(s),x=Float64Array.from(fit.match.coordinatesM),positions=modalPositions(body,x),sheets=prepareIntramuscularAponeuroses(body);
 const independent=nodalSheets(s,sheets,positions),canonical=evaluateIntramuscularAponeuroses(body,sheets,x,{hessian:false});
 near(independent.energyJ,canonical.energy,1e-9);vectorNear(projectLegacy(body,independent.gradientN),canonical.gradient,2e-6);
 const r=freeResolution(body,independent.gradientN);assert.equal(r.rank,45);assert.equal(r.freeComponents,1485);assert.equal(r.heldNodes,90);
 const max=maxAbs(independent.gradientN.flat()),index=independent.gradientN.flat().findIndex(v=>Math.abs(v)===max),node=Math.floor(index/3),axis=index%3;
 for(const h of [2e-7,1e-7]){
  const A=structuredClone(positions),B=structuredClone(positions);A[node][axis]+=h;B[node][axis]-=h;
  near((nodalSheets(s,sheets,A).energyJ-nodalSheets(s,sheets,B).energyJ)/(2*h),independent.gradientN[node][axis],1e-4);
 }
});
