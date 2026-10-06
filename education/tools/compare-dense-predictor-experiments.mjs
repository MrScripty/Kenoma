/** Compare terminal source-bound controls; do not optimize or advance states. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {prepareAnatomicalArm} from '../web/anatomical-arm.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';
const base='data/anatomical-arm-v1/audit/',out=process.argv[2];assert.ok(out&&!fs.existsSync(out),'Explicit new output required');
const paths={original:base+'anatomical-dense-release-refinement.json',originalReplay:base+'anatomical-dense-release-refinement-recheck.json',prior:base+'dense-release-secant-retry.json',priorReplay:base+'dense-release-secant-retry-recheck.json',bounded:base+'dense-predictor-bounded-secant.json',boundedReplay:base+'dense-predictor-bounded-secant-recheck.json',copy:base+'dense-predictor-accepted-copy.json',copyReplay:base+'dense-predictor-accepted-copy-recheck.json',common:base+'dense-controlled-release-interval-summary.json',commonExecution:base+'dense-controlled-release-interval.json',commonReplay:base+'dense-controlled-release-interval-recheck.json',full:base+'dense-release-secant-matched-times.json'};
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),read=p=>JSON.parse(fs.readFileSync(p)),records=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,read(p)]));
for(const key of ['bounded','copy']){
 const r=records[key],v=records[key+'Replay'];assert.notEqual(r.result,'RUNNING');
 assert.equal(v.result,'PASS_FRESH_DENSE_PREDICTOR_REPLAY');assert.equal(v.executionReceiptSHA256,hash(paths[key]));
 for(const [p,h] of Object.entries(r.sourceHashes))assert.equal(hash(p),h,p);
 assert.equal(r.maxIterationsPerFrozenContactRule,120);assert.equal(r.pointsPerElement,256);assert.equal(r.parameters.stationarityToleranceN,.0001);
}
assert.equal(records.originalReplay.result,'PASS_PRESERVED_REJECTION');assert.equal(records.originalReplay.executionReceiptSHA256,hash(paths.original));
assert.equal(records.priorReplay.result,'PASS_FRESH_DENSE_CONTROL_REPLAY');assert.equal(records.priorReplay.executionReceiptSHA256,hash(paths.prior));assert.equal(records.common.result,'PASS_SOURCE_BOUND_CONTROL_SUMMARY');assert.equal(records.full.result,'PASS_COMPLETED_ACCEPTED_RELEASE_MATCHED_TIMES');
assert.equal(records.commonReplay.result,'PASS_FRESH_DENSE_CONTROL_REPLAY');assert.equal(records.commonReplay.executionReceiptSHA256,hash(paths.commonExecution));
for(const r of Object.values(records))for(const [p,h] of Object.entries(r.sourceHashes??{}))assert.equal(hash(p),h,p);
const old=records.original.snapshots.at(-1),stateKeys=['coordinatesM','qRad','omegaRadPerS','activation','massKg','timeS','contactRule'];
for(const key of ['bounded','copy','prior'])for(const field of stateKeys)assert.deepEqual(records[key].oldState[field],old[field],key+' same physical old '+field);
assert.deepEqual(records.bounded.startCoordinatesM,records.prior.startCoordinatesM,'Predictor reproduces previous secant guess');
assert.deepEqual(records.copy.startCoordinatesM,old.coordinatesM,'Cold copy exactly old coordinates');
const j=old.coordinatesM.length-1,deg=q=>q*180/Math.PI;
assert.equal(old.coordinatesM[j]/JOINT_SCALE_M,old.qRad,'Last coordinate is joint');
const rows=['bounded','copy','prior'].map(key=>{
 const r=records[key],v=records[key+'Replay'],checked=v.rows[0],g=checked.rows.at(-1)??checked.rejected;
 assert.equal(Boolean(r.accepted),Boolean(checked.verifiedSteps));
 return {key,result:r.result,accepted:r.accepted,startAngleDeg:deg(r.startCoordinatesM[j]/JOINT_SCALE_M),maximumStartCorrectionM:Math.max(...r.startCoordinatesM.map((x,k)=>Math.abs(x-old.coordinatesM[k]))),iterationsAcrossFrozenContactRules:r.contactRefinement.reduce((n,t)=>n+t.iterations,0),contactWitnessesAdded:r.contactRefinement.reduce((n,t)=>n+t.added,0),minimumRecordedIterationResidualN:Math.min(...r.trace.map(t=>t.residualN)),recordedResidualN:r.residualN,independentResidualN:g.independentResidualN,minimumCornerJ:g.minimumCornerJ,crossings:g.crossings,routingAccepted:g.routingAccepted,sampledPenetrationsM:g.penetrations,finalAcceptedAngleDeg:r.accepted?deg(r.state.qRad):null,acceptedTimeS:r.accepted?r.state.timeS:r.oldState.timeS,rollback:r.rollback??null};
});
const originalTrace=records.original.trace.filter(t=>t.stage===records.original.attempts.length-1),originalFailure={result:records.original.result,accepted:false,iterationsAcrossFrozenContactRules:originalTrace.length,minimumRecordedIterationResidualN:Math.min(...originalTrace.map(t=>t.residualN)),recordedResidualN:records.original.attempts.at(-1).residualN,independentResidualN:records.originalReplay.rejected.independentResidualN,acceptedTimeS:old.timeS,rejectedTargetTimeS:old.timeS+records.original.attempts.at(-1).hS,originalReplayRetainedOldTimeS:records.originalReplay.rejected.timeS,rollback:records.original.rollback};
let previousSecantEndpointReproduced=null;
if(records.bounded.accepted){previousSecantEndpointReproduced=stateKeys.every(k=>JSON.stringify(records.bounded.state[k])===JSON.stringify(records.prior.state[k]));assert.ok(previousSecantEndpointReproduced,'Same seed/mechanics endpoint reproduction');}
let acceptedSeedEndpointComparison=null;
if(records.bounded.accepted&&records.copy.accepted){
 const data='data/anatomical-arm-v1/',arm=prepareAnatomicalArm(read(data+'generated/arm-reference.json'),read(data+'config/attachments-apparatus.json'),read(data+'audit/modal-fixed-end-results.json'),{parameters:records.original.parameters,contactParameters:records.original.contactParameters,routingRecipe:read(data+'config/apparatus-routing.json')});
 const a=records.bounded.state,b=records.copy.state;let maximumNodalDifferenceM=0;
 for(const body of arm.model.bodies){const pa=modalPositions(body.modal,a.coordinatesM.slice(body.offset,body.offset+63)),pb=modalPositions(body.modal,b.coordinatesM.slice(body.offset,body.offset+63));for(let k=0;k<pa.length;k++)maximumNodalDifferenceM=Math.max(maximumNodalDifferenceM,Math.hypot(...pa[k].map((v,d)=>v-pb[k][d])));}
 acceptedSeedEndpointComparison={copyMinusBoundedAngleDeg:deg(b.qRad-a.qRad),maximumNodalDifferenceM,maximumCoordinateDifferenceM:Math.max(...a.coordinatesM.map((v,k)=>Math.abs(v-b.coordinatesM[k])))};
}
const receipt={schema:1,result:'PASS_SOURCE_BOUND_PREDICTOR_COMPARISON',samePhysicalOldState:{timeS:old.timeS,angleDeg:deg(old.qRad),massKg:old.massKg,requestHS:records.bounded.request.hS},sameMechanicsAndGates:true,predictorBound:records.bounded.predictor,previousSecantGuessExactlyReproduced:true,previousSecantEndpointReproduced,acceptedSeedEndpointComparison,originalFailure,rows,commonStateControl:{differentPhysicalOldState:true,oldTimeS:records.commonExecution.oldState.timeS,localMatchedEndpoint:records.common.localMatchedEndpoint,cases:records.common.cases.map(c=>({factor:c.factor,acceptedSteps:c.acceptedSteps,maximumAcceptedIndependentResidualN:c.maximumAcceptedIndependentResidualN,traceIterations:c.traceIterations,addedWitnesses:c.attempts.reduce((n,a)=>n+a.contactRefinement.reduce((m,r)=>m+r.added,0),0)}))},fullReleaseLimits:{maximumAngleDifferenceDeg:records.full.maximumAbsoluteAngleDifferenceDeg,maximumNodalDifferenceM:records.full.maximumNodalDifferenceM,minimumCornerJ:records.full.fine.minimumCornerJ},sourceHashes:{...Object.fromEntries(Object.values(paths).map(p=>[p,hash(p)])),'tools/compare-dense-predictor-experiments.mjs':hash('tools/compare-dense-predictor-experiments.mjs')},limits:['Initialization comparison from one identical physical state; not a new complete trajectory.','Common-state interval controls start from another old state; do not attribute their differences or costs solely to initialization.','Repeated secant success is reproducibility of the same deterministic case, not statistical evidence of general solver reliability.','Wall time is not a controlled performance benchmark; other research processes are active.','No full-nodal, mesh/quadrature/timestep convergence, calibrated anatomy or whole-envelope acceptance.']};
fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));
