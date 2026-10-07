/** Offline arithmetic only, from the failed run's retained complete vectors. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {buildConstructedStage,compareChangedShells} from '../../tools/element247-two-shell-protocol.mjs';
import {compareShellStages,hashBytes} from '../../tools/element247-shell-runtime.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),old='review/element247-shell-run-20261007/material/',current='review/element247-two-shell-run-20261007/material/';
const source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486'),arrays=read(current+'saved-arrays.json'),baseline=read(old+'A55-terminal46-assembly.json');
const originalNew=['s1','s2'].map(s=>read(current+`T24-terminal46-${s}-shell.json`));originalNew.forEach((r,i)=>{assert.equal(r.id,'s'+(i+1));assert.equal(r.shell,undefined);assert.equal(r.pointCount,2000);});
// The material run failed because its producer supplied id rather than shell.
// This explicit adapter is confined to offline analysis; raw files and the
// frozen producer are untouched, and no terminal completion is reconstructed.
const changed=originalNew.map(r=>({...r,shell:r.id})),rows=[...changed,...baseline.originalShells.slice(2).map(s=>read(current+`A55-terminal46-${s}-shell.json`))],stage=buildConstructedStage(source,rows,arrays.terminalDirectionM),comparison=compareChangedShells(['s1','s2'].map(s=>read(old+`A55-terminal46-${s}-shell.json`)),changed,arrays.terminalDirectionM,source.elements_ten_node[247]),whole=compareShellStages(baseline,stage,arrays.terminalDirectionM,source.elements_ten_node[247],5.492029235357012e-7);
const result={schema:1,result:'OFFLINE_RETAINED_VECTOR_ARITHMETIC_FROM_INCOMPLETE_RUN',sourceCommit:'97da4bdea7d0be11fc18222221b8b551b53a8e3b',specimenCalls:0,terminalCompletion:false,qualifiedRun:false,metadataAdapter:'For arithmetic only, set shell=id on two retained records; original files remain byte-exact.',changedShellComparison:comparison,constructedWholeValues:stage,constructedWholeComparison:{...whole,qualification:false,reusedTailAgreementIsByConstruction:true,scope:'Offline constructed values from partial evidence; no successful execution completion'},originalFailureN:8.611662232570753e-5,element247Qualification:false,patchQualification:false};
console.log(JSON.stringify(result,null,2));
