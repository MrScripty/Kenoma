/** Frozen original calibration poses: no contact, new fit or optimizer. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareModalBody,modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
import {prepareIntramuscularAponeuroses,evaluateIntramuscularAponeuroses} from '../web/anatomical-aponeurosis.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),read=p=>JSON.parse(fs.readFileSync(base+p)),fixture=read('audit/modal-fixed-end-results.json'),priorReplay=read('audit/modal-fixed-end-recheck.json'),geometry=read('generated/arm-reference.json');
for(const [p,h] of Object.entries(priorReplay.sourceHashes))if(hash(p)!==h)throw Error('Changed calibration replay operator '+p);
if(hash('data/anatomical-arm-v1/audit/modal-fixed-end-results.json')!==priorReplay.savedMatchReceiptSHA256)throw Error('Changed calibration receipt');
if(hash('data/anatomical-arm-v1/generated/arm-reference.json')!==fixture.referenceGeometrySHA256)throw Error('Changed calibration geometry');
const rows=[];
for(const record of fixture.records){
 const source=geometry.muscles.find(m=>m.element_id===record.elementId),body=prepareModalBody(source),sheets=prepareIntramuscularAponeuroses(body),x=Float64Array.from(record.match.coordinatesM),material={...MUSCLE_FIXTURE,sigma0:record.match.sigma0Pa},sheet=evaluateIntramuscularAponeuroses(body,sheets,x,{hessian:false}),positions=modalPositions(body,x),modal=evaluateModalBody(body,x,1,{material,hessian:false}),rules=[];
 const original=Float64Array.from(modal.gradient,(v,k)=>v+sheet.gradient[k]),residual=Math.max(...original.slice(9,54).map(Math.abs)),force=-source.basis.axis.reduce((s,v,k)=>s+v*original[k],0);
 if(residual>fixture.stationarityToleranceN||Math.abs(force-record.match.forceN)>1e-8||Math.abs(force/record.modelReference.value-1)>fixture.forceToleranceRelative||Math.abs(modal.minJ-record.match.minimumJ)>1e-12)throw Error('Original fixed-end replay '+record.elementId);
 for(const depth of [1,2]){
  const full=evaluateCompressionBody(prepareCompressionBody(source,body.nodeModes,depth),positions,1,material),gradient=Float64Array.from(full.gradientN,(v,k)=>v+sheet.gradient[k]),freeResidualN=Math.max(...gradient.slice(9,54).map(Math.abs)),fixedEndForceN=-source.basis.axis.reduce((s,v,k)=>s+v*gradient[k],0);
  if(depth===1&&Math.max(...gradient.map((v,k)=>Math.abs(v-original[k])))>2e-6)throw Error('Independent original P2 projection');
  rules.push({pointsPerElement:4*8**depth,freeResidualN,passesOriginalForceGateAtFrozenPose:freeResidualN<=fixture.stationarityToleranceN,fixedEndForceN,minimumSampledJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeFractionBelow09:full.referenceVolumeFractionBelow09,bodyEnergiesJ:full.energies});
 }
 rows.push({elementId:record.elementId,activation:1,sigma0Pa:material.sigma0,bulkPa:material.bulk,sigma0OverBulk:material.sigma0/material.bulk,modelForceTargetN:record.modelReference.value,originalModalResidualN:residual,internalSheetEnergyJ:sheet.energy,rules});console.log('HEAD',JSON.stringify(rows.at(-1)));
}
const files=[...Object.keys(priorReplay.sourceHashes),'web/anatomical-element.mjs','tools/anatomical-compression-quadrature.mjs','tools/anatomical-fixed-end-compression-audit.mjs','data/anatomical-arm-v1/generated/arm-reference.json','data/anatomical-arm-v1/audit/modal-fixed-end-results.json','data/anatomical-arm-v1/audit/modal-fixed-end-recheck.json','data/elbow-v1/sources/arm26.osim'];
const result={schema:1,result:'PASS_ORIGINAL_FIXED_END_REPLAY_WITH_FROZEN_COMPRESSION_DIAGNOSTICS',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),unchangedStationarityToleranceN:fixture.stationarityToleranceN,rows,limits:['Original calibration coordinates and fitted active stress scales are unchanged; activation is one and both end rings are fixed.','Only muscle and its embedded sheets enter this isolated fixture. Whole-arm contact, apparatus and time advancement are absent.','The original 32-point calibration is independently replayed. Frozen 256-point failures do not accept a denser calibration or retune stress scales.','Compression already present in these isolated fixtures cannot be attributed solely to subsequent whole-arm contact. Stress/bulk ratios describe authored parameters, not physiological calibration.']};
fs.writeFileSync(base+'audit/anatomical-fixed-end-compression.json',JSON.stringify(result,null,2)+'\n');console.log('RESULT',result.result);
