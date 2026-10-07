/** Stream one region; injected callback only; durable explicit reuse dependencies. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {assembleElement} from './fixed-field-integration-assembly.mjs';
import {hashBytes,treeBytes} from './element247-shell-runtime.mjs';
import {shells} from './element247-shell-protocol.mjs';
import {regionRule,packPoints} from './fine-window-maps.mjs';
import {regionPointCount,regionRecord,constructStage,regionKey,normalizedOrigin,weightOrigin,reusedOrigin,newRegion} from './fine-window-protocol.mjs';
export function assembleStage({source,r,state,positions,direction,identity,limits,store,context,preflight,readArtifact,readHistorical,materialCallback,checkpoint=()=>{}}){
 const rows=[],sources=[];
 for(const s of shells(r.depth)){
  const key=regionKey(r,s.id),geometryKey=`${r.element}-${r.id}-${s.id}`,cert=preflight.regions[geometryKey],points=[...regionRule(r,s)];assert.equal(points.length,regionPointCount(r,s));assert.equal(hashBytes(packPoints(points)),cert.normalizedSha256);context.state=state;context.element=r.element;context.rule=r.id;context.region=s.id;context.partialRegion=null;checkpoint('before-region');let local,weights,origin;
  const reuse=reusedOrigin(r,state,s);
  if(reuse){
   const data=reuse.kind==='historical'?readHistorical(reuse.name):fs.readFileSync(path.join(store.directory,reuse.name)),sourceRow=JSON.parse(data),stageBytes=reuse.kind==='historical'?readHistorical(reuse.stage):fs.readFileSync(path.join(store.directory,reuse.stage)),stage=JSON.parse(stageBytes);
   if(reuse.kind==='same-invocation'){
    assert.equal(store.files[reuse.stage]?.sha256,hashBytes(stageBytes),'Missing/damaged accepted prior P4 stage');assert.equal(store.files[reuse.name]?.sha256,hashBytes(data),'Missing/damaged prior P4 row');assert.equal(stage.state,state);assert.equal(stage.recipe.id,'P4');assert.equal(stage.reusedPoints,0);assert.equal(stage.newCallbackPoints,42000);assert.deepEqual(sourceRow.evaluationIdentity,identity);assert.equal(sourceRow.state,state);
    assert.ok(stage.rowSources.some(x=>x.shell===s.id&&x.sha256===hashBytes(data)&&x.name===reuse.name),'P4 stage receipt does not bind row');
   }else assert.equal(hashBytes(data),cert.reuseRows[state].sha256,'Historical row identity');
   for(const name of ['pointCount','minimumSampleJ','energiesJ','localGradientsN'])assert.notEqual(sourceRow[name],undefined);assert.equal(sourceRow.element,r.element);assert.equal(sourceRow.shell,s.id);assert.equal(sourceRow.lo,s.lo);assert.equal(sourceRow.hi,s.hi);assert.equal(sourceRow.pointCount,points.length);
   const W=weightOrigin(r,s),weightData=W.kind==='historical'?readHistorical(W.name):fs.readFileSync(path.join(store.directory,W.name));assert.equal(hashBytes(weightData),cert.physicalSha256,'Reuse weight identity');assert.equal(weightData.length,points.length*8);weights=weightData;local=sourceRow;
   origin={kind:reuse.kind,name:reuse.name,sha256:hashBytes(data),stageName:reuse.stage,stageSha256:hashBytes(stageBytes),normalizedSha256:cert.normalizedSha256,physicalSha256:cert.physicalSha256,identityMatches:true,earnsIndependentResolutionCredit:false};
   context.reusedLogicalPoints+=points.length;context.sharedRegions++;
  }else{
   try{const result=assembleElement({source,element:r.element,positions,points,limits,materialCallback,onProgress:p=>{context.partialRegion=p;checkpoint('during-region');}});({physicalWeights:weights,...local}=result);}catch(error){if(error.partialElement){context.partialRegion=error.partialElement;retainWeights(store,error.partialPhysicalWeights,context);}throw error;}
   origin={kind:'new',normalizedSha256:cert.normalizedSha256,physicalSha256:cert.physicalSha256};
  }
  context.partialRegion={...local,completedPoints:local.pointCount,physicalWeightsComplete:true};context.physicalWeightEvidenceComplete=false;
  try{
   assert.equal(hashBytes(weights),cert.physicalSha256);assert.equal(weights.length,points.length*8);
   if(newRegion(r,s)){const W=weightOrigin(r,s);if(state==='control45')store.write(W.name,weights);else assert.equal(hashBytes(fs.readFileSync(path.join(store.directory,W.name))),cert.physicalSha256);context.retainedWeightFile=W.name;}else context.retainedWeightFile=weightOrigin(r,s).name;
   context.physicalWeightEvidenceComplete=true;const row=regionRecord(local,r,state,s,identity,origin),ids=source.elements_ten_node[r.element];row.terminalDirectionalDerivativesJ=Object.fromEntries(Object.keys(row.localGradientsN).map(t=>[t,row.localGradientsN[t].reduce((sum,v,i)=>sum+v.reduce((a,x,d)=>a+x*direction[ids[i]][d],0),0)]));let record;
   if(newRegion(r,s)){const name=`${state}-${key}-region.json`;store.json(name,row);record={shell:s.id,kind:'new',name,...store.files[name]};rows.push(JSON.parse(fs.readFileSync(path.join(store.directory,name))));context.newRegions++;}else{record={shell:s.id,...origin};rows.push(row);}
   sources.push(record);context.completedRegions.push(`${state}-${key}`);checkpoint('after-region-output');
  }catch(error){if(!context.physicalWeightEvidenceComplete)retainWeights(store,weights,context);throw error;}
  context.partialRegion=null;
 }
 const result=constructStage(source,r,state,rows,sources);store.json(`${state}-${r.element}-${r.id}-stage.json`,result);checkpoint('after-stage-output');return result;
}
function retainWeights(store,weights,context){
 context.physicalWeightEvidenceComplete=false;context.partialWeightSha256=hashBytes(weights);
 try{assert.ok(weights.length<=524288);store.bytes=treeBytes(store.runRoot);store.write('partial-weights.f64le',weights,{emergency:true});assert.equal(hashBytes(fs.readFileSync(path.join(store.directory,'partial-weights.f64le'))),context.partialWeightSha256);context.retainedWeightFile='partial-weights.f64le';context.physicalWeightEvidenceComplete=true;}catch(error){context.partialWeightWriteError=String(error.message).slice(0,256);}
}
