import test from 'node:test';
import assert from 'node:assert/strict';
import {makeCase,solveReference,solveCompliant,diagnose} from '../contributions/continuum_reference/continuum.mjs';
import {continuumFields,surfaceOwners,vonMises,CONTINUUM_SCALES} from '../web/continuum-display.mjs';
test('element stress field uses owning tetrahedra, retains discontinuities and matches independent uniaxial/shear invariants',()=>{
 assert.equal(vonMises([2000,0,0,0,0,0]),2000);assert.equal(vonMises([100,100,100,0,0,0]),0);
 assert.ok(Math.abs(vonMises([0,0,0,100,0,0])-Math.sqrt(3)*100)<1e-12);
 const p=makeCase({n:2,kind:'affine'}),r=solveReference(p),exact={u:Float64Array.from(p.mesh.nodes.flatMap(p.exact))},owners=surfaceOwners(p.mesh);
 owners.forEach((e,i)=>assert.ok(p.mesh.surface[i].tri.every(node=>p.mesh.tets[e].includes(node))));
 const fields=continuumFields(p,r,exact,diagnose(p,r.u),diagnose(p,exact.u),true,'stress',owners);
 assert.equal(fields.max,4000);assert.equal(fields.units,'Pa');
 for(const v of fields.fields.flat())assert.ok(Math.abs(v-1600)<1e-6,'authored affine stress diag(2400,800,800) has von Mises 1600 Pa');
 const jumpDiag={stressPa:p.elements.map((_,i)=>[i*100,0,0,0,0,0])};
 const jumps=continuumFields(p,r,exact,jumpDiag,jumpDiag,true,'stress',owners);
 jumps.fields[0].forEach((v,face)=>assert.equal(v,owners[face]*100));
});
test('matched nodal error uses its actual target and a fixed common SI scale across sweeps',()=>{
 const p=makeCase({n:3}),h=.002,r=solveReference(p,{h}),owners=surfaceOwners(p.mesh),rd=diagnose(p,r.u,{h});
 const fields=[1,100].map(sweeps=>{const fast=solveCompliant(p,{h,sweeps});return continuumFields(p,r,fast,rd,diagnose(p,fast.u,{h}),false,'error',owners);});
 assert.equal(fields[0].max,CONTINUUM_SCALES.error);assert.equal(fields[1].max,fields[0].max);
 assert.ok(fields[0].fields[0].every(v=>v===0));assert.ok(fields[1].observedMax<fields[0].observedMax/10);
 const analytic={u:Float64Array.from(p.mesh.nodes.flatMap(p.exact))},staticR=solveReference(p);
 const stat=continuumFields(p,staticR,analytic,diagnose(p,staticR.u),diagnose(p,analytic.u),true,'error',owners);
 assert.ok(stat.fields[1].every(v=>v===0));assert.ok(stat.observedMax>0);assert.equal(stat.target,'exact static displacement');
});
