/** Same-old-state 256-point re-equilibration, not a new accepted trajectory. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration,stepAnatomicalArm} from '../web/anatomical-arm.mjs';
import {contactRecipe,restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
import {denseModalBody,incrementalGradient} from './anatomical-dense-quadrature.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),plain=v=>JSON.parse(JSON.stringify(v,(_,x)=>ArrayBuffer.isView(x)?Array.from(x):x));
const run=read('audit/contact-lift-release-results.json'),check=read('audit/contact-lift-release-recheck.json');
if(check.result!=='PASS'||check.executionReceiptSHA256!==hash('data/anatomical-arm-v1/audit/contact-lift-release-results.json'))throw Error('Current accepted baseline required');
for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed baseline '+p);
const index=3,old=plain(run.snapshots[index-1]),target=run.snapshots[index],request=run.attempts[index],out=base+'audit/anatomical-dense-step.json';
// The baseline snapshots omit accumulated ledger fields; these are bookkeeping
// only. Coordinates, contact rule, activation, inertia and old velocity are exact.
Object.assign(old,{step:index,effort:run.attempts[index-1].effort,massEvents:[],history:[],mechanicalWorkJ:0});
old.coordinatesM=Float64Array.from(old.coordinatesM);
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')});
for(const b of arm.model.bodies){b.modal=denseModalBody(b.modal);console.log('PREPARED',b.id,b.modal.points.length,'points');}
arm.quadrature='diagnostic-subdivision-256';
restoreContactRecipe(arm.contact,target.contactRule);
const frozen=anatomicalConfiguration(arm,Float64Array.from(target.coordinatesM),target.activation,{hessian:false}),frozenResidualN=Math.max(...incrementalGradient(arm,frozen,target,old,request.hS).map(Math.abs));
const sourceFiles=[...Object.keys(run.sourceHashes),'tools/anatomical-compression-quadrature.mjs','tools/anatomical-dense-quadrature.mjs','tools/anatomical-dense-step.mjs','data/anatomical-arm-v1/audit/contact-lift-release-results.json','data/anatomical-arm-v1/audit/contact-lift-release-recheck.json'];
const receipt={schema:1,result:'RUNNING',sourceHashes:Object.fromEntries(sourceFiles.map(p=>[p,hash(p)])),baselineIndex:index,pointsPerElement:256,parameters:run.parameters,contactParameters:run.contactParameters,oldState:plain(old),baselineState:target,request:{effort:request.effort,hS:request.hS,maxIterationsPerFrozenContactRule:240},frozenResidualN,trace:[],limits:['One increment retains the exact 32-point old state, activation and velocity. This is a same-old-state integration comparison, not a self-consistent 256-point trajectory.','Material parameters, 460 displacement/joint coordinates, Newton algorithm, contact law and all acceptance gates are unchanged.','256-point integration and corner determinant queries are finite samples, not determinant positivity, quadrature, mesh, full nodal or timestep convergence certificates.','Compression, finite-radius tendon, coplanar contact and continuous-motion gaps remain open.']};
const save=()=>fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');save();
arm.onIteration=row=>{const progress={iteration:row.iteration,residualN:row.maxGradient,step:row.step};receipt.trace.push(progress);save();console.log('ITERATION',JSON.stringify(progress));};
const begin=performance.now(),step=stepAnatomicalArm(arm,old,{effort:request.effort,h:request.hS,maxIterations:240,startCoordinates:Float64Array.from(target.coordinatesM)});
receipt.elapsedMS=performance.now()-begin;receipt.accepted=step.accepted;receipt.result=step.accepted?'ACCEPTED_SAME_OLD_STATE_COMPARISON':'REJECTED_SAME_OLD_STATE_COMPARISON';receipt.reason=step.reason;
receipt.candidate=plain(step.accepted?step.state:{coordinatesM:step.result.fullCoordinates,contactRule:step.result.candidateContactRule,activation:request.effort+(old.activation-request.effort)*Math.exp(-request.hS/arm.parameters.activationTimeS),massKg:old.massKg});
receipt.solverReceipt=plain(step.accepted?step.receipt:{residualN:step.maxGradientN,contactRefinement:step.result.contactRefinement,iterations:step.result.acceptedIterations,evaluations:step.result.evaluations,reason:step.reason});
receipt.restoredOldContactOnReject=step.accepted?null:JSON.stringify(contactRecipe(arm.contact))===JSON.stringify(old.contactRule);
if(step.accepted){
 restoreContactRecipe(arm.contact,step.state.contactRule);
 const c=anatomicalConfiguration(arm,step.state.coordinatesM,step.state.activation,{hessian:false}),gradient=incrementalGradient(arm,c,step.state,old,request.hS),residualN=Math.max(...gradient.map(Math.abs)),surface=finitePoseAudit(arm.model,c.positions,step.state.qRad),routing=finiteRoutingAudit(arm.model,step.state.coordinatesM);
 if(residualN>arm.parameters.stationarityToleranceN||surface.transverseCrossingPairs||!routing.accepted||c.contact.maximumSampledBonePenetrationM>0||c.contact.maximumSampledSoftPenetrationM>0||c.contact.maximumSampledTendonPenetrationM>0)throw Error('Fresh dense-step acceptance failed');
 receipt.freshCheck={residualN,surfaceAudit:surface,routingAudit:routing,minimumJ:Math.min(...c.headResults.map(b=>b.minJ)),angleDifferenceRad:step.state.qRad-target.qRad,maximumCoordinateDifferenceM:Math.max(...step.state.coordinatesM.map((v,k)=>Math.abs(v-target.coordinatesM[k])))};
}
save();console.log('RESULT',receipt.result,JSON.stringify(receipt.freshCheck));
