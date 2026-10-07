/** Counted regional assembly; supplied callback only; no evaluator imported. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {assembleElement} from './fixed-field-integration-assembly.mjs';
import {hashBytes,treeBytes} from './element247-shell-runtime.mjs';
import {shells} from './element247-shell-protocol.mjs';
import {regionRow,constructStage,regionKey,normalizationKey,regionRule,packPoints} from './selective-fixed-patch-protocol.mjs';
export function assembleStage({source,r,state,positions,direction,limits,store,materialCallback,context,preflight,readArtifact,reusedRows={},checkpoint=()=>{}}){
 const rows=[];
 for(const s of shells(r.depth)){
  const key=regionKey(r,s.id),points=[...regionRule(r,s)];context.state=state;context.element=r.element;context.rule=r.id;context.region=s.id;context.partialRegion=null;checkpoint('before-region');
  assert.equal(hashBytes(packPoints(points)),preflight.artifactHashes[`${normalizationKey(r)}-${s.id}-points.f64le`]);let local,weights;
  if(reusedRows[s.id]){local=reusedRows[s.id];weights=readArtifact(`${key}-weights.f64le`);context.reusedPoints+=local.pointCount;}
  else{
   try{const result=assembleElement({source,element:r.element,positions,points,limits,materialCallback,onProgress:p=>{context.partialRegion=p;checkpoint('during-region');}});({physicalWeights:weights,...local}=result);}
   catch(error){if(error.partialElement){context.partialRegion=error.partialElement;retainWeights(store,error.partialPhysicalWeights,context);}throw error;}
  }
  // Snapshot before identity, derivative, scatter, serialization or writes.
  context.partialRegion={...local,completedPoints:local.pointCount,physicalWeightsComplete:true};context.physicalWeightEvidenceComplete=false;
  try{
   assert.equal(weights.length,points.length*8);assert.equal(hashBytes(weights),preflight.artifactHashes[`${key}-weights.f64le`]);
   if(state==='control45')store.write(`${key}-weights.f64le`,weights);else{const retained=fs.readFileSync(path.join(store.directory,`${key}-weights.f64le`));assert.equal(hashBytes(retained),hashBytes(weights));}
   context.retainedWeightFile=`${key}-weights.f64le`;context.physicalWeightEvidenceComplete=true;
   const row=regionRow(local,r,s);const ids=source.elements_ten_node[r.element];row.terminalDirectionalDerivativesJ=Object.fromEntries(Object.keys(row.localGradientsN).map(t=>[t,row.localGradientsN[t].reduce((a,v,i)=>a+v.reduce((b,x,d)=>b+x*direction[ids[i]][d],0),0)]));context.partialRegion={...row,completedPoints:row.pointCount,physicalWeightsComplete:true};
   const name=`${state}-${key}-region.json`;store.json(name,row);const serialized=JSON.parse(fs.readFileSync(path.join(store.directory,name)));rows.push(serialized);context.completedRegions.push(`${state}-${key}`);checkpoint('after-region-output');
  }catch(error){if(!context.physicalWeightEvidenceComplete)retainWeights(store,weights,context);throw error;}
  context.partialRegion=null;
 }
 const result=constructStage(source,r,rows);store.json(`${state}-${r.element}-${r.id}-stage.json`,result);checkpoint('after-stage-output');return result;
}
function retainWeights(store,weights,context){
 context.partialWeightSha256=hashBytes(weights);context.physicalWeightEvidenceComplete=false;
 try{assert.ok(weights.length<=65536);store.bytes=treeBytes(store.runRoot);store.write('partial-weights.f64le',weights,{emergency:true});const retained=fs.readFileSync(path.join(store.directory,'partial-weights.f64le'));assert.equal(hashBytes(retained),context.partialWeightSha256);context.physicalWeightEvidenceComplete=true;context.retainedWeightFile='partial-weights.f64le';}catch(error){context.partialWeightWriteError=String(error.message).slice(0,256);}
}
