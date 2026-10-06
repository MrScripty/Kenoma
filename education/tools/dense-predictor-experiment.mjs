/** Same retained old state / mechanics / gates; only nonlinear initialization differs. */
import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {prepareAnatomicalArm,stepAnatomicalArm} from '../web/anatomical-arm.mjs';
import {denseModalBody} from './anatomical-dense-quadrature.mjs';
import {contactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {boundedAcceptedStatePredictor} from './accepted-state-predictor.mjs';
const strategy=process.argv[2];assert.ok(['bounded-secant','accepted-copy'].includes(strategy),'Explicit fixed strategy required');
const base='data/anatomical-arm-v1/',out=base+'audit/dense-predictor-'+strategy+'.json';assert.ok(!fs.existsSync(out),'Preserve existing execution');
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),read=p=>JSON.parse(fs.readFileSync(p)),plain=v=>JSON.parse(JSON.stringify(v,(_,x)=>ArrayBuffer.isView(x)?Array.from(x):x));
const reference=base+'audit/anatomical-dense-release-refinement.json',original=read(reference),referenceReplay=base+'audit/anatomical-dense-release-refinement-recheck.json',replay=read(referenceReplay);
assert.equal(replay.result,'PASS_PRESERVED_REJECTION');assert.equal(replay.executionReceiptSHA256,hash(reference));
for(const [p,h] of Object.entries(original.sourceHashes))assert.equal(hash(p),h,p);
const arm=prepareAnatomicalArm(read(base+'generated/arm-reference.json'),read(base+'config/attachments-apparatus.json'),read(base+'audit/modal-fixed-end-results.json'),{parameters:original.parameters,contactParameters:original.contactParameters,routingRecipe:read(base+'config/apparatus-routing.json')});
for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);arm.quadrature='diagnostic-subdivision-256';
const request=original.attempts.at(-1),old={...plain(original.snapshots.at(-1)),history:[],massEvents:[]};old.coordinatesM=Float64Array.from(old.coordinatesM);
const prediction=strategy==='bounded-secant'?boundedAcceptedStatePredictor(original.snapshots,{hS:request.hS}):{coordinatesM:old.coordinatesM.slice(),strategy:'accepted-state-copy',reason:'zero-order cold control',historyS:null,extrapolationFraction:0,maximumCorrectionM:0};
const comparisons=[base+'audit/dense-release-secant-retry.json',base+'audit/dense-release-secant-retry-recheck.json',base+'audit/dense-controlled-release-interval.json',base+'audit/dense-controlled-release-interval-recheck.json'];
if(strategy==='bounded-secant')assert.deepEqual(Array.from(prediction.coordinatesM),read(comparisons[0]).startCoordinatesM,'Exact prior accepted secant guess');
const before=plain(old),run={schema:1,result:'RUNNING',referenceExecutionPath:reference,sourceHashes:{...original.sourceHashes,[reference]:hash(reference),[referenceReplay]:hash(referenceReplay),...Object.fromEntries(comparisons.map(p=>[p,hash(p)])),'tools/dense-predictor-experiment.mjs':hash('tools/dense-predictor-experiment.mjs'),'tools/accepted-state-predictor.mjs':hash('tools/accepted-state-predictor.mjs')},parameters:original.parameters,contactParameters:original.contactParameters,pointsPerElement:256,maxIterationsPerFrozenContactRule:120,request:{effort:request.effort,hS:request.hS},oldState:plain(old),predictor:{...prediction,coordinatesM:undefined},startCoordinatesM:plain(prediction.coordinatesM),trace:[],limits:['Research-only initialization; no production source or physical acceptance changes.','Same retained 0.420 s old state, integration, constitutive/contact law, 0.0001 N gate and 120-iteration limit per frozen contact rule.','Any failed candidate retains its original rejection and does not advance accepted state or time.']};
const save=()=>fs.writeFileSync(out,JSON.stringify(run)+'\n');save();
arm.onIteration=r=>{run.trace.push({iteration:r.iteration,residualN:r.maxGradient,step:r.step,regularizationNPerM:r.regularization,cgIterations:r.cgIterations,cgConverged:r.cgConverged,agreementRatio:r.agreementRatio});save();console.log('ITERATION',strategy,r.iteration,r.maxGradient);};
const started=performance.now(),step=stepAnatomicalArm(arm,old,{effort:request.effort,h:request.hS,maxIterations:120,startCoordinates:prediction.coordinatesM});
assert.deepEqual(plain(old),before,'Accepted input immutable');
run.elapsedMS=performance.now()-started;run.accepted=step.accepted;run.reason=step.reason;run.residualN=step.maxGradientN??step.receipt.maximumFreeModalGradientN;run.contactRefinement=plain(step.result?.contactRefinement??step.receipt.contactRefinement);
if(step.accepted){run.result='ACCEPTED_ISOLATED_INCREMENT';run.state=plain({...step.state,history:undefined});run.receipt=plain(step.receipt);}else{run.result='REJECTED_INCREMENT';run.rejectedCandidate=plain({coordinatesM:step.result.fullCoordinates,contactRule:step.result.candidateContactRule});run.rollback={sameStateObject:step.state===old,stateUnchanged:JSON.stringify(plain(old))===JSON.stringify(before),oldContactRestored:JSON.stringify(contactRecipe(arm.contact))===JSON.stringify(old.contactRule)};assert.ok(Object.values(run.rollback).every(Boolean));process.exitCode=2;}
save();console.log('RESULT',strategy,run.result,run.residualN);
