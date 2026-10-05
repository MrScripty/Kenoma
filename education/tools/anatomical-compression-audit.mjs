import {recordedInputMatches} from './recorded-inputs.mjs';
/** Frozen-pose sensitivity of the actual accepted anatomical trajectory.
 * Independent P2 element assembly; no changed state is accepted or advanced.
 */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/';
const read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
const run=read('audit/contact-lift-release-results.json'),check=read('audit/contact-lift-release-recheck.json');
if(check.result!=='PASS'||check.executionReceiptSHA256!==hash('data/anatomical-arm-v1/audit/contact-lift-release-results.json')||check.verifierSHA256!==hash('tools/verify-anatomical-contact-trajectory.mjs'))throw Error('A current source-bound accepted trajectory is required');
for(const [p,h] of Object.entries(run.sourceHashes))if(!recordedInputMatches(p,h))throw Error('Changed execution input '+p);
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),j=arm.model.jointIndex,p=arm.parameters;
const worst=check.rows.reduce((best,r,i)=>r.minimumJ<check.rows[best].minimumJ?i:best,0),peak=run.snapshots.reduce((best,s,i)=>s.qRad>run.snapshots[best].qRad?i:best,0);
const selected=new Set([-1,0,worst,peak,run.snapshots.length-1]);
const states=[{label:'held',state:run.held.state,index:-1},...run.snapshots.map((state,index)=>({label:run.attempts[index].label,state,index}))];
const diagnostics=states.map(({label,state,index})=>({label,index,timeS:state.timeS,qRad:state.qRad,activation:state.activation,heads:[],selectedForDenseAudit:selected.has(index)}));
const baselines=new Map();
for(const {state,index} of states.filter(s=>selected.has(s.index))){
 restoreContactRecipe(arm.contact,state.contactRule);
 const c=anatomicalConfiguration(arm,Float64Array.from(state.coordinatesM),state.activation,{hessian:false}),gradient=c.gradient.slice();
 if(index>=0){
  const old=index?run.snapshots[index-1]:run.held.state,h=run.attempts[index].hS,q=state.qRad;
  const com=attachmentMap(arm.comM,arm.model.frame,q),grip=attachmentMap(arm.gripM,arm.model.frame,q),stop=q<p.minimumAngleRad?q-p.minimumAngleRad:q>p.maximumAngleRad?q-p.maximumAngleRad:0,I=arm.baseInertiaKgM2+state.massKg*arm.gripRadiusSquaredM2;
  gradient[j]+=(p.gMPerS2*(p.segmentMassKg*com.B[2]+state.massKg*grip.B[2])+p.stopStiffnessNmPerRad*stop+I/h**2*(q-old.qRad-h*old.omegaRadPerS)+p.jointDampingNmS/h*(q-old.qRad))/JOINT_SCALE_M;
 }
 const residual=Math.max(...gradient.filter((_,k)=>index>=0||k!==j).map(Math.abs));
 const recorded=index>=0?check.rows[index].residualN:check.heldResidualN;
 if(!Number.isFinite(residual)||residual>p.stationarityToleranceN||Math.abs(residual-recorded)>1e-9)throw Error('Frozen original balance '+index);
 baselines.set(index,{gradient,residual,volumeEnergyJ:0,bulkGradient:new Float64Array(arm.model.ndof),quadDeltas:[new Float64Array(arm.model.ndof),new Float64Array(arm.model.ndof),new Float64Array(arm.model.ndof)]});
}
let maximumModalProjectionDifferenceN=0,maximumModalEnergyDifferenceJ=0;
const summarize=r=>({bodyEnergyJ:r.energyJ,volumeEnergyJ:r.energies.volume,minimumJ:r.minimumJ,minimumCornerJ:r.minimumCornerJ,globalVolumeRatio:r.globalVolumeRatio,referenceVolumeFractionBelow09:r.referenceVolumeFractionBelow09});
for(const [bi,b] of arm.model.bodies.entries()){
 const prepared=[0,1,2].map(depth=>prepareCompressionBody(b.modal.source,b.modal.nodeModes,depth));
 for(const [si,{state,index}] of states.entries()){
  const x=Float64Array.from(state.coordinatesM.slice(b.offset,b.offset+63)),positions=modalPositions(b.modal,x),activation=['FJ1486','FJ1512','FJ1478'].includes(b.id)?state.activation:0;
  const profiles=prepared.slice(0,selected.has(index)?3:2).map(body=>evaluateCompressionBody(body,positions,activation,b.material));
  const modal=evaluateModalBody(b.modal,x,activation,{material:b.material,hessian:false}),exact32=profiles[1];
  const gd=Math.max(...modal.gradient.map((v,k)=>Math.abs(v-exact32.gradientN[k]))),ed=Math.abs(modal.energy-exact32.energyJ);
  maximumModalProjectionDifferenceN=Math.max(maximumModalProjectionDifferenceN,gd);maximumModalEnergyDifferenceJ=Math.max(maximumModalEnergyDifferenceJ,ed);
  if(gd>2e-6||ed>2e-10||Math.abs(modal.minJ-exact32.minimumJ)>1e-12)throw Error('Independent P2 projection mismatch '+b.id+' '+index);
  diagnostics[si].heads.push({elementId:b.id,material:b.material,quadrature:profiles.map((r,k)=>({pointsPerElement:prepared[k].pointsPerElement,...summarize(r),gradientDifferenceFrom32N:Math.max(...r.gradientN.map((v,d)=>Math.abs(v-exact32.gradientN[d])))}))});
  if(selected.has(index)){
   const baseline=baselines.get(index);baseline.volumeEnergyJ+=exact32.energies.volume;
   for(let k=0;k<63;k++){
    baseline.bulkGradient[b.offset+k]+=exact32.bulkGradientN[k];
    profiles.forEach((r,d)=>baseline.quadDeltas[d][b.offset+k]+=r.gradientN[k]-exact32.gradientN[k]);
   }
  }
 }
 console.log('BODY',bi,b.id,'all 16 poses, 256-point selected poses');
}
const selectedResults=states.filter(s=>selected.has(s.index)).map(({state,index,label})=>{
 const b=baselines.get(index),residual=delta=>Math.max(...b.gradient.map((v,k)=>index<0&&k===j?0:Math.abs(v+delta[k])));
 return {label,index,timeS:state.timeS,baselineResidualN:b.residual,quadrature:[4,32,256].map((pointsPerElement,k)=>{const r=residual(b.quadDeltas[k]);return {pointsPerElement,frozenTotalReducedResidualN:r,passesOriginalForceGateAtFrozenPose:r<=p.stationarityToleranceN};}),bulkSensitivity:[.5,1,2].map(factor=>{const r=residual(b.bulkGradient.map(v=>(factor-1)*v));return {factor,baselineBulkPa:arm.model.bodies[0].material.bulk,frozenEnergyChangeJ:(factor-1)*b.volumeEnergyJ,frozenTotalReducedResidualN:r,passesOriginalForceGateAtFrozenPose:r<=p.stationarityToleranceN,coordinatesChanged:false};})};
});
const sourceFiles=[...Object.keys(run.sourceHashes),'tools/anatomical-compression-quadrature.mjs','tools/anatomical-compression-audit.mjs','tools/verify-anatomical-contact-trajectory.mjs'];
const receipt={schema:1,result:'COMPLETED_FROZEN_POSE_DIAGNOSTIC',baseImplementationCommit:'e3f546712bceee543993f798b13da97efc88d849',executionReceiptSHA256:check.executionReceiptSHA256,acceptedReplaySHA256:hash('data/anatomical-arm-v1/audit/contact-lift-release-recheck.json'),sourceHashes:Object.fromEntries(sourceFiles.map(f=>[f,hash(f)])),unchangedStationarityToleranceN:p.stationarityToleranceN,maximumModalProjectionDifferenceN,maximumModalEnergyDifferenceJ,states:diagnostics,selectedResults,limits:['Saved coordinates, activation, tendon/contact rules and fitted stress scales are held fixed. No new equilibrium or trajectory is accepted.','4/32/256 positive P2 integration and corner determinant queries are finite samples, not a global determinant or mesh convergence proof.','Half/double bulk changes are diagnostics at unchanged coordinates, not calibration or re-equilibrated sensitivity.','Nodal gradients used here contain the body potential only. Total reduced residual deltas retain the original tendon, contact and incremental joint terms. This is not full nodal force balance.','Compression, timestep sensitivity, source articulation, finite-radius tendon, coplanar and continuous-motion limitations remain open.']};
fs.writeFileSync(base+'audit/anatomical-compression-sensitivity.json',JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({result:receipt.result,poses:diagnostics.length,selected:selectedResults.length,maximumModalProjectionDifferenceN,maximumModalEnergyDifferenceJ,selectedResults}));
