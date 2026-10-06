/** Full element tangent of the existing body law; no optimizer. */
import {materialTensor} from '../web/anatomical-modal.mjs';
export function elementBodyTangent(e,positions,activation,material){
 const X=e.nodes.map(n=>positions[n]),H=new Float64Array(900);
 for(const p of e.points){const F=Array.from({length:9},(_,k)=>X.reduce((s,v,n)=>s+v[Math.floor(k/3)]*p.gradient[n][k%3],0)),C=materialTensor(F,p.fibre,activation,material),w=p.weightM3;
  for(let r=0;r<3;r++)for(let s=0;s<3;s++)for(let j=0;j<10;j++){
   const t=[0,0,0];for(let a=0;a<3;a++)for(let b=0;b<3;b++)t[a]+=C[(3*r+a)*9+3*s+b]*p.gradient[j][b];
   for(let i=0;i<10;i++)H[(3*i+r)*30+3*j+s]+=w*p.gradient[i].reduce((v,g,a)=>v+g*t[a],0);
  }
 }
 return H;
}
