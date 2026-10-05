/** Reproducible missed-contact regressions and actual 0.5 kg lift/release.
 * Archived coordinates are nonlinear START guesses only. Every step
 * uses the accepted old state in the implicit objective and all original gates.
 */
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {prepareAnatomicalArm,initialAnatomicalState,stepAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {refineContactFromGeometry,contactRecipe} from '../web/anatomical-contact-refinement.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),plain=v=>JSON.parse(JSON.stringify(v,(_,x)=>ArrayBuffer.isView(x)?Array.from(x):x)),args=process.argv.slice(2),option=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];},h=Number(option('--step','.03')),liftSteps=Number(option('--lift-steps','4')),releaseSteps=Number(option('--release-steps','10')),maxIterations=Number(option('--iterations','240')),out=option('--output',base+'audit/contact-lift-release-results.json'),rest=read('audit/arm-rest-results.json'),loaded=read('audit/arm-loaded-rejected-candidate.json'),quarter=read('audit/activation-continuation-results.json').stages[0],guessFile='audit/contact-feature-v2/interrupted-lift.json',guesses=read(guessFile),softFile='audit/contact-missed-soft-v3/candidate.json',missedSoft=read(softFile);
if(!(h>0&&liftSteps>0&&releaseSteps>0&&maxIterations>0))throw new RangeError('Experiment options');
const files=['tools/anatomical-contact-experiment.mjs',...fs.readdirSync(root+'web').filter(p=>p.startsWith('anatomical-')&&p.endsWith('.mjs')).map(p=>'web/'+p),...['generated/arm-reference.json','config/attachments-apparatus.json','config/apparatus-routing.json','audit/modal-fixed-end-results.json','audit/arm-rest-results.json','audit/arm-loaded-rejected-candidate.json','audit/activation-continuation-results.json',guessFile,softFile].map(p=>'data/anatomical-arm-v1/'+p)],sourceHashes=Object.fromEntries(files.map(p=>[p,createHash('sha256').update(fs.readFileSync(root+p)).digest('hex')]));
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:rest.parameters,contactParameters:rest.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),regressions=[];
for(const [label,candidate] of [['loaded',loaded],['quarter',quarter]]){
 const x=Float64Array.from(candidate.coordinatesM),c=anatomicalConfiguration(arm,x,0,{hessian:false});
 regressions.push({label,baselineSampledBonePenetrationM:c.contact.maximumSampledBonePenetrationM,baselineSampledTendonPenetrationM:c.contact.maximumSampledTendonPenetrationM,refinement:refineContactFromGeometry(arm.model,arm.contact,x,c.positions)});
}
let stage='rest';arm.onIteration=row=>{console.log(stage,row.iteration,row.maxGradient,row.step);fs.writeFileSync('/tmp/kenoma-contact-experiment-progress.json',JSON.stringify({stage,coordinatesM:Array.from(row.fullCoordinates),residualN:row.maxGradient,accepted:false}));};
const begin=performance.now(),held=initialAnatomicalState(arm,{massKg:.5,startCoordinates:Float64Array.from(rest.state.coordinatesM),maxIterations});
const payload={schema:1,sourceHashes,parameters:arm.parameters,contactParameters:arm.contactParameters,quadrature:arm.quadrature,hS:h,effort:.04,requestedLiftSteps:liftSteps,requestedReleaseSteps:releaseSteps,regressions,nonlinearGuesses:{files:[guessFile,softFile],limits:'Archived coordinates are guesses only; the accepted old state defines every implicit step.'},held:plain(held.accepted?{accepted:true,state:held.state,receipt:held.receipt}:{accepted:false,reason:held.reason,residualN:held.maxGradientN}),attempts:[],snapshots:[],completedAllSteps:false,limits:['Atlas-derived reduced teaching arm, not full nodal or medical validation.','Geometric witnesses adapt material quadrature between solves; each Newton objective is frozen.','Reference-area rule changes have a separate energy event. No continuous-motion, finite-radius tendon or coplanar-contact certificate.','Historical failed coordinates are nonlinear guesses, never accepted or advanced as states.','Release removes effort; activation and inertia can carry motion after release.']};
function save(){payload.elapsedMS=performance.now()-begin;fs.writeFileSync(out,JSON.stringify(payload,null,2)+'\n');}
save();console.log('REST',held.accepted,held.reason);if(!held.accepted){process.exitCode=2;}else{
 let state=held.state;
 // First use the same short step as the archived failure to compare directly.
 const schedule=[{effort:.04,h:.01,label:'regression-load'},...Array.from({length:liftSteps},()=>({effort:.04,h,label:'lift'})),...Array.from({length:releaseSteps},()=>({effort:0,h,label:'release'}))];
 for(const [i,request] of schedule.entries()){
  stage=request.label+' '+i;
  const guess=i===guesses.snapshots.length&&request.label==='lift'&&request.h===missedSoft.hS&&request.effort===missedSoft.effort?missedSoft.coordinatesM:guesses.snapshots[i]&&guesses.attempts[i]?.label===request.label&&guesses.attempts[i]?.hS===request.h?guesses.snapshots[i].coordinatesM:i===0?loaded.coordinatesM:null;
  const start=performance.now(),step=stepAnatomicalArm(arm,state,{effort:request.effort,h:request.h,maxIterations,...(guess?{startCoordinates:Float64Array.from(guess)}:{})});
  payload.attempts.push(plain({label:request.label,hS:request.h,effort:request.effort,accepted:step.accepted,elapsedMS:performance.now()-start,receipt:step.receipt,reason:step.reason,residualN:step.maxGradientN,surfaceAudit:step.surfaceAudit,routingAudit:step.routingAudit,contactRefinement:step.result?.contactRefinement}));
  if(!step.accepted){payload.rejectedCandidate=plain({coordinatesM:step.result.fullCoordinates,contactRule:step.result.candidateContactRule,configuration:{...step.result.configuration,hessian:undefined}});console.log('REJECTED',i,request.label,step.reason,step.maxGradientN,step.surfaceAudit?.transverseCrossingPairs);save();process.exitCode=2;break;}
  state=step.state;payload.snapshots.push(plain({coordinatesM:state.coordinatesM,contactRule:contactRecipe(arm.contact),qRad:state.qRad,omegaRadPerS:state.omegaRadPerS,activation:state.activation,timeS:state.timeS,massKg:state.massKg}));save();console.log('STEP',i,request.label,state.qRad,state.omegaRadPerS,step.receipt.maximumFreeModalGradientN);
 }
 payload.completedAllSteps=payload.attempts.length===schedule.length&&payload.attempts.every(s=>s.accepted);
 if(payload.completedAllSteps){const peak=Math.max(...payload.snapshots.map(s=>s.qRad)),last=payload.snapshots.at(-1);payload.behavior={liftAngleIncreaseRad:Math.max(...payload.snapshots.slice(0,liftSteps+1).map(s=>s.qRad))-held.state.qRad,peakAngleRad:peak,finalAngleRad:last.qRad,releaseFallFromPeakRad:peak-last.qRad,finalActivation:last.activation,finalVelocityRadPerS:last.omegaRadPerS};if(!(payload.behavior.liftAngleIncreaseRad>0&&payload.behavior.releaseFallFromPeakRad>0&&last.omegaRadPerS<0)){payload.behaviorAccepted=false;process.exitCode=3;}else payload.behaviorAccepted=true;}
 save();
}
