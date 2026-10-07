/** Freeze/hash/geometry/coverage/moment checks and retained-data arithmetic.
 * No stress evaluation, constitutive callback, optimizer or new nodal state. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {execFileSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {ELEMENT,SHELL_RECIPES,REQUIRED_SHELL_COMPARISONS,SHELL_BUDGET,shells,shellRule,assertMoments,exactReferenceMoment,rationalNumber,monomials,monomial} from './element247-shell-protocol.mjs';
import {PATCH,TERMS,digest,assertPatch,checkedFixedState} from './fixed-field-integration-protocol.mjs';
import {elementSegmentPolynomials} from './isolated-segment-geometry.mjs';
import {referencePoint,tensor} from './isolated-collapse-components.mjs';
import {determinant} from '../web/anatomical-material.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),sha=b=>createHash('sha256').update(b).digest('hex'),hash=p=>sha(fs.readFileSync(root+p));
const manifestPath='research/element247-shell-protocol-20261007-inputs.json',m=read(manifestPath),paths=[...Object.keys(m.inputs),...m.newSources];
for(const p of paths)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});
execFileSync('git',['diff','--exit-code','HEAD','--',...paths],{cwd:root,stdio:'pipe'});
for(const [p,h] of Object.entries(m.inputs))assert.equal(hash(p),h,p);
assert.equal(m.baseCommit,'74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b');assert.equal(m.executionAuthorized,false);assert.equal(m.materialAssemblyAuthorized,false);assert.equal(m.element,ELEMENT);assert.deepEqual(m.recipes,SHELL_RECIPES);assert.deepEqual(m.requiredComparisons,REQUIRED_SHELL_COMPARISONS);assert.deepEqual(m.proposedFutureBudget,SHELL_BUDGET);assert.equal(m.integrationForceGateN,1e-5);assert.equal(m.integrationDerivativeGateJ,5.492029235357012e-7);assert.equal(m.physicalForceGateN,1e-4);assert.equal(m.geometryGateJ,1e-6);assert.equal(m.referenceJacobianGate,1e-15);assert.equal(m.patchQualificationAuthorized,false);
const outputArgs=process.argv.slice(2);assert.ok(outputArgs.length===0||(outputArgs.length===2&&outputArgs[0]==='--output'),'Use --output fresh-directory only');
const output=outputArgs.length?path.resolve(outputArgs[1]):root+'review/element247-shell-protocol-20261007';assert.equal(fs.existsSync(output),false,'Preserve existing evidence; choose a fresh output directory');
const arrays=read('review/fixed-field-integration-run-20261007/saved-arrays.json'),source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(x=>x.element_id==='FJ1486'),prior=read('review/fixed-field-integration-run-20261007/completion-receipt.json');
assert.equal(prior.result,'UNRESOLVED_FIXED_PATCH_INTEGRATION');assertPatch(source,arrays.patchElements);assert.deepEqual(m.patchElements,PATCH);assert.deepEqual(m.secondaryElements,[197,200,203,206,246,248]);assert.equal(source.nodes_m.length,585);assert.equal(source.elements_ten_node.length,252);assert.equal(source.elements_ten_node[ELEMENT][0],92);
assert.equal(digest(arrays.terminalDirectionM),m.terminalDirectionSha256);const l1=arrays.terminalDirectionM.flat().reduce((s,x)=>s+Math.abs(x),0);assert.equal(l1*1e-5,m.integrationDerivativeGateJ);assert.ok(arrays.heldNodeOrder.every(n=>arrays.terminalDirectionM[n].every(x=>x===0)));
const before=digest({positions:arrays.positionsM,direction:arrays.terminalDirectionM,reference:source.nodes_m,elements:source.elements_ten_node});
const geometry=m.states.map(s=>checkedFixedState(source,arrays.positionsM[s.id],s.positionsSha256,(_,certificate)=>({id:s.id,positionsSha256:s.positionsSha256,certificate})));
const ids=source.elements_ten_node[ELEMENT],X=ids.map(n=>source.nodes_m[n]),poly=elementSegmentPolynomials(X,X,X),minimumReferenceCoefficient=Math.min(...poly.coefficients.map(c=>Number(c.referenceNumerator)/(poly.denominatorFactor*2**poly.denominatorPowerOfTwo)));
assert.ok(minimumReferenceCoefficient>1e-15);const exactVolume=rationalNumber(exactReferenceMoment(poly,[0,0,0,0],0,1));
const sourceHashes=Object.fromEntries(paths.map(p=>[p,hash(p)]));fs.mkdirSync(output,{recursive:true});
const inventories=[],pointArtifacts=[];
for(const recipe of SHELL_RECIPES){
 const points=[...shellRule(recipe)];assert.equal(points.length,recipe.points);const binary=Buffer.alloc(points.length*48),physical=Buffer.alloc(points.length*8),q=points.map((p,i)=>{const ref=referencePoint(source,ELEMENT,p.L,p.weight);[...p.L,p.weight,p.r].forEach((v,d)=>binary.writeDoubleLE(v,48*i+8*d));physical.writeDoubleLE(ref.weightM3,8*i);return ref;});
 const perShell=[];let first=0,minimumPhysicalWeight=Infinity,maximumReferenceMomentRelativeError=0;
 const ranges=Object.fromEntries(m.states.map(s=>[s.id,{minimumSampleJ:Infinity,maximumSampleJ:-Infinity}]));
 for(let i=0;i<points.length;i++){
  assert.ok(q[i].weightM3>0&&Number.isFinite(q[i].weightM3));minimumPhysicalWeight=Math.min(minimumPhysicalWeight,q[i].weightM3);
  for(const s of m.states){const J=determinant(tensor(ids.map(n=>arrays.positionsM[s.id][n]),q[i].gradient));assert.ok(J>1e-6&&Number.isFinite(J),'Unchanged sample domain guard');ranges[s.id].minimumSampleJ=Math.min(ranges[s.id].minimumSampleJ,J);ranges[s.id].maximumSampleJ=Math.max(ranges[s.id].maximumSampleJ,J);}
 }
 for(const s of shells(recipe.depth)){
  const count=points.filter(p=>p.shell===s.id).length,ps=points.slice(first,first+count),qs=q.slice(first,first+count);assert.ok(ps.every(p=>p.shell===s.id));
  const normalized=assertMoments(ps,s);let relative=0;const physicalMoments=[];
  for(const alpha of monomials(2)){
   const expected=rationalNumber(exactReferenceMoment(poly,alpha,s.lo,s.hi)),actual=qs.reduce((v,p,i)=>v+p.weightM3*monomial(ps[i].L,alpha),0),error=Math.abs(actual-expected)/expected;
   assert.ok(error<=2e-10,`Physical reference shell ${recipe.id}/${s.id}/${alpha}: ${error}`);relative=Math.max(relative,error);physicalMoments.push({alpha,expectedM3:expected,actualM3:actual,relativeError:error});
  }
  maximumReferenceMomentRelativeError=Math.max(maximumReferenceMomentRelativeError,relative);perShell.push({...s,firstPoint:first,points:count,comparisonShell:s.hi<=2**-20?'core':s.id,normalized,referenceMoments:physicalMoments});first+=count;
 }
 assert.equal(first,points.length);const volume=q.reduce((s,p)=>s+p.weightM3,0);assert.ok(Math.abs(volume-exactVolume)/exactVolume<2e-10);
 for(const [name,data] of [[`${recipe.id}-normalized-points.f64le`,binary],[`${recipe.id}-reference-weights.f64le`,physical]]){fs.writeFileSync(path.join(output,name),data,{flag:'wx'});pointArtifacts.push({name,bytes:data.length,sha256:sha(data)});}
 inventories.push({recipe,pointCount:points.length,perShell,referenceVolumeM3:volume,exactReferenceVolumeM3:exactVolume,minimumPhysicalWeightM3:minimumPhysicalWeight,maximumReferenceMomentRelativeError,minimumRadialCoordinate:Math.min(...points.map(p=>p.r)),domainRanges:ranges});
}
// Preserve the entire incident patch in a zero-evaluation localization. Removal
// of247 is arithmetic diagnosis only, never a permissible integration rule.
const localization=[];
for(const state of m.states.map(s=>s.id))for(const [a,b] of [['U4','U5'],['D4','D5'],['U5','D5']]){
 const A=read(`review/fixed-field-integration-run-20261007/${a}-${state}-assembly.json`),B=read(`review/fixed-field-integration-run-20261007/${b}-${state}-assembly.json`),termResults={};
 const locals=Object.fromEntries(PATCH.map(e=>[e,[read(`review/fixed-field-integration-run-20261007/${a}-${state}-element-${e}-local.json`),read(`review/fixed-field-integration-run-20261007/${b}-${state}-element-${e}-local.json`)]]));
 for(const term of [...TERMS,'total']){
  const full=A.hybridNodalGradientsN[term].map((v,i)=>v.map((x,d)=>x-B.hybridNodalGradientsN[term][i][d])),summed=Array.from({length:585},()=>[0,0,0]),byElement=[];
  for(const e of PATCH){const [la,lb]=locals[e],difference=la.localGradientsN[term].map((v,i)=>v.map((x,d)=>x-lb.localGradientsN[term][i][d]));let work=0;source.elements_ten_node[e].forEach((n,i)=>{for(let d=0;d<3;d++){summed[n][d]+=difference[i][d];work+=difference[i][d]*arrays.terminalDirectionM[n][d];}});byElement.push({element:e,localDifferenceN:difference,infinityDifferenceN:Math.max(...difference.flat().map(Math.abs)),directionalDifferenceJ:work});}
  const scatterError=Math.max(...full.flatMap((v,i)=>v.map((x,d)=>Math.abs(x-summed[i][d]))));assert.ok(scatterError<1e-10,'Retained patch scatter differs from full difference');
  const e247=byElement.find(x=>x.element===ELEMENT),without247=structuredClone(full);ids.forEach((n,i)=>{for(let d=0;d<3;d++)without247[n][d]-=e247.localDifferenceN[i][d];});
  termResults[term]={fullInfinityDifferenceN:Math.max(...full.flat().map(Math.abs)),without247InfinityDifferenceN:Math.max(...without247.flat().map(Math.abs)),retainedScatterMaximumErrorN:scatterError,byElement};
 }
 localization.push({state,a,b,terms:termResults,qualification:false,removalIsDiagnosticOnly:true});
}
const terminalU=localization.find(x=>x.state==='terminal46'&&x.a==='U4'&&x.b==='U5');assert.ok(terminalU.terms.total.without247InfinityDifferenceN>1e-5,'Secondary patch discrepancy must remain unresolved');
const testCommand=['--test','tests/element247_shell_protocol.test.mjs'],testOutput=execFileSync(process.execPath,testCommand,{cwd:root,encoding:'utf8'});assert.ok(/pass 8/.test(testOutput)&&/fail 0/.test(testOutput));fs.writeFileSync(path.join(output,'tests.log'),testOutput,{flag:'wx'});
assert.equal(digest({positions:arrays.positionsM,direction:arrays.terminalDirectionM,reference:source.nodes_m,elements:source.elements_ten_node}),before);for(const [p,h] of Object.entries(sourceHashes))assert.equal(hash(p),h);
fs.writeFileSync(path.join(output,'retained-patch-localization.json'),JSON.stringify({scope:'Producing-agent retained-data arithmetic; not independent acceptance. No constitutive calls.',priorResult:prior.result,patchElements:PATCH,secondaryElements:m.secondaryElements,comparisons:localization},null,2)+'\n',{flag:'wx'});
const result={schema:1,result:'PASS_STRUCTURAL_WHOLE_ELEMENT247_SHELL_PREFLIGHT_NO_ASSEMBLY',sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),sourceHashes,constitutivePointCalls:0,newNodalFields:0,nonlinearSolves:0,optimizerTrials:0,refits:0,executionAuthorized:false,materialAssemblyAuthorized:false,patchQualification:false,priorResult:prior.result,unchangedStateSha256:before,states:geometry,element247:{ids,corner:0,node:92,wholeReferenceBernsteinMinimum:minimumReferenceCoefficient,exactReferenceVolumeM3:exactVolume},ruleInventories:inventories,pointArtifacts,terminalDirection:{sha256:digest(arrays.terminalDirectionM),l1M:l1,unchangedDerivativeGateJ:m.integrationDerivativeGateJ},plannedFutureBudget:SHELL_BUDGET,requiredComparisons:REQUIRED_SHELL_COMPARISONS,tests:{pass:8,fail:0,command:'node '+testCommand.join(' '),sha256:sha(Buffer.from(testOutput))},secondaryWarning:{without247TerminalU4U5InfinityN:terminalU.terms.total.without247InfinityDifferenceN,stillAboveForceBudget:true},limits:['Structural coverage and polynomial moments do not prove nonlinear material force accuracy.','Five future finite rules are fixed-method comparisons, not a certified exact-integral error bound.','No material assembly or runner is authorized or executed here.','Resolving247 alone cannot qualify the16-element patch; secondary and other incident elements remain.','Old UNRESOLVED and historical independent-review limits remain.']};
fs.writeFileSync(path.join(output,'structural-preflight.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({result:result.result,sourceCommit:result.sourceCommit,sourceHashes:Object.keys(sourceHashes).length,constitutivePointCalls:0,tests:result.tests,plannedMaterialCalls:SHELL_BUDGET.plannedMaterialCalls,without247TerminalDifferenceN:result.secondaryWarning.without247TerminalU4U5InfinityN,output}));
