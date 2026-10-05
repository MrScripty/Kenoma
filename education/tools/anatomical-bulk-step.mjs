/** Controlled bulk sensitivity of one implicit dense increment. The frozen
 * dense prefix supplies the SAME old state for both material perturbations. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration,stepAnatomicalArm} from '../web/anatomical-arm.mjs';
import {contactRecipe,restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
import {modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {denseModalBody,incrementalGradient} from './anatomical-dense-quadrature.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',args=process.argv.slice(2),option=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];},factor=Number(option('--factor','2')),mode=option('--mode','solve'),prefixPath=base+'audit/anatomical-dense-loading-prefix.json',out=option('--output',base+`audit/anatomical-bulk-step-${factor}.json`),read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),plain=v=>JSON.parse(JSON.stringify(v,(_,x)=>ArrayBuffer.isView(x)?Array.from(x):x));
if(![.5,2].includes(factor)||!['solve','replay'].includes(mode))throw Error('Bulk diagnostic domain');
const prefix=JSON.parse(fs.readFileSync(prefixPath));for(const [p,h] of Object.entries(prefix.sourceHashes))if(hash(p)!==h)throw Error('Changed dense prefix '+p);
if(prefix.snapshots.length!==4||prefix.attempts.length!==4||!prefix.attempts.every(a=>a.accepted)||prefix.pointsPerElement!==256)throw Error('Accepted dense loading prefix required');
const index=3,old=plain(prefix.snapshots[2]),target=prefix.snapshots[3],request=prefix.attempts[3];Object.assign(old,{history:[],massEvents:[]});old.coordinatesM=Float64Array.from(old.coordinatesM);
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:prefix.parameters,contactParameters:prefix.contactParameters,routingRecipe:read('config/apparatus-routing.json')});
for(const b of arm.model.bodies){b.modal=denseModalBody(b.modal);b.material={...b.material,bulk:b.material.bulk*factor};}
arm.quadrature='diagnostic-subdivision-256';
let run;
if(mode==='solve'){
 if(fs.existsSync(out))throw Error('Preserve existing evidence: choose a new output path');
 const files=[...Object.keys(prefix.sourceHashes),'data/anatomical-arm-v1/audit/anatomical-dense-loading-prefix.json','tools/anatomical-bulk-step.mjs'];
 run={schema:1,result:'RUNNING',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),factor,parameters:prefix.parameters,contactParameters:prefix.contactParameters,oldState:plain(old),targetState:target,request:{effort:request.effort,hS:request.hS,maxIterationsPerFrozenContactRule:240},trace:[],limits:['One changed-material increment retains the identical accepted dense old state. It is not a new calibrated material or a bulk-dependent self-consistent trajectory.','Only muscle-body bulk moduli change. Stress matches, shear/fibre terms, attachment/contact parameters, modes, solver and acceptance gates are unchanged.','Full P2 body projection and finite geometry checks do not qualify full nodal, mesh, determinant, time or integration convergence.']};
 const save=()=>fs.writeFileSync(out,JSON.stringify(run,null,2)+'\n');save();arm.onIteration=r=>{const row={iteration:r.iteration,residualN:r.maxGradient,step:r.step};run.trace.push(row);save();console.log('ITERATION',JSON.stringify(row));};
 const begin=performance.now(),before=plain(old),step=stepAnatomicalArm(arm,old,{effort:request.effort,h:request.hS,maxIterations:240,startCoordinates:Float64Array.from(target.coordinatesM)});
 run.elapsedMS=performance.now()-begin;run.accepted=step.accepted;run.result=step.accepted?'ACCEPTED_BULK_COMPARISON':'REJECTED_BULK_COMPARISON';run.reason=step.reason;run.solverReceipt=plain(step.accepted?step.receipt:{residualN:step.maxGradientN,contactRefinement:step.result.contactRefinement,iterations:step.result.acceptedIterations});
 run.candidate=plain(step.accepted?{...step.state,history:undefined}:{coordinatesM:step.result.fullCoordinates,contactRule:step.result.candidateContactRule});
 run.rollback=step.accepted?null:{sameStateObject:step.state===old,stateUnchanged:JSON.stringify(plain(old))===JSON.stringify(before),oldContactRestored:JSON.stringify(contactRecipe(arm.contact))===JSON.stringify(old.contactRule)};save();console.log('RESULT',run.result,run.reason);
}else{run=JSON.parse(fs.readFileSync(out));for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed bulk execution '+p);if(run.factor!==factor||JSON.stringify(run.oldState)!==JSON.stringify(plain(old))||JSON.stringify(run.targetState)!==JSON.stringify(target))throw Error('Changed comparison state');}
const near=(a,b,t,label)=>{if(!(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t))throw Error(`${label}: ${a} vs ${b}`);},x=Float64Array.from(run.candidate.coordinatesM),q=x[arm.model.jointIndex]/JOINT_SCALE_M,tau=request.effort>=old.activation?arm.parameters.activationTimeS:arm.parameters.releaseTimeS,activation=request.effort+(old.activation-request.effort)*Math.exp(-request.hS/tau);
if(run.accepted){near(run.candidate.qRad,q,1e-14,'q');near(run.candidate.activation,activation,1e-14,'activation');near(run.candidate.timeS,old.timeS+request.hS,1e-14,'time');near(run.candidate.omegaRadPerS,(q-old.qRad)/request.hS,1e-14,'velocity');}
restoreContactRecipe(arm.contact,run.candidate.contactRule);
const c=anatomicalConfiguration(arm,x,activation,{hessian:false}),gradient=incrementalGradient(arm,c,{qRad:q,massKg:old.massKg},old,request.hS),independent=gradient.slice(),heads=[];
let maximumGradientAssemblyDifferenceN=0;
for(const b of arm.model.bodies){const coordinates=x.slice(b.offset,b.offset+63),a=['FJ1486','FJ1512','FJ1478'].includes(b.id)?activation:0,modal=evaluateModalBody(b.modal,coordinates,a,{material:b.material,hessian:false}),full=evaluateCompressionBody(prepareCompressionBody(b.modal.source,b.modal.nodeModes,2),modalPositions(b.modal,coordinates),a,b.material),gd=Math.max(...modal.gradient.map((v,k)=>Math.abs(v-full.gradientN[k])));if(gd>2e-6||Math.abs(modal.energy-full.energyJ)>2e-10)throw Error('P2 projection');maximumGradientAssemblyDifferenceN=Math.max(maximumGradientAssemblyDifferenceN,gd);for(let k=0;k<63;k++)independent[b.offset+k]+=full.gradientN[k]-modal.gradient[k];heads.push({elementId:b.id,bulkPa:b.material.bulk,minimumJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeFractionBelow09:full.referenceVolumeFractionBelow09});}
const residualN=Math.max(...gradient.map(Math.abs)),independentResidualN=Math.max(...independent.map(Math.abs)),surface=finitePoseAudit(arm.model,c.positions,q),routing=finiteRoutingAudit(arm.model,x),sampledPenetrationsM={bone:c.contact.maximumSampledBonePenetrationM,soft:c.contact.maximumSampledSoftPenetrationM,tendon:c.contact.maximumSampledTendonPenetrationM},passes=residualN<=arm.parameters.stationarityToleranceN&&independentResidualN<=arm.parameters.stationarityToleranceN&&!surface.transverseCrossingPairs&&routing.accepted&&Object.values(sampledPenetrationsM).every(v=>v===0);
if(run.accepted&&!passes)throw Error('Bulk acceptance failure');if(!run.accepted&&(passes||!Object.values(run.rollback).every(v=>v===true)))throw Error('Bulk rejection or rollback not reproduced');
if(run.accepted)near(residualN,run.solverReceipt.maximumFreeModalGradientN,1e-9,'solver residual');
const replay={schema:1,result:run.accepted?'PASS_ACCEPTED_BULK_COMPARISON':'PASS_PRESERVED_BULK_REJECTION',executionReceiptSHA256:createHash('sha256').update(fs.readFileSync(out)).digest('hex'),verifierSHA256:hash('tools/anatomical-bulk-step.mjs'),factor,residualN,independentResidualN,maximumGradientAssemblyDifferenceN,surfaceAudit:surface,routingAudit:routing,sampledPenetrationsM,heads,angleDifferenceRad:q-target.qRad,maximumCoordinateDifferenceM:Math.max(...x.map((v,k)=>Math.abs(v-target.coordinatesM[k]))),limits:run.limits};
fs.writeFileSync(out.replace(/\.json$/,'-recheck.json'),JSON.stringify(replay,null,2)+'\n');console.log('REPLAY',JSON.stringify(replay));
