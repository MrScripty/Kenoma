/** Explicit Galerkin restriction of the existing atlas P2 displacement field.
 * Seven ring planes each have three translations and six transverse affine
 * coefficients. This is 63 DOF per head, not a full nodal FEM solve. Reference
 * quadrature/material/potential are unchanged. No float/formal equivalence claim.
 */
import {prepareQuadraticElement} from './anatomical-element.mjs';
import {muscleMaterial,determinant,inverseTranspose,activeCurve,MUSCLE_FIXTURE} from './anatomical-material.mjs';
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),sub=(a,b)=>a.map((v,i)=>v-b[i]);
export function materialTensor(F,fibre,activation,p=MUSCLE_FIXTURE){
 const J=determinant(F);if(!(J>1e-6))throw new RangeError('Material tensor determinant');const G=inverseTranspose(F,J),I1=dot(F,F),iso=J**(-2/3),log=Math.log(J),f=Array.from({length:3},(_,r)=>dot(F.slice(3*r,3*r+3),fibre)),lambda=Math.hypot(...f),n=f.map(v=>v/lambda),e=Math.max(lambda-1,0),curve=activeCurve(lambda,p.activeWidth),u=(lambda-1)/p.activeWidth,prime=Math.abs(u)<1?-4*u*(1-u*u)/p.activeWidth:0,k=p.kf/p.b*Math.expm1(p.b*e)+activation*p.sigma0*curve.value,kPrime=(lambda>1?p.kf*Math.exp(p.b*e):0)+activation*p.sigma0*prime;
 return Float64Array.from({length:81},(_,index)=>{const i=Math.floor(index/9),j=index%9,r=Math.floor(i/3),a=i%3,s=Math.floor(j/3),b=j%3;return p.mu*iso*((r===s&&a===b?1:0)-2/3*F[j]*G[i]+I1/3*G[3*r+b]*G[3*s+a]-2/3*G[j]*(F[i]-I1/3*G[i]))+p.bulk*(G[j]*G[i]-log*G[3*r+b]*G[3*s+a])+(kPrime*n[r]*n[s]+k/lambda*((r===s?1:0)-n[r]*n[s]))*fibre[a]*fibre[b];});
}
export function prepareModalBody(m,{quadrature='subdivided32'}={}){
 const rings=m.segmentation.rings,sectors=m.segmentation.sectors;if(rings!==7||sectors!==16)throw new RangeError('Explicit seven-ring mode definition');
 const [start,end]=m.belly_interval_m,b=m.basis,length=end-start,radius=Math.sqrt(m.reference_volume_m3/(Math.PI*length)),nodeModes=m.nodes_m.map(X=>{
  const z=dot(sub(X,b.origin),b.axis),t=Math.max(0,Math.min(rings-1,(z-start)/length*(rings-1))),r=Math.min(rings-2,Math.floor(t)),fraction=t-r,center=m.centerline_m[r].map((v,d)=>v+(m.centerline_m[r+1][d]-v)*fraction),rel=sub(X,center),uv=[1,dot(rel,b.u)/radius,dot(rel,b.v)/radius],rows=[];for(const [ring,h] of [[r,1-fraction],[r+1,fraction]])for(let k=0;k<3;k++)if(Math.abs(h*uv[k])>1e-14)rows.push({base:ring*9+k*3,value:h*uv[k]});return rows;
 });
 const points=[];for(const [index,tet] of m.elements_ten_node.entries()){const element=prepareQuadraticElement(tet.map(i=>m.nodes_m[i]),{quadrature,fibre:m.reference_fibres[index]});for(const p of element.points){const groups=new Map();for(let i=0;i<10;i++)for(const mode of nodeModes[tet[i]]){if(!groups.has(mode.base))groups.set(mode.base,[0,0,0]);const v=groups.get(mode.base);for(let d=0;d<3;d++)v[d]+=mode.value*p.gradient[i][d];}const F=Float64Array.from({length:9},(_,k)=>tet.reduce((s,j,i)=>s+m.nodes_m[j][Math.floor(k/3)]*p.gradient[i][k%3],0));points.push({element:index,weightM3:p.referenceWeightM3,fibre:p.fibre,F0:F,groups:[...groups].filter(([,v])=>Math.hypot(...v)>1e-11).map(([base,gradient])=>({base,gradient}))});}}
 return {source:m,ndof:rings*9,radiusM:radius,quadrature,nodeModes,points};
}
export function modalPositions(body,x){return body.source.nodes_m.map((X,i)=>X.map((v,d)=>v+body.nodeModes[i].reduce((s,m)=>s+m.value*x[m.base+d],0)));}
export function modalSample(body,indices,weights,x){const groups=new Map(),X=[0,0,0];indices.forEach((node,i)=>{for(let d=0;d<3;d++)X[d]+=weights[i]*body.source.nodes_m[node][d];for(const mode of body.nodeModes[node])groups.set(mode.base,(groups.get(mode.base)||0)+weights[i]*mode.value);});const modes=[...groups].filter(([,value])=>Math.abs(value)>1e-13).map(([base,value])=>({base,value}));return {position:X.map((v,d)=>v+modes.reduce((s,m)=>s+m.value*x[m.base+d],0)),modes};}
export function evaluateModalBody(body,x,activation,{material=MUSCLE_FIXTURE,hessian=true}={}){
 if(x.length!==body.ndof||!x.every(Number.isFinite))throw new RangeError('Modal coordinates');const n=body.ndof,gradient=new Float64Array(n),H=hessian?new Float64Array(n*n):null,energies={matrix:0,volume:0,passiveFiber:0,activePotential:0};let minJ=Infinity,volume=0,lambdaWeighted=0;
 for(const p of body.points){const F=Float64Array.from(p.F0);for(const mode of p.groups)for(let d=0;d<3;d++)for(let k=0;k<3;k++)F[3*d+k]+=x[mode.base+d]*mode.gradient[k];const result=muscleMaterial(Array.from(F),p.fibre,activation,material),w=p.weightM3;for(const key of Object.keys(energies))energies[key]+=w*result.energy[key];minJ=Math.min(minJ,result.J);volume+=w*result.J;lambdaWeighted+=w*result.lambda;
  for(const a of p.groups)for(let d=0;d<3;d++)for(let k=0;k<3;k++)gradient[a.base+d]+=w*result.P[3*d+k]*a.gradient[k];
  if(H){const C=materialTensor(F,p.fibre,activation,material);for(const a of p.groups)for(const b of p.groups)for(let r=0;r<3;r++)for(let s=0;s<3;s++){let value=0;for(let i=0;i<3;i++)for(let j=0;j<3;j++)value+=a.gradient[i]*C[(3*r+i)*9+3*s+j]*b.gradient[j];H[(a.base+r)*n+b.base+s]+=w*value;}}
 }
 return {energy:Object.values(energies).reduce((a,b)=>a+b,0),energies,passiveStoredJ:energies.matrix+energies.volume+energies.passiveFiber,gradient,hessian:H,minJ,currentVolumeM3:volume,meanFibreStretch:lambdaWeighted/body.source.reference_volume_m3};
}
