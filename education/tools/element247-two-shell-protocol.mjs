/** One fixed selective geometry rule and retained-vector arithmetic. No law calls. */
import assert from 'node:assert/strict';
import {GAUSS} from './fixed-field-integration-protocol.mjs';
import {shells,shellMap,shellComparisonPass} from './element247-shell-protocol.mjs';
import {ALL_TERMS,emptyAssembly,scatter,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {RECONSTRUCTION_GATES} from './element247-shell-runtime.mjs';

export const TWO_SHELL_BUDGET=Object.freeze({plannedMaterialCalls:4000,maximumMaterialCalls:4000,maximumWallSeconds:180,nodeHeapMiB:1024,maximumRssBytes:2147483648,maximumOutputBytes:67108864,invocations:1});
export const SELECTIVE_RECIPE=Object.freeze({id:'T24',state:'terminal46',element:247,depth:20,radialOrder:5,angularOrder:5,radialParts:1,angularParts:4,faceOrder:[1,2,3],changedShells:['s1','s2'],evaluatedPoints:4000,constructedPoints:13500,reusedRecipe:'A55',reusedPoints:9500});
export const FORCE_GATE_N=1e-5,WORK_GATE_J=5.492029235357012e-7;
export const CHANGED_SHELLS=shells(20).slice(0,2),REUSED_SHELLS=shells(20).slice(2);
export function* changedRule(){
 const g=GAUSS[5];
 for(const s of CHANGED_SHELLS)for(let ap=0;ap<4;ap++)for(let bp=0;bp<4;bp++)
  for(let i=0;i<5;i++)for(let j=0;j<5;j++)for(let k=0;k<5;k++){
   const dr=s.hi-s.lo,r=s.lo+dr*g.x[i],a=(ap+g.x[j])/4,b=(bp+g.x[k])/4,m=shellMap(r,a,b,[1,2,3]);
   yield {L:m.L,weight:6*dr*g.w[i]*g.w[j]*g.w[k]*m.jacobian/16,r,shell:s.id,comparisonShell:s.id};
  }
}
export function packPoints(points){const b=Buffer.alloc(points.length*48);points.forEach((p,i)=>[...p.L,p.weight,p.r].forEach((v,d)=>b.writeDoubleLE(v,48*i+8*d)));return b;}
export function buildConstructedStage(source,rows,direction){
 assert.deepEqual(rows.map(s=>s.shell),shells(20).map(s=>s.id));
 const assembly=emptyAssembly(585),ids=source.elements_ten_node[247];assert.equal(source.nodes_m.length,585);
 for(const row of rows){assert.equal(row.element,247);assert.equal(row.pointCount,['s1','s2'].includes(row.shell)?2000:500);scatter(source,row,assembly);}
 const localGradientsN=Object.fromEntries(ALL_TERMS.map(t=>[t,Array.from({length:10},()=>[0,0,0])])),energiesJ=Object.fromEntries(ALL_TERMS.map(t=>[t,0]));
 for(const row of rows)for(const t of ALL_TERMS){energiesJ[t]+=row.energiesJ[t];for(let i=0;i<10;i++)for(let d=0;d<3;d++)localGradientsN[t][i][d]+=row.localGradientsN[t][i][d];}
 let maximumForceDifferenceN=0,maximumEnergyDifferenceJ=0;
 for(const t of ALL_TERMS){const expected=source.nodes_m.map(()=>[0,0,0]);ids.forEach((n,i)=>{expected[n]=localGradientsN[t][i].slice();});for(let n=0;n<585;n++)for(let d=0;d<3;d++)maximumForceDifferenceN=Math.max(maximumForceDifferenceN,Math.abs(expected[n][d]-assembly.nodal[t][n][d]));maximumEnergyDifferenceJ=Math.max(maximumEnergyDifferenceJ,Math.abs(energiesJ[t]-assembly.energiesJ[t]));}
 assert.ok(maximumForceDifferenceN<=RECONSTRUCTION_GATES.forceN&&maximumEnergyDifferenceJ<=RECONSTRUCTION_GATES.energyJ);
 return {element:247,state:'terminal46',recipe:SELECTIVE_RECIPE,pointCount:13500,evaluatedPoints:4000,reusedPoints:9500,originalShells:rows.map(r=>r.shell),comparisonShells:rows.map(r=>({...r,originalShells:[r.shell]})),localGradientsN,nodalGradientsN:assembly.nodal,energiesJ,terminalDirectionalDerivativesJ:Object.fromEntries(ALL_TERMS.map(t=>[t,assembly.nodal[t].reduce((a,X,n)=>a+X.reduce((v,x,d)=>v+x*direction[n][d],0),0)])),reconstruction:{gates:RECONSTRUCTION_GATES,component:componentSumCheck(assembly),elementToGlobal:{maximumForceDifferenceN,maximumEnergyDifferenceJ,all585Nodes:true}},qualification:false,reusedTailAgreementIsByConstruction:true};
}
export function compareChangedShells(oldRows,newRows,direction,ids){
 for(const rows of [oldRows,newRows])assert.deepEqual(rows.map(s=>s.shell),['s1','s2']);
 const terms={};
 for(const t of ALL_TERMS){
  const aggregate=Array.from({length:10},()=>[0,0,0]),absolute=Array.from({length:10},()=>[0,0,0]),differences=[];let work=0,workTriangle=0;
  for(let s=0;s<2;s++){const delta=oldRows[s].localGradientsN[t].map((v,i)=>v.map((x,d)=>x-newRows[s].localGradientsN[t][i][d]));let w=0;for(let i=0;i<10;i++)for(let d=0;d<3;d++){aggregate[i][d]+=delta[i][d];absolute[i][d]+=Math.abs(delta[i][d]);w+=delta[i][d]*direction[ids[i]][d];}work+=w;workTriangle+=Math.abs(w);differences.push({shell:oldRows[s].shell,localDifferenceN:delta,directionalDifferenceJ:w});}
  const c={differences,aggregateDifferenceN:aggregate,absoluteShellDifferenceN:absolute,aggregateInfinityN:Math.max(...aggregate.flat().map(Math.abs)),shellTriangleInfinityN:Math.max(...absolute.flat()),aggregateDirectionalDifferenceJ:Math.abs(work),shellTriangleDirectionalDifferenceJ:workTriangle};
  const scattered=direction.map(()=>[0,0,0]);ids.forEach((n,i)=>{scattered[n]=aggregate[i].slice();});terms[t]={...c,scatteredDifferenceN:scattered,forceGateN:FORCE_GATE_N,derivativeGateJ:WORK_GATE_J,pass:shellComparisonPass(c,WORK_GATE_J)};
 }
 return {scope:'Changed shells s1/s2 only',state:'terminal46',a:'A55',b:'T24',differenceSign:'retained A55 minus new T24',terms,pass:ALL_TERMS.every(t=>terms[t].pass),qualification:false};
}
