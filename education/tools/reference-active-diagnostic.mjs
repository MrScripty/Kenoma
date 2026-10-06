/** Research active potential only. Never loaded by production mechanics.
 * Reference normalization and full/isochoric stretch are explicit ablations.
 * sigma0 stays the peak full-stretch first-Piola coefficient; passive is frozen. */
import {muscleMaterial,determinant,inverseTranspose,activeCurve} from '../web/anatomical-material.mjs';
import {materialTensor} from '../web/anatomical-modal.mjs';
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export function activeReferenceDiagnostic(F,fibre,activation,material,{optimalStretch=1,isochoric=false}={}){
 if(!(optimalStretch>0&&Number.isFinite(optimalStretch))||!Number.isFinite(activation)||activation<0||activation>1)throw new RangeError('Explicit positive optimal/reference fiber stretch and bounded activation required');
 const passive=muscleMaterial(F,fibre,0,material),J=determinant(F),G=inverseTranspose(F,J),lambda=passive.lambda,n=passive.direction,scale=isochoric?J**(-1/3):1,stretch=scale*lambda,ratio=stretch/optimalStretch,curve=activeCurve(ratio,material.activeWidth),t=(ratio-1)/material.activeWidth,prime=Math.abs(t)<1?-4*t*(1-t*t)/material.activeWidth:0,k=activation*material.sigma0*curve.value,kp=activation*material.sigma0*prime/optimalStretch,L=Array.from({length:9},(_,i)=>n[Math.floor(i/3)]*fibre[i%3]),gradient=L.map((v,i)=>scale*(v-(isochoric?lambda*G[i]/3:0))),hessian=Array.from({length:81},(_,ij)=>{
  const i=Math.floor(ij/9),j=ij%9,r=Math.floor(i/3),a=i%3,s=Math.floor(j/3),b=j%3,base=((r===s?1:0)-n[r]*n[s])*fibre[a]*fibre[b]/lambda;
  return scale*(base+(isochoric?-(L[i]*G[j]+G[i]*L[j])/3+lambda*G[i]*G[j]/9+lambda*G[3*r+b]*G[3*s+a]/3:0));
 }),Pactive=gradient.map(v=>k*v),P=passive.P.map((v,i)=>v+Pactive[i]),Cpassive=materialTensor(F,fibre,0,material),C=Array.from(Cpassive,(v,ij)=>{const i=Math.floor(ij/9),j=ij%9;return v+kp*gradient[i]*gradient[j]+k*hessian[ij];}),activeCauchy=Array.from({length:9},(_,i)=>dot(Pactive.slice(3*Math.floor(i/3),3*Math.floor(i/3)+3),F.slice(3*(i%3),3*(i%3)+3))/J),energy=passive.passiveStored+activation*material.sigma0*optimalStretch*curve.primitive;
 return {P,C,energy,Pactive,activeCauchy,J,lambda,activeStretch:stretch,normalizedActiveStretch:ratio,forceLength:curve.value,normalizedForceLengthSlope:prime,firstPiolaActiveScalarPa:k,activeMeanCauchyPa:(activeCauchy[0]+activeCauchy[4]+activeCauchy[8])/3,optimalStretch,isochoric};
}
export function incompressiblePolarizationBasis(F,m){
 const G=inverseTranspose(F),g=[0,1,2].map(i=>dot(G.slice(3*i,3*i+3),m)),N=Math.hypot(...g),normal=g.map(v=>v/N),axis=normal.map(Math.abs).reduce((a,_,i)=>Math.abs(normal[i])<Math.abs(normal[a])?i:a,0),seed=[0,0,0];seed[axis]=1;
 const u=seed.map((v,i)=>v-normal[axis]*normal[i]),U=Math.hypot(...u);for(let i=0;i<3;i++)u[i]/=U;const v=[normal[1]*u[2]-normal[2]*u[1],normal[2]*u[0]-normal[0]*u[2],normal[0]*u[1]-normal[1]*u[0]];
 return {normal,g,u,v};
}
export function constrainedMinimum(Q,F,m){
 const {g,u,v}=incompressiblePolarizationBasis(F,m),ray=(a,b)=>dot(a,[0,1,2].map(i=>dot(Q.slice(3*i,3*i+3),b))),A=ray(u,u),D=ray(v,v),B=(ray(u,v)+ray(v,u))/2,angle=.5*Math.atan2(-2*B,D-A),polarization=u.map((x,i)=>Math.cos(angle)*x+Math.sin(angle)*v[i]),value=ray(polarization,polarization),constraint=dot(g,polarization),expected=(A+D-Math.hypot(A-D,2*B))/2;
 if(Math.abs(value-expected)>1e-7*Math.max(1,Math.abs(expected))||Math.abs(constraint)>1e-12)throw Error('Constrained eigenpair failure');return {valuePa:value,polarization,determinantFirstDerivativeConstraint:constraint};
}
