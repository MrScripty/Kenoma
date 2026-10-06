/** Self-consistent dense lift/release. Archived poses are starting guesses;
 * only this run's accepted state defines the next implicit objective. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,initialAnatomicalState,stepAnatomicalArm} from '../web/anatomical-arm.mjs';
import {contactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {denseModalBody} from './anatomical-dense-quadrature.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),plain=v=>JSON.parse(JSON.stringify(v,(_,x)=>ArrayBuffer.isView(x)?Array.from(x):x));
const args=process.argv.slice(2),option=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];},out=option('--output',base+'audit/anatomical-dense-trajectory.json'),factor=Number(option('--time-factor','1'));
if(![1,2].includes(factor))throw Error('Supported matched-time refinement factors: 1, 2');
if(fs.existsSync(out))throw Error('Preserve existing evidence: choose a new output path');
const baselineFile='data/anatomical-arm-v1/audit/contact-lift-release-results.json',baseline=read('audit/contact-lift-release-results.json'),check=read('audit/contact-lift-release-recheck.json');
if(check.result!=='PASS'||check.executionReceiptSHA256!==hash(baselineFile)||!baseline.completedAllSteps)throw Error('Current accepted baseline required');
for(const [p,h] of Object.entries(baseline.sourceHashes))if(hash(p)!==h)throw Error('Changed baseline '+p);
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:baseline.parameters,contactParameters:baseline.contactParameters,routingRecipe:read('config/apparatus-routing.json'),contactRule:baseline.held.state.contactRule});
for(const b of arm.model.bodies){b.modal=denseModalBody(b.modal);console.log('PREPARED',b.id,b.modal.points.length);}
arm.quadrature='diagnostic-subdivision-256';
const schedule=baseline.attempts.flatMap((a,i)=>Array.from({length:factor},(_,part)=>({label:a.label,effort:a.effort,hS:a.hS/factor,baselineIndex:i,part:part+1})));
const files=[...Object.keys(baseline.sourceHashes),baselineFile,'data/anatomical-arm-v1/audit/contact-lift-release-recheck.json','tools/anatomical-compression-quadrature.mjs','tools/anatomical-dense-quadrature.mjs','tools/anatomical-dense-trajectory.mjs'];
const run={schema:1,result:'RUNNING',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),parameters:arm.parameters,contactParameters:arm.contactParameters,pointsPerElement:256,timeRefinementFactor:factor,maxIterationsPerFrozenContactRule:240,schedule,held:null,attempts:[],snapshots:[],trace:[],completedAllSteps:false,limits:['Self-consistent 256-point reduced trajectory: only accepted dense states advance coordinates, velocity, activation and time.','Archived 32-point target poses are nonlinear guesses only. The same unchanged material, 460 coordinates, Newton algorithm, contact law and 1e-4 N gate apply.','Finite geometry and determinant samples do not qualify full nodal, mesh, integration or timestep convergence.','Bulk compression, finite-radius tendon, coplanar geometry and continuous-motion contact gaps remain open.']};
const begin=performance.now();let stage='held';
function save(){run.elapsedMS=performance.now()-begin;fs.writeFileSync(out,JSON.stringify(run,null,2)+'\n');}
arm.onIteration=row=>{const entry={stage,iteration:row.iteration,residualN:row.maxGradient,step:row.step};run.trace.push(entry);save();console.log('ITERATION',JSON.stringify(entry));};
save();
const held=initialAnatomicalState(arm,{massKg:baseline.held.state.massKg,startCoordinates:Float64Array.from(baseline.held.state.coordinatesM),maxIterations:240});
run.held=plain(held.accepted?{accepted:true,state:held.state,receipt:{...held.receipt,configuration:undefined}}:{accepted:false,reason:held.reason,residualN:held.maxGradientN,candidate:{coordinatesM:held.result.fullCoordinates,contactRule:held.result.candidateContactRule}});
console.log('HELD',held.accepted,held.reason);save();
if(!held.accepted){run.result='REJECTED_HELD';save();process.exitCode=2;}else{
 let state=held.state;
 for(const [i,request] of schedule.entries()){
  stage=i;const old=plain(state),start=performance.now(),target=baseline.snapshots[request.baselineIndex];
  const step=stepAnatomicalArm(arm,state,{effort:request.effort,h:request.hS,maxIterations:240,startCoordinates:Float64Array.from(target.coordinatesM)});
  run.attempts.push(plain({...request,accepted:step.accepted,elapsedMS:performance.now()-start,receipt:step.receipt,reason:step.reason,residualN:step.maxGradientN,surfaceAudit:step.surfaceAudit,routingAudit:step.routingAudit}));
  if(!step.accepted){
   run.rejectedCandidate=plain({coordinatesM:step.result.fullCoordinates,contactRule:step.result.candidateContactRule,contactRefinement:step.result.contactRefinement});
   run.rollback={sameStateObject:step.state===state,stateUnchanged:JSON.stringify(plain(state))===JSON.stringify(old),oldContactRestored:JSON.stringify(contactRecipe(arm.contact))===JSON.stringify(state.contactRule)};
   if(!Object.values(run.rollback).every(Boolean))throw Error('Rejected state/time/contact advancement');
   run.result='REJECTED_INCREMENT';save();console.log('REJECTED',i,step.reason,step.maxGradientN);process.exitCode=2;break;
  }
  state=step.state;run.snapshots.push(plain({...state,history:undefined}));save();console.log('STEP',i,state.timeS,state.qRad,state.omegaRadPerS,step.receipt.maximumFreeModalGradientN);
 }
 run.completedAllSteps=run.snapshots.length===schedule.length;
 if(run.completedAllSteps){
  const peak=Math.max(...run.snapshots.map(s=>s.qRad)),last=run.snapshots.at(-1),lift=run.snapshots.filter((_,i)=>schedule[i].effort>0);
  run.behavior={liftAngleIncreaseRad:Math.max(...lift.map(s=>s.qRad))-held.state.qRad,peakAngleRad:peak,finalAngleRad:last.qRad,releaseFallFromPeakRad:peak-last.qRad,finalActivation:last.activation,finalVelocityRadPerS:last.omegaRadPerS};
  run.behaviorAccepted=run.behavior.liftAngleIncreaseRad>0&&run.behavior.releaseFallFromPeakRad>0&&last.omegaRadPerS<0;
  run.result=run.behaviorAccepted?'ACCEPTED_DENSE_TRAJECTORY':'REJECTED_BEHAVIOR';if(!run.behaviorAccepted)process.exitCode=3;
 }
 save();console.log('RESULT',run.result,JSON.stringify(run.behavior));
}
