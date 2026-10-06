import test from 'node:test';import assert from 'node:assert/strict';
import {currentNewtonPreconditioner} from '../tools/current-newton-preconditioner.mjs';
import {denseReferencePreconditioner} from '../web/anatomical-preconditioner.mjs';
import {pcg} from '../web/anatomical-newton.mjs';
test('current SPD preconditioning solves the unchanged linear operator in one PCG step',()=>{
 const H=[[4,1],[1,3]],reference=denseReferencePreconditioner([[1,0],[0,1]]),p=currentNewtonPreconditioner(H,reference),apply=v=>Float64Array.from(H,row=>row.reduce((s,a,i)=>s+a*v[i],0)),b=new Float64Array([1,2]),r=pcg(apply,b,{precondition:p.precondition,maxIterations:80,tolerance:1e-3});assert.ok(r.converged);assert.equal(r.iterations,1);assert.ok(Math.hypot(...apply(r.x).map((v,i)=>v-b[i]))<1e-12);assert.equal(p.stats.referenceApplications,0);
});
test('indefinite factorization falls back without masking negative curvature or choosing a shift',()=>{
 const H=[[-1,0],[0,2]],p=currentNewtonPreconditioner(H,denseReferencePreconditioner([[1,0],[0,1]])),r=pcg(v=>new Float64Array([-v[0],2*v[1]]),new Float64Array([1,0]),{precondition:p.precondition,maxIterations:80,tolerance:1e-3});assert.equal(r.reason,'nonpositive curvature');assert.deepEqual(p.stats.rejectedSPDShiftsNPerM,[0]);assert.equal(p.stats.referenceApplications,1);
 const shifted=p.precondition(new Float64Array([1,1]),2);assert.ok(Math.abs(shifted[0]-1)<1e-12&&Math.abs(shifted[1]-.25)<1e-12);assert.equal(p.stats.currentApplications,1);assert.deepEqual(p.stats.rejectedSPDShiftsNPerM,[0]);
});
