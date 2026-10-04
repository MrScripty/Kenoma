import test from 'node:test';
import assert from 'node:assert/strict';
import {forceState,leverState,cross2,springTrace,springStep,springEnergy,exactSpring,DEFAULTS} from '../web/mechanics.mjs';
const near=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
test('force worked example and work-energy consistency across signed forces',()=>{
  near(forceState({mass:2,force:4,time:2}).position,4);
  for (const force of [-8,-1,0,4,8]) {
    const s=forceState({mass:2,force,time:1.7}); near(s.work,s.kinetic);
  }
});
test('lever sign, zero moment arm and exact scaled worked example',()=>{
  near(leverState(DEFAULTS.torque).torque,-14.715);
  near(leverState({...DEFAULTS.torque,angle:90}).torque,0);
  assert.ok(leverState({...DEFAULTS.torque,angle:120}).torque>0);
  assert.equal(cross2([300,0],[0,-49050]),-14715000);
});
test('potential gradient gives the negative gravitational torque',()=>{
  const q=37,h=1e-5;
  const up=leverState({...DEFAULTS.torque,angle:q+h}).potential;
  const down=leverState({...DEFAULTS.torque,angle:q-h}).potential;
  near(-(up-down)/(2*h*Math.PI/180),leverState({...DEFAULTS.torque,angle:q}).torque,1e-7);
});
test('torque identities hold for a deterministic grid of integer inputs',()=>{
  for(let a=-5;a<=5;a++) for(let b=-3;b<=3;b++) {
    const r=[a,b],f=[b,2],g=[3,a],o=[1,-2];
    near(cross2(r,[f[0]+g[0],f[1]+g[1]]),cross2(r,f)+cross2(r,g));
    near(cross2([r[0]-o[0],r[1]-o[1]],f),cross2(r,f)-cross2(o,f));
  }
});
test('step/replay/reset gives identical sequences',()=>{
  for(const method of ['explicit','symplectic','verlet']) {
    const p={...DEFAULTS.energy,method};
    assert.deepEqual(springTrace(p,600),springTrace(p,600));
    assert.deepEqual(springTrace(p,1)[1],{step:1,time:p.dt,...springStep(p,p),energy:springEnergy(springStep(p,p),p)});
  }
});
test('energy diagnostics distinguish unstable explicit from bounded symplectic and Verlet',()=>{
  const p=DEFAULTS.energy,e0=springEnergy(p,p);
  assert.ok(springTrace({...p,method:'explicit'},600).at(-1).energy>e0*1000);
  assert.ok(Math.max(...springTrace(p,600).map(s=>Math.abs(s.energy/e0-1)))<0.07);
  assert.ok(Math.max(...springTrace({...p,method:'verlet'},600).map(s=>Math.abs(s.energy/e0-1)))<0.005);
});
test('Verlet convergence against independent analytic oscillator',()=>{
  const errors=[0.04,0.02,0.01].map(dt=>{
    const p={...DEFAULTS.energy,dt,method:'verlet'};
    return Math.abs(springTrace(p,Math.round(2/dt)).at(-1).x-exactSpring(2,p).x);
  });
  assert.ok(errors[1]<errors[0]/3); assert.ok(errors[2]<errors[1]/3);
});
test('invalid domains fail explicitly',()=>{
  assert.throws(()=>forceState({mass:0,force:1,time:1}),RangeError);
  assert.throws(()=>springStep({x:0,v:0},{...DEFAULTS.energy,method:'bogus'}),RangeError);
  assert.throws(()=>leverState({...DEFAULTS.torque,angle:NaN}),RangeError);
});
