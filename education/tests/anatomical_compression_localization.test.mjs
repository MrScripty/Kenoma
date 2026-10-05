import test from 'node:test';
import assert from 'node:assert/strict';
import {meanStressSplit} from '../tools/anatomical-compression-localization.mjs';
import {MUSCLE_FIXTURE,muscleMaterial} from '../web/anatomical-material.mjs';
const near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<t,`${a} vs ${b}`);
test('full fibre stretch gives an active mean stress while the isochoric matrix has zero trace',()=>{
 for(const F of [[.78,.11,0,0,1.08,.06,.04,0,.94],[1.13,.1,0,0,.98,0,0,0,1.02]]){
  const r=meanStressSplit(F,[1,0,0],.037,{...MUSCLE_FIXTURE,sigma0:20e6});
  near(r.matrixPa,0,1e-8);near(r.totalPa,r.volumePa+r.activePa+r.passiveFibrePa,1e-8);assert.ok(r.activePa>0);
 }
});
test('dilation energy derivative independently checks the mean Cauchy stress identity',()=>{
 const F=[.78,.11,0,0,1.08,.06,.04,0,.94],p={...MUSCLE_FIXTURE,sigma0:20e6},a=.037,h=1e-6,r=meanStressSplit(F,[1,0,0],a,p),energy=t=>muscleMaterial(F.map(v=>v*Math.exp(t)),[1,0,0],a,p).solvePotential;
 near((energy(h)-energy(-h))/(2*h),3*r.J*r.totalPa,1e-3);
});
