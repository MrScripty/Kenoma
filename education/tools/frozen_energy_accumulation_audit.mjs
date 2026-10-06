/** Same frozen original-material energy terms, three accumulation orders.
 * Diagnostic only: no operator/source repair or changed qualification receipt.
 */
import fs from 'node:fs';
import {muscleMaterial,determinant,inverseTranspose} from '../web/anatomical-material.mjs';
import {quadraticShape} from '../web/anatomical-element.mjs';
import {compressionQuadrature} from './anatomical-compression-quadrature.mjs';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const {mesh,positionsM:x,pressures,material,activation,depth}=input;
const terms={continuousP1:[],brokenP1:[],pointwise:[]};
const tensor=(nodes,grad)=>Array.from({length:9},(_,k)=>nodes.reduce((s,X,n)=>s+X[Math.floor(k/3)]*grad[n][k%3],0));
for(const [e,ids] of mesh.tets.entries())for(const point of compressionQuadrature(depth)){
 const ref=ids.map(i=>mesh.X[i]),current=ids.map(i=>x[i]),shape=quadraticShape(point.L),jac=tensor(ref,shape.gradient),det=determinant(jac);
 if(!(det>1e-15))throw Error('Original reference determinant guard');
 const inv=inverseTranspose(jac,det),grad=shape.gradient.map(a=>[0,1,2].map(i=>[0,1,2].reduce((s,j)=>s+inv[3*i+j]*a[j],0)));
 const w=point.weight*det/6,F=tensor(current,grad),r=muscleMaterial(F,[1,0,0],activation,material),log=Math.log(r.J);
 for(const space of Object.keys(terms)){
  const indices=space==='continuousP1'?ids.slice(0,4):[4*e,4*e+1,4*e+2,4*e+3];
  const pq=space==='pointwise'?material.bulk*log:point.L.reduce((s,l,i)=>s+l*pressures[space][indices[i]],0);
  terms[space].push(w*(space==='pointwise'?r.solvePotential:r.solvePotential-r.energy.volume+pq*log-pq*pq/(2*material.bulk)));
 }
}
function pairwise(values){
 let row=values.slice();
 while(row.length>1){const next=[];for(let i=0;i<row.length;i+=2)next.push(row[i]+(row[i+1]??0));row=next;}
 return row[0]??0;
}
function compensated(values){
 let sum=0,correction=0;
 for(const value of values){const next=sum+value;correction+=Math.abs(sum)>=Math.abs(value)?(sum-next)+value:(value-next)+sum;sum=next;}
 return sum+correction;
}
const results=Object.fromEntries(Object.entries(terms).map(([space,row])=>[space,{
 termCount:row.length,naiveEnergyJ:row.reduce((s,v)=>s+v,0),pairwiseEnergyJ:pairwise(row),compensatedEnergyJ:compensated(row),
 minimumWeightedEnergyTermJ:Math.min(...row),maximumWeightedEnergyTermJ:Math.max(...row)}]));
process.stdout.write(JSON.stringify({results,scope:'Same retained frozen terms only; no original failure reclassification or threshold change'}));
