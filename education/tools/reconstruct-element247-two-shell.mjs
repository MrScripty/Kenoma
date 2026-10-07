/** Offline retained-value reconstruction. Never executes a quadrature or material callback. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {withChangedShellIdentity} from './element247-two-shell-schema.mjs';
import {buildConstructedStage,compareChangedShells,WORK_GATE_J} from './element247-two-shell-protocol.mjs';
import {compareShellStages} from './element247-shell-runtime.mjs';

export const FAILED_EVIDENCE_COMMIT='9c9edbc9f3dd9729f2becc5215054897d139735e';
const EXECUTED_COMMIT='97da4bdea7d0be11fc18222221b8b551b53a8e3b';
const OLD='review/element247-shell-run-20261007/material/';
const RAW='review/element247-two-shell-run-20261007/';
const OUTCOME='review/element247-two-shell-outcome-20261007/';
const PREF='review/element247-two-shell-preflight-20261007/';
const sha=b=>createHash('sha256').update(b).digest('hex');
const regions=[...Array.from({length:20},(_,i)=>`s${i+1}`),'core'];
function snapshotBlob(root,name) {
 const ref=`${FAILED_EVIDENCE_COMMIT}:education/${name}`;
 const size=Number(execFileSync('git',['cat-file','-s',ref],{cwd:root,encoding:'utf8'}).trim());
 assert.ok(Number.isSafeInteger(size)&&size>=0,'IMMUTABLE_BLOB_SIZE');
 return execFileSync('git',['cat-file','blob',ref],{cwd:root,maxBuffer:size+65536});
}

// Every read is bound to an immutable Git blob; test injection only changes
// the bytes presented for verification, never the expected immutable bytes.
export function immutableSnapshotReader(root,readFile=fs.readFileSync) {
 const inventory={};
 const read=name=>{
  assert.ok(!path.isAbsolute(name)&&!name.split('/').includes('..'),'PORTABLE_INPUT_PATH');
  const disk=readFile(path.join(root,name));
  const frozen=snapshotBlob(root,name);
  assert.ok(disk.equals(frozen),`IMMUTABLE_INPUT_MISMATCH:${name}`);
  inventory[name]={bytes:disk.length,sha256:sha(disk)};
  return disk;
 };
 return {read,json:name=>JSON.parse(read(name)),inventory};
}

export function reconstructRetainedDiagnostic(root) {
 const bound=immutableSnapshotReader(root),read=bound.json,bytes=bound.read;
 const summary=read(OUTCOME+'failure-summary.json'),incomplete=read(RAW+'material/incomplete-receipt.json'),start=read(RAW+'material/material-start.json');
 assert.equal(summary.result,'INCOMPLETE_TWO_SHELL_DIAGNOSTIC');assert.equal(summary.runComplete,false);
 assert.equal(start.sourceCommit,EXECUTED_COMMIT);assert.equal(start.runId,summary.runId);
 assert.equal(start.authorizationSha256,summary.authorizationSha256);
 for(const [name,item] of Object.entries(summary.rawOutputInventory)){
  const b=bytes(RAW+name);assert.equal(b.length,item.bytes);assert.equal(sha(b),item.sha256);
 }
 assert.equal(Object.keys(summary.rawOutputInventory).length,57);
 for(const [name,item] of Object.entries(incomplete.retainedFiles)){
  const b=bytes(RAW+'material/'+name);assert.equal(b.length,item.bytes);assert.equal(sha(b),item.sha256);
 }
 assert.equal(Object.keys(incomplete.retainedFiles).length,49);
 const originalSourceHashes=start.sourceHashes;
 assert.equal(Object.keys(originalSourceHashes).length,1598);
 const allowedSourceRepairs=new Set(['tools/element247-two-shell-runtime.mjs','tests/element247_two_shell.test.mjs']);
 const sourceChanges={};
 for(const [name,expected] of Object.entries(originalSourceHashes)){
  const frozen=snapshotBlob(root,name);
  assert.equal(sha(frozen),expected,`ORIGINAL_SOURCE_HASH:${name}`);
  const current=fs.readFileSync(path.join(root,name));
  if(sha(current)!==expected){assert.ok(allowedSourceRepairs.has(name),`UNEXPECTED_SOURCE_CHANGE:${name}`);sourceChanges[name]={originalSha256:expected,repairedSha256:sha(current)};}
 }
 assert.deepEqual(Object.keys(sourceChanges).sort(),[...allowedSourceRepairs].sort());
 const arrays=read(RAW+'material/saved-arrays.json');assert.deepEqual(arrays,read(OLD+'saved-arrays.json'));
 assert.ok(arrays.heldNodeOrder.every(n=>arrays.terminalDirectionM[n].every(x=>x===0)));
 const source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486');
 const baseline=read(OLD+'A55-terminal46-assembly.json');
 const retainedChanged=['s1','s2'].map(s=>read(RAW+`material/T24-terminal46-${s}-shell.json`));
 retainedChanged.forEach((r,i)=>{assert.equal(r.id,`s${i+1}`);assert.equal(r.shell,undefined);assert.equal(r.pointCount,2000);});
 const changed=retainedChanged.map(withChangedShellIdentity);
 // Exactly one field is added on in-memory copies; numerical bytes stay bound above.
 changed.forEach((r,i)=>{const {shell,...unchanged}=r;assert.equal(shell,retainedChanged[i].id);assert.deepEqual(unchanged,retainedChanged[i]);});
 const rows=[...changed],reuse=read(RAW+'material/reuse-manifest.json');
 assert.equal(reuse.regions,19);assert.equal(reuse.materialCalls,0);assert.equal(reuse.reusedPoints,9500);assert.equal(reuse.byteExact,true);
 for(const shell of regions.slice(2)){
  for(const suffix of ['shell.json','weights.f64le']){
   const name=`A55-terminal46-${shell}-${suffix}`;assert.ok(bytes(RAW+'material/'+name).equals(bytes(OLD+name)));
  }
  rows.push(read(RAW+`material/A55-terminal46-${shell}-shell.json`));
 }
 const weights=bytes(RAW+'material/changed-reference-weights.f64le');
 assert.ok(weights.equals(bytes(PREF+'changed-reference-weights.f64le')));
 assert.ok(bytes(RAW+'material/changed-normalized-points.f64le').equals(bytes(PREF+'changed-normalized-points.f64le')));
 ['s1','s2'].forEach((s,i)=>assert.ok(bytes(RAW+`material/T24-terminal46-${s}-weights.f64le`).equals(weights.subarray(i*16000,(i+1)*16000))));
 assert.ok(bytes(RAW+'material/constructed-reference-weights.f64le').equals(Buffer.concat([weights,...regions.slice(2).map(s=>bytes(OLD+`A55-terminal46-${s}-weights.f64le`))])));
 assert.ok(bytes(RAW+'material/constructed-normalized-points.f64le').equals(Buffer.concat([bytes(RAW+'material/changed-normalized-points.f64le'),bytes(OLD+'A55-normalized-points.f64le').subarray(1000*48)])));
 const stage=buildConstructedStage(source,rows,arrays.terminalDirectionM);
 const changedComparison=compareChangedShells(['s1','s2'].map(s=>read(OLD+`A55-terminal46-${s}-shell.json`)),changed,arrays.terminalDirectionM,source.elements_ten_node[247]);
 const whole={...compareShellStages(baseline,stage,arrays.terminalDirectionM,source.elements_ten_node[247],WORK_GATE_J),qualification:false,reusedTailAgreementIsByConstruction:true};
 const previous=read(OUTCOME+'offline-comparisons.json');
 assert.deepEqual(stage,previous.constructedWholeValues);assert.deepEqual(changedComparison,previous.changedShellComparison);
 const {scope:previousScope,...previousWhole}=previous.constructedWholeComparison;assert.deepEqual(whole,previousWhole);
 const original=read(OLD+'shell-vector-comparisons.json').comparisons.find(c=>c.state==='terminal46'&&c.a==='C55'&&c.b==='A55');
 assert.equal(original.pass,false);assert.equal(original.terms.total.shellTriangleInfinityN,8.611662232570753e-5);
 const external=read(RAW+'external-exit.json'),worker=read(RAW+'launcher-exit.pending.json'),publicExit=read(OUTCOME+'executor-public-entry-exit.json');
 assert.equal(external.childExitCode,1);assert.equal(worker.launcherExitCode,1);
 assert.equal(publicExit.finalToolResult.exit_code,1);assert.equal(publicExit.sourceCommit,EXECUTED_COMMIT);assert.equal(publicExit.invocations,1);
 const runtime=incomplete.runtime;['reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks','plannedCalls','maximumCalls'].forEach(k=>assert.equal(runtime[k],4000));assert.equal(runtime.activeBatch,null);
 const auth=read('research/element247-two-shell-authorization-20261007.json');assert.equal(auth.invocations,1);assert.equal(sha(bytes('research/element247-two-shell-authorization-20261007.json')),start.authorizationSha256);
 for(const name of ['material/completion-receipt.json','material/terminal-completion.json','external-final.json','launcher-acceptance.json'])assert.ok(!fs.existsSync(path.join(root,RAW+name)),'FAILED_RUN_MUST_REMAIN_INCOMPLETE');
 // Bind all transitive local source modules, including helpers imported for arithmetic.
 const reconstructionSources={};
 const visit=name=>{
  if(reconstructionSources[name])return;
  const b=fs.readFileSync(path.join(root,name));reconstructionSources[name]={bytes:b.length,sha256:sha(b)};
  for(const match of b.toString().matchAll(/(?:from\s*|import\s*)['"]([.][^'"]+)['"]/g))visit(path.posix.normalize(path.posix.join(path.posix.dirname(name),match[1])));
 };
 ['tools/reconstruct-element247-two-shell.mjs','tools/element247-two-shell-runtime.mjs','tests/element247_two_shell.test.mjs'].forEach(visit);
 const reconstructionSourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
 execFileSync('git',['diff','--exit-code','HEAD','--',...Object.keys(reconstructionSources).map(n=>'education/'+n)],{cwd:path.dirname(root)});
 return {
  schema:1,result:'RECONSTRUCTED_RETAINED_TWO_SHELL_DIAGNOSTIC',
  evidenceKind:'Retained finite-rule measurements plus independently reviewable offline arithmetic; incomplete execution',
  reconstructionSourceCommit,failedEvidenceCommit:FAILED_EVIDENCE_COMMIT,originalExecutedCommit:EXECUTED_COMMIT,originalRunId:start.runId,
  provenance:{immutableInputInventory:bound.inventory,originalSourceHashes,repairedSourceChanges:sourceChanges,reconstructionSources,retainedNumericalFiles:49,rawFiles:57},
  newSpecimenCalls:0,newMaterialCalls:0,newQuadratureEvaluations:0,newNonlinearSolves:0,newFields:0,refits:0,
  operationalCompletion:false,originalExitCodes:{child:1,worker:1,publicEntry:1},publicExitEvidence:publicExit,
  originalIncompleteReceipt:RAW+'material/incomplete-receipt.json',authorizationStatus:'CONSUMED_BY_ORIGINAL_ONE_SHOT; NO_RETRY_AUTHORIZATION',
  retainedMeasurementCounts:{reserved:4000,entered:4000,completed:4000,changedShells:2,reusedRegions:19,reusedPoints:9500,constructedPoints:13500},
  metadataRepair:'Set shell=id only on in-memory copies of the two bound retained records; numerical fields unchanged',
  changedShellComparison:changedComparison,constructedWholeValues:stage,constructedWholeComparison:{...whole,scope:'Offline constructed whole; reused tails agree by construction'},
  comparisonCoverage:{
   changedShells:'Complete A55 versus T24 s1/s2 signed vectors, triangles, energy values and directional derivatives for all five terms',
   constructedWhole:'Complete 21-region constructed values and A55 comparison, all585 nodes including held nodes',
   reuseFullyCoversDesiredArithmetic:true,
   reusedTailLimit:'All19 A55 regions are reused byte-exact; zero tail differences are by construction and give no new refinement evidence',
   unavailable:['Independent T24 evaluations of s3..s20/core','Higher refinement, radial, chart or depth sensitivity of T24','Other fields, states or elements','Successful run completion or element/patch qualification']
  },
  originalFailureN:8.611662232570753e-5,element247Qualification:false,patchQualification:false,priorPatchResult:'UNRESOLVED_FIXED_PATCH_INTEGRATION',secondaryElementsUnresolved:[197,200,203,206,246,248]
 };
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
 assert.deepEqual(process.argv.slice(2),[],'OFFLINE_ONLY_NO_EXECUTE_OPTION');
 console.log(JSON.stringify(reconstructRetainedDiagnostic(fileURLToPath(new URL('../',import.meta.url))),null,2));
}
