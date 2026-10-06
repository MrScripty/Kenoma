/** Independent original-material full-P2 frozen-field assembly, no solver.
 * Pointwise uses original muscleMaterial/solvePotential/materialTensor directly.
 * Mixed adjusts p and retains fixed-pressure prestress plus supplied exact dp.
 */
import fs from 'node:fs';
import {muscleMaterial,determinant,inverseTranspose} from '../web/anatomical-material.mjs';
import {materialTensor} from '../web/anatomical-modal.mjs';
import {quadraticShape} from '../web/anatomical-element.mjs';
import {compressionQuadrature} from './anatomical-compression-quadrature.mjs';
import {triangleRecords,transverseCrossings} from '../web/anatomical-intersections.mjs';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const {mesh,positionsM:x,pressureSpace:space,pressurePa:p,material,activation,depth,direction:v,directionalPressurePa:dp}=input;
const rule=compressionQuadrature(depth),np=space==='continuousP1'?mesh.nv:space==='brokenP1'?4*mesh.tets.length:0;
const g=mesh.X.map(()=>[0,0,0]),hv=v?mesh.X.map(()=>[0,0,0]):null,weak=Array(np).fill(0),b=Array(np).fill(0),deltaWeak=v?Array(np).fill(0):null;
const massLocal=mesh.tets.map(()=>Array(16).fill(0));
let energy=0,volume=0,pointSquare=0,minJ=Infinity,maxJ=-Infinity,meanVolume=0,volumeSquare=0,pressureMin=Infinity,pressureMax=-Infinity,directionalMismatchSquare=0;
const tensor=(nodes,grad)=>Array.from({length:9},(_,k)=>nodes.reduce((s,X,n)=>s+X[Math.floor(k/3)]*grad[n][k%3],0));
function reference(ref,L){
 const shape=quadraticShape(L),jac=tensor(ref,shape.gradient),det=determinant(jac);
 if(!(det>1e-15))throw Error('Original reference determinant guard');
 const inv=inverseTranspose(jac,det),grad=shape.gradient.map(a=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+inv[3*i+j]*a[j],0)));
 return {grad,det};
}
for(const [e,ids] of mesh.tets.entries()){
 const ref=ids.map(i=>mesh.X[i]),current=ids.map(i=>x[i]),dv=v?ids.map(i=>v[i]):null;
 const pressureIds=space==='continuousP1'?ids.slice(0,4):[4*e,4*e+1,4*e+2,4*e+3];
 for(const point of rule){
  const {grad,det}=reference(ref,point.L),w=point.weight*det/6,F=tensor(current,grad);
  const r=muscleMaterial(F,[1,0,0],activation,material),G=inverseTranspose(F),log=Math.log(r.J);
  const pq=space==='pointwise'?material.bulk*log:point.L.reduce((s,l,i)=>s+l*p[pressureIds[i]],0);
  const P=space==='pointwise'?r.P:r.P.map((z,i)=>z+(pq-material.bulk*log)*G[i]);
  energy+=w*(space==='pointwise'?r.solvePotential:r.solvePotential-r.energy.volume+pq*log-pq*pq/(2*material.bulk));
  volume+=w;meanVolume+=w*(r.J-1);volumeSquare+=w*(r.J-1)**2;pointSquare+=w*(log-pq/material.bulk)**2;
  pressureMin=Math.min(pressureMin,pq);pressureMax=Math.max(pressureMax,pq);minJ=Math.min(minJ,r.J);maxJ=Math.max(maxJ,r.J);
  for(let n=0;n<10;n++)for(let d=0;d<3;d++)g[ids[n]][d]+=w*[0,1,2].reduce((s,k)=>s+P[3*d+k]*grad[n][k],0);
  for(let i=0;i<4;i++){
   if(np){b[pressureIds[i]]+=w*point.L[i]*log;weak[pressureIds[i]]+=w*point.L[i]*(log-pq/material.bulk);}
   for(let j=0;j<4;j++)massLocal[e][4*i+j]+=w*point.L[i]*point.L[j];
  }
  if(v){
   const dF=tensor(dv,grad),dlog=G.reduce((s,z,i)=>s+z*dF[i],0);
   const dpq=space==='pointwise'?material.bulk*dlog:point.L.reduce((s,l,i)=>s+l*dp[pressureIds[i]],0);
   const C=materialTensor(F,[1,0,0],activation,material);
   if(space!=='pointwise')for(let i=0;i<9;i++)for(let j=0;j<9;j++){
    const a=i%3,bb=j%3,rr=Math.floor(i/3),ss=Math.floor(j/3);
    C[9*i+j]+=-material.bulk*G[i]*G[j]+(material.bulk*log-pq)*G[3*rr+bb]*G[3*ss+a];
   }
   const dP=Array.from({length:9},(_,i)=>dF.reduce((s,z,j)=>s+C[9*i+j]*z,0)+(space==='pointwise'?0:G[i]*dpq));
   for(let n=0;n<10;n++)for(let d=0;d<3;d++)hv[ids[n]][d]+=w*[0,1,2].reduce((s,k)=>s+dP[3*d+k]*grad[n][k],0);
   directionalMismatchSquare+=w*(dlog-dpq/material.bulk)**2;
   if(np)for(let i=0;i<4;i++)deltaWeak[pressureIds[i]]+=w*point.L[i]*(dlog-dpq/material.bulk);
  }
 }
 for(const L of [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]){
  const {grad}=reference(ref,L),J=determinant(tensor(current,grad));minJ=Math.min(minJ,J);maxJ=Math.max(maxJ,J);
 }
}
const flat=g.flat(),cap=-g.reduce((s,a,i)=>s+(mesh.X[i][0]===0?a[0]:0),0),virtual=-g.reduce((s,a,i)=>s+(1-mesh.X[i][0]/.14)*a[0],0);
const surface=input.surface===false?null:transverseCrossings(triangleRecords(x,mesh.surface),triangleRecords(x,mesh.surface));
process.stdout.write(JSON.stringify({gradientN:flat,tangentActionNPerM:hv?hv.flat():null,energyJ:energy,weak,b,massLocal,deltaWeak,
 freeNodalResidualN:Math.hypot(...mesh.free.map(i=>flat[i])),capForceN:cap,virtualForceN:virtual,
 pointwisePressureRMS:Math.sqrt(pointSquare/volume),referenceVolumeM3:volume,meanVolumeChange:meanVolume/volume,
 localVolumeRMS:Math.sqrt(volumeSquare/volume),pressureMinimumSamplePa:pressureMin,pressureMaximumSamplePa:pressureMax,
 directionalProjectionErrorRMSPerM:v?Math.sqrt(directionalMismatchSquare/volume):null,Jmin:minJ,Jmax:maxJ,surface}));
