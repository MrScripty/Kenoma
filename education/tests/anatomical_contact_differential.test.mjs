import test from 'node:test';import assert from 'node:assert/strict';import {closestTriangle} from '../web/anatomical-distance.mjs';import {closestFeatureDifferential} from '../web/anatomical-contact-differential.mjs';
const norm=a=>Math.hypot(...a),sub=(a,b)=>a.map((v,i)=>v-b[i]),triangle=[[.01,.02,-.01],[.05,.025,.005],[.015,.06,.012]];
function query(point,T,inside){const q=closestTriangle(point,T),d=sub(point,q.point),distance=norm(d);return {...q,inside,signedDistanceM:distance*(inside?-1:1),gradient:d.map(v=>v/distance*(inside?-1:1))};}
test('face, edge and vertex contact differentials include triangle motion and agree with independent second differences',()=>{for(const [P,inside,expected] of [[[.025,.035,.018],false,'face'],[[.038,.002,.009],false,'edge'],[[-.03,-.02,-.04],true,'vertex']]){const Q=query(P,triangle,inside),r=closestFeatureDifferential(P,triangle,Q);assert.equal(r.feature,expected);assert.ok(Math.abs(r.value-Q.signedDistanceM)<1e-14);const values=[P,...triangle].flat(),v=values.map((_,i)=>Math.sin(i+1)*.003),eps=1e-5,shift=t=>{const flat=values.map((x,i)=>x+t*v[i]),X=Array.from({length:4},(_,i)=>flat.slice(3*i,3*i+3));return closestFeatureDifferential(X[0],X.slice(1),query(X[0],X.slice(1),inside));},plus=shift(eps),minus=shift(-eps);for(let i=0;i<12;i++){const hv=v.reduce((s,x,j)=>s+r.hessian[i*12+j]*x,0),fd=(plus.gradient[i]-minus.gradient[i])/(2*eps);assert.ok(Math.abs(hv-fd)<1e-8,`${expected} ${i}: ${hv} versus ${fd}`);}for(let d=0;d<3;d++){const net=[0,1,2,3].reduce((s,k)=>s+r.gradient[3*k+d],0);assert.ok(Math.abs(net)<1e-12);}}});
import {regularizedMinimum} from '../web/anatomical-contact-differential.mjs';
test('simplex contact envelope is conservative, isolated-feature exact and permutation invariant',()=>{
 const w=1e-6;
 for(const distances of [[.0002],[.0002,.0005],[.0002,.0002],[.0002,.00020025,.0002005,.000202]]){
  const r=regularizedMinimum(distances,w),minimum=Math.min(...distances);
  assert.ok(r.weights.every(v=>v>=0));assert.ok(Math.abs(r.weights.reduce((s,v)=>s+v,0)-1)<1e-12);
  assert.ok(r.value<=minimum+1e-15);assert.ok(r.value>=minimum-w/2-1e-15);
  assert.ok(Math.abs(regularizedMinimum(distances.toReversed(),w).value-r.value)<1e-15);
  if(distances.length===1||distances[1]-minimum>w)assert.equal(r.value,minimum);
  distances.forEach((d,i)=>{const h=1e-9,P=distances.slice(),M=distances.slice();P[i]+=h;M[i]-=h;const fd=(regularizedMinimum(P,w).value-regularizedMinimum(M,w).value)/(2*h);assert.ok(Math.abs(fd-r.weights[i])<1e-6);});
 }
});
