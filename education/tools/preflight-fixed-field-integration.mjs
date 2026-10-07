/** Hash/geometry/quadrature/accounting preflight. NO constitutive assembly. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {execFileSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {PATCH,RECIPES,COMPARISONS,GAUSS,digest,inventory,schedule,assertPatch,checkedFixedState} from './fixed-field-integration-protocol.mjs';
import {meshPartition} from './isolated-displacement-family.mjs';
import {elementSegmentPolynomials} from './isolated-segment-geometry.mjs';
import {referencePoint} from './isolated-collapse-components.mjs';
import {furtherQuadrature} from './anatomical-integration-refinement.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
const manifestPath='research/fixed-field-integration-protocol-20261007-inputs.json',m=read(manifestPath),newSources=[manifestPath,'research/fixed-field-integration-protocol-20261007.md','tools/fixed-field-integration-protocol.mjs','tools/preflight-fixed-field-integration.mjs','tests/fixed_field_integration_protocol.test.mjs'];
const paths=[...Object.keys(m.inputs),...newSources];
for(const p of paths)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});
execFileSync('git',['diff','--exit-code','HEAD','--',...paths],{cwd:root,stdio:'pipe'});
for(const [p,h] of Object.entries(m.inputs))assert.equal(hash(p),h,p);
const raw=read('review/isolated-geometry-backtracking-20261006/results.json'),source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(x=>x.element_id==='FJ1486'),partition=meshPartition(source);
assert.equal(raw.result,'REFUSED_BOUNDED_RESPONSE');assert.equal(source.nodes_m.length,585);assert.equal(source.elements_ten_node.length,252);assert.equal(partition.held.length,90);assert.equal(partition.free.length,495);assertPatch(source,m.patchElements);assert.deepEqual(m.recipes,RECIPES);assert.deepEqual(m.requiredComparisons,COMPARISONS);assert.deepEqual(m.gaussBinary64,GAUSS);
assert.deepEqual(m.budget,{maximumMaterialCalls:9000000,plannedMaterialCalls:8847360,maximumWallSeconds:900,nodeHeapMiB:6144,processRssGiB:8,maximumOutputMiB:256,invocations:1});
assert.equal(m.physicalForceGateN,1e-4);assert.equal(m.integrationForceGateN,1e-5);assert.equal(m.geometryGateJ,1e-6);assert.equal(m.referenceJacobianGate,1e-15);assert.equal(m.body,'FJ1486');assert.equal(m.activation,1);assert.equal(m.executionAuthorized,false);
assert.deepEqual(m.material,raw.material);const fit=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json').records.find(r=>r.elementId==='FJ1486');assert.equal(raw.material.sigma0,fit.match.sigma0Pa);
const config=read('data/anatomical-arm-v1/config/materials.json');for(const [k,v] of Object.entries(raw.material))if(k!=='sigma0')assert.equal(v,config.parameters[k].value);
const states=[raw.trace.find(x=>x.label==='45-mode-control'&&x.iteration===1),raw.trace.find(x=>x.label==='46-mode-response'&&x.iteration===13)],direction=raw.lineSearchEvents.find(x=>x.kind==='NEWTON_DIRECTION'&&x.label==='46-mode-response'&&x.iteration===13).scaledNodalIncrementM;
assert.equal(digest(direction),m.terminalDirectionSha256);assert.equal(direction.length,585);assert.ok(direction.every(X=>X.length===3&&X.every(Number.isFinite)));assert.ok(partition.held.every(n=>direction[n].every(x=>x===0)));
const l1=direction.flat().reduce((a,b)=>a+Math.abs(b),0);assert.equal(l1,m.terminalDirectionL1M);assert.equal(l1*1e-5,m.integrationDerivativeGateJ);
const before=digest({positions:states.map(s=>s.fullNodalAudit.positionsM),direction,material:raw.material,reference:source.nodes_m,connectivity:source.elements_ten_node});
assert.deepEqual(m.states.map(s=>[s.id,s.label,s.iteration]),[['control45','45-mode-control',1],['terminal46','46-mode-response',13]]);
const geometry=states.map((s,i)=>checkedFixedState(source,s.fullNodalAudit.positionsM,m.states[i].positionsSha256,(_,certificate)=>({id:m.states[i].id,label:s.label,iteration:s.iteration,positionsSha256:digest(s.fullNodalAudit.positionsM),certificate})));
assert.equal(geometry[0].iteration,1);assert.equal(geometry[1].iteration,13);
// All reference Bernstein coefficients exceed the existing absolute reference
// Jacobian gate, so all generated points lie in the certified reference domain.
let minimumReferenceCoefficient=Infinity;
for(const ids of source.elements_ten_node){const X=ids.map(n=>source.nodes_m[n]),p=elementSegmentPolynomials(X,X,X);for(const c of p.coefficients){const v=Number(c.referenceNumerator)/(p.denominatorFactor*2**p.denominatorPowerOfTwo);assert.ok(v>1e-15);minimumReferenceCoefficient=Math.min(minimumReferenceCoefficient,v);}}
assert.ok(source.reference_fibres.every(f=>f.length===3&&f.every(Number.isFinite)&&Math.abs(Math.hypot(...f)-1)<1e-10));
const ruleInventories=RECIPES.map(inventory),baseRule=furtherQuadrature();assert.equal(baseRule.length,2048);
const referencePatch=PATCH.map(element=>{let sum=0,min=Infinity;const weights=createHash('sha256');for(const p of baseRule){const q=referencePoint(source,element,p.L,p.weight);assert.ok(q.weightM3>0);sum+=q.weightM3;min=Math.min(min,q.referenceJacobian);const b=Buffer.alloc(8);b.writeDoubleLE(q.weightM3);weights.update(b);}return {element,referenceVolumeM3:sum,minimumSampleReferenceJacobian:min,baselinePhysicalWeightsFloat64LESha256:weights.digest('hex'),points:2048};});
const counts=schedule(252);assert.equal(counts.reduce((s,r)=>s+r.materialCalls,0),m.budget.plannedMaterialCalls);
assert.equal(before,digest({positions:states.map(s=>s.fullNodalAudit.positionsM),direction,material:raw.material,reference:source.nodes_m,connectivity:source.elements_ten_node}));
const afterHashes=Object.fromEntries(paths.map(p=>[p,hash(p)]));for(const [p,h] of Object.entries(m.inputs))assert.equal(afterHashes[p],h);
const output=root+'review/fixed-field-integration-protocol-20261007/';assert.ok(!fs.existsSync(output),'Preserve existing structural evidence');
const testCommand=['--test','tests/fixed_field_integration_protocol.test.mjs'],testOutput=execFileSync('node',testCommand,{cwd:root,encoding:'utf8',stdio:'pipe'});assert.match(testOutput,/pass 8/);assert.match(testOutput,/fail 0/);
for(const p of ['tools/fixed-field-integration-protocol.mjs','tools/preflight-fixed-field-integration.mjs'])execFileSync('node',['--check',p],{cwd:root,stdio:'pipe'});
fs.mkdirSync(output,{recursive:true});fs.writeFileSync(output+'tests.log',testOutput);
const result={schema:1,result:'PASS_STRUCTURAL_FIXED_FIELD_INTEGRATION_PREFLIGHT_NO_ASSEMBLY',sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),sourceHashes:afterHashes,node:process.version,constitutivePointCalls:0,newNodalFields:0,nonlinearSolves:0,optimizerTrials:0,refits:0,stateBeforeAfterSha256:before,unchangedState:true,executionAuthorized:false,states:geometry,terminalDirection:{sha256:digest(direction),serialization:'JSON.stringify(array), UTF-8',l1M:l1,integrationDerivativeGateJ:l1*1e-5},patch:{elements:PATCH,remainingElements:236,completeIncidentPatch:true,referencePatch,minimumWholeMeshReferenceBernsteinCoefficient:minimumReferenceCoefficient},ruleInventories,plannedSchedule:counts,budget:m.budget,criteria:{physicalForceGateN:1e-4,integrationForceGateN:1e-5,derivativeGateJ:l1*1e-5,allNodesIncludingHeld:true,allTermsAndIndependentTotal:true,requiredComparisons:COMPARISONS},tests:{command:'node '+testCommand.join(' '),pass:8,fail:0,logSha256:createHash('sha256').update(testOutput).digest('hex')},limitations:['No constitutive assembly executed or qualified','Only future bounded patch agreement; 236 unchanged elements cannot receive a global integration claim','Old full-raw and 55 additional certificate independent-review limits retained','No new material, displacement modes or calibration authorized']};
fs.writeFileSync(output+'structural-preflight.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({result:result.result,sourceCommit:result.sourceCommit,constitutivePointCalls:0,tests:result.tests,plannedCalls:8847360,derivativeGateJ:l1*1e-5}));
