/** Only two counted material batches; same assembler and completed-weight retention. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {assembleElement,emptyAssembly,scatter,ALL_TERMS,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {hashBytes,treeBytes} from './element247-shell-runtime.mjs';
import {CHANGED_SHELLS} from './element247-two-shell-protocol.mjs';
import {withChangedShellIdentity} from './element247-two-shell-schema.mjs';
export function assembleChangedShells({source,positions,direction,points,limits,store,materialCallback,context,onCheckpoint=()=>{}}){
 const rows=[],weights=[];
 for(const s of CHANGED_SHELLS){
  const ps=points.filter(p=>p.shell===s.id);assert.equal(ps.length,2000);context.shell=s.id;context.partialShell=null;onCheckpoint('before-changed-shell');let e;
  try{e=assembleElement({source,element:247,positions,points:ps,limits,materialCallback,onProgress:p=>{context.partialShell=p;onCheckpoint('during-changed-shell');}});}catch(error){
   if(error.partialElement){context.partialShell=error.partialElement;context.partialWeightSha256=hashBytes(error.partialPhysicalWeights);try{assert.ok(error.partialPhysicalWeights.length<=65536);store.write(`T24-terminal46-${s.id}-partial-weights.f64le`,error.partialPhysicalWeights,{emergency:true});}catch(w){context.partialWeightWriteError=w.message;}}
   throw error;
  }
  const {physicalWeights,...local}=e;context.partialShell={...local,...s,completedPoints:e.pointCount,physicalWeightsComplete:true};
  const weightName=`T24-terminal46-${s.id}-weights.f64le`;
  try{
   const ids=source.elements_ten_node[247],row=withChangedShellIdentity({...local,...s,comparisonShell:s.id,terminalDirectionalDerivativesJ:Object.fromEntries(ALL_TERMS.map(t=>[t,local.localGradientsN[t].reduce((v,X,i)=>v+X.reduce((a,x,d)=>a+x*direction[ids[i]][d],0),0)]))});context.partialShell={...row,completedPoints:e.pointCount,physicalWeightsComplete:true};
   const check=emptyAssembly(585);scatter(source,e,check);row.reconstruction=componentSumCheck(check);store.write(weightName,physicalWeights);store.json(`T24-terminal46-${s.id}-shell.json`,row);rows.push(row);weights.push(physicalWeights);context.completedShells.push(s.id);onCheckpoint('after-changed-shell-output');
  }catch(error){
   const expected=hashBytes(physicalWeights);context.partialWeightSha256=expected;context.physicalWeightEvidenceComplete=false;
   try{const file=path.join(store.directory,weightName),stat=fs.lstatSync(file);if(stat.isFile()&&stat.size===physicalWeights.length&&hashBytes(fs.readFileSync(file))===expected){context.retainedWeightFile=weightName;context.physicalWeightEvidenceComplete=true;}}catch(w){context.normalWeightReadError=w.message;}
   if(!context.physicalWeightEvidenceComplete)try{assert.ok(physicalWeights.length<=65536);store.bytes=treeBytes(store.runRoot);const name=`T24-terminal46-${s.id}-partial-weights.f64le`;store.write(name,physicalWeights,{emergency:true});assert.equal(hashBytes(fs.readFileSync(path.join(store.directory,name))),expected);context.retainedWeightFile=name;context.physicalWeightEvidenceComplete=true;}catch(w){context.partialWeightWriteError=w.message;}
   throw error;
  }
  context.partialShell=null;
 }
 return {rows,physicalWeights:Buffer.concat(weights)};
}
