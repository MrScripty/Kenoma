import test from 'node:test';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {materialCut,forceLength} from './model.mjs';
// Default is the repository operator. Private review may provide its pinned
// materialized path explicitly; this test never downloads or edits it.
const source=process.env.KENOMA_MATERIAL_MODULE?pathToFileURL(process.env.KENOMA_MATERIAL_MODULE):new URL('../../web/anatomical-material.mjs',import.meta.url);
const {muscleMaterial,MUSCLE_FIXTURE,activeCurve}=await import(source.href);
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-9*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
test('the lesson nominal coefficient matches the existing full-stretch active operator',()=>{
 for(const F of [[.8,0,0,0,1.1,0,0,0,1.2],[1,0,0,.2,1,0,.1,.3,1],[0,-1,0,1,0,0,0,0,1],[1.2,.1,0,.1,1,0,0,0,.9]])for(const a of [0,.3,1]){
  const r=muscleMaterial(F,[1,0,0],a),P=a*MUSCLE_FIXTURE.sigma0*forceLength(r.lambda);
  const scalar=materialCut({referenceAreaM2:1e-4,lambda:r.lambda,J:r.J,nominalStressPa:P});
  const activeCauchy=Array.from({length:9},(_,i)=>[0,1,2].reduce((sum,k)=>sum+r.Pactive[3*Math.floor(i/3)+k]*F[3*(i%3)+k],0)/r.J);
  const sigma=r.direction.reduce((sum,n,i)=>sum+n*r.direction.reduce((v,m,j)=>v+activeCauchy[3*i+j]*m,0),0);
  close(sigma,scalar.cauchyFiberStressPa);
  close(Math.hypot(r.Pactive[0],r.Pactive[3],r.Pactive[6])*1e-4,scalar.axialForceN);
 }
});
test('the optional length law equals the repository curve on supported sample points',()=>{
 for(const lambda of [.4,.5,.6,.8,1,1.2,1.4,1.5,1.6])close(forceLength(lambda),activeCurve(lambda).value);
});
