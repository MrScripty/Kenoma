import test from 'node:test';
import assert from 'node:assert/strict';
import {equilibrium,storedEnergy,labState,axialStiffness,shearStiffness,DEFAULT_INPUT} from './model.mjs';
const close=(x,y)=>assert.ok(Math.abs(x-y)<=1e-24+1e-12*Math.max(Math.abs(x),Math.abs(y)),`${x} != ${y}`);
// Exactly 24 admitted closed-form states. No optimizer, trajectory or anatomy.
export const CASES=[0,1e-6,2e-6].flatMap(delta=>[[100,100],[50,200]].flatMap(([K1,K2])=>[[0,0],[100,100],[0,100],[25,400]].map(([CL,CR])=>({K1,K2,CL,CR,delta}))));
test('24 closed-form states match an independent reciprocal-compliance oracle',()=>{
 assert.equal(CASES.length,24);
 for(const p of CASES){
  const r=equilibrium(p),rightBranch=p.CR===0?0:p.delta/(1/p.K1+1/p.CR),leftBranch=p.CL===0?0:p.delta/(1/p.K2+1/p.CL);
  close(r.upperForceN,rightBranch);close(r.lowerForceN,leftBranch);
  close(r.leftPullN,rightBranch+leftBranch);close(r.rightPullN,rightBranch+leftBranch);
  for(const residual of [r.externalLeftForceN+r.externalRightForceN,r.upperResidualN,r.lowerResidualN])
   assert.ok(Math.abs(residual)<1e-18,'Sub-attonewton roundoff bound for this authored SI range');
  close(r.energyJ,r.reducedEnergyJ);
  assert(r.effectiveStiffnessNPerM>=0&&r.effectiveStiffnessNPerM<p.K1+p.K2);
  // Independent quadratic completion evaluated at a displaced trial point.
  const du=3e-7,dv=-2e-7;
  close(storedEnergy(p,r.u+du,r.v+dv)-r.energyJ,(p.K1+p.CR)*du*du/2+(p.K2+p.CL)*dv*dv/2);
 }
});
test('material moduli, geometry, stiffness and SI are separate',()=>{
 close(axialStiffness(1e6,1e-6,.01),100);close(shearStiffness(20000,1e-6,.0002),100);
 const r=labState();close(r.u,.5e-6);close(r.v,.5e-6);close(r.rightPullN,.0001);close(r.energyJ,5e-11);
 assert.deepEqual(r.input,DEFAULT_INPUT);
});
test('zero links disconnect end force while a driven free endpoint can still move',()=>{
 const r=labState({...DEFAULT_INPUT,leftShearKPa:0,rightShearKPa:0});
 close(r.u,0);close(r.v,r.delta);close(r.rightPullN,0);close(r.energyJ,0);
});
test('input rejection includes invalid material and preserves caller data',()=>{
 for(const x of [NaN,Infinity,-1])assert.throws(()=>axialStiffness(x,1,.01),RangeError);
 for(const x of [0,-1,NaN])assert.throws(()=>shearStiffness(0,1,x),RangeError);
 for(const patch of [{deltaMicrometres:NaN},{deltaMicrometres:3},{leftShearKPa:-1},{rightShearKPa:81},{preset:'human'},{leftShearKPa:''}]){
  const input={...DEFAULT_INPUT,...patch},before={...input};assert.throws(()=>labState(input),RangeError);assert.deepEqual(input,before);
 }
});
