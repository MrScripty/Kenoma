/** No optimizer: independently project full P2 body forces at EVERY state,
 * replay temporal lineage, finite geometry and the mechanical ledger. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {denseModalBody,incrementalGradient} from './anatomical-dense-quadrature.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',args=process.argv.slice(2),option=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];},input=option('--input',base+'audit/anatomical-dense-trajectory.json'),output=option('--output',base+'audit/anatomical-dense-trajectory-recheck.json'),read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),run=JSON.parse(fs.readFileSync(input)),baseline=read('audit/contact-lift-release-results.json');
const near=(a,b,t,label)=>{if(!(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t))throw Error(`${label}: ${a} vs ${b}`);};
for(const [p,h] of Object.entries(run.sourceHashes))if(hash(root+p)!==h)throw Error('Changed execution source '+p);
if(run.pointsPerElement!==256||run.parameters.stationarityToleranceN!==.0001||JSON.stringify(run.parameters)!==JSON.stringify(baseline.parameters)||JSON.stringify(run.contactParameters)!==JSON.stringify(baseline.contactParameters)||!run.held?.accepted)throw Error('Changed dense parameters or no accepted held state');
if(!['ACCEPTED_DENSE_TRAJECTORY','REJECTED_INCREMENT'].includes(run.result)||run.snapshots.length!==run.attempts.filter(a=>a.accepted).length)throw Error('Incomplete or inconsistent execution');
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),p=arm.parameters,j=arm.model.jointIndex;
for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);
const prepared=arm.model.bodies.map(b=>prepareCompressionBody(b.modal.source,b.modal.nodeModes,2));
let maximumGradientAssemblyDifferenceN=0,maximumEnergyAssemblyDifferenceJ=0;
const stored=(s,a,rule)=>{restoreContactRecipe(arm.contact,rule);return anatomicalConfiguration(arm,Float64Array.from(s.coordinatesM),a,{hessian:false});};
function rigid(s){const com=attachmentMap(arm.comM,arm.model.frame,s.qRad),grip=attachmentMap(arm.gripM,arm.model.frame,s.qRad),d=s.qRad<p.minimumAngleRad?s.qRad-p.minimumAngleRad:s.qRad>p.maximumAngleRad?s.qRad-p.maximumAngleRad:0;return p.gMPerS2*(p.segmentMassKg*com.position[2]+s.massKg*grip.position[2])+.5*p.stopStiffnessNmPerRad*d*d;}
function audit(state,old,request){
 const x=Float64Array.from(state.coordinatesM),c=stored(state,state.activation,state.contactRule),gradient=old?incrementalGradient(arm,c,state,old,request.hS):c.gradient.slice(),independent=gradient.slice(),heads=[];
 for(const [bi,b] of arm.model.bodies.entries()){
  const coordinates=x.slice(b.offset,b.offset+63),a=['FJ1486','FJ1512','FJ1478'].includes(b.id)?state.activation:0,modal=evaluateModalBody(b.modal,coordinates,a,{material:b.material,hessian:false}),full=evaluateCompressionBody(prepared[bi],modalPositions(b.modal,coordinates),a,b.material);
  const gd=Math.max(...modal.gradient.map((v,k)=>Math.abs(v-full.gradientN[k]))),ed=Math.abs(modal.energy-full.energyJ);
  if(gd>2e-6||ed>2e-10)throw Error('Independent P2 projection '+b.id);near(modal.minJ,full.minimumJ,1e-12,'J');
  maximumGradientAssemblyDifferenceN=Math.max(maximumGradientAssemblyDifferenceN,gd);maximumEnergyAssemblyDifferenceJ=Math.max(maximumEnergyAssemblyDifferenceJ,ed);
  for(let k=0;k<63;k++)independent[b.offset+k]+=full.gradientN[k]-modal.gradient[k];
  heads.push({elementId:b.id,minimumJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeFractionBelow09:full.referenceVolumeFractionBelow09,volumeEnergyJ:full.energies.volume});
 }
 if(!old){gradient[j]=0;independent[j]=0;}
 const residualN=Math.max(...gradient.map(Math.abs)),independentResidualN=Math.max(...independent.map(Math.abs)),surface=finitePoseAudit(arm.model,c.positions,state.qRad),routing=finiteRoutingAudit(arm.model,x),sampledPenetrationsM={bone:c.contact.maximumSampledBonePenetrationM,soft:c.contact.maximumSampledSoftPenetrationM,tendon:c.contact.maximumSampledTendonPenetrationM};
 const passes=residualN<=p.stationarityToleranceN&&independentResidualN<=p.stationarityToleranceN&&surface.transverseCrossingPairs===0&&routing.accepted&&Object.values(sampledPenetrationsM).every(v=>v===0);
 return {c,gradient,passes,row:{timeS:state.timeS,qRad:state.qRad,activation:state.activation,residualN,independentResidualN,minimumJ:Math.min(...heads.map(h=>h.minimumJ)),minimumCornerJ:Math.min(...heads.map(h=>h.minimumCornerJ)),heads,surfaceAudit:surface,routingAudit:routing,sampledPenetrationsM}};
}
const held=run.held.state;near(held.timeS,0,0,'held time');near(held.activation,0,0,'held activation');near(held.omegaRadPerS,0,0,'held velocity');near(held.massKg,baseline.held.state.massKg,0,'mass');near(held.qRad,arm.model.frame.atlas_bind_angle_rad,1e-14,'held angle');
const heldAudit=audit(held);if(!heldAudit.passes)throw Error('Held acceptance');near(heldAudit.row.residualN,run.held.receipt.maximumFreeModalGradientN,1e-9,'held residual');
let old=held;const rows=[];
for(const [i,state] of run.snapshots.entries()){
 const request=run.schedule[i],attempt=run.attempts[i],r=attempt.receipt,b=baseline.attempts[request.baselineIndex];
 if(!attempt.accepted||attempt.hS!==request.hS||attempt.effort!==request.effort||request.hS!==b.hS/run.timeRefinementFactor||request.effort!==b.effort)throw Error('Changed schedule');
 const tau=request.effort>=old.activation?p.activationTimeS:p.releaseTimeS;
 near(state.activation,request.effort+(old.activation-request.effort)*Math.exp(-request.hS/tau),1e-14,'activation lineage');near(state.qRad,state.coordinatesM[j]/JOINT_SCALE_M,1e-14,'joint coordinate');near(state.timeS,old.timeS+request.hS,1e-14,'time lineage');near(state.omegaRadPerS,(state.qRad-old.qRad)/request.hS,1e-14,'velocity lineage');near(state.massKg,old.massKg,0,'mass lineage');
 const checked=audit(state,old,request);if(!checked.passes)throw Error('Acceptance gate '+i);near(checked.row.residualN,r.maximumFreeModalGradientN,1e-9,'solver residual');
 const prior=stored(old,old.activation,old.contactRule),oldAtRule=stored(old,old.activation,state.contactRule),oldAtActivation=stored(old,state.activation,state.contactRule),c=checked.c,I=arm.baseInertiaKgM2+state.massKg*arm.gripRadiusSquaredM2,passive=z=>z.physicalPotentialJ-z.energies.activePotentialJ;
 const quadrature=oldAtRule.physicalPotentialJ-prior.physicalPotentialJ,activeWork=oldAtActivation.energies.activePotentialJ-c.energies.activePotentialJ,oldE=passive(oldAtActivation)+rigid(old)+.5*I*old.omegaRadPerS**2,newE=passive(c)+rigid(state)+.5*I*state.omegaRadPerS**2,damping=p.jointDampingNmS*request.hS*state.omegaRadPerS**2,kineticDefect=.5*I*(state.omegaRadPerS-old.omegaRadPerS)**2,workDefect=newE-oldE-activeWork+damping+kineticDefect,impulse=request.hS*JOINT_SCALE_M*checked.gradient[j];
 for(const [a,b,label] of [[quadrature,r.referenceQuadratureUpdateJ,'rule energy event'],[activeWork,r.activeMechanicalWorkJ,'active work'],[oldE,r.oldMechanicalJ,'old energy'],[newE,r.newMechanicalJ,'new energy'],[workDefect,r.nonlinearWorkDefectJ,'work defect'],[impulse,r.impulseResidualNmS,'impulse']])near(a,b,1e-9,label);
 rows.push({...checked.row,step:i+1,label:request.label,referenceQuadratureUpdateJ:quadrature,activeMechanicalWorkJ:activeWork,nonlinearWorkDefectJ:workDefect,impulseResidualNmS:impulse,angleDifferenceFrom32Rad:state.qRad-baseline.snapshots[request.baselineIndex].qRad,matchedBaselineTime:request.part===run.timeRefinementFactor});old=state;console.log('VERIFIED',i,state.timeS,checked.row.independentResidualN);
}
let rejected=null;
if(run.result==='REJECTED_INCREMENT'){
 const request=run.attempts.at(-1),x=run.rejectedCandidate.coordinatesM,tau=request.effort>=old.activation?p.activationTimeS:p.releaseTimeS,state={...old,coordinatesM:x,qRad:x[j]/JOINT_SCALE_M,activation:request.effort+(old.activation-request.effort)*Math.exp(-request.hS/tau),contactRule:run.rejectedCandidate.contactRule},checked=audit(state,old,request);
 if(checked.passes||!Object.values(run.rollback).every(v=>v===true))throw Error('Unreproducible rejection or rollback');rejected={reason:request.reason,...checked.row};
}else if(!run.completedAllSteps||!run.behaviorAccepted||run.snapshots.length!==run.schedule.length)throw Error('Unqualified completion');
const result={schema:1,result:rejected?'PASS_PRESERVED_REJECTION':'PASS_DENSE_TRAJECTORY',executionReceiptSHA256:hash(input),verifierSHA256:hash(fileURLToPath(import.meta.url)),pointsPerElement:256,unchangedStationarityToleranceN:p.stationarityToleranceN,verifiedSteps:rows.length,maximumGradientAssemblyDifferenceN,maximumEnergyAssemblyDifferenceJ,held:heldAudit.row,rows,rejected,behavior:run.behavior,limits:run.limits};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');console.log('RESULT',result.result,rows.length);
