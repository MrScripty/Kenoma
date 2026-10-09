/** Synthetic dense arithmetic only: no arm/material/configuration import. */
import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import {execFileSync} from 'node:child_process';
import {minimizeNewton} from '../web/anatomical-newton.mjs';
import {denseReferencePreconditioner} from '../web/anatomical-preconditioner.mjs';
const BASE='ee35cc58dc98f3e45c0687287cfc7e8c06496950';
const before=execFileSync('git',['show',BASE+':education/web/anatomical-arm.mjs'],{encoding:'utf8'});
const after=fs.readFileSync(new URL('../web/anatomical-arm.mjs',import.meta.url),'utf8');
const extract=text=>{const start=text.indexOf('hessianVector:')+'hessianVector:'.length,end=text.indexOf(',fullCoordinates:x',start);assert.ok(start>12&&end>start);return text.slice(start,end);};
const oldExpression=extract(before),newExpression=extract(after);
export const kernels=(matrix,n,free)=>[oldExpression,newExpression].map(expression=>new Function('r','n','free','return ('+expression+');')({hessian:matrix},n,free));
const bitwise=(a,b)=>assert.equal(Buffer.from(a.buffer,a.byteOffset,a.byteLength).compare(Buffer.from(b.buffer,b.byteOffset,b.byteLength)),0);
test('only the dense product expression changes; all laws/options/gates/solver bytes remain',()=>{
 assert.equal(after.replace(newExpression,oldExpression),before);
 for(const name of ['anatomical-newton','anatomical-preconditioner'])assert.equal(fs.readFileSync(new URL('../web/'+name+'.mjs',import.meta.url),'utf8'),execFileSync('git',['show',BASE+':education/web/'+name+'.mjs'],{encoding:'utf8'}));
});
test('products are bit-identical for synthetic full/held/permuted domains and retain input bytes',()=>{
 for(const n of [0,1,3,9,63,460]){
  const matrix=Float64Array.from({length:n*n},(_,i)=>Math.sin(i*.31)*(i%7-3));
  const domains=[Array.from({length:n},(_,i)=>i),Array.from({length:n},(_,i)=>i).filter(i=>i!==Math.floor(n/2)),Array.from({length:n},(_,i)=>n-1-i)];
  for(const free of domains){const [old,next]=kernels(matrix,n,free);for(const scale of [0,1,1e-100,1e100]){const v=Float64Array.from(free,(_,i)=>Math.cos(i*.17)*scale),saved=v.slice(),H=matrix.slice();bitwise(old(v),next(v));bitwise(v,saved);bitwise(matrix,H);}}
 }
});
test('IEEE cancellation, signed zero, nonfinite propagation and fresh result identity agree',()=>{
 for(const row of [[1e16,1,-1e16],[-0,0,-0],[Infinity,1,-Infinity],[NaN,2,3]]){
  const H=Float64Array.from([...row,...row,...row]),[old,next]=kernels(H,3,[0,1,2]),v=Float64Array.of(1,1,1);const a=old(v),b=next(v);for(let i=0;i<3;i++)assert.ok(Object.is(a[i],b[i]));assert.notEqual(b,next(v));assert.notEqual(b,v);
 }
});
test('synthetic Newton/PCG with regularization/retraction/backtracking has identical decisions and receipts',()=>{
 for(const n of [2,7,16])for(const held of [false,true])for(const stretch of [1,4]){
  const free=Array.from({length:n},(_,i)=>i).filter(i=>!held||i!==n-1),H=Float64Array.from({length:n*n},(_,k)=>{const i=Math.floor(k/n),j=k%n;return i===j?3+i*.1:((i+j)%3-1)*.03;}),f=Float64Array.from(free,(_,i)=>(i%3-1)*.3),start=Float64Array.from(free,(_,i)=>(i%2?-.8:.6));
  const solve=which=>{
   const [old,next]=kernels(H,n,free),apply=which?next:old,objective=x=>{const hx=apply(x),gradient=hx.map((v,i)=>v-f[i]),energy=x.reduce((s,v,i)=>s+.5*v*hx[i]-f[i]*v,0),matrix=free.map(i=>Float64Array.from(free,j=>H[i*n+j]));return {energy,gradient,diagonal:Float64Array.from(free,i=>H[i*n+i]),hessianVector:apply,precondition:denseReferencePreconditioner(matrix)};};
   const events=[],r=minimizeNewton(objective,start,{maxIterations:40,tolerance:1e-10,cgMaxIterations:100,initialRegularization:10,minimumRegularization:.001,adaptRegularizationToStep:true,prepareRetraction:(x,d)=>s=>x.map((v,i)=>v+stretch*s*d[i]),onIteration:e=>events.push(e)});
   return {x:r.x,gradient:r.gradient,energy:r.energy,converged:r.converged,reason:r.reason,acceptedIterations:r.acceptedIterations,evaluations:r.evaluations,hessianProducts:r.hessianProducts,trace:r.trace,events};
  };
  const a=solve(0),b=solve(1);assert.deepEqual(b,a);assert.equal(a.converged,true);if(stretch===4){assert.ok(a.trace.some(row=>row.step<1));assert.ok(a.evaluations>a.acceptedIterations+1);}
 }
});
