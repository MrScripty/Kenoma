import test from 'node:test';import assert from 'node:assert/strict';
import {TISSUE,blockEnergy,blockStress,tissueAt,lbsPoint} from '../web/tissue.mjs';
import {SERIES,seriesEquilibrium,seriesInitial,seriesResults,seriesStep,seriesTrace} from '../web/series.mjs';
const close=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
test('series force equilibrium, length partition, slack and rigid limit',()=>{
 for(const path of [.18,.23,.28])for(const a of [0,.2,1]){
  const m=seriesEquilibrium(path,a);close(m.tension,m.active+m.passive);close(m.fiber+m.tendon,path);
  assert.ok(m.tension>=0&&m.tendon>=SERIES.tendonLength);
 }
 const slack=seriesEquilibrium(.18,0);close(slack.tension,0);close(slack.tendon,SERIES.tendonLength);
 const rigid=seriesEquilibrium(.23,.6,{...SERIES,tendon:'rigid'}),stiff=seriesEquilibrium(.23,.6,{...SERIES,tendonK:1e12});
 close(rigid.fiber,stiff.fiber,1e-9);close(rigid.tension,stiff.tension,1e-5);
});
test('fixed ends permit fiber shortening and tendon storage under activation',()=>{
 const p={...SERIES,mode:'prescribed',angle:90};const start=seriesInitial(p),initial=seriesResults(start,p);let s=start;
 for(let i=0;i<60;i++)s=seriesStep(s,p);
 const r=seriesResults(s,p);close(s.q,start.q);assert.ok(r.fiber<initial.fiber&&r.tendon>initial.tendon&&r.tendonEnergy>0&&s.work>0);
 assert.ok(Math.abs(r.energy-initial.energy-s.work)<1e-5);
 const next=seriesStep(s,{...p,excitation:0}),release=seriesResults(next,{...p,excitation:0});
 assert.ok(next.a>0&&release.fiber>r.fiber&&release.active>0&&release.fiberSpeed>0);
});
test('active fiber power differs from skeletal power but obeys the full elastic balance',()=>{
 const s={...seriesInitial(),a:.4,w:.8},r=seriesResults(s);
 assert.ok(Math.abs(r.activePower-r.hingeMusclePower)>1);
 const passivePower=r.passive*r.fiberSpeed+r.tension*r.tendonSpeed;
 close(r.activePower-passivePower,r.hingeMusclePower);
});
test('hyperelastic stress independently matches energy gradients',()=>{
 for(const [t,h] of [[1,1],[1.15,.7],[.9,.85]]){
  const e=1e-6,V=TISSUE.width*TISSUE.height*TISSUE.depth,p=blockStress(t,h);
  close((blockEnergy(t+e,h)-blockEnergy(t-e,h))/(2*e),2*V*p.px,1e-7);
  close((blockEnergy(t,h+e)-blockEnergy(t,h-e))/(2*e),V*p.py,1e-7);
 }
 close(blockEnergy(1,1),0);close(blockStress(1,1).px,0);close(blockStress(1,1).py,0);
});
test('compression preserves most volume and satisfies free sides and ideal contact',()=>{
 const r=tissueAt(Math.PI/2);assert.ok(r.normal>0&&r.lateralStretch>1&&r.volumeRatio>.97&&r.volumeRatio<1);
 close(r.clearance,0);close(r.complementarity,0);assert.ok(r.lateralStressResidual<1e-8);
 const e=1e-6;close(r.torque,-(tissueAt(Math.PI/2+e).energy-tissueAt(Math.PI/2-e).energy)/(2*e),1e-7);
 const separated=tissueAt(.2);close(separated.normal,0);assert.ok(separated.clearance>0);
 const noContact=tissueAt(Math.PI/2,TISSUE,false);assert.ok(noContact.penetration>0);close(noContact.normal,0);
 const noBulk=tissueAt(Math.PI/2,{...TISSUE,bulk:0});assert.ok(noBulk.volumeRatio<.5);close(noBulk.normal,0,1e-8);
 close(r.skinVolumeRatio,.5); // original exact shared-pivot LBS fixture at 90 degrees
 const [a,b,c]=[[1,0,0],[0,1,0],[0,0,1]].map(v=>lbsPoint(v,Math.PI/2));
 close(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]),.5);
});
test('coupled pulse/release work balance refines and tissue feedback is explicit',()=>{
 const coarse=seriesTrace({...SERIES,dt:.01}),fine=seriesTrace({...SERIES,dt:.0025});
 assert.deepEqual(fine,seriesTrace({...SERIES,dt:.0025}));assert.ok(!fine.at(-1).halted);
 const error=rows=>Math.max(...rows.map(r=>Math.abs(r.balanceResidual)));
 assert.ok(error(fine)<error(coarse));assert.ok(error(fine)<.0001);
 const s={...seriesInitial(),q:Math.PI/2,a:.6},on=seriesResults(s),off=seriesResults(s,{...SERIES,contact:'off'});
 close((on.acceleration-off.acceleration)*on.inertia,on.tissue.torque);
});
