/** Frozen replay/spectrum inputs. No optimizer and no state advancement. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {denseModalBody,incrementalGradient} from './anatomical-dense-quadrature.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';

const base='data/anatomical-arm-v1/',out=base+'review/dense-release-rejection';
assert.ok(!fs.existsSync(out),'Preserve existing diagnostic');fs.mkdirSync(out,{recursive:true});
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),inputs={};
const read=p=>{inputs[p]=hash(p);return JSON.parse(fs.readFileSync(p));};
const fine=read(base+'audit/anatomical-dense-release-refinement.json'),replay=read(base+'audit/anatomical-dense-release-refinement-recheck.json'),coarse=read(base+'audit/anatomical-dense-trajectory.json'),coarseReplay=read(base+'audit/anatomical-dense-trajectory-recheck.json');
assert.equal(replay.result,'PASS_PRESERVED_REJECTION');assert.equal(replay.executionReceiptSHA256,inputs[base+'audit/anatomical-dense-release-refinement.json']);assert.equal(coarseReplay.result,'PASS_DENSE_TRAJECTORY');assert.equal(coarseReplay.executionReceiptSHA256,inputs[base+'audit/anatomical-dense-trajectory.json']);
for(const [p,h] of Object.entries(fine.sourceHashes))assert.equal(hash(p),h,'Original execution source '+p);
assert.equal(JSON.stringify(fine.parameters),JSON.stringify(coarse.parameters));assert.equal(JSON.stringify(fine.contactParameters),JSON.stringify(coarse.contactParameters));
const arm=prepareAnatomicalArm(read(base+'generated/arm-reference.json'),read(base+'config/attachments-apparatus.json'),read(base+'audit/modal-fixed-end-results.json'),{parameters:fine.parameters,contactParameters:fine.contactParameters,routingRecipe:read(base+'config/apparatus-routing.json')});
for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);
const p=arm.parameters,n=arm.model.ndof,j=arm.model.jointIndex,oldFine=fine.snapshots.at(-1),request=fine.attempts.at(-1),h=request.hS;
const rejected={...oldFine,coordinatesM:fine.rejectedCandidate.coordinatesM,qRad:fine.rejectedCandidate.coordinatesM[j]/JOINT_SCALE_M,activation:oldFine.activation*Math.exp(-h/p.releaseTimeS),timeS:oldFine.timeS+h,contactRule:fine.rejectedCandidate.contactRule};
const accepted=coarse.snapshots.at(-1),oldCoarse=coarse.snapshots.at(-2),coarseH=coarse.attempts.at(-1).hS;
assert.ok(Math.abs(rejected.timeS-accepted.timeS)<1e-12);assert.ok(Math.abs(rejected.activation-accepted.activation)<1e-13);
function matrix(state,old,step){
 restoreContactRecipe(arm.contact,state.contactRule);const c=anatomicalConfiguration(arm,Float64Array.from(state.coordinatesM),state.activation),gradient=incrementalGradient(arm,c,state,old,step),H=c.hessian.slice(),q=state.qRad;
 const com=attachmentMap(arm.comM,arm.model.frame,q),grip=attachmentMap(arm.gripM,arm.model.frame,q),axis=arm.model.frame.axis_unit,crossZ=v=>axis[0]*v[1]-axis[1]*v[0],I=arm.baseInertiaKgM2+state.massKg*arm.gripRadiusSquaredM2,stop=q<p.minimumAngleRad||q>p.maximumAngleRad?p.stopStiffnessNmPerRad:0;
 const extra=(p.gMPerS2*(p.segmentMassKg*crossZ(com.B)+state.massKg*crossZ(grip.B))+stop+I/step**2+p.jointDampingNmS/step)/JOINT_SCALE_M**2;H[j*n+j]+=extra;
 return {c,gradient,H,extra};
}
const named={};
for(const [name,state,old,step] of [['rejected-native',rejected,oldFine,h],['coarse-native',accepted,oldCoarse,coarseH]]){
 console.log('EVALUATING',name);const r=matrix(state,old,step);named[name]=r;
 fs.writeFileSync(out+'/'+name+'-hessian.f64',Buffer.from(r.H.buffer));fs.writeFileSync(out+'/'+name+'-gradient.f64',Buffer.from(r.gradient.buffer));
 const indices=Array.from({length:n},(_,k)=>k).sort((a,b)=>Math.abs(r.gradient[b])-Math.abs(r.gradient[a]));
 named[name].summary={timeS:state.timeS,oldTimeS:old.timeS,hS:step,qRad:state.qRad,activation:state.activation,residualN:Math.abs(r.gradient[indices[0]]),jointGradientN:r.gradient[j],dynamicAndGravityJointHessianNPerM:r.extra,largestComponents:indices.slice(0,12).map(k=>({index:k,body:arm.model.bodies.find(b=>k>=b.offset&&k<b.offset+63)?.id??(k===j?'joint':'apparatus'),localIndex:arm.model.bodies.find(b=>k>=b.offset&&k<b.offset+63)?k-arm.model.bodies.find(b=>k>=b.offset&&k<b.offset+63).offset:null,valueN:r.gradient[k]})),energyJ:r.c.physicalPotentialJ,contact:r.c.contact};
 assert.ok(Math.abs(named[name].summary.residualN-(name==='rejected-native'?replay.rejected.residualN:coarseReplay.rows.at(-1).residualN))<1e-9);
}
// Same coordinates, activation, material integration, old state and contact rule.
// Only h changes in a frozen incremental objective; this is not a trajectory.
const frozenFine=named['rejected-native'],frozenCoarseGradient=incrementalGradient(arm,frozenFine.c,rejected,oldFine,coarseH),nonJointDifference=Math.max(...frozenCoarseGradient.map((v,k)=>k===j?0:Math.abs(v-frozenFine.gradient[k])));
assert.equal(nonJointDifference,0);
const I=arm.baseInertiaKgM2+rejected.massKg*arm.gripRadiusSquaredM2,hessianJointDifference=(I/coarseH**2+p.jointDampingNmS/coarseH-I/h**2-p.jointDampingNmS/h)/JOINT_SCALE_M**2;
const frozenProbe={description:'Identical rejected pose, accepted old state, activation, mass, integration and contact rule; only objective h varies. No activation re-integration or solve.',hS:[h,coarseH],nonJointGradientDifferenceN:nonJointDifference,jointGradientN:[frozenFine.gradient[j],frozenCoarseGradient[j]],jointHessianDifferenceNPerM:hessianJointDifference,coarseObjectiveResidualN:Math.max(...frozenCoarseGradient.map(Math.abs))};
const positions=s=>arm.model.bodies.map(b=>modalPositions(b.modal,s.coordinatesM.slice(b.offset,b.offset+63)));
const matched=[];for(const [i,a] of coarse.snapshots.entries()){const k=fine.snapshots.findIndex(b=>Math.abs(a.timeS-b.timeS)<1e-12);if(k<0)continue;const b=fine.snapshots[k],pa=positions(a),pb=positions(b);let nodal=0;for(let head=0;head<pa.length;head++)for(let node=0;node<pa[head].length;node++)nodal=Math.max(nodal,Math.hypot(...pa[head][node].map((v,d)=>v-pb[head][node][d])));assert.ok(Math.abs(a.activation-b.activation)<1e-13);matched.push({timeS:a.timeS,angleDifferenceDeg:(b.qRad-a.qRad)*180/Math.PI,maximumNodalDifferenceM:nodal,coarseResidualN:coarseReplay.rows[i].independentResidualN,fineResidualN:replay.rows[k].independentResidualN});}
const prev=fine.snapshots.at(-2),predictor=oldFine.coordinatesM.map((v,k)=>v+h/(oldFine.timeS-prev.timeS)*(v-prev.coordinatesM[k])),baseline=read(base+'audit/contact-lift-release-results.json'),originalGuess=baseline.snapshots[request.baselineIndex];
const maxCoordinate=(a,b)=>Math.max(...a.map((v,k)=>k===j?0:Math.abs(v-b[k])));
const seedComparison={originalGuessStrategy:request.guessStrategy,oldAngleDeg:oldFine.qRad*180/Math.PI,originalGuessAngleDeg:originalGuess.qRad*180/Math.PI,acceptedSecantPredictorAngleDeg:predictor[j]/JOINT_SCALE_M*180/Math.PI,rejectedCandidateAngleDeg:rejected.qRad*180/Math.PI,maximumOriginalGuessChangeM:maxCoordinate(originalGuess.coordinatesM,oldFine.coordinatesM),maximumPredictorChangeM:maxCoordinate(predictor,oldFine.coordinatesM)};
const trace=fine.trace.filter(r=>r.stage===fine.snapshots.length),receipt={schema:1,result:'PASS_FROZEN_DENSE_REJECTION_DIAGNOSIS',ndof:n,jointIndex:j,bodyOffsets:arm.model.bodies.map(b=>({id:b.id,offset:b.offset,count:63})),stationarityToleranceN:p.stationarityToleranceN,native:Object.fromEntries(Object.entries(named).map(([name,r])=>[name,r.summary])),frozenProbe,matched,seedComparison,rejection:{reason:request.reason,retainedOldTimeS:oldFine.timeS,rejectedTargetTimeS:rejected.timeS,iterations:trace.length,minimumTraceResidualN:Math.min(...trace.map(r=>r.residualN)),finalTraceResidualN:trace.at(-1).residualN,contactRefinement:fine.rejectedCandidate.contactRefinement,geometry:{minimumCornerJ:replay.rejected.minimumCornerJ,crossings:replay.rejected.surfaceAudit.transverseCrossingPairs,routingAccepted:replay.rejected.routingAudit.accepted,sampledPenetrationsM:replay.rejected.sampledPenetrationsM},rollback:fine.rollback},sourceHashes:{...fine.sourceHashes,...inputs,'tools/diagnose-dense-release-rejection.mjs':hash('tools/diagnose-dense-release-rejection.mjs')},limits:['Native coarse/fine objectives have different accepted histories; this is explicitly separate from the identical-pose/old-state probe.','The fixed-h probe holds activation constant to isolate the objective operator; it is not a valid alternative physical increment.','Saved rejection replay labels retained old time; target time is explicitly recomputed as old+h here.','Spectra of the reduced objective do not prove whole-tissue/full-nodal stability or feasibility.']};
fs.writeFileSync(out+'/frozen.json',JSON.stringify(receipt,null,2)+'\n');console.log('RESULT',receipt.result,JSON.stringify({native:Object.fromEntries(Object.entries(named).map(([k,v])=>[k,{residualN:v.summary.residualN,largest:v.summary.largestComponents[0]}])),frozenProbe,seedComparison}));
