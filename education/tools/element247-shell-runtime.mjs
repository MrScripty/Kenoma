/** Counted shell assembly and complete evidence. Law supplied by caller. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {RuntimeLimits,EvidenceStore,ResourceRefusal} from './fixed-field-integration-runtime.mjs';
import {assembleElement,emptyAssembly,scatter,ALL_TERMS,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {SHELL_BUDGET,shells,COMPARISON_DEPTH,compareShellVectors,shellComparisonPass} from './element247-shell-protocol.mjs';
export {RuntimeLimits,ResourceRefusal};
export const RECONSTRUCTION_GATES={forceN:1e-8,energyJ:1e-9};
export const hashBytes=b=>createHash('sha256').update(b).digest('hex');
export function treeBytes(directory){let total=0;for(const e of fs.readdirSync(directory,{withFileTypes:true})){const p=path.join(directory,e.name);assert.ok(!e.isSymbolicLink(),'Output symlinks forbidden');if(e.isDirectory())total+=treeBytes(p);else{assert.ok(e.isFile(),'Unexpected output entry');total+=fs.statSync(p).size;}}return total;}
export class ShellEvidenceStore extends EvidenceStore{
 constructor(runRoot,options={}){super(path.join(runRoot,'material'),{maximumBytes:SHELL_BUDGET.maximumOutputBytes,emergencyBytes:2*1024**2,...options});this.runRoot=runRoot;this.checkStorage('created');}
 checkStorage(phase){if(!this.runRoot)return super.checkStorage(phase);this.bytes=treeBytes(this.runRoot);if(this.bytes>this.maximumBytes-this.emergencyBytes)throw new ResourceRefusal('STORAGE_LIMIT',{phase,combinedBytes:this.bytes,maximumNormalBytes:this.maximumBytes-this.emergencyBytes});}
 failure(error,context,limits){
  this.bytes=treeBytes(this.runRoot);
  const compact={schema:1,result:'INCOMPLETE_ELEMENT247_SHELL_INTEGRATION',reason:error.reason??error.message,detail:error.detail??null,runtime:limits.receipt(),context,retainedFiles:this.files,combinedBytesBeforeReceipt:this.bytes};
  const bytes=Buffer.from(JSON.stringify(compact)+'\n');assert.ok(bytes.length<=1024**2,'Child failure evidence must fit its1MiB reserve');return this.write('incomplete-receipt.json',bytes,{emergency:true});
 }
}
export const shellLimits=()=>new RuntimeLimits({plannedCalls:SHELL_BUDGET.plannedMaterialCalls,maximumCalls:SHELL_BUDGET.maximumMaterialCalls,wallMs:1000*SHELL_BUDGET.maximumWallSeconds,rssBytes:SHELL_BUDGET.maximumRssBytes,now:()=>process.uptime()*1000,startedMs:0});
export function assembleShellStage({source,element,positions,direction,recipe,points,limits,store,materialCallback,context,onCheckpoint=()=>{}}){
 const assembly=emptyAssembly(source.nodes_m.length),original=[],localNames=[],physical=[];
 for(const s of shells(recipe.depth)){
  const ps=points.filter(p=>p.shell===s.id);assert.ok(ps.length);context.shell=s.id;context.partialShell=null;onCheckpoint('before-shell');let e;
  try{e=assembleElement({source,element,positions,points:ps,limits,materialCallback,onProgress:p=>{context.partialShell=p;onCheckpoint('during-shell');}});}catch(error){
   if(error.partialElement){context.partialShell=error.partialElement;context.partialWeightSha256=hashBytes(error.partialPhysicalWeights);try{assert.ok(error.partialPhysicalWeights.length<=65536);store.write(`${recipe.id}-${context.state}-${s.id}-partial-weights.f64le`,error.partialPhysicalWeights,{emergency:true});}catch(w){context.partialWeightWriteError=w.message;}}
   throw error;
  }
  const {physicalWeights,...local}=e,ids=source.elements_ten_node[element],work=Object.fromEntries(ALL_TERMS.map(t=>[t,local.localGradientsN[t].reduce((v,X,i)=>v+X.reduce((a,x,d)=>a+x*direction[ids[i]][d],0),0)])),row={...local,shell:s.id,lo:s.lo,hi:s.hi,comparisonShell:s.hi<=2**(-COMPARISON_DEPTH)?'core':s.id,terminalDirectionalDerivativesJ:work};
  const localAssembly=emptyAssembly(source.nodes_m.length);scatter(source,e,localAssembly);row.reconstruction=componentSumCheck(localAssembly);
  const name=`${recipe.id}-${context.state}-${s.id}-shell.json`,weightName=`${recipe.id}-${context.state}-${s.id}-weights.f64le`;
  try{store.write(weightName,physicalWeights);store.json(name,row);}catch(error){context.partialShell={...row,completedPoints:e.pointCount,physicalWeightsComplete:true};context.partialWeightSha256=hashBytes(physicalWeights);if(!fs.existsSync(path.join(store.directory,weightName)))try{assert.ok(physicalWeights.length<=65536);store.write(`${recipe.id}-${context.state}-${s.id}-partial-weights.f64le`,physicalWeights,{emergency:true});}catch(w){context.partialWeightWriteError=w.message;}throw error;}
  localNames.push(name);physical.push(physicalWeights);original.push(row);scatter(source,e,assembly);context.completedShells.push(s.id);context.partialShell=null;context.partialNodal=assembly.nodal;context.partialEnergiesJ=assembly.energiesJ;onCheckpoint('after-shell-output');
 }
 const grouped=shells(COMPARISON_DEPTH).map(s=>({shell:s.id,localGradientsN:Object.fromEntries(ALL_TERMS.map(t=>[t,Array.from({length:10},()=>[0,0,0])])),energiesJ:Object.fromEntries(ALL_TERMS.map(t=>[t,0])),originalShells:[]}));
 for(const row of original){const bin=grouped.find(g=>g.shell===row.comparisonShell);assert.ok(bin);bin.originalShells.push(row.shell);for(const t of ALL_TERMS){bin.energiesJ[t]+=row.energiesJ[t];for(let i=0;i<10;i++)for(let d=0;d<3;d++)bin.localGradientsN[t][i][d]+=row.localGradientsN[t][i][d];}}
 const localGradientsN=Object.fromEntries(ALL_TERMS.map(t=>[t,Array.from({length:10},()=>[0,0,0])])),energiesJ=Object.fromEntries(ALL_TERMS.map(t=>[t,0]));
 // A separate retention reconstruction from the original shells, checked
 // against both the grouped representation and the directly scattered stage.
 for(const s of original)for(const t of ALL_TERMS){energiesJ[t]+=s.energiesJ[t];for(let i=0;i<10;i++)for(let d=0;d<3;d++)localGradientsN[t][i][d]+=s.localGradientsN[t][i][d];}
 const shellToElement={maximumForceDifferenceN:0,maximumEnergyDifferenceJ:0},elementToGlobal={maximumForceDifferenceN:0,maximumEnergyDifferenceJ:0,all585Nodes:source.nodes_m.length===585};
 for(const t of ALL_TERMS){const fromGroups=Array.from({length:10},()=>[0,0,0]);let energy=0;for(const g of grouped){energy+=g.energiesJ[t];for(let i=0;i<10;i++)for(let d=0;d<3;d++)fromGroups[i][d]+=g.localGradientsN[t][i][d];}
  shellToElement.maximumEnergyDifferenceJ=Math.max(shellToElement.maximumEnergyDifferenceJ,Math.abs(energy-energiesJ[t]));for(let i=0;i<10;i++)for(let d=0;d<3;d++)shellToElement.maximumForceDifferenceN=Math.max(shellToElement.maximumForceDifferenceN,Math.abs(fromGroups[i][d]-localGradientsN[t][i][d]));
  const expected=source.nodes_m.map(()=>[0,0,0]);source.elements_ten_node[element].forEach((n,i)=>{expected[n]=localGradientsN[t][i].slice();});for(let n=0;n<expected.length;n++)for(let d=0;d<3;d++)elementToGlobal.maximumForceDifferenceN=Math.max(elementToGlobal.maximumForceDifferenceN,Math.abs(expected[n][d]-assembly.nodal[t][n][d]));elementToGlobal.maximumEnergyDifferenceJ=Math.max(elementToGlobal.maximumEnergyDifferenceJ,Math.abs(energiesJ[t]-assembly.energiesJ[t]));
 }
 for(const c of [shellToElement,elementToGlobal])assert.ok(c.maximumForceDifferenceN<=RECONSTRUCTION_GATES.forceN&&c.maximumEnergyDifferenceJ<=RECONSTRUCTION_GATES.energyJ,'Shell/element/global reconstruction gates');
 return {element,recipe,state:context.state,pointCount:points.length,originalShells:original.map(s=>s.shell),localShellFiles:localNames,comparisonShells:grouped,localGradientsN,nodalGradientsN:assembly.nodal,energiesJ:assembly.energiesJ,terminalDirectionalDerivativesJ:Object.fromEntries(ALL_TERMS.map(t=>[t,assembly.nodal[t].reduce((a,X,n)=>a+X.reduce((v,x,d)=>v+x*direction[n][d],0),0)])),reconstruction:{gates:RECONSTRUCTION_GATES,component:componentSumCheck(assembly),shellToElement,elementToGlobal},physicalWeights:Buffer.concat(physical)};
}
export function compareShellStages(A,B,direction,ids,gateJ){
 assert.equal(A.state,B.state);assert.equal(A.element,B.element);const terms={};
 for(const t of ALL_TERMS){const c=compareShellVectors(A.comparisonShells.map(s=>({shell:s.shell,localGradientsN:s.localGradientsN[t]})),B.comparisonShells.map(s=>({shell:s.shell,localGradientsN:s.localGradientsN[t]})),ids.map(n=>direction[n]));
  const scattered=direction.map(()=>[0,0,0]);ids.forEach((n,i)=>{for(let d=0;d<3;d++)scattered[n][d]=c.aggregateDifferenceN[i][d];});
  for(let n=0;n<direction.length;n++)for(let d=0;d<3;d++)assert.ok(Math.abs(scattered[n][d]-(A.nodalGradientsN[t][n][d]-B.nodalGradientsN[t][n][d]))<=RECONSTRUCTION_GATES.forceN,'Comparison grouping/scatter');
  terms[t]={...c,scatteredDifferenceN:scattered,forceGateN:1e-5,derivativeGateJ:gateJ,pass:shellComparisonPass(c,gateJ)};
 }
 return {state:A.state,a:A.recipe.id,b:B.recipe.id,terms,pass:ALL_TERMS.every(t=>terms[t].pass)};
}
