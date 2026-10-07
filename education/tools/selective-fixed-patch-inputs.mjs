/** Immutable retained inputs and whole-field/hybrid reconstruction, no law calls. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {hashBytes} from './element247-shell-runtime.mjs';
import {emptyAssembly,scatter,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {replacePatch,assertPatch,digest} from './fixed-field-integration-protocol.mjs';
import {PATCH,ALL_TERMS,STATES,CORNERS,QUIET,SECONDARY,RECON,validateLocal,candidateRule,compareUnits} from './selective-fixed-patch-protocol.mjs';
export const ROOT=fileURLToPath(new URL('../',import.meta.url)),MANIFEST='research/selective-fixed-patch-20261007-inputs.json',PREF='review/selective-fixed-patch-preflight-20261007/',RUN='review/selective-fixed-patch-run-20261007',AUTH='research/selective-fixed-patch-authorization-20261007.json';
export const OLD='review/fixed-field-integration-run-20261007/',SHELL='review/element247-shell-run-20261007/material/',FAILED='review/element247-two-shell-run-20261007/material/';
export const bytes=p=>fs.readFileSync(ROOT+p),read=p=>JSON.parse(bytes(p)),hash=p=>hashBytes(bytes(p));
export function loadInputs(){
 const m=read(MANIFEST);for(const [p,h] of Object.entries(m.inputs))assert.equal(hash(p),h,p);
 const arrays=read(OLD+'saved-arrays.json'),source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486');assertPatch(source,arrays.patchElements);
 assert.equal(source.nodes_m.length,585);assert.equal(source.elements_ten_node.length,252);assert.equal(arrays.freeNodeOrder.length,495);assert.equal(arrays.heldNodeOrder.length,90);
 assert.deepEqual([...arrays.freeNodeOrder,...arrays.heldNodeOrder].sort((a,b)=>a-b),Array.from({length:585},(_,i)=>i));
 assert.equal(digest(arrays.terminalDirectionM),m.terminalDirectionSha256);assert.ok(arrays.heldNodeOrder.every(n=>arrays.terminalDirectionM[n].every(x=>x===0)));
 for(const state of m.states)assert.equal(digest(arrays.positionsM[state.id]),state.positionsSha256);
 for(const [e,c] of Object.entries(CORNERS))assert.equal(source.elements_ten_node[Number(e)][c],92);
 assert.deepEqual(m.material,read('research/fixed-field-integration-protocol-20261007-inputs.json').material);
 return {manifest:m,source,arrays};
}
function assertAssembly(a,b){let force=0,energy=0;for(const t of ALL_TERMS){energy=Math.max(energy,Math.abs(a.energiesJ[t]-b.energiesJ[t]));assert.equal(b.nodal[t].length,585);for(let n=0;n<585;n++)for(let d=0;d<3;d++)force=Math.max(force,Math.abs(a.nodal[t][n][d]-b.nodal[t][n][d]));}assert.ok(force<=RECON.forceN&&energy<=RECON.energyJ);return {maximumForceDifferenceN:force,maximumEnergyDifferenceJ:energy,all585Nodes:true};}
export function baselineFor(source,state){
 const saved=read(OLD+`U3-${state}-assembly.json`),baseline=emptyAssembly(585),oldPatch=emptyAssembly(585);assert.deepEqual(saved.elementOrder,Array.from({length:252},(_,i)=>i));assert.equal(saved.localElements.length,252);
 for(let e=0;e<252;e++){const name=`U3-${state}-element-${e}-local.json`;assert.equal(saved.localElements[e],name);const row=read(OLD+name);validateLocal(row,e);assert.equal(row.pointCount,2048);scatter(source,row,baseline);if(PATCH.includes(e))scatter(source,row,oldPatch);}
 const reconstruction=assertAssembly(baseline,{nodal:saved.hybridNodalGradientsN,energiesJ:saved.hybridEnergiesJ});componentSumCheck(baseline);componentSumCheck(oldPatch);return {baseline,oldPatch,reconstruction,retainedBaselineFiles:252,outsidePatchElements:236};
}
export function retainedRow(state,e,id){const row=read(OLD+`${id}-${state}-element-${e}-local.json`);validateLocal(row,e);return row;}
export function retained247(state){const stage=read(SHELL+`A55-${state}-assembly.json`);const rows=Array.from({length:21},(_,i)=>read(SHELL+`A55-${state}-${i===20?'core':'s'+(i+1)}-shell.json`));assert.deepEqual(rows.map(x=>x.shell),stage.originalShells);stage.minimumSampleJ=Math.min(...rows.map(x=>x.minimumSampleJ));validateLocal(stage,247);return stage;}
export function assembleCandidate(source,state,q,stages,base){
 const rows=PATCH.map(e=>{const id=candidateRule(q,e);return e===247&&q==='Q0'?retained247(state):stages[`${e}-${id}`]??retainedRow(state,e,id);});assert.deepEqual(rows.map(x=>x.element),PATCH);
 const patch=emptyAssembly(585);for(const row of rows){validateLocal(row,row.element);scatter(source,row,patch);}componentSumCheck(patch);
 const hybrid=replacePatch(source,PATCH,base.baseline.nodal,base.oldPatch.nodal,patch.nodal),energiesJ=Object.fromEntries(ALL_TERMS.map(t=>[t,base.baseline.energiesJ[t]-base.oldPatch.energiesJ[t]+patch.energiesJ[t]]));componentSumCheck({nodal:hybrid,energiesJ});
 return {state,candidate:q,elementOrder:PATCH,localElements:rows.map(({element,pointCount,minimumSampleJ,localGradientsN,energiesJ})=>({element,pointCount,minimumSampleJ,localGradientsN,energiesJ})),baselineNodalGradientsN:base.baseline.nodal,hybridNodalGradientsN:hybrid,patchNodalGradientsN:patch.nodal,hybridEnergiesJ:energiesJ,patchEnergiesJ:patch.energiesJ,reconstruction:base.reconstruction,outsidePatchElements:236,outsidePatchQualified:false};
}
export function candidateComparison(source,state,a,b,candidates,stages,direction){
 const A=candidates[a],B=candidates[b],units=[];
 for(const e of PATCH){const shellResolved=e===247||(a==='Q0'&&b==='Q1'&&SECONDARY.includes(e));
 if(shellResolved){const get=q=>e===247&&q==='Q0'?retained247(state):stages[`${e}-${candidateRule(q,e)}`];const ar=get(a).comparisonShells,br=get(b).comparisonShells;assert.deepEqual(ar.map(x=>x.shell),br.map(x=>x.shell));assert.equal(ar.length,21);for(let i=0;i<21;i++)units.push({id:`${e}-${ar[i].shell}`,a:{...ar[i],element:e},b:{...br[i],element:e}});}
 else units.push({id:`${e}-whole`,a:A.localElements.find(x=>x.element===e),b:B.localElements.find(x=>x.element===e)});
 }
 const result=compareUnits(source,units,direction,a==='Q0'&&b==='Q1'?156:36);
 for(const t of ALL_TERMS)for(let n=0;n<585;n++)for(let d=0;d<3;d++)assert.ok(Math.abs(result.terms[t].aggregateDifferenceN[n][d]-(A.hybridNodalGradientsN[t][n][d]-B.hybridNodalGradientsN[t][n][d]))<=RECON.forceN,'Comparison/full hybrid reconstruction');
 return {state,a,b,...result,required:!(a==='Q0'&&b==='Q2')};
}
export function radialComparison(source,state,stages,direction){const A=stages['247-F44'],B=stages['247-R44'];return {state,a:'F44',b:'R44',required:true,scope:'Isolated247 radial comparison; other15 cancel by construction without qualification',...compareUnits(source,A.comparisonShells.map((a,i)=>({id:`247-${a.shell}`,a:{...a,element:247},b:{...B.comparisonShells[i],element:247}})),direction,21)};}
