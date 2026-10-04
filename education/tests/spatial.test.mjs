import test from 'node:test';
import assert from 'node:assert/strict';
import {SPATIAL,SPATIAL_MESH as mesh,solveSpatial,spatialEnergy,volumeGradient,signedVolume,capsuleGap,skinPoint,spatialInitial,spatialStep,spatialResults} from '../web/spatial.mjs';
const close=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<t,`${a} vs ${b}`);
test('positive conforming authored mesh, closed separate membrane, correct SI reference volume',()=>{
 assert.equal(mesh.coreCount,81);assert.equal(mesh.tets.length,192);assert.ok(mesh.volume.every(v=>v>0));close(mesh.volume.reduce((a,b)=>a+b,0),.038*.36*.042);
 for(const faces of [mesh.surface,mesh.skinSurface]){const edges=new Map();for(const f of faces)for(let j=0;j<3;j++){const i=f[j],k=f[(j+1)%3],key=[i,k].sort((a,b)=>a-b).join(',');let e=edges.get(key)||[];e.push([i,k]);edges.set(key,e);}for(const e of edges.values()){assert.equal(e.length,2);assert.equal(e[0][0],e[1][1]);}}
 assert.ok(mesh.skinSurface.flat().every(v=>v>=mesh.coreCount));
});
test('volume gradient independently matches finite differences and has zero resultant',()=>{
 const x=mesh.rest.map(p=>p.map((v,d)=>v+(d===0?.007*v*v:0))),t=mesh.tets[77],g=volumeGradient(x,t),h=1e-7;
 for(let i=0;i<4;i++)for(let d=0;d<3;d++){const a=x.map(p=>p.slice()),b=x.map(p=>p.slice());a[t[i]][d]+=h;b[t[i]][d]-=h;close((signedVolume(a,t)-signedVolume(b,t))/(2*h),g[i][d],1e-11);}
 for(let d=0;d<3;d++)close(g.reduce((s,v)=>s+v[d],0),0,1e-15);
});
test('complete edge/volume/membrane/tether/contact energy gradient matches central difference',()=>{
 const q=.7,a=.4,x=mesh.rest.map(X=>skinPoint(X,q));x[35][0]=.014;x[35][2]=.004;
 const r=spatialEnergy(x,q,a),h=1e-7;assert.ok(r.contacts.length>0);
 for(const v of [13,35,44,104])for(let d=0;d<3;d++){const xp=x.map(p=>p.slice()),xm=x.map(p=>p.slice());xp[v][d]+=h;xm[v][d]-=h;close((spatialEnergy(xp,q,a).total-spatialEnergy(xm,q,a).total)/(2*h),r.fullGradient[3*v+d],2e-6);}
});
test('passive reference is zero energy; activation shortens spatial fibres with separate skin',()=>{
 const off=solveSpatial(0,0),on=solveSpatial(0,.6,{...SPATIAL,sweeps:320});close(off.total,0);close(off.muscleLengthM,.18);assert.ok(on.muscleLengthM<.172);assert.ok(on.energy.active>0&&on.energy.skin>0);assert.ok(on.converged);assert.ok(on.fiberArcLengthM>=on.muscleLengthM&&on.fiberArcLengthM<.172);assert.equal(on.fiberChainLengthsM.length,9);assert.ok(Math.abs(on.meanJ-1)<.002);
});
test('same-pose compression comparison, sampled contact improvement and iteration defect remain measurable',()=>{
 const q=Math.PI/2,lo=solveSpatial(q,.6),hi=solveSpatial(q,.6,{...SPATIAL,sweeps:640}),off=solveSpatial(q,.6,{...SPATIAL,sweeps:640,boneContact:'off'});
 assert.ok(hi.maxPenetrationM<.00005);assert.ok(hi.baselinePenetrationM>.009);assert.ok(hi.minJ>.7&&hi.meanJ>.95);assert.ok(hi.baselineMinJ<.18);assert.ok(hi.contactNormalSumN>.5);assert.ok(off.maxPenetrationM>hi.maxPenetrationM*10);assert.equal(off.contactNormalSumN,0);assert.ok(hi.maxFreeForceN<lo.maxFreeForceN);assert.ok(hi.total<=lo.total+1e-10);
 assert.deepEqual(hi.baseline,mesh.rest.map(X=>skinPoint(X,q)));assert.ok(lo.acceptedEnergy.every((E,i,A)=>i===0||E<=A[i-1]+1e-13));assert.ok(hi.volumeRatios.every(J=>J>.01));
});
test('reported contact/support resultant equals the unresolved free gradient, not a hidden extra force',()=>{
 const r=solveSpatial(Math.PI/2,.6),sum=[0,0,0];r.gradient.forEach((g,i)=>sum[i%3]+=g);for(let d=0;d<3;d++)close(r.forceBalanceN[d],-sum[d],1e-10);
});
test('skin-off ablation removes membrane and fascia energies; shape-off removes spatial actuator only',()=>{
 const r=solveSpatial(.5,.6,{...SPATIAL,skin:'off',activeShape:'off'});assert.equal(r.energy.skin,0);assert.equal(r.energy.fascia,0);assert.equal(r.energy.active,0);assert.equal(r.a,.6);
});
test('deterministic reset, lift/release continuity and teaching domain halt',()=>{
 const p={...SPATIAL},initial=spatialInitial(p);let s=initial;
 for(let i=0;i<60;i++)s=spatialStep(s,p);assert.ok(s.q>initial.q&&s.a>.59);const before={...s};const released=spatialStep(s,{...p,excitation:0});assert.ok(released.a<s.a);assert.deepEqual(s,before);
 let lowering=released;for(let n=61;n<180;n++)lowering=spatialStep(lowering,{...p,excitation:0});assert.ok(lowering.q<initial.q&&lowering.w<0&&lowering.a<.011);const afterRelease=solveSpatial(lowering.q,lowering.a,{...p,sweeps:80});assert.ok(afterRelease.muscleLengthM>.165);
 assert.deepEqual(solveSpatial(.5,.3,{...p,sweeps:80}),solveSpatial(.5,.3,{...p,sweeps:80}));assert.deepEqual(spatialInitial(p),initial);assert.throws(()=>solveSpatial(101*Math.PI/180,.3),RangeError);
 const end={...initial,q:100*Math.PI/180,w:10};const stopped=spatialStep(end,p);assert.ok(stopped.halted);assert.equal(stopped.q,end.q);
});
