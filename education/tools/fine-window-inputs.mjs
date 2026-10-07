/** Immutable value/geometry reuse and all16 candidate arithmetic; zero law evaluation. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {hashBytes} from './element247-shell-runtime.mjs';
import {digest,replacePatch} from './fixed-field-integration-protocol.mjs';
import {emptyAssembly,scatter,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {baselineFor} from './selective-fixed-patch-inputs.mjs';
import {PATCH,QUIET,FOCUS,STATES,ALL_TERMS,RECON,candidateRule,compareUnits,applyAllocation,regionPointCount} from './fine-window-protocol.mjs';
export {baselineFor};
export const ROOT=fileURLToPath(new URL('../',import.meta.url)),MANIFEST='research/fine-window-runner-20261007-inputs.json',PREF='review/fine-window-preflight-20261007/',AUTH='research/fine-window-authorization-20261007.json',RUN='review/fine-window-run-20261007',OLD='review/fixed-field-integration-run-20261007/',RAW='review/selective-fixed-patch-run-20261007/material/',SHELL='review/element247-shell-run-20261007/material/';
export const read=p=>JSON.parse(fs.readFileSync(ROOT+p)),bytes=p=>fs.readFileSync(ROOT+p),hash=p=>hashBytes(bytes(p));
export function loadInputs(){
 const m=read(MANIFEST),accepted=read('research/selective-fine-window-schedule-20261007.json'),index=read('review/selective-fine-window-schedule-20261007/reuse-index.json');assert.equal(m.executionAuthorized,false);assert.equal(m.parentPreparationAccepted,true);
 for(const [p,v] of Object.entries(index.files)){assert.equal(hash(p.replace(/^education\//,'')),v.sha256,p);assert.equal(bytes(p.replace(/^education\//,'')).length,v.bytes);}
 for(const [p,h] of Object.entries(m.inputs))assert.equal(hash(p),h,p);
 const arrays=read(OLD+'saved-arrays.json'),source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486');assert.equal(source.nodes_m.length,585);assert.equal(source.elements_ten_node.length,252);assert.deepEqual(PATCH,source.elements_ten_node.flatMap((v,e)=>v.includes(92)?[e]:[]));assert.equal(arrays.freeNodeOrder.length,495);assert.equal(arrays.heldNodeOrder.length,90);assert.deepEqual([...arrays.freeNodeOrder,...arrays.heldNodeOrder].sort((a,b)=>a-b),Array.from({length:585},(_,i)=>i));assert.ok(arrays.heldNodeOrder.every(n=>arrays.terminalDirectionM[n].every(x=>x===0)));
 assert.equal(digest(arrays.terminalDirectionM),accepted.directionSha256);for(const state of accepted.states)assert.equal(digest(arrays.positionsM[state.id]),state.positionsSha256);assert.deepEqual(m.states,accepted.states);assert.deepEqual(m.material,accepted.material);
 return {manifest:m,accepted,index,source,arrays};
}
export function evaluationIdentity(m,state){return {positionsSha256:m.states.find(x=>x.id===state).positionsSha256,referenceSha256:m.inputs['data/anatomical-arm-v1/generated/arm-reference.json'],materialSha256:digest(m.material),lawModulesSha256:digest(m.immutableModuleHashes),activation:1};}
export function retainedStage(state,e,id){
 if(QUIET.includes(e))return read(OLD+`${id}-${state}-element-${e}-local.json`);
 if(e===247&&id==='A55'){const stage=read(SHELL+`A55-${state}-assembly.json`);return {...stage,minimumSampleJ:Math.min(...Array.from({length:21},(_,i)=>read(SHELL+`A55-${state}-${i===20?'core':'s'+(i+1)}-shell.json`).minimumSampleJ))};}
 return read(RAW+`${state}-${e}-${id}-stage.json`);
}
export function assembleCandidate(source,state,q,stages,base){
 const rows=PATCH.map(e=>{const id=candidateRule(q,e);return stages[`${state}-${e}-${id}`]??retainedStage(state,e,id);});assert.deepEqual(rows.map(x=>x.element),PATCH);const patch=emptyAssembly(585);for(const row of rows)scatter(source,row,patch);componentSumCheck(patch);
 const hybrid=replacePatch(source,PATCH,base.baseline.nodal,base.oldPatch.nodal,patch.nodal),energiesJ=Object.fromEntries(ALL_TERMS.map(t=>[t,base.baseline.energiesJ[t]-base.oldPatch.energiesJ[t]+patch.energiesJ[t]]));componentSumCheck({nodal:hybrid,energiesJ});
 return {state,candidate:q,elementOrder:PATCH,localElements:rows.map(({element,pointCount,minimumSampleJ,localGradientsN,energiesJ})=>({element,pointCount,minimumSampleJ,localGradientsN,energiesJ})),baselineNodalGradientsN:base.baseline.nodal,hybridNodalGradientsN:hybrid,patchNodalGradientsN:patch.nodal,hybridEnergiesJ:energiesJ,patchEnergiesJ:patch.energiesJ,reconstruction:base.reconstruction,outsidePatchElements:236,outsidePatchQualified:false};
}
export function candidateUnits(state,a,b,stages){
 const units=[];for(const e of PATCH){const get=q=>{const id=candidateRule(q,e);return stages[`${state}-${e}-${id}`]??retainedStage(state,e,id);},A=get(a),B=get(b);
  if(QUIET.includes(e))units.push({id:`${e}-whole`,a:A,b:B});else{assert.deepEqual(A.comparisonShells.map(x=>x.shell),B.comparisonShells.map(x=>x.shell));assert.equal(A.comparisonShells.length,21);for(let i=0;i<21;i++)units.push({id:`${e}-${A.comparisonShells[i].shell}`,a:{...A.comparisonShells[i],element:e},b:{...B.comparisonShells[i],element:e}});}
 }assert.equal(units.length,156);return units;
}
export function candidateComparison(source,state,a,b,candidates,stages,direction,required){
 const units=candidateUnits(state,a,b,stages),c=applyAllocation(compareUnits(source,units,direction,156),source,units,direction,a,b);for(const t of ALL_TERMS)for(let n=0;n<585;n++)for(let d=0;d<3;d++)assert.ok(Math.abs(c.terms[t].aggregateDifferenceN[n][d]-(candidates[a].hybridNodalGradientsN[t][n][d]-candidates[b].hybridNodalGradientsN[t][n][d]))<=RECON.forceN);
 const whole=PATCH.map(e=>({id:`${e}-whole`,a:candidates[a].localElements.find(x=>x.element===e),b:candidates[b].localElements.find(x=>x.element===e)})),diagnostic=compareUnits(source,whole,direction,16);return {state,a,b,required,...c,common16Diagnostic:Object.fromEntries(ALL_TERMS.map(t=>{const x=diagnostic.terms[t];return [t,{signedN:x.aggregateInfinityN,triangleN:x.unitTriangleInfinityN,signedWorkJ:x.aggregateDirectionalDifferenceJ,triangleWorkJ:x.unitTriangleDirectionalDifferenceJ}];})),quietIdenticalReuseEarnsNoRefinementCredit:!(a==='I0'&&b==='I1')&&!(a==='S2'&&b==='I1')};
}
export function quietComparison(source,state,a,b,direction){
 const units=QUIET.map(e=>({id:`${e}-whole`,a:retainedStage(state,e,a),b:retainedStage(state,e,b)})),c=compareUnits(source,units,direction,9),fraction=a==='U4'?.85:.2;
 for(const t of ALL_TERMS){const x=c.terms[t];x.allocatedPass=x.aggregateInfinityN<=fraction*1e-5&&x.unitTriangleInfinityN<=fraction*1e-5&&x.aggregateDirectionalDifferenceJ<=fraction*5.492029235357012e-7&&x.unitTriangleDirectionalDifferenceJ<=fraction*5.492029235357012e-7;}
 return {state,a,b,required:true,scope:'Previously measured quiet9 independent witness; not new material calls',allocatedForceN:fraction*1e-5,allocatedWorkJ:fraction*5.492029235357012e-7,...c,globalPass:c.pass,pass:c.pass&&ALL_TERMS.every(t=>c.terms[t].allocatedPass)};
}
