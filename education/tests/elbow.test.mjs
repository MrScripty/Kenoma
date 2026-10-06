import test from 'node:test';import assert from 'node:assert/strict';
import {ELBOW,activation,elbowInitial,elbowGeometry,elbowResults,elbowStep,elbowTrace} from '../web/elbow.mjs';
const close=(a,b,t=1e-9)=>assert.ok(Math.abs(a-b)<t,`${a} vs ${b}`);
test('activation exact transient, bounds and continuing release',()=>{
 close(activation(0,1,0.05,0.05),1-Math.exp(-1));
 for(const a of [0,.3,1])for(const u of [0,.6,1])for(const h of [0,.005,10])assert.ok(activation(a,u,h,.05)>=0&&activation(a,u,h,.05)<=1);
 const a=activation(0,.6,.2,.05);assert.ok(activation(a,0,.005,.15)>0);
 assert.throws(()=>activation(0,2,.01,.05));
});
test('path derivative, force moment and virtual power agree independently',()=>{
 for(const q of [.2,.8,1.5,2.2]){
  const r=elbowGeometry(q),eps=1e-6;
  close(r.momentArm,-(elbowGeometry(q+eps).length-elbowGeometry(q-eps).length)/(2*eps),1e-10);
  const fx=-r.point[0]/r.length,fy=(ELBOW.origin-r.point[1])/r.length;
  close(r.point[0]*fy-r.point[1]*fx,r.momentArm);
  const s={...elbowInitial(),q,w:.4,a:.6};const x=elbowResults(s);close(x.activePower,-x.active*x.fiberSpeed);
 }
});
test('gravity counted once and inertia include explicit point masses',()=>{
 const s={...elbowInitial(),q:Math.PI/2};const r=elbowResults(s);
 close(r.gravityTorque,-19.37475);close(r.inertia,.68125);
 const eps=1e-6;close(r.gravityTorque,-(elbowResults({...s,q:s.q+eps}).energy-elbowResults({...s,q:s.q-eps}).energy)/(2*eps),1e-7);
});
test('forward lift, delayed release, replay and refined work balance',()=>{
 const coarse=elbowTrace({...ELBOW,dt:.01}),fine=elbowTrace({...ELBOW,dt:.005}),ref=elbowTrace({...ELBOW,dt:.0025});
 assert.deepEqual(fine,elbowTrace({...ELBOW,dt:.005}));assert.ok(fine[60].q>fine[0].q);
 assert.ok(fine[61].a>0&&fine[61].a<fine[60].a);assert.ok(fine.at(-1).q<fine[60].q || fine.at(-1).w<fine[60].w);
 assert.ok(!ref.at(-1).halted);const err=t=>Math.abs(t.at(-1).q-ref.at(-1).q);
 assert.ok(err(fine)<err(coarse));assert.ok(Math.max(...ref.map(s=>Math.abs(s.balanceResidual)))<1e-5);
});
test('prescribed hold reports external motor and domain stop invents no impulse',()=>{
 const p={...ELBOW,mode:'prescribed'},s=elbowInitial(p),next=elbowStep(s,p),r=elbowResults(next,p);
 close(next.q,s.q);close(next.w,0);assert.ok(next.a>0);close(r.motorTorque+r.activeTorque+r.passiveTorque+r.gravityTorque,0);
 const edge={...s,q:0,w:-2},stopped=elbowStep(edge,ELBOW);assert.ok(stopped.halted);close(stopped.q,0);close(stopped.w,-2);close(stopped.time,0);
});
test('straight-path dead centre keeps zero angle despite developed tension, without a halt or nudge',()=>{
 const p={...ELBOW,angle:0,excitation:1};let s=elbowInitial(p);
 for(let i=0;i<200;i++)s=elbowStep(s,p);
 const r=elbowResults(s,p);
 assert.equal(s.q,0);assert.equal(s.w,0);assert.equal(s.halted,false);
 assert.ok(s.a>.999&&r.tension>1100);assert.equal(r.momentArm,0);
 assert.equal(r.activeTorque,0);assert.equal(r.passiveTorque,0);
});
