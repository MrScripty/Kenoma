/** Same existing P2 energy and material tangent, projected onto45/46 columns.
 * No fitting, material regularization, coupled load or time evolution. */
import {muscleMaterial,determinant} from '../web/anatomical-material.mjs';
import {materialTensor} from '../web/anatomical-modal.mjs';
import {prepareFurtherBody} from './anatomical-integration-refinement.mjs';
import {prepareCompressionBody} from './anatomical-compression-quadrature.mjs';

const tensor=(nodes,gradient)=>Array.from({length:9},(_,k)=>nodes.reduce((s,X,i)=>s+X[Math.floor(k/3)]*gradient[i][k%3],0));
export function prepareResponseBody(source,modal,material,points=2048){
 const prepared=points===2048?prepareFurtherBody(source,modal.nodeModes):prepareCompressionBody(source,modal.nodeModes,points===32?1:2);
 const held=new Set([...source.distal_nodes,...source.proximal_nodes]);
 for(const e of prepared.elements)for(const p of e.points){
  const groups=new Map();
  for(let i=0;i<10;i++)if(!held.has(e.nodes[i]))for(const m of modal.nodeModes[e.nodes[i]])if(m.base>=9&&m.base<54){
   if(!groups.has(m.base))groups.set(m.base,[0,0,0]);const gradient=groups.get(m.base);
   for(let k=0;k<3;k++)gradient[k]+=m.value*p.gradient[i][k];
  }
  p.responseGroups=[...groups].map(([base,gradient])=>({base:base-9,gradient}));
 }
 return {source,modal,material,prepared,held,direction:null};
}
export function addResponseDirection(body,fullNodalDirection){
 if(body.direction)throw Error('Production direction is frozen once');
 if(fullNodalDirection.length!==body.source.nodes_m.length||fullNodalDirection.some(v=>v.length!==3||!v.every(Number.isFinite)))throw Error('Direction dimensions');
 if([...body.held].some(n=>fullNodalDirection[n].some(v=>v!==0)))throw Error('Direction has nonzero cap trace');
 body.direction=fullNodalDirection.map(v=>v.slice());
 for(const e of body.prepared.elements)for(const p of e.points)p.responseExtra=tensor(e.nodes.map(n=>body.direction[n]),p.gradient);
}
export function responsePositions(body,z){
 const dimension=body.direction?46:45;if(z.length!==dimension||!z.every(Number.isFinite))throw Error('Response coordinate domain');
 return body.source.nodes_m.map((X,n)=>X.map((v,d)=>body.held.has(n)?v:v+body.modal.nodeModes[n].reduce((s,m)=>m.base>=9&&m.base<54?s+m.value*z[m.base-9+d]:s,0)+(body.direction?body.direction[n][d]*z[45]:0)));
}
export function responseNodeStep(body,step){
 return body.source.nodes_m.map((_,n)=>[0,1,2].map(d=>body.held.has(n)?0:body.modal.nodeModes[n].reduce((s,m)=>m.base>=9&&m.base<54?s+m.value*step[m.base-9+d]:s,0)+(body.direction?body.direction[n][d]*step[45]:0)));
}
export function evaluateResponse(body,z,{hessian=true}={}){
 const positions=responsePositions(body,z),n=z.length,gradient=new Float64Array(n),H=hessian?new Float64Array(n*n):null;
 const energies={matrix:0,volume:0,passiveFiber:0,activePotential:0};let minJ=Infinity,cornerJ=Infinity;
 for(const e of body.prepared.elements){
  const X=e.nodes.map(node=>positions[node]);
  for(const p of e.points){
   const F=tensor(X,p.gradient),law=muscleMaterial(F,p.fibre,1,body.material),w=p.weightM3;
   minJ=Math.min(minJ,law.J);for(const key of Object.keys(energies))energies[key]+=w*law.energy[key];
   const groups=p.responseGroups;
   for(const g of groups)for(let r=0;r<3;r++)for(let k=0;k<3;k++)gradient[g.base+r]+=w*law.P[3*r+k]*g.gradient[k];
   if(body.direction)for(let i=0;i<9;i++)gradient[45]+=w*law.P[i]*p.responseExtra[i];
   if(H){
    const C=materialTensor(F,p.fibre,1,body.material);
    for(let a=0;a<groups.length;a++)for(let b=0;b<=a;b++){
     const A=groups[a],B=groups[b];
     for(let r=0;r<3;r++)for(let s=0;s<3;s++)if(a!==b||r>=s){
      let value=0;for(let i=0;i<3;i++)for(let j=0;j<3;j++)value+=A.gradient[i]*C[(3*r+i)*9+3*s+j]*B.gradient[j];
      const k=A.base+r,l=B.base+s;H[k*n+l]+=w*value;if(k!==l)H[l*n+k]+=w*value;
     }
    }
    if(body.direction){
     const CG=new Float64Array(9);for(let i=0;i<9;i++)for(let j=0;j<9;j++)CG[i]+=C[9*i+j]*p.responseExtra[j];
     for(const A of groups)for(let r=0;r<3;r++){
      const value=w*A.gradient.reduce((s,v,i)=>s+v*CG[3*r+i],0),k=A.base+r;H[k*n+45]+=value;H[45*n+k]+=value;
     }
     H[45*n+45]+=w*p.responseExtra.reduce((s,v,i)=>s+v*CG[i],0);
    }
   }
  }
  for(const p of e.corners)cornerJ=Math.min(cornerJ,determinant(tensor(X,p.gradient)));
 }
 if(!(cornerJ>1e-6))throw Error('Corner determinant below unchanged material domain guard');
 return {energyJ:Object.values(energies).reduce((s,v)=>s+v,0),energiesJ:energies,gradientN:gradient,hessianNPerM:H,minimumSampledJ:minJ,minimumCornerJ:cornerJ,positions};
}
export function cholesky(H,n){
 if(H.length!==n*n)throw Error('Tangent dimensions');const L=new Float64Array(n*n);
 for(let i=0;i<n;i++)for(let j=0;j<=i;j++){
  let s=H[i*n+j];for(let k=0;k<j;k++)s-=L[i*n+k]*L[j*n+k];
  if(i===j){if(!(s>0&&Number.isFinite(s)))throw Error('Nonpositive projected tangent pivot '+i+' value '+s);L[i*n+j]=Math.sqrt(s);}
  else L[i*n+j]=s/L[j*n+j];
 }
 return L;
}
export function solveCholesky(L,b){
 const n=b.length,y=new Float64Array(n),x=new Float64Array(n);
 for(let i=0;i<n;i++){let s=b[i];for(let j=0;j<i;j++)s-=L[i*n+j]*y[j];y[i]=s/L[i*n+i];}
 for(let i=n-1;i>=0;i--){let s=y[i];for(let j=i+1;j<n;j++)s-=L[j*n+i]*x[j];x[i]=s/L[i*n+i];}
 return x;
}
