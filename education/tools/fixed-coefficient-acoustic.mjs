/** Read-only rank-one probes of the unchanged material tangent. Pa throughout. */
import {materialTensor} from '../web/anatomical-modal.mjs';
import {muscleMaterial,inverseTranspose} from '../web/anatomical-material.mjs';
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),norm=a=>Math.hypot(...a),unit=a=>a.map(v=>v/norm(a));
export function acousticMatrix(C,m){return Array.from({length:9},(_,k)=>{const i=Math.floor(k/3),j=k%3;let s=0;for(let a=0;a<3;a++)for(let b=0;b<3;b++)s+=C[(3*i+a)*9+3*j+b]*m[a]*m[b];return s;});}
export function minimumEigenpair(Q){
 const A=Q.map((v,k)=>(v+Q[(k%3)*3+Math.floor(k/3)])/2),V=[1,0,0,0,1,0,0,0,1];
 for(let sweep=0;sweep<30;sweep++){
  let p=0,q=1;for(const [i,j] of [[0,2],[1,2]])if(Math.abs(A[3*i+j])>Math.abs(A[3*p+q])){p=i;q=j;}
  const off=A[3*p+q];if(Math.abs(off)<=1e-14*Math.max(1,...A.map(Math.abs)))break;
  const angle=.5*Math.atan2(2*off,A[3*q+q]-A[3*p+p]),c=Math.cos(angle),s=Math.sin(angle),app=A[3*p+p],aqq=A[3*q+q];
  for(let k=0;k<3;k++)if(k!==p&&k!==q){const ap=A[3*k+p],aq=A[3*k+q];A[3*k+p]=A[3*p+k]=c*ap-s*aq;A[3*k+q]=A[3*q+k]=s*ap+c*aq;}
  A[3*p+p]=c*c*app-2*s*c*off+s*s*aqq;A[3*q+q]=s*s*app+2*s*c*off+c*c*aqq;A[3*p+q]=A[3*q+p]=0;
  for(let k=0;k<3;k++){const vp=V[3*k+p],vq=V[3*k+q];V[3*k+p]=c*vp-s*vq;V[3*k+q]=s*vp+c*vq;}
 }
 const i=[0,1,2].reduce((a,b)=>A[3*a+a]<A[3*b+b]?a:b),u=unit([V[i],V[3+i],V[6+i]]),Qu=[0,1,2].map(k=>dot(Q.slice(3*k,3*k+3),u)),value=dot(u,Qu),error=norm(Qu.map((v,k)=>v-value*u[k]))/Math.max(1,norm(Qu));
 if(error>1e-8)throw Error('Acoustic eigenpair residual '+error);return {valuePa:value,polarization:u,relativeEigenResidual:error};
}
export function referenceDirections(b){const basis=[b.axis,b.u,b.v],all=basis.map(v=>v.slice());for(const [i,j] of [[0,1],[0,2],[1,2]])for(const sign of [-1,1])all.push(basis[i].map((v,d)=>v+sign*basis[j][d]));for(const s of [-1,1])for(const t of [-1,1])all.push(basis[0].map((v,d)=>v+s*basis[1][d]+t*basis[2][d]));return all.map(unit);}
export function witnessChecks(F,fibre,a,p,m,u,Q){
 const r=muscleMaterial(F,fibre,a,p),G=inverseTranspose(F,r.J),v=[0,1,2].map(i=>dot(G.slice(3*i,3*i+3),m)),n=r.direction,lambda=r.lambda,t=(lambda-1)/p.activeWidth,fL=Math.abs(t)<1?(1-t*t)**2:0,prime=Math.abs(t)<1?-4*t*(1-t*t)/p.activeWidth:0,axial=dot(fibre,m)**2;
 const fiber=(k,kp)=>Array.from({length:9},(_,i)=>axial*(kp*n[Math.floor(i/3)]*n[i%3]+k/lambda*((Math.floor(i/3)===i%3?1:0)-n[Math.floor(i/3)]*n[i%3])));
 const volume=v.flatMap(x=>v.map(y=>p.bulk*(1-Math.log(r.J))*x*y)),passive=fiber(p.kf/p.b*Math.expm1(p.b*Math.max(lambda-1,0)),lambda>1?p.kf*Math.exp(p.b*(lambda-1)):0),active=fiber(a*p.sigma0*fL,a*p.sigma0*prime),matrix=Q.map((x,i)=>x-volume[i]-passive[i]-active[i]);
 const ray=M=>dot(u,[0,1,2].map(i=>dot(M.slice(3*i,3*i+3),u))),parts=Object.fromEntries(Object.entries({matrix,volume,passiveFiber:passive,active}).map(([k,M])=>[k,ray(M)])),Qu=[0,1,2].map(i=>dot(Q.slice(3*i,3*i+3),u)),probes=[];
 for(const h of [1e-6,5e-7]){const delta=F.map((_,i)=>u[Math.floor(i/3)]*m[i%3]),plus=muscleMaterial(F.map((v,i)=>v+h*delta[i]),fibre,a,p).P,minus=muscleMaterial(F.map((v,i)=>v-h*delta[i]),fibre,a,p).P,fd=[0,1,2].map(i=>dot(plus.slice(3*i,3*i+3).map((v,j)=>(v-minus[3*i+j])/(2*h)),m)),relativeError=norm(fd.map((v,i)=>v-Qu[i]))/Math.max(1,norm(Qu));if(relativeError>1e-4)throw Error('Stress rank-one derivative failure '+relativeError);probes.push({step:h,relativeVectorError:relativeError,rayleighPa:dot(u,fd)});}
 return {J:r.J,stretch:lambda,rayleighPartsPa:parts,rayleighSumPa:Object.values(parts).reduce((s,v)=>s+v,0),stressFiniteDifferences:probes};
}
