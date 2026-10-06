/** Independent full-nodal mixed replay using unchanged original Node material.
 * JSON stdin. No solver; pressure and candidate supplied by research Python.
 */
import fs from 'node:fs';
import {muscleMaterial,determinant,inverseTranspose} from '../web/anatomical-material.mjs';
import {materialTensor} from '../web/anatomical-modal.mjs';
import {quadraticShape,prepareQuadraticElement} from '../web/anatomical-element.mjs';
import {compressionQuadrature} from './anatomical-compression-quadrature.mjs';
import {triangleRecords,transverseCrossings} from '../web/anatomical-intersections.mjs';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
if(input.materialSamples){
 const output=input.materialSamples.map(s=>{const r=muscleMaterial(s.F,[1,0,0],input.activation,input.material),G=inverseTranspose(s.F),log=Math.log(r.J),C=Array.from(materialTensor(s.F,[1,0,0],input.activation,input.material));
 for(let i=0;i<9;i++)for(let j=0;j<9;j++){const a=i%3,b=j%3,r=Math.floor(i/3),t=Math.floor(j/3);C[9*i+j]+=-input.material.bulk*G[i]*G[j]+(input.material.bulk*log-s.p)*G[3*r+b]*G[3*t+a];}
 return {P:r.P.map((v,i)=>v+(s.p-input.material.bulk*log)*G[i]),C};});
 process.stdout.write(JSON.stringify(output));
}else{
 const {mesh,positionsM:x,pressurePa:p,material,activation,depth}=input,rule=compressionQuadrature(depth),g=mesh.X.map(()=>[0,0,0]),b=Array(mesh.nv).fill(0),weak=Array(mesh.nv).fill(0);
 let pointSquare=0,volume=0,minJ=Infinity,maxJ=-Infinity,energy=0;
 // Original element reference prep uses four points, then independently maps dense shapes.
 for(const ids of mesh.tets){
  const ref=ids.map(i=>mesh.X[i]),current=ids.map(i=>x[i]);
  for(const point of rule){
   const shape=quadraticShape(point.L),jac=Array.from({length:9},(_,k)=>ref.reduce((s,X,i)=>s+X[Math.floor(k/3)]*shape.gradient[i][k%3],0)),det=determinant(jac),inv=inverseTranspose(jac,det);
   if(!(det>1e-15))throw Error('Reference determinant');
   const grad=shape.gradient.map(v=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+inv[3*i+j]*v[j],0))),w=point.weight*det/6;
   const F=Array.from({length:9},(_,k)=>current.reduce((s,X,i)=>s+X[Math.floor(k/3)]*grad[i][k%3],0)),r=muscleMaterial(F,[1,0,0],activation,material),G=inverseTranspose(F),log=Math.log(r.J),pq=point.L.reduce((s,v,i)=>s+v*p[ids[i]],0),P=r.P.map((v,i)=>v+(pq-material.bulk*log)*G[i]);
   for(let n=0;n<10;n++)for(let d=0;d<3;d++)g[ids[n]][d]+=w*[0,1,2].reduce((s,k)=>s+P[3*d+k]*grad[n][k],0);
   for(let i=0;i<4;i++){b[ids[i]]+=w*point.L[i]*log;weak[ids[i]]+=w*point.L[i]*(log-pq/material.bulk);}
   energy+=w*(r.energy.matrix+r.energy.passiveFiber+r.energy.activePotential+pq*log-pq*pq/(2*material.bulk));
   minJ=Math.min(minJ,r.J);maxJ=Math.max(maxJ,r.J);volume+=w;pointSquare+=w*(log-pq/material.bulk)**2;
  }
  for(const L of [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]){
   const shape=quadraticShape(L),jac=Array.from({length:9},(_,k)=>ref.reduce((s,X,i)=>s+X[Math.floor(k/3)]*shape.gradient[i][k%3],0)),inv=inverseTranspose(jac),grad=shape.gradient.map(v=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+inv[3*i+j]*v[j],0))),F=Array.from({length:9},(_,k)=>current.reduce((s,X,i)=>s+X[Math.floor(k/3)]*grad[i][k%3],0)),J=determinant(F);minJ=Math.min(minJ,J);maxJ=Math.max(maxJ,J);
  }
 }
 const flat=g.flat(),freeNorm=Math.hypot(...mesh.free.map(i=>flat[i])),cap=-g.reduce((s,v,i)=>s+(mesh.X[i][0]===0?v[0]:0),0),virtual=-g.reduce((s,v,i)=>s+(1-mesh.X[i][0]/.14)*v[0],0),T=triangleRecords(x,mesh.surface),crossings=transverseCrossings(T,T);
 process.stdout.write(JSON.stringify({gradientN:flat,b,weak,freeNodalResidualN:freeNorm,capForceN:cap,virtualForceN:virtual,energyJ:energy,pointwisePressureRMS:Math.sqrt(pointSquare/volume),Jmin:minJ,Jmax:maxJ,surface:crossings}));
}
