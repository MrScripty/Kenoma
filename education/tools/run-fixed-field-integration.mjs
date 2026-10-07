/** ONE authorized saved-field assembly. No solve, new field or calibration. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {execFileSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {PATCH,RECIPES,COMPARISONS,TERMS,rule,digest,checkedFixedState,replacePatch,compareVectors} from './fixed-field-integration-protocol.mjs';
import {RuntimeLimits,EvidenceStore,preservingFailure} from './fixed-field-integration-runtime.mjs';
import {assembleElement,emptyAssembly,scatter,ALL_TERMS,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {stressComponents} from './isolated-collapse-components.mjs';
import {meshPartition} from './isolated-displacement-family.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
assert.deepEqual(process.argv.slice(2),['--execute'],'Explicit --execute is required; no alternate recipes/states/budgets');
assert.deepEqual(process.execArgv,['--max-old-space-size=6144'],'Frozen heap invocation required');
const runtime=new RuntimeLimits({startedMs:0}),manifest=read('research/fixed-field-integration-run-20261007-inputs.json'),protocol=read('research/fixed-field-integration-protocol-20261007-inputs.json'),preflight=read('review/fixed-field-integration-runtime-20261007/runtime-preflight.json'),head=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
assert.equal(manifest.plannedMaterialCalls,8847360);assert.equal(manifest.maximumMaterialCalls,9000000);assert.equal(manifest.maximumWallSeconds,900);assert.equal(manifest.invocations,1);assert.equal(manifest.executionAuthorized,true);
const paths=[...Object.keys(manifest.inputs),...manifest.newSources,'review/fixed-field-integration-runtime-20261007/runtime-preflight.json','review/fixed-field-integration-runtime-20261007/tests.log'];for(const p of paths)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});execFileSync('git',['diff','--exit-code','HEAD','--',...paths],{cwd:root,stdio:'pipe'});
for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h,p);for(const [p,h] of Object.entries(preflight.sourceHashes))assert.equal(hash(p),h,p);assert.equal(preflight.result,'PASS_RUNTIME_ENFORCEMENT_PREFLIGHT_NO_SPECIMEN_ASSEMBLY');assert.equal(preflight.specimenConstitutiveCalls,0);assert.ok(preflight.tests.fail===0);
assert.equal(hash('review/fixed-field-integration-runtime-20261007/tests.log'),preflight.tests.logSha256);
assert.ok(execFileSync('git',['merge-base','--is-ancestor',preflight.sourceCommit,head],{cwd:root})!==null);
const output=root+'review/fixed-field-integration-run-20261007/',store=new EvidenceStore(output);let context={stage:'setup',sourceCommit:head,preflightSourceCommit:preflight.sourceCommit};
const sourceHashes=Object.fromEntries(paths.map(p=>[p,hash(p)]));
function checkpoint(phase){runtime.check(phase);store.checkStorage(phase);}
preservingFailure(store,runtime,()=>context,()=>{
 const raw=read('review/isolated-geometry-backtracking-20261006/results.json'),source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486'),partition=meshPartition(source),direction=raw.lineSearchEvents.find(e=>e.kind==='NEWTON_DIRECTION'&&e.label==='46-mode-response'&&e.iteration===13).scaledNodalIncrementM;
 assert.equal(digest(direction),protocol.terminalDirectionSha256);assert.deepEqual(raw.material,protocol.material);assert.ok(partition.held.every(n=>direction[n].every(x=>x===0)));assert.equal(source.nodes_m.length,585);assert.equal(source.elements_ten_node.length,252);assert.deepEqual(PATCH,source.elements_ten_node.flatMap((ids,i)=>ids.includes(92)?[i]:[]));
 const selected=protocol.states.map(s=>({id:s.id,row:raw.trace.find(r=>r.label===s.label&&r.iteration===s.iteration)})),before=digest({states:selected.map(s=>s.row.fullNodalAudit.positionsM),direction,material:raw.material}),states=selected.map((s,i)=>checkedFixedState(source,s.row.fullNodalAudit.positionsM,protocol.states[i].positionsSha256,(positions,certificate)=>({...s,positions,certificate})));
 store.json('execution-start.json',{schema:1,invocation:1,sourceCommit:head,preflightSourceCommit:preflight.sourceCommit,preflightSha256:hash('review/fixed-field-integration-runtime-20261007/runtime-preflight.json'),sourceHashes,startedUTC:new Date().toISOString(),authorization:manifest.authorization,command:process.argv,material:raw.material,states:states.map(s=>({id:s.id,positionsSha256:digest(s.positions),certificate:s.certificate})),terminalDirectionSha256:digest(direction),runtime:runtime.receipt()});
 store.json('saved-arrays.json',{positionsM:Object.fromEntries(states.map(s=>[s.id,s.positions])),terminalDirectionM:direction,freeNodeOrder:partition.free,heldNodeOrder:partition.held,patchElements:PATCH});
 const base={},basePatch={},stageResults=Object.fromEntries(states.map(s=>[s.id,{}]));let maximumStressReconstructionError=0;
 const material=(F,f)=>{const r=stressComponents(F,f,1,raw.material);maximumStressReconstructionError=Math.max(maximumStressReconstructionError,r.stressReconstructionMaximumErrorPa);return r;};
 for(const recipe of RECIPES){
  checkpoint('before-recipe-'+recipe.id);const points=[...rule(recipe)],packed=Buffer.alloc(points.length*40);points.forEach((p,i)=>[...p.L,p.weight].forEach((v,k)=>packed.writeDoubleLE(v,i*40+k*8)));store.write(recipe.id+'-normalized-points.f64le',packed);
  const elements=recipe.id==='U3'?source.elements_ten_node.map((_,i)=>i):PATCH;
  for(const [stateIndex,state] of states.entries()){
   const assembly=emptyAssembly(585),localRecords=[],originalPatch=emptyAssembly(585);context={stage:recipe.id,state:state.id,completedElements:[],partialElement:null,partialNodal:assembly.nodal,partialEnergiesJ:assembly.energiesJ};
   for(const element of elements){
    checkpoint('before-element');let e;
    try{e=assembleElement({source,element,positions:state.positions,points,limits:runtime,materialCallback:material,onProgress:p=>{context.partialElement=p;if(p.completedPoints%4096===0)store.checkStorage('during-batch');}});}catch(error){if(error.partialElement){context.partialElement=error.partialElement;context.partialPhysicalWeightsSha256=createHash('sha256').update(error.partialPhysicalWeights).digest('hex');try{store.write(`${recipe.id}-${state.id}-element-${element}-partial-weights.f64le`,error.partialPhysicalWeights);}catch(writeError){context.partialWeightWriteError=writeError.message;}}throw error;}
    const weightName=`${recipe.id}-element-${element}-reference-weights.f64le`;
    if(stateIndex===0)store.write(weightName,e.physicalWeights);else assert.equal(createHash('sha256').update(e.physicalWeights).digest('hex'),store.files[weightName].sha256,'Reference weights changed across fixed states');
    scatter(source,e,assembly);if(recipe.id==='U3'&&PATCH.includes(element))scatter(source,e,originalPatch);const {physicalWeights,...local}=e;const localName=`${recipe.id}-${state.id}-element-${element}-local.json`;store.json(localName,local);localRecords.push(localName);context.completedElements.push(element);context.partialElement=null;checkpoint('after-element-output');
   }
   assert.equal(localRecords.length,elements.length);let hybrid;
   if(recipe.id==='U3'){
    base[state.id]=assembly;basePatch[state.id]=originalPatch;hybrid=assembly;
    const expected=state.row.fullNodalAudit,free=partition.free.flatMap(n=>hybrid.nodal.total[n]);assert.ok(Math.max(...free.map((x,k)=>Math.abs(x-expected.fullFreeGradientN[k])))<=1e-8,'U3 full-free replay');for(const t of TERMS)assert.ok(Math.abs(hybrid.energiesJ[t]-expected.energiesJ[t])<=1e-9,'U3 component energy replay');
   }else{
    hybrid={nodal:replacePatch(source,PATCH,base[state.id].nodal,basePatch[state.id].nodal,assembly.nodal),energiesJ:Object.fromEntries(ALL_TERMS.map(t=>[t,base[state.id].energiesJ[t]-basePatch[state.id].energiesJ[t]+assembly.energiesJ[t]]))};
   }
   const reconstruction=componentSumCheck(hybrid),derivatives=Object.fromEntries(ALL_TERMS.map(t=>[t,hybrid.nodal[t].reduce((sum,X,n)=>sum+X.reduce((s,x,d)=>s+x*direction[n][d],0),0)])),record={state:state.id,recipe,elementOrder:elements,localElements:localRecords,hybridNodalGradientsN:hybrid.nodal,hybridEnergiesJ:hybrid.energiesJ,patchNodalGradientsN:recipe.id==='U3'?originalPatch.nodal:assembly.nodal,patchEnergiesJ:recipe.id==='U3'?originalPatch.energiesJ:assembly.energiesJ,terminalDirectionalDerivativesJ:derivatives,reconstruction,runtime:runtime.receipt()};
   store.json(`${recipe.id}-${state.id}-assembly.json`,record);stageResults[state.id][recipe.id]=hybrid;checkpoint('after-state-stage-output');console.log(JSON.stringify({stage:recipe.id,state:state.id,actual:runtime.actual,reserved:runtime.reserved,elapsedSeconds:runtime.receipt().elapsedMs/1000}));
  }
 }
 const comparisons=[];for(const state of states)for(const [a,b] of [['U3','U4'],...COMPARISONS]){
  const required=a!=='U3',A=stageResults[state.id][a],B=stageResults[state.id][b],terms={};for(const t of ALL_TERMS){const delta=B.nodal[t].map((X,n)=>X.map((x,d)=>x-A.nodal[t][n][d])),metrics=compareVectors(A.nodal[t],B.nodal[t],direction);let maxNode=0,maxD=0;for(let n=0;n<585;n++)for(let d=0;d<3;d++)if(Math.abs(delta[n][d])>Math.abs(delta[maxNode][maxD])){maxNode=n;maxD=d;}terms[t]={...metrics,differenceVectorN:delta,maximumEntry:{node:maxNode,component:maxD},maximumFreeDifferenceN:Math.max(...partition.free.flatMap(n=>delta[n].map(Math.abs))),maximumHeldDifferenceN:Math.max(...partition.held.flatMap(n=>delta[n].map(Math.abs))),energyDifferenceJ:B.energiesJ[t]-A.energiesJ[t]};}comparisons.push({state:state.id,a,b,required,terms,pass:ALL_TERMS.every(t=>terms[t].pass)});
 }
 assert.equal(before,digest({states:selected.map(s=>s.row.fullNodalAudit.positionsM),direction,material:raw.material}),'State or parameters mutated');for(const [p,h] of Object.entries(sourceHashes))assert.equal(hash(p),h,p);
 store.json('full-vector-comparisons.json',{comparisons});runtime.finish();checkpoint('before-completion-record');
 const result=comparisons.filter(c=>c.required).every(c=>c.pass)?'PASS_BOUNDED_FIXED_PATCH_AGREEMENT':'UNRESOLVED_FIXED_PATCH_INTEGRATION';
 store.json('completion-receipt.json',{schema:1,result,sourceCommit:head,sourceHashes,preflightSourceCommit:preflight.sourceCommit,completedUTC:new Date().toISOString(),runtime:runtime.receipt(),storageBytesBeforeReceipt:store.bytes,outputInventory:store.files,maximumStressReconstructionErrorPa:maximumStressReconstructionError,unchangedStates:true,newNodalFields:0,nonlinearSolves:0,optimizerTrials:0,refits:0,failedComparisons:comparisons.filter(c=>c.required&&!c.pass).map(c=>({state:c.state,a:c.a,b:c.b,failedTerms:ALL_TERMS.filter(t=>!c.terms[t].pass)})),scope:'Bounded fixed PATCH agreement only; 236 unchanged elements, global integration, equilibrium, displacement and anatomy remain unqualified',authority:'An incomplete-receipt.json overrides any provisional completion record; final post-write resource check is mandatory.',oldIndependentReviewLimits:'Full previous raw and55 additional certificates not independently replayed; no expansion of that scope.'});
 runtime.finish();checkpoint('after-final-completion-write');console.log(JSON.stringify({result,actualConstitutiveCallbacks:runtime.actual,completedCallbacks:runtime.completed,reserved:runtime.reserved,elapsedSeconds:runtime.receipt().elapsedMs/1000,storageBytes:store.bytes,sourceCommit:head}));
});
