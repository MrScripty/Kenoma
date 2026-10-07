/** Synthetic callbacks and retained records only; zero specimen law calls. */
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import test from 'node:test';import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {changedRule,packPoints,buildConstructedStage,compareChangedShells,TWO_SHELL_BUDGET,SELECTIVE_RECIPE} from '../tools/element247-two-shell-protocol.mjs';
import {assembleChangedShells} from '../tools/element247-two-shell-runtime.mjs';
import {withChangedShellIdentity} from '../tools/element247-two-shell-schema.mjs';
import {RuntimeLimits,ShellEvidenceStore} from '../tools/element247-shell-runtime.mjs';
import {ALL_TERMS} from '../tools/fixed-field-integration-assembly.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),old='review/element247-shell-run-20261007/material/';
const source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486'),arrays=read(old+'saved-arrays.json'),direction=arrays.terminalDirectionM,ids=source.elements_ten_node[247];
const fixture=()=>{const runRoot=path.join(fs.mkdtempSync(path.join(os.tmpdir(),'kenoma-two-shell-fixture-')),'run');fs.mkdirSync(runRoot);return {store:new ShellEvidenceStore(runRoot),limits:new RuntimeLimits({plannedCalls:4000,maximumCalls:4000}),context:{state:'terminal46',completedShells:[],partialShell:null}};};
const synthetic=(bad=false)=>({actual:{J:1,P:Array(9).fill(bad?1:0),energy:Object.fromEntries(ALL_TERMS.slice(0,-1).map(t=>[t,0]))},stresses:Object.fromEntries(ALL_TERMS.slice(0,-1).map(t=>[t,Array(9).fill(0)]))});
test('exactly two fixed 2000-point rules and an exact 4000 budget',()=>{const p=[...changedRule()];assert.equal(p.length,4000);for(const s of ['s1','s2'])assert.equal(p.filter(x=>x.shell===s).length,2000);assert.ok(p.every(x=>x.weight>0&&x.L.every(v=>v>0&&v<1)));assert.equal(packPoints(p).length,192000);assert.deepEqual(SELECTIVE_RECIPE.faceOrder,[1,2,3]);assert.equal(TWO_SHELL_BUDGET.maximumMaterialCalls,4000);});
test('4000 synthetic callbacks complete once, with no callback on reused records',()=>{const f=fixture();let calls=0;const changed=assembleChangedShells({source,positions:arrays.positionsM.terminal46,direction,points:[...changedRule()],...f,materialCallback:()=>{calls++;return synthetic();}});f.limits.finish();assert.equal(calls,4000);assert.equal(f.limits.actual,4000);assert.equal(changed.rows.length,2);assert.equal(changed.physicalWeights.length,32000);});
test('nonzero synthetic producer records serialize and cross the actual constructor boundary',()=>{
 const f=fixture();let calls=0;
 // Explicit constants, not a specimen material law. Four nonzero components
 // sum to the independently provided total stress and energy density.
 const stress=[2,-1,3,4,1,-2,5,-3,6];
 const callback=()=>{calls++;return {actual:{J:1,P:stress.map(x=>10*x),energy:Object.fromEntries(ALL_TERMS.slice(0,-1).map((t,i)=>[t,7*(i+1)]))},stresses:Object.fromEntries(ALL_TERMS.slice(0,-1).map((t,i)=>[t,stress.map(x=>(i+1)*x)]))};};
 const changed=assembleChangedShells({source,positions:arrays.positionsM.terminal46,direction,points:[...changedRule()],...f,materialCallback:callback});f.limits.finish();assert.equal(calls,4000);
 const records=['s1','s2'].map(shell=>JSON.parse(fs.readFileSync(path.join(f.store.directory,`T24-terminal46-${shell}-shell.json`))));
 assert.deepEqual(records,changed.rows);records.forEach(r=>assert.equal(r.shell,r.id));
 assert.ok(records.every(r=>r.localGradientsN.total.flat().some(x=>x!==0)&&r.energiesJ.total>0));
 const tails=Array.from({length:19},(_,i)=>({element:247,shell:i===18?'core':`s${i+3}`,pointCount:500,localGradientsN:Object.fromEntries(ALL_TERMS.map(t=>[t,Array.from({length:10},()=>[0,0,0])])),energiesJ:Object.fromEntries(ALL_TERMS.map(t=>[t,0]))}));
 const rows=[...records,...tails],before=JSON.stringify(rows),stage=buildConstructedStage(source,rows,direction);
 assert.equal(JSON.stringify(rows),before);assert.equal(stage.pointCount,13500);assert.equal(stage.evaluatedPoints,4000);assert.equal(stage.reusedPoints,9500);
 for(const t of ALL_TERMS){
  assert.equal(stage.energiesJ[t],records[0].energiesJ[t]+records[1].energiesJ[t]);
  const expected=Array.from({length:585},()=>[0,0,0]);ids.forEach((n,i)=>{expected[n]=records[0].localGradientsN[t][i].map((x,d)=>x+records[1].localGradientsN[t][i][d]);});
  assert.deepEqual(stage.nodalGradientsN[t],expected);
 }
 // The exact former failure is caught at this boundary, even with nonzero data.
 const damaged=structuredClone(rows);delete damaged[0].shell;assert.throws(()=>buildConstructedStage(source,damaged,direction));
 const record=structuredClone(records[0]);delete record.shell;const snapshot=JSON.stringify(record);assert.deepEqual(withChangedShellIdentity(record),records[0]);assert.equal(JSON.stringify(record),snapshot);
 assert.throws(()=>withChangedShellIdentity({...record,shell:'s2'}),/CONFLICTING/);
 assert.throws(()=>withChangedShellIdentity({...record,comparisonShell:'s2'}),/COMPARISON/);
 assert.equal(stage.qualification,false);
});
test('complete synthetic reconstruction failure retains full current-shell weights',()=>{const f=fixture();assert.throws(()=>assembleChangedShells({source,positions:arrays.positionsM.terminal46,direction,points:[...changedRule()],...f,materialCallback:()=>synthetic(true)}),/Component reconstruction/);assert.equal(f.limits.actual,2000);assert.equal(f.context.partialShell.completedPoints,2000);assert.equal(f.context.physicalWeightEvidenceComplete,true);assert.equal(fs.statSync(path.join(f.store.directory,f.context.retainedWeightFile)).size,16000);});
test('truncated normal weight bytes are preserved alongside verified full emergency bytes',()=>{const f=fixture(),original=f.store.write.bind(f.store);f.store.write=(name,data,options)=>{if(name==='T24-terminal46-s1-weights.f64le'){fs.writeFileSync(path.join(f.store.directory,name),data.subarray(0,13));throw Error('synthetic truncated write');}return original(name,data,options);};assert.throws(()=>assembleChangedShells({source,positions:arrays.positionsM.terminal46,direction,points:[...changedRule()],...f,materialCallback:()=>synthetic()}),/truncated/);assert.equal(fs.statSync(path.join(f.store.directory,'T24-terminal46-s1-weights.f64le')).size,13);assert.equal(f.context.physicalWeightEvidenceComplete,true);assert.equal(fs.statSync(path.join(f.store.directory,f.context.retainedWeightFile)).size,16000);});
test('retained-data constructed values preserve all585 nodes and independent total',()=>{const rows=Array.from({length:21},(_,i)=>read(old+`A55-terminal46-${i===20?'core':'s'+(i+1)}-shell.json`));rows[0].pointCount=rows[1].pointCount=2000;const before=JSON.stringify(rows),stage=buildConstructedStage(source,rows,direction),baseline=read(old+'A55-terminal46-assembly.json');assert.deepEqual(stage.nodalGradientsN,baseline.nodalGradientsN);assert.deepEqual(stage.energiesJ,baseline.energiesJ);assert.equal(JSON.stringify(rows),before);assert.equal(stage.reusedPoints,9500);assert.equal(stage.qualification,false);});
test('changed-only comparison retains nonzero signed vectors without invented tail evidence',()=>{const oldRows=['s1','s2'].map(s=>read(old+`A55-terminal46-${s}-shell.json`)),newRows=structuredClone(oldRows);newRows[0].localGradientsN.volume[9][1]+=2e-5;newRows[0].localGradientsN.total[9][1]+=2e-5;const c=compareChangedShells(oldRows,newRows,direction,ids);assert.equal(c.pass,false);assert.equal(c.terms.total.differences.length,2);assert.ok(c.terms.total.shellTriangleInfinityN>1e-5);assert.equal(c.terms.total.scatteredDifferenceN[575][1],c.terms.total.aggregateDifferenceN[9][1]);assert.equal(c.qualification,false);});
