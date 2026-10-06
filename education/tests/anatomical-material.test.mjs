import test from 'node:test';
import assert from 'node:assert/strict';
import {MUSCLE_FIXTURE,muscleMaterial,tendonMaterial,tendonSegment,activeCurve} from '../web/anatomical-material.mjs';
const I=[1,0,0,0,1,0,0,0,1],close=(a,b,t=1e-7)=>assert(Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`),multiply=(A,B)=>Array.from({length:9},(_,i)=>{const r=Math.floor(i/3),c=i%3;return [0,1,2].reduce((s,k)=>s+A[r*3+k]*B[k*3+c],0);});
test('Authored finite-strain passive/active stress is the independent central-difference potential derivative',()=>{
 for(const F of [I,[.86,.04,0,.01,1.08,.03,0,.01,1.09],[1.12,.06,-.02,0,.99,.02,.01,0,.95]])for(const a of [0,.6,1]){
  const f=[.6,.8,0],r=muscleMaterial(F,f,a),h=1e-7;
  // Passive tension switches at lambda=1: its energy is C1, and a symmetric
  // derivative there has O(h) error. Keep an explicit sub-millipascal floor.
  for(let i=0;i<9;i++){const plus=F.slice(),minus=F.slice();plus[i]+=h;minus[i]-=h;const difference=(muscleMaterial(plus,f,a).solvePotential-muscleMaterial(minus,f,a).solvePotential)/(2*h);assert(Math.abs(difference-r.P[i])<=.001+4e-6*Math.abs(r.P[i]),`${difference} != ${r.P[i]} Pa`);}
 }
});
test('Finite rigid rotations preserve energy and rotate first Piola stress objectively',()=>{
 const q=.9,R=[Math.cos(q),-Math.sin(q),0,Math.sin(q),Math.cos(q),0,0,0,1],F=[.93,.04,0,0,1.08,.02,.01,0,1.01],a=muscleMaterial(F,[0,1,0],.6),b=muscleMaterial(multiply(R,F),[0,1,0],.6),RP=multiply(R,a.P);
 close(a.solvePotential,b.solvePotential);close(a.lambda,b.lambda);b.P.forEach((v,i)=>close(v,RP[i]));
 const rest=muscleMaterial(R,[0,1,0],0);close(rest.passiveStored,0,1e-8);rest.P.forEach(v=>close(v,0,1e-8));
});
test('Active axial traction, supported force-length interval and potential are separate from passive storage',()=>{
 const r=muscleMaterial(I,[0,1,0],.6);close(r.P[4],.6*MUSCLE_FIXTURE.sigma0);close(r.passiveStored,0);close(r.energy.activePotential,0);
 for(const l of [.2,.5,.9,1,1.1,1.5,2]){const h=1e-6,d=(activeCurve(l+h).primitive-activeCurve(l-h).primitive)/(2*h);close(d,activeCurve(l).value,1e-8);}
 assert(activeCurve(.2).value===0&&activeCurve(2).value===0);
});
test('Tensile tendon has consistent energy, slack and continuous toe stress/tangent',()=>{
 for(const e of [-.1,0,.01,.029,.03,.05]){const h=1e-7,r=tendonMaterial(e),d=(tendonMaterial(e+h).energyDensityPa-tendonMaterial(e-h).energyDensityPa)/(2*h);close(d,r.stressPa,1e-5);assert(r.stressPa>=0);}
 const below=tendonMaterial(.03-1e-10),above=tendonMaterial(.03+1e-10);close(below.stressPa,above.stressPa,1e-7);close(below.tangentPa,above.tangentPa,1e-7);
 const L0=.05,A0=1e-5,l=.052,h=1e-7,r=tendonSegment(l,L0,A0);close((tendonSegment(l+h,L0,A0).storedEnergyJ-tendonSegment(l-h,L0,A0).storedEnergyJ)/(2*h),r.forceN,1e-7);assert.equal(tendonSegment(.04,L0,A0).forceN,0);
});
test('Invalid/inverted material states fail rather than yield plausible stresses',()=>{
 assert.throws(()=>muscleMaterial([-1,0,0,0,1,0,0,0,1],[0,1,0],.6));assert.throws(()=>muscleMaterial(I,[0,2,0],.6));assert.throws(()=>muscleMaterial(I,[0,1,0],1.2));assert.throws(()=>tendonSegment(.1,0,1e-5));
});
