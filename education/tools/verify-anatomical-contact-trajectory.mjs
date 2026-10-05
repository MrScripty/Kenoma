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
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/contact-lift-release-results.json');
for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed trajectory execution source '+p);
if(!run.completedAllSteps||!run.behaviorAccepted||!run.held.accepted)throw Error('No completed accepted lift/release to verify');
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),p=arm.parameters,j=arm.model.jointIndex;
function stored(state,activation,rule){restoreContactRecipe(arm.contact,rule||arm.initialContactRule);return anatomicalConfiguration(arm,Float64Array.from(state.coordinatesM),activation,{hessian:false});}
function rigid(state){const com=attachmentMap(arm.comM,arm.model.frame,state.qRad),grip=attachmentMap(arm.gripM,arm.model.frame,state.qRad),d=state.qRad<p.minimumAngleRad?state.qRad-p.minimumAngleRad:state.qRad>p.maximumAngleRad?state.qRad-p.maximumAngleRad:0;return {energy:p.gMPerS2*(p.segmentMassKg*com.position[2]+state.massKg*grip.position[2])+.5*p.stopStiffnessNmPerRad*d*d,gradient:p.gMPerS2*(p.segmentMassKg*com.B[2]+state.massKg*grip.B[2])+p.stopStiffnessNmPerRad*d};}
const near=(a,b,t,label)=>{if(!(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t))throw Error(`${label}: ${a} != ${b}`);};
const heldInitial=run.held.state;
const held=stored(heldInitial,0,heldInitial.contactRule),heldResidual=Math.max(...held.gradient.filter((_,i)=>i!==j).map(Math.abs));if(!Number.isFinite(heldResidual)||heldResidual>p.stationarityToleranceN)throw Error('Held residual');
const heldSurface=finitePoseAudit(arm.model,held.positions,heldInitial.qRad),heldRouting=finiteRoutingAudit(arm.model,Float64Array.from(heldInitial.coordinatesM));
if(heldSurface.transverseCrossingPairs||!heldRouting.accepted||held.contact.maximumSampledBonePenetrationM>0||held.contact.maximumSampledSoftPenetrationM>0||held.contact.maximumSampledTendonPenetrationM>0)throw Error('Held geometry');
function verifySteps(snapshots,attempts,initial){
 let old=initial;const rows=[];
 for(const [i,state] of snapshots.entries()){
 const attempt=attempts[i],r=attempt.receipt,h=attempt.hS,tau=attempt.effort>=old.activation?p.activationTimeS:p.releaseTimeS,activation=attempt.effort+(old.activation-attempt.effort)*Math.exp(-h/tau);
 near(state.activation,activation,1e-14,'activation');near(state.qRad,state.coordinatesM[j]/JOINT_SCALE_M,1e-14,'joint coordinate');near(state.timeS,old.timeS+h,1e-14,'time');near(state.omegaRadPerS,(state.qRad-old.qRad)/h,1e-14,'velocity');
 const prior=stored(old,old.activation,old.contactRule),oldAtRule=stored(old,old.activation,state.contactRule),oldAtActivation=stored(old,activation,state.contactRule),c=stored(state,activation,state.contactRule),G=rigid(state),G0=rigid(old),I=arm.baseInertiaKgM2+state.massKg*arm.gripRadiusSquaredM2;
 c.gradient[j]+=(G.gradient+I/h**2*(state.qRad-old.qRad-h*old.omegaRadPerS)+p.jointDampingNmS/h*(state.qRad-old.qRad))/JOINT_SCALE_M;
 const residual=Math.max(...c.gradient.map(Math.abs)),surface=finitePoseAudit(arm.model,c.positions,state.qRad),routing=finiteRoutingAudit(arm.model,Float64Array.from(state.coordinatesM));
 if(!Number.isFinite(residual)||residual>p.stationarityToleranceN||surface.transverseCrossingPairs||!routing.accepted||c.contact.maximumSampledBonePenetrationM>0||c.contact.maximumSampledSoftPenetrationM>0||c.contact.maximumSampledTendonPenetrationM>0)throw Error('Trajectory acceptance gate '+i);
 near(residual,r.maximumFreeModalGradientN,1e-9,'residual');
 const quadrature=oldAtRule.physicalPotentialJ-prior.physicalPotentialJ,activeWork=oldAtActivation.energies.activePotentialJ-c.energies.activePotentialJ,passive=z=>z.physicalPotentialJ-z.energies.activePotentialJ,oldE=passive(oldAtActivation)+G0.energy+.5*I*old.omegaRadPerS**2,newE=passive(c)+G.energy+.5*I*state.omegaRadPerS**2,damping=p.jointDampingNmS*h*state.omegaRadPerS**2,kineticDefect=.5*I*(state.omegaRadPerS-old.omegaRadPerS)**2,workDefect=newE-oldE-activeWork+damping+kineticDefect,impulse=h*JOINT_SCALE_M*c.gradient[j];
 for(const [a,b,label] of [[quadrature,r.referenceQuadratureUpdateJ,'quadrature event'],[activeWork,r.activeMechanicalWorkJ,'active work'],[oldE,r.oldMechanicalJ,'old energy'],[newE,r.newMechanicalJ,'new energy'],[workDefect,r.nonlinearWorkDefectJ,'work defect'],[impulse,r.impulseResidualNmS,'impulse']])near(a,b,1e-9,label);
 rows.push({step:i+1,label:attempt.label,timeS:state.timeS,qRad:state.qRad,activation,residualN:residual,transverseCrossingPairs:surface.transverseCrossingPairs,tendonViolations:routing.violations.length,minimumJ:Math.min(...c.headResults.map(h=>h.minJ)),referenceQuadratureUpdateJ:quadrature,activeMechanicalWorkJ:activeWork,nonlinearWorkDefectJ:workDefect,impulseResidualNmS:impulse});old=state;
 }
 return rows;
}
const rows=verifySteps(run.snapshots,run.attempts,run.held.state);
const viewer=read('audit/viewer-cache-load-results.json');
if(!viewer.accepted||JSON.stringify(viewer.parameters)!==JSON.stringify(run.parameters)||JSON.stringify(viewer.contactParameters)!==JSON.stringify(run.contactParameters))throw Error('Viewer load parameter mismatch');
for(const [p,h] of Object.entries(viewer.sourceHashes))if(hash(p)!==h){const archived='data/anatomical-arm-v1/audit/contact-missed-soft-v3/'+p;if(!fs.existsSync(root+archived)||hash(archived)!==h)throw Error('Missing viewer load execution source '+p);};
const viewerRows=verifySteps([viewer.state],[{label:'viewer-cache-load',effort:viewer.request.effort,hS:viewer.request.hS,receipt:viewer.receipt}],viewer.oldState);
const peak=Math.max(...run.snapshots.map(s=>s.qRad)),last=run.snapshots.at(-1),lift=Math.max(...run.snapshots.slice(0,run.requestedLiftSteps+1).map(s=>s.qRad))-run.held.state.qRad;
if(!(lift>0&&peak-last.qRad>0&&last.omegaRadPerS<0))throw Error('Loaded lift / release reversal absent');
const evidence={schema:1,result:'PASS',executionReceiptSHA256:hash('data/anatomical-arm-v1/audit/contact-lift-release-results.json'),verifierSHA256:hash('tools/verify-anatomical-contact-trajectory.mjs'),executionSourceHashes:run.sourceHashes,heldResidualN:heldResidual,heldGeometry:{surfaceAudit:heldSurface,routingAudit:heldRouting},viewerCacheLoad:{executionReceiptSHA256:hash('data/anatomical-arm-v1/audit/viewer-cache-load-results.json'),rows:viewerRows},verifiedSteps:rows.length,behavior:run.behavior,rows,limits:['Fresh evaluation of reduced stationary coordinates and finite triangle/axial-line gates; no optimizer used.','This is not full nodal, clinical, finite-radius tendon, coplanar or continuous-motion validation.','The work defect is reported, not asserted to vanish. Quadrature updates are separate numerical model events.']};
fs.writeFileSync(base+'audit/contact-lift-release-recheck.json',JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify({result:'PASS',steps:rows.length,behavior:evidence.behavior}));
