/** Frozen dense loading state at 2048 positive points. The audited state is
 * unchanged, and a failed residual is never advanced as a finer state. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {denseModalBody,incrementalGradient} from './anatomical-dense-quadrature.mjs';
import {evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {prepareFurtherBody} from './anatomical-integration-refinement.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/anatomical-dense-loading-prefix.json');
for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed dense prefix '+p);
const i=3,state=run.snapshots[i],old=run.snapshots[i-1],request=run.attempts[i];if(!request.accepted||run.pointsPerElement!==256)throw Error('Accepted dense loading state required');
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')});
for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);
restoreContactRecipe(arm.contact,state.contactRule);const x=Float64Array.from(state.coordinatesM),c=anatomicalConfiguration(arm,x,state.activation,{hessian:false}),gradient=incrementalGradient(arm,c,state,old,request.hS),finerGradient=gradient.slice(),heads=[];
const baselineResidualN=Math.max(...gradient.map(Math.abs));if(!(baselineResidualN<=arm.parameters.stationarityToleranceN))throw Error('Dense baseline gate');
for(const b of arm.model.bodies){
 const coordinates=x.slice(b.offset,b.offset+63),activation=['FJ1486','FJ1512','FJ1478'].includes(b.id)?state.activation:0,modal=evaluateModalBody(b.modal,coordinates,activation,{material:b.material,hessian:false}),full=evaluateCompressionBody(prepareFurtherBody(b.modal.source,b.modal.nodeModes),modalPositions(b.modal,coordinates),activation,b.material);
 for(let k=0;k<63;k++)finerGradient[b.offset+k]+=full.gradientN[k]-modal.gradient[k];
 heads.push({elementId:b.id,minimumJ256:modal.minJ,minimumJ2048:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeFractionBelow09:full.referenceVolumeFractionBelow09,energyDifferenceJ:full.energyJ-modal.energy,maximumProjectedGradientDifferenceN:Math.max(...full.gradientN.map((v,k)=>Math.abs(v-modal.gradient[k])))});console.log('BODY',JSON.stringify(heads.at(-1)));
}
const frozenResidual2048N=Math.max(...finerGradient.map(Math.abs)),files=[...Object.keys(run.sourceHashes),'data/anatomical-arm-v1/audit/anatomical-dense-loading-prefix.json','tools/anatomical-further-integration-audit.mjs','tools/anatomical-integration-refinement.mjs'];
const result={schema:1,result:'COMPLETED_FROZEN_DENSE_REFINEMENT',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),timeS:state.timeS,pointsPerElement:2048,unchangedStationarityToleranceN:arm.parameters.stationarityToleranceN,baselineResidualN,frozenResidual2048N,passesOriginalForceGateAtFrozenPose:frozenResidual2048N<=arm.parameters.stationarityToleranceN,heads,limits:['Coordinates, activation, old dense state, velocity and contact recipe are unchanged. No finer equilibrium is solved or accepted.','2048-point energy/force sensitivity and corner checks remain finite samples, not a convergence or positivity certificate.']};
fs.writeFileSync(base+'audit/anatomical-further-integration.json',JSON.stringify(result,null,2)+'\n');console.log('RESULT',JSON.stringify({baselineResidualN,frozenResidual2048N}));
