/** Independent full P2 gradient assembly and finite geometry replay. No solve. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {denseModalBody,incrementalGradient} from './anatomical-dense-quadrature.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/anatomical-dense-step.json'),baseline=read('audit/contact-lift-release-results.json');
const near=(a,b,t,label)=>{if(!(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t))throw Error(`${label}: ${a} vs ${b}`);};
for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed dense-step source '+p);
if(run.pointsPerElement!==256||run.parameters.stationarityToleranceN!==.0001||JSON.stringify(run.parameters)!==JSON.stringify(baseline.parameters)||JSON.stringify(run.contactParameters)!==JSON.stringify(baseline.contactParameters))throw Error('Changed accuracy experiment parameters');
if(!['ACCEPTED_SAME_OLD_STATE_COMPARISON','REJECTED_SAME_OLD_STATE_COMPARISON'].includes(run.result))throw Error('Incomplete accuracy experiment');
const i=run.baselineIndex,old=run.oldState,target=baseline.snapshots[i],request=baseline.attempts[i];
for(const key of ['coordinatesM','contactRule','qRad','omegaRadPerS','activation','massKg','timeS'])if(JSON.stringify(old[key])!==JSON.stringify(baseline.snapshots[i-1][key]))throw Error('Changed old state '+key);
if(JSON.stringify(run.baselineState)!==JSON.stringify(target)||request.hS!==run.request.hS||request.effort!==run.request.effort)throw Error('Changed baseline or increment');
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')});
for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);
restoreContactRecipe(arm.contact,target.contactRule);
const frozen=anatomicalConfiguration(arm,Float64Array.from(target.coordinatesM),target.activation,{hessian:false}),frozenResidualN=Math.max(...incrementalGradient(arm,frozen,target,old,request.hS).map(Math.abs));
near(frozenResidualN,run.frozenResidualN,1e-9,'frozen residual');
const state=run.candidate,x=Float64Array.from(state.coordinatesM),q=x[arm.model.jointIndex]/JOINT_SCALE_M,tau=request.effort>=old.activation?arm.parameters.activationTimeS:arm.parameters.releaseTimeS,activation=request.effort+(old.activation-request.effort)*Math.exp(-request.hS/tau);
near(state.activation,activation,1e-14,'activation');
if(run.accepted){near(state.qRad,q,1e-14,'q');near(state.timeS,old.timeS+request.hS,1e-14,'time');near(state.omegaRadPerS,(q-old.qRad)/request.hS,1e-14,'omega');}
restoreContactRecipe(arm.contact,state.contactRule);
const c=anatomicalConfiguration(arm,x,activation,{hessian:false}),gradient=incrementalGradient(arm,c,{qRad:q,massKg:old.massKg},old,request.hS),independent=gradient.slice(),heads=[];
let maximumGradientAssemblyDifferenceN=0,maximumEnergyAssemblyDifferenceJ=0;
for(const b of arm.model.bodies){
 const coordinates=x.slice(b.offset,b.offset+63),a=['FJ1486','FJ1512','FJ1478'].includes(b.id)?activation:0,modal=evaluateModalBody(b.modal,coordinates,a,{material:b.material,hessian:false}),full=evaluateCompressionBody(prepareCompressionBody(b.modal.source,b.modal.nodeModes,2),modalPositions(b.modal,coordinates),a,b.material),gd=Math.max(...modal.gradient.map((v,k)=>Math.abs(v-full.gradientN[k]))),ed=Math.abs(modal.energy-full.energyJ);
 if(gd>2e-6||ed>2e-10)throw Error('Full P2 projection '+b.id);near(modal.minJ,full.minimumJ,1e-12,'minimum J');
 maximumGradientAssemblyDifferenceN=Math.max(maximumGradientAssemblyDifferenceN,gd);maximumEnergyAssemblyDifferenceJ=Math.max(maximumEnergyAssemblyDifferenceJ,ed);
 for(let k=0;k<63;k++)independent[b.offset+k]+=full.gradientN[k]-modal.gradient[k];
 heads.push({elementId:b.id,minimumJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeFractionBelow09:full.referenceVolumeFractionBelow09,volumeEnergyJ:full.energies.volume});
}
const residualN=Math.max(...gradient.map(Math.abs)),independentResidualN=Math.max(...independent.map(Math.abs)),surface=finitePoseAudit(arm.model,c.positions,q),routing=finiteRoutingAudit(arm.model,x),sampledPenetrationsM={bone:c.contact.maximumSampledBonePenetrationM,soft:c.contact.maximumSampledSoftPenetrationM,tendon:c.contact.maximumSampledTendonPenetrationM};
const passesGates=residualN<=arm.parameters.stationarityToleranceN&&independentResidualN<=arm.parameters.stationarityToleranceN&&!surface.transverseCrossingPairs&&routing.accepted&&Object.values(sampledPenetrationsM).every(v=>v===0);
if(run.accepted&&!passesGates)throw Error('Dense acceptance gates');
if(!run.accepted&&(!run.restoredOldContactOnReject||passesGates))throw Error('Rejected case has no reproducible gate failure or rollback');
if(run.accepted){near(residualN,run.solverReceipt.maximumFreeModalGradientN,1e-9,'solver residual');near(residualN,run.freshCheck.residualN,1e-9,'fresh residual');}
const result={schema:1,result:run.accepted?'PASS_ACCEPTED_COMPARISON':'PASS_PRESERVED_REJECTION',executionReceiptSHA256:hash('data/anatomical-arm-v1/audit/anatomical-dense-step.json'),verifierSHA256:hash('tools/verify-anatomical-dense-step.mjs'),unchangedStationarityToleranceN:arm.parameters.stationarityToleranceN,frozenResidualN,residualN,independentResidualN,maximumGradientAssemblyDifferenceN,maximumEnergyAssemblyDifferenceJ,surfaceAudit:surface,routingAudit:routing,sampledPenetrationsM,heads,angleDifferenceRad:q-target.qRad,maximumCoordinateDifferenceM:Math.max(...x.map((v,k)=>Math.abs(v-target.coordinatesM[k]))),limits:run.limits};
fs.writeFileSync(base+'audit/anatomical-dense-step-recheck.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({result:result.result,residualN,independentResidualN,angleDifferenceRad:result.angleDifferenceRad,heads}));
