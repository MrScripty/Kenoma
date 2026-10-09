/** Invoked only by the separately approved supervisor. Importing this file does
 * not load physical modules. Output on fd3 is PROVISIONAL until process disposal. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {Budget,createObserver,detached,json,sha256,transaction,observationStatus} from './core.mjs';
import {installLoader} from './loader.mjs';import {verifyHeld,verifyLeaves} from './replay.mjs';
export async function numericalWorker(manifest,runId){
 const run=manifest.policy.runs.find(r=>r.id===runId);if(!run)throw Error('Unknown fixed run');
 const limits=Object.fromEntries(['attempts','configurationEntries','muscleMaterial','tendonMaterial','materialTensor','hessianProducts'].map(k=>[k,run[k]]));
 const budget=new Budget(limits),emit=e=>{const bytes=json({run:runId,...e})+'\n';if(Buffer.byteLength(bytes)+transcript>manifest.policy.perRunTranscriptBytes-manifest.policy.reservedTranscriptBytes)budget.refuse('transcriptBytes',{executed:transcript});transcript+=Buffer.byteLength(bytes);fs.writeSync(1,bytes);};let transcript=0;
 const observer=createObserver(budget,emit,manifest.policy.perRunOutputBytes-manifest.policy.reservedReceiptBytes);globalThis.__kenomaValidation=observer;
 const hook=installLoader(manifest.modules);let arm,initial,rule,packet;
 try{
  const imports=await Promise.all(['anatomical-arm','anatomical-contact-refinement','anatomical-audit','anatomical-routing-audit','anatomical-transfer','anatomical-apparatus'].map(n=>import('kenoma:education/web/'+n+'.mjs')));
  const contracts=await import('kenoma:education/tools/anatomical-replay-contracts.mjs'),api=Object.assign({},...imports,contracts);
  const input=rel=>{const i=manifest.inputs[rel];if(!i||sha256(i.text)!==i.sha256)throw Error('Changed pinned input');return JSON.parse(i.text);};
  const rest=input('audit/arm-rest-results.json');if(rest.accepted!==true||rest.quadrature!=='subdivided32')throw Error('Changed held input');
  arm=api.prepareAnatomicalArm(input('generated/arm-reference.json'),input('config/attachments-apparatus.json'),input('audit/modal-fixed-end-results.json'),{quadrature:'subdivided32',parameters:rest.parameters,contactParameters:rest.contactParameters,routingRecipe:input('config/apparatus-routing.json')});
  if(arm.model.ndof!==460||arm.model.branches.length!==585||arm.model.bodies.reduce((s,b)=>s+b.modal.points.length,0)!==56448||arm.model.bodies.reduce((s,b)=>s+b.internalAponeuroses.branches.length,0)!==48)throw Error('Changed accounting topology');
  initial=detached(rest.state);rule=api.contactRecipe(arm.contact);arm.onIteration=row=>observer.progress(row);
  packet=await transaction({state:initial,capture:()=>api.contactRecipe(arm.contact),restore:r=>api.restoreContactRecipe(arm.contact,r),budget,
   operation:async()=>{
    if(runId==='A')return {accepted:true,status:'PASS',heldRecheck:verifyHeld(api,arm,initial),finalState:detached(initial),finalContactRule:detached(rule),leaves:[]};
    let result;
    const step=(s,h,depth=0)=>api.stepAnatomicalArm(arm,{...s,coordinatesM:Float64Array.from(s.coordinatesM)},{effort:.04,h,maxIterations:120,...(depth?{subdivisionDepth:depth}:{})});
    if(runId==='D'){
     const first=step(initial,.005);budget.alive();if(!first.accepted)return {accepted:false,status:'SOLVER_REFUSAL',reason:first.reason??null};
     result=step(first.state,.005);budget.alive();
    }else{result=step(initial,.01,runId==='C'?1:0);budget.alive();}
    if(!result.accepted)return {accepted:false,status:'SOLVER_REFUSAL',reason:result.reason??null,residualN:result.maxGradientN??null,substepIntegration:result.substepIntegration??null};
    const leaves=runId==='D'?observer.records().filter(r=>r.accepted):observer.select(result);
    if(leaves.length!==(runId==='D'?2:result.substepIntegration?.committedSubsteps??1))throw Error('Missing leaf coverage');
    const finalState=detached(result.state);const rechecks=verifyLeaves(api,arm,initial,leaves,.01);budget.alive();
    return {accepted:true,status:'PASS',finalState,finalContactRule:detached(api.contactRecipe(arm.contact)),leaves,rechecks,substepIntegration:result.substepIntegration??null};
   }});
  budget.alive();
 }catch(error){
  if(arm&&rule){try{const api=await import('kenoma:education/web/anatomical-contact-refinement.mjs');api.restoreContactRecipe(arm.contact,rule);}catch{}}
  packet={accepted:false,status:budget.latch?'RESOURCE_INCONCLUSIVE':'EXCEPTION',error:String(error)};
 }finally{if(arm)arm.onIteration=undefined;arm=null;hook.deregister();delete globalThis.__kenomaValidation;}
 const observations=observer.records();observer.dispose();const accepted=packet.accepted;delete packet.accepted;
 return detached({...packet,executionScope:manifest.scope,status:budget.latch?'RESOURCE_INCONCLUSIVE':packet.status,workerStatus:'PROVISIONAL_PENDING_SUPERVISOR',numericalCandidateAccepted:accepted&&!budget.latch,finalAcceptance:false,run:runId,sourceCommit:manifest.operatorCommit,harnessCommit:manifest.harnessCommit,inputStateSHA256:sha256(manifest.inputs['audit/arm-rest-results.json'].text),observations,observationStatus,counters:budget.snapshot(),transcriptBytes:transcript,modelDisposed:true,anatomicalQualification:false});
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [flag,manifestPath,runId,expected]=process.argv.slice(2);if(flag!=='--numerical-run'||!manifestPath||!runId||!expected)throw Error('Explicit supervised numerical entry required');
 const bytes=fs.readFileSync(manifestPath);if(sha256(bytes)!==expected)throw Error('Stale manifest');const manifest=JSON.parse(bytes);
 const packet=await numericalWorker(manifest,runId);const fd=Number(process.env.KENOMA_RESULT_FD);if(!Number.isInteger(fd)||fd<3)throw Error('Missing supervisor result channel');fs.writeFileSync(fd,json(packet)+'\n');
}
