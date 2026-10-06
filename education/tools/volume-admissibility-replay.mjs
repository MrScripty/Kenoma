/** Independent original-material volume map and full Rayleigh decomposition.
 * No solve, projection, changed law, changed K or removed prestress.
 */
import fs from 'node:fs';
import {muscleMaterial,determinant,inverseTranspose,activeCurve} from '../web/anatomical-material.mjs';
import {materialTensor} from '../web/anatomical-modal.mjs';
import {quadraticShape} from '../web/anatomical-element.mjs';
import {compressionQuadrature} from './anatomical-compression-quadrature.mjs';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const {mesh,positionsM:x,direction:v,material,activation,depth}=input;
const tensor=(nodes,grad)=>Array.from({length:9},(_,k)=>nodes.reduce((s,X,n)=>s+X[Math.floor(k/3)]*grad[n][k%3],0));
function refPoint(ref,L){
 const shape=quadraticShape(L),jac=tensor(ref,shape.gradient),det=determinant(jac);
 if(!(det>1e-15))throw Error('Original reference determinant guard');
 const inv=inverseTranspose(jac,det),grad=shape.gradient.map(a=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+inv[3*i+j]*a[j],0)));
 return {grad,det};
}
let volume=0,square=0,maximum=0,cornerMaximum=0,total=0,active=0,passive=0,prestress=0,volumeTerm=0;
const baseEnergy={matrix:0,volume:0,passiveFiber:0,activePotential:0},samples=[];
for(const ids of mesh.tets){
 const ref=ids.map(i=>mesh.X[i]),current=ids.map(i=>x[i]),dv=ids.map(i=>v[i]);
 for(const point of compressionQuadrature(depth)){
  const {grad,det}=refPoint(ref,point.L),w=point.weight*det/6,F=tensor(current,grad),dF=tensor(dv,grad);
  const r=muscleMaterial(F,[1,0,0],activation,material),G=inverseTranspose(F),dlog=G.reduce((s,z,i)=>s+z*dF[i],0);
  const C=materialTensor(F,[1,0,0],activation,material),lambda=r.lambda,n=[0,1,2].map(i=>F[3*i]/lambda),df=[dF[0],dF[3],dF[6]];
  const longitudinal=n.reduce((s,z,i)=>s+z*df[i],0),transverse=df.reduce((s,z)=>s+z*z,0)-longitudinal**2;
  const u=(lambda-1)/material.activeWidth,curve=activeCurve(lambda,material.activeWidth),prime=Math.abs(u)<1?-4*u*(1-u*u)/material.activeWidth:0;
  const passiveK=material.kf/material.b*Math.expm1(material.b*Math.max(lambda-1,0));
  const passivePrime=lambda>1?material.kf*Math.exp(material.b*(lambda-1)):0;
  const invd=Array.from({length:9},(_,k)=>[0,1,2].reduce((s,i)=>s+G[3*i+Math.floor(k/3)]*dF[3*i+k%3],0));
  const trace=invd.reduce((s,z,k)=>s+z*invd[3*(k%3)+Math.floor(k/3)],0);
  total+=w*dF.reduce((s,z,i)=>s+z*dF.reduce((t,a,j)=>t+C[9*i+j]*a,0),0);
  active+=w*activation*material.sigma0*(prime*longitudinal**2+curve.value/lambda*transverse);
  passive+=w*(passivePrime*longitudinal**2+passiveK/lambda*transverse);
  prestress-=w*material.bulk*Math.log(r.J)*trace;volumeTerm+=w*material.bulk*dlog*dlog;
  volume+=w;square+=w*dlog*dlog;maximum=Math.max(maximum,Math.abs(dlog));samples.push(dlog);
  for(const key of Object.keys(baseEnergy))baseEnergy[key]+=w*r.energy[key];
 }
 for(const L of [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]){
  const {grad}=refPoint(ref,L),F=tensor(current,grad),G=inverseTranspose(F),dF=tensor(dv,grad);
  cornerMaximum=Math.max(cornerMaximum,Math.abs(G.reduce((s,z,i)=>s+z*dF[i],0)));
 }
}
process.stdout.write(JSON.stringify({directionalLogJRMSPerM:Math.sqrt(square/volume),maximumAbsDirectionalLogJAtQuadraturePerM:maximum,
 maximumAbsDirectionalLogJAtCornersPerM:cornerMaximum,directionalLogJSamplesPerM:samples,
 euclideanNodalNorm:Math.hypot(...v.flat()),maximumHeldCapVariationM:Math.max(...mesh.cap.flatMap(i=>v[i].map(Math.abs))),
 baseConstituentEnergiesJ:baseEnergy,rayleigh:{matrixNPerM:total-active-passive-prestress-volumeTerm,passiveFiberNPerM:passive,
 activeNPerM:active,pressurePrestressNPerM:prestress,volumeConstraintNPerM:volumeTerm,totalNPerM:total},
 scope:'Direct original physical material tensor and pointwise linearized volume map; tangent-space diagnostic only'}));
