import test from 'node:test';import assert from 'node:assert/strict';
import {activeReferenceDiagnostic,constrainedMinimum} from '../tools/reference-active-diagnostic.mjs';import {muscleMaterial,MUSCLE_FIXTURE,determinant} from '../web/anatomical-material.mjs';import {materialTensor} from '../web/anatomical-modal.mjs';import {acousticMatrix} from '../tools/fixed-coefficient-acoustic.mjs';
const p={...MUSCLE_FIXTURE,sigma0:8708387.370104775},F=[1.23,.11,.02,-.04,.93,.03,.01,-.02,.88],f=[1,0,0],a=.03,norm=v=>Math.hypot(...v),relative=(x,y)=>norm(x.map((v,i)=>v-y[i]))/Math.max(1,norm(y));
test('Baseline exactly reproduces original stress, potential and physical tangent',()=>{const r=activeReferenceDiagnostic(F,f,a,p),old=muscleMaterial(F,f,a,p);assert.ok(relative(r.P,old.P)<1e-10);assert.ok(relative(r.C,Array.from(materialTensor(F,f,a,p)))<1e-10);assert.ok(Math.abs(r.energy-old.solvePotential)<1e-10);});
test('Reference/isochoric analytic derivatives and objectivity pass independent finite differences',()=>{
 for(const optimalStretch of [1,1.4,.9183062882196172])for(const isochoric of [false,true]){const options={optimalStretch,isochoric},r=activeReferenceDiagnostic(F,f,a,p,options),direction=F.map((_,i)=>Math.sin(i+1)/3),Cd=r.P.map((_,i)=>direction.reduce((s,v,j)=>s+r.C[9*i+j]*v,0));
  for(const h of [1e-6,5e-7]){const plus=activeReferenceDiagnostic(F.map((v,i)=>v+h*direction[i]),f,a,p,options),minus=activeReferenceDiagnostic(F.map((v,i)=>v-h*direction[i]),f,a,p,options),fd=plus.P.map((v,i)=>(v-minus.P[i])/(2*h)),energyFD=(plus.energy-minus.energy)/(2*h);assert.ok(relative(fd,Cd)<1e-4);assert.ok(Math.abs(energyFD-direction.reduce((s,v,i)=>s+v*r.P[i],0))/Math.max(1,Math.abs(energyFD))<1e-6);}
  const rotated=[...F.slice(3,6).map(v=>-v),...F.slice(0,3),...F.slice(6,9)],q=activeReferenceDiagnostic(rotated,f,a,p,options),Pexpected=[...r.P.slice(3,6).map(v=>-v),...r.P.slice(0,3),...r.P.slice(6,9)];assert.ok(relative(q.P,Pexpected)<1e-10);assert.ok(Math.abs(q.energy-r.energy)<1e-9);
 }
});
test('Exactly admissible rank-one paths retain J and full/iso active laws agree at J=1 up to pressure',()=>{
 const scale=determinant(F)**(-1/3),base=F.map(v=>v*scale),m=[Math.SQRT1_2,Math.SQRT1_2,0];
 for(const optimalStretch of [1,1.4]){const full=activeReferenceDiagnostic(base,f,a,p,{optimalStretch}),iso=activeReferenceDiagnostic(base,f,a,p,{optimalStretch,isochoric:true}),qfull=acousticMatrix(full.C,m),qiso=acousticMatrix(iso.C,m),r=constrainedMinimum(qfull,base,m),s=constrainedMinimum(qiso,base,m);assert.ok(Math.abs(r.valuePa-s.valuePa)/Math.max(1,Math.abs(r.valuePa))<1e-8);
  for(const h of [-1e-3,1e-3]){const trial=base.map((v,i)=>v+h*r.polarization[Math.floor(i/3)]*m[i%3]),x=activeReferenceDiagnostic(trial,f,a,p,{optimalStretch}),y=activeReferenceDiagnostic(trial,f,a,p,{optimalStretch,isochoric:true});assert.ok(Math.abs(determinant(trial)-1)<1e-12);assert.ok(Math.abs(x.energy-y.energy)<1e-9);}
  assert.ok(Math.abs(iso.activeMeanCauchyPa)<1e-8);const c=full.activeMeanCauchyPa;assert.ok(relative(full.activeCauchy.map((v,i)=>v-iso.activeCauchy[i]),[c,0,0,0,c,0,0,0,c])<1e-10);
 }
});
