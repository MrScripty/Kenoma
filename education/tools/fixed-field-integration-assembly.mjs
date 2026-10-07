/** Fixed-field component assembly, with an injected counted constitutive callback. */
import assert from 'node:assert/strict';
import {TERMS,referencePoint,tensor} from './isolated-collapse-components.mjs';
export const ALL_TERMS=[...TERMS,'total'];
export const zeros=n=>Array.from({length:n},()=>[0,0,0]);
export const vectors=n=>Object.fromEntries(ALL_TERMS.map(t=>[t,zeros(n)]));
export const energyZeros=()=>Object.fromEntries(ALL_TERMS.map(t=>[t,0]));
export function assembleElement({source,element,positions,points,limits,materialCallback,onProgress=()=>{}}){
 const ids=source.elements_ten_node[element],X=ids.map(n=>positions[n]),local=vectors(10),energies=energyZeros(),physicalWeights=Buffer.alloc(points.length*8);let completedPoints=0,minimumJ=Infinity;
 const partial=()=>({element,completedPoints,pointCount:points.length,localGradientsN:local,energiesJ:energies,physicalWeightsComplete:false});
 limits.beginBatch(points.length,`element-${element}`);
 try{
  for(let k=0;k<points.length;k++){
   const p=points[k],q=referencePoint(source,element,p.L,p.weight),F=tensor(X,q.gradient),r=limits.invoke(()=>materialCallback(F,q.fibre));
   assert.ok(Number.isFinite(r.actual.J)&&r.actual.J>1e-6);assert.ok(q.weightM3>0&&Number.isFinite(q.weightM3));
   physicalWeights.writeDoubleLE(q.weightM3,k*8);minimumJ=Math.min(minimumJ,r.actual.J);
   const stresses={...r.stresses,total:r.actual.P};
   for(const t of ALL_TERMS){const e=t==='total'?TERMS.reduce((s,a)=>s+r.actual.energy[a],0):r.actual.energy[t];assert.ok(Number.isFinite(e));energies[t]+=q.weightM3*e;assert.ok(stresses[t].length===9&&stresses[t].every(Number.isFinite));}
   for(let i=0;i<10;i++)for(let d=0;d<3;d++)for(let a=0;a<3;a++){const v=q.weightM3*q.gradient[i][a];for(const t of ALL_TERMS)local[t][i][d]+=v*stresses[t][3*d+a];}
   completedPoints++;if(completedPoints%128===0)onProgress(partial());
  }
  limits.endBatch();onProgress(partial());
  return {element,pointCount:completedPoints,minimumSampleJ:minimumJ,energiesJ:energies,localGradientsN:local,physicalWeights};
 }catch(error){error.partialElement=partial();error.partialPhysicalWeights=physicalWeights.subarray(0,completedPoints*8);throw error;}
}
export function scatter(source,e,assembly){const ids=source.elements_ten_node[e.element];for(const t of ALL_TERMS){assembly.energiesJ[t]+=e.energiesJ[t];ids.forEach((n,i)=>{for(let d=0;d<3;d++)assembly.nodal[t][n][d]+=e.localGradientsN[t][i][d];});}}
export const emptyAssembly=n=>({nodal:vectors(n),energiesJ:energyZeros()});
export function componentSumCheck(assembly){let force=0;for(let n=0;n<assembly.nodal.total.length;n++)for(let d=0;d<3;d++)force=Math.max(force,Math.abs(TERMS.reduce((s,t)=>s+assembly.nodal[t][n][d],0)-assembly.nodal.total[n][d]));const energy=Math.abs(TERMS.reduce((s,t)=>s+assembly.energiesJ[t],0)-assembly.energiesJ.total);assert.ok(force<=1e-8&&energy<=1e-9,`Component reconstruction ${force}N / ${energy}J`);return {maximumForceDifferenceN:force,energyDifferenceJ:energy};}
