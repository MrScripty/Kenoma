/** Independent synthetic arithmetic/control checks; no arm/material import. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {minimizeNewton} from '../web/anatomical-newton.mjs';
const BASE='ee35cc58dc98f3e45c0687287cfc7e8c06496950';
const sources=[execFileSync('git',['show',BASE+':education/web/anatomical-arm.mjs'],{encoding:'utf8'}),fs.readFileSync(new URL('../web/anatomical-arm.mjs',import.meta.url),'utf8')];
const expressions=sources.map(text=>{const marker='hessianVector:',start=text.indexOf(marker)+marker.length,end=text.indexOf(',fullCoordinates:x',start);assert.ok(start>=marker.length&&end>start);return text.slice(start,end);});
const kernels=(H,n,free)=>expressions.map(expression=>new Function('r','n','free','return ('+expression+');')({hessian:H},n,free));
const bytes=x=>Buffer.from(x.buffer,x.byteOffset,x.byteLength);
const bitwise=(x,y)=>assert.equal(bytes(x).compare(bytes(y)),0);

test('finite subnormals, rounding ties, cancellation and overflow retain exact product bits',()=>{
 const values=[0,-0,Number.MIN_VALUE,-Number.MIN_VALUE,2**-1022,-(2**-1022),2**-500,2**500,1,-1,1+Number.EPSILON,2**53,-(2**53),Number.MAX_VALUE,-Number.MAX_VALUE];
 const n=7,H=Float64Array.from({length:n*n},(_,i)=>values[(i*11+3)%values.length]);
 for(const free of [[0,1,2,3,4,5,6],[0,1,2,3,4,5],[6,2,4,0]]){
  const [old,next]=kernels(H,n,free);
  for(let shift=0;shift<values.length;shift++){
   const v=Float64Array.from(free,(_,i)=>values[(i*7+shift)%values.length]),input=v.slice(),matrix=H.slice();
   bitwise(old(v),next(v));bitwise(v,input);bitwise(H,matrix);
  }
 }
});

test('actual-size dense full and last-joint-held domains read fresh matrix/vector values without aliasing',()=>{
 const n=460,H=Float64Array.from({length:n*n},(_,i)=>((i*17)%29-14)*.03125);
 for(const free of [Array.from({length:n},(_,i)=>i),Array.from({length:n-1},(_,i)=>i)]){
  const [old,next]=kernels(H,n,free),v=Float64Array.from(free,(_,i)=>(i%11-5)*.0625);
  bitwise(old(v),next(v));const retained=next(v),saved=retained.slice();
  H[0]=3.25;v[0]=.75;bitwise(old(v),next(v));bitwise(retained,saved);
  const later=next(v);assert.notEqual(later.buffer,retained.buffer);assert.notEqual(later.buffer,H.buffer);assert.notEqual(later.buffer,v.buffer);
 }
});

function solve(which,mode){
 const n=3,H=Float64Array.of(3,.125,-.0625,.125,4,.03125,-.0625,.03125,5),free=[0,1,2],apply=kernels(H,n,free)[which],events=[];
 let calls=0;
 const objective=x=>{
  calls++;
  if(calls>1&&mode==='range-refusal')throw new RangeError('synthetic rejected trial');
  if(calls>1&&mode==='unknown-exception')throw new TypeError('synthetic terminal exception');
  const hx=apply(x),gradient=hx.map((v,i)=>v-[.4,-.3,.2][i]);
  return {energy:x.reduce((s,v,i)=>s+.5*v*hx[i]-[.4,-.3,.2][i]*v,0),gradient,diagonal:Float64Array.of(3,4,5),hessianVector:apply};
 };
 const r=minimizeNewton(objective,Float64Array.of(.8,-.7,.6),{
  tolerance:1e-4,maxIterations:mode==='zero-limit'?0:mode==='nonlinear-limit'?1:8,
  cgMaxIterations:mode==='linear-limit'?0:30,
  initialRegularization:mode==='nonlinear-limit'?10:0,minimumRegularization:0,
  adaptRegularizationToStep:true,onIteration:e=>events.push(e)
 });
 return {x:r.x,energy:r.energy,gradient:r.gradient,converged:r.converged,reason:r.reason,acceptedIterations:r.acceptedIterations,evaluations:r.evaluations,hessianProducts:r.hessianProducts,trace:r.trace,events,calls};
}

test('ordinary nonlinear/linear limits and all rejected RangeError trials retain explicit refusals and counts',()=>{
 const expected={'zero-limit':'nonlinear iteration limit','nonlinear-limit':'nonlinear iteration limit','linear-limit':'no positive-curvature descent direction','range-refusal':'no admissible decreasing step'};
 for(const [mode,reason] of Object.entries(expected)){
  const before=solve(0,mode),after=solve(1,mode);assert.deepEqual(after,before);assert.equal(after.converged,false);assert.equal(after.reason,reason);
  if(mode==='range-refusal'){assert.equal(after.evaluations,41);assert.equal(after.acceptedIterations,0);assert.equal(after.events.length,0);assert.ok(after.hessianProducts>0);}
  if(mode==='nonlinear-limit')assert.equal(after.acceptedIterations,1);
  if(mode==='zero-limit'||mode==='linear-limit'){assert.equal(after.evaluations,1);assert.equal(after.acceptedIterations,0);}
 }
});

test('unknown synthetic trial exceptions propagate unchanged in both kernels',()=>{
 for(const which of [0,1])assert.throws(()=>solve(which,'unknown-exception'),{name:'TypeError',message:'synthetic terminal exception'});
});
