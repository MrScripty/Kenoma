import test from 'node:test';
import assert from 'node:assert/strict';
import {ELBOW,elbowResults} from '../web/elbow.mjs';
import {SERIES,seriesEquilibrium,seriesInitial,seriesResults,seriesStep,seriesTrace} from '../web/series.mjs';
import {SPATIAL,spatialResults,spatialStep} from '../web/spatial.mjs';
const near=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
const independentlyActive=(f,a,p)=>p.maxForce*a*Math.exp(-(((f-p.optimalFiber)/(p.width*p.optimalFiber))**2));
test('rigid tendon/contact-off cumulatively retains Lab4 force–length, moments and energy over the full pose/activation domain',()=>{
 for(const angle of [0,15,30,60,90,110,135])for(const a of [0,.2,.6,1]){
  const s={...seriesInitial(),q:angle*Math.PI/180,w:.4,a},p={...SERIES,tendon:'rigid',contact:'off'},earlier=elbowResults(s,ELBOW),later=seriesResults(s,p);
  for(const key of ['active','passive','tension','fiber','fiberSpeed','muscleTorque','activeTorque','passiveTorque','gravityTorque','acceleration','energy','activePower']){
   if(key==='muscleTorque')near(later[key],earlier.activeTorque+earlier.passiveTorque);
   else near(later[key],earlier[key]);
  }
 }
 const s={...seriesInitial(),q:Math.PI/2,a:.6},r=seriesResults(s,{...SERIES,tendon:'rigid',contact:'off'});
 near(r.active,independentlyActive(r.fiber,.6,SERIES));assert.ok(r.active>670&&r.active<672);assert.ok(r.active<720-40);
});
test('compliant nonlinear equilibrium matches an independent tension-coordinate root and force–length law',()=>{
 for(const path of [.14,.18,.23,.28])for(const a of [0,.2,.6,1])for(const tendonK of [15000,30000,60000]){
  const p={...SERIES,tendonK},L=path-p.tendonLength;
  const residual=T=>T-independentlyActive(L-T/tendonK,a,p)-p.passiveK*Math.max(0,L-T/tendonK-p.optimalFiber);
  let lo=0,hi=p.maxForce*a+p.passiveK*Math.max(0,L-p.optimalFiber);
  for(let i=0;i<60;i++){const mid=(lo+hi)/2;if(residual(mid)>0)hi=mid;else lo=mid;}
  const m=seriesEquilibrium(path,a,p);near(m.tension,(lo+hi)/2);near(m.active,independentlyActive(m.fiber,a,p));
  near(m.forceResidual,0);near(m.tendon,p.tendonLength+m.tension/tendonK);near(m.fiber+m.tendon,path);
  assert.ok(m.denominator>0&&m.fiber>0&&m.tension>=0);
 }
 assert.throws(()=>seriesEquilibrium(.23,.6,{...SERIES,tendonK:1000}),/monotone/);
});
test('implicit fiber velocity matches differentiated equilibria including active length slope and activation input',()=>{
 for(const angle of [30,90,120])for(const tendon of ['rigid','compliant'])for(const excitation of [0,.9]){
  const p={...SERIES,tendon,excitation},s={...seriesInitial(p),q:angle*Math.PI/180,w:.5,a:.4},r=seriesResults(s,p),e=1e-7;
  const plus=seriesEquilibrium(r.length+e*r.pathSpeed,s.a+e*r.activationRate,p);
  const minus=seriesEquilibrium(r.length-e*r.pathSpeed,s.a-e*r.activationRate,p);
  near(r.fiberSpeed,(plus.fiber-minus.fiber)/(2*e),1e-8);
  near(r.activePower-(r.passive*r.fiberSpeed+r.tension*r.tendonSpeed),r.hingeMusclePower);
 }
});
test('repaired law preserves fixed-end work balance, release lengthening, replay and trajectory refinement',()=>{
 const p={...SERIES,mode:'prescribed',angle:90,dt:.0025},initial=seriesInitial(p),E0=seriesResults(initial,p).energy;let s=initial;
 for(let i=0;i<120;i++)s=seriesStep(s,p);
 const held=seriesResults(s,p);assert.ok(held.fiber<seriesResults(initial,p).fiber);near(held.energy-E0,s.work,1e-6);
 const release=seriesStep(s,{...p,excitation:0}),released=seriesResults(release,{...p,excitation:0});
 assert.ok(released.fiber>held.fiber&&released.active>0&&released.activePower<0);assert.equal(release.q,initial.q);
 const coarse=seriesTrace({...SERIES,dt:.01}),fine=seriesTrace({...SERIES,dt:.0025});
 const error=trace=>Math.max(...trace.map(x=>Math.abs(x.balanceResidual)));
 assert.deepEqual(fine,seriesTrace({...SERIES,dt:.0025}));assert.ok(!fine.at(-1).halted&&error(fine)<error(coarse));
 assert.ok(error(fine)<1e-5);
});
test('spatial hinge consumer uses the repaired shared law without adding spatial tissue force to the hinge',()=>{
 const p={...SPATIAL,tendon:'rigid',sweeps:80},s={...seriesInitial(p),q:Math.PI/2,a:.6};
 const actual=spatialResults(s,p),line=seriesResults(s,{...p,contact:'off'});
 near(actual.hinge.active,670.6825658707231);assert.deepEqual(actual.hinge,line);
 assert.deepEqual(spatialStep(s,p),seriesStep(s,{...p,contact:'off'}));
});
