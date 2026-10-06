import {fineCoverage,stateLineage} from './anatomical-replay-contracts.mjs';
import {recordedInputMatches} from './recorded-inputs.mjs';
/** Independent residual, finite geometry and mechanical-ledger replay.
 * No optimizer is invoked and no zero-test/metadata-only success is accepted.
 */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/contact-lift-release-results.json'),fine=read('audit/contact-fine-release-results.json'),prefix=read('audit/contact-coarse-release-base.json'),check=read('audit/contact-lift-release-recheck.json');
if(check.verifierSHA256!==hash('tools/verify-anatomical-contact-trajectory.mjs'))throw Error('Stale primary replay verifier digest');
if(check.result!=='PASS'||check.executionReceiptSHA256!==hash('data/anatomical-arm-v1/audit/contact-lift-release-results.json')||fine.baseReceiptSHA256!==hash('data/anatomical-arm-v1/audit/contact-coarse-release-base.json'))throw Error('Source-bound base receipt');
for(const [p,h] of Object.entries(fine.sourceHashes))if(!recordedInputMatches(p,h))throw Error('Changed finer execution source '+p);
for(const [i,s] of prefix.snapshots.entries())if(JSON.stringify(s)!==JSON.stringify(run.snapshots[i]))throw Error('Base differs from verified primary trajectory');
const initial=prefix.snapshots.at(-1);for(const key of ['coordinatesM','contactRule','qRad','omegaRadPerS','activation','timeS','massKg'])if(JSON.stringify(initial[key])!==JSON.stringify(fine.initialState[key]))throw Error('Continuation initial state '+key);
fineCoverage(fine);if(fine.snapshots.length!==22||fine.requestedSteps!==27||fine.completedAllSteps!==false||fine.executionStatus!=='INTERRUPTED_AFTER_ACCEPTED_PREFIX')throw Error('Changed declared 22-of-27 interrupted prefix');if(fine.attempts.length!==fine.snapshots.length||!fine.attempts.every(a=>a.accepted))throw Error('Not an accepted prefix');
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),p=arm.parameters,j=arm.model.jointIndex;
function stored(state,activation,rule){restoreContactRecipe(arm.contact,rule||arm.initialContactRule);return anatomicalConfiguration(arm,Float64Array.from(state.coordinatesM),activation,{hessian:false});}
function rigid(state){const com=attachmentMap(arm.comM,arm.model.frame,state.qRad),grip=attachmentMap(arm.gripM,arm.model.frame,state.qRad),d=state.qRad<p.minimumAngleRad?state.qRad-p.minimumAngleRad:state.qRad>p.maximumAngleRad?state.qRad-p.maximumAngleRad:0;return {energy:p.gMPerS2*(p.segmentMassKg*com.position[2]+state.massKg*grip.position[2])+.5*p.stopStiffnessNmPerRad*d*d,gradient:p.gMPerS2*(p.segmentMassKg*com.B[2]+state.massKg*grip.B[2])+p.stopStiffnessNmPerRad*d};}
const near=(a,b,t,label)=>{if(!(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t))throw Error(`${label}: ${a} != ${b}`);};
function verifySteps(snapshots,attempts,initial){
 let old=initial;const rows=[];
 for(const [i,state] of snapshots.entries()){
 const attempt=attempts[i];stateLineage(state,old,attempt,p,arm.model.ndof,j);const r=attempt.receipt,h=attempt.hS,tau=attempt.effort>=old.activation?p.activationTimeS:p.releaseTimeS,activation=attempt.effort+(old.activation-attempt.effort)*Math.exp(-h/tau);
 near(state.activation,activation,1e-14,'activation');near(state.qRad,state.coordinatesM[j]/JOINT_SCALE_M,1e-14,'joint coordinate');near(state.timeS,old.timeS+h,1e-14,'time');near(state.omegaRadPerS,(state.qRad-old.qRad)/h,1e-14,'velocity');
 const prior=stored(old,old.activation,old.contactRule),oldAtRule=stored(old,old.activation,state.contactRule),oldAtActivation=stored(old,activation,state.contactRule),c=stored(state,activation,state.contactRule),G=rigid(state),G0=rigid(old),I=arm.baseInertiaKgM2+state.massKg*arm.gripRadiusSquaredM2;
 c.gradient[j]+=(G.gradient+I/h**2*(state.qRad-old.qRad-h*old.omegaRadPerS)+p.jointDampingNmS/h*(state.qRad-old.qRad))/JOINT_SCALE_M;
 const residual=Math.max(...c.gradient.map(Math.abs)),surface=finitePoseAudit(arm.model,c.positions,state.qRad),routing=finiteRoutingAudit(arm.model,Float64Array.from(state.coordinatesM));
 if(!Number.isFinite(residual)||residual>p.stationarityToleranceN||surface.transverseCrossingPairs||!routing.accepted||c.contact.maximumSampledBonePenetrationM>0||c.contact.maximumSampledSoftPenetrationM>0||c.contact.maximumSampledTendonPenetrationM>0)throw Error('Trajectory acceptance gate '+i);
 near(residual,r.maximumFreeModalGradientN,1e-9,'residual');
 const quadrature=oldAtRule.physicalPotentialJ-prior.physicalPotentialJ,activeWork=oldAtActivation.energies.activePotentialJ-c.energies.activePotentialJ,passive=z=>z.physicalPotentialJ-z.energies.activePotentialJ,oldE=passive(oldAtActivation)+G0.energy+.5*I*old.omegaRadPerS**2,newE=passive(c)+G.energy+.5*I*state.omegaRadPerS**2,damping=p.jointDampingNmS*h*state.omegaRadPerS**2,kineticDefect=.5*I*(state.omegaRadPerS-old.omegaRadPerS)**2,workDefect=newE-oldE-activeWork+damping+kineticDefect,impulse=h*JOINT_SCALE_M*c.gradient[j];
 for(const [a,b,label] of [[quadrature,r.referenceQuadratureUpdateJ,'quadrature event'],[activeWork,r.activeMechanicalWorkJ,'active work'],[oldE,r.oldMechanicalJ,'old energy'],[newE,r.newMechanicalJ,'new energy'],[workDefect,r.nonlinearWorkDefectJ,'work defect'],[impulse,r.impulseResidualNmS,'impulse']])near(a,b,1e-9,label);
 rows.push({step:i+1,label:attempt.label,timeS:state.timeS,qRad:state.qRad,activation,residualN:residual,transverseCrossingPairs:surface.transverseCrossingPairs,tendonViolations:routing.violations.length,minimumJ:Math.min(...c.headResults.map(h=>h.minJ)),curvatureFallbacks:c.contact.curvatureFallbacks,referenceQuadratureUpdateJ:quadrature,activeMechanicalWorkJ:activeWork,nonlinearWorkDefectJ:workDefect,impulseResidualNmS:impulse});old=state;
 }
 return rows;
}
const rows=verifySteps(fine.snapshots,fine.attempts,fine.initialState);
const matched=rows.flatMap(row=>{const coarse=run.snapshots.find(s=>Math.abs(s.timeS-row.timeS)<1e-12);return coarse?[{timeS:row.timeS,coarseAngleRad:coarse.qRad,fineAngleRad:row.qRad,differenceRad:row.qRad-coarse.qRad}]:[];});
const evidence={schema:1,result:'PASS_ACCEPTED_PREFIX',executionStatus:fine.executionStatus,executionReceiptSHA256:hash('data/anatomical-arm-v1/audit/contact-fine-release-results.json'),baseReceiptSHA256:fine.baseReceiptSHA256,verifierSHA256:hash('tools/verify-anatomical-release-prefix.mjs'),executionSourceHashes:fine.sourceHashes,verifiedSteps:rows.length,requestedSteps:fine.requestedSteps,completedAllSteps:fine.completedAllSteps,rows,matchedTimes:matched,maximumMatchedAngleDifferenceRad:Math.max(...matched.map(m=>Math.abs(m.differenceRad))),limits:['Interrupted 22-of-27-step finer release comparison; no full fine trajectory is claimed.','Adaptive material rules differ. Matched-time differences report sensitivity, not a convergence rate.','Same reduced finite-pose limitations as the completed primary trajectory.']};
fs.writeFileSync(base+'audit/contact-fine-release-recheck.json',JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify({result:evidence.result,steps:rows.length,maximumMatchedAngleDifferenceRad:evidence.maximumMatchedAngleDifferenceRad}));
