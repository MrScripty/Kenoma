import {recordedInputMatches} from './recorded-inputs.mjs';
/** Fresh residual replay of the failed unassisted starting guess. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),rest=read('audit/arm-rest-results.json'),rows=[];
for(const path of ['audit/contact-cold-start-rejected.json','audit/contact-default-start-rejected.json']){
 const d=read(path),arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:d.parameters||rest.parameters,contactParameters:d.contactParameters||rest.contactParameters,routingRecipe:read('config/apparatus-routing.json'),contactRule:d.candidateContactRule||d.oldState.contactRule});
 if(d.sourceHashes)for(const [p,h] of Object.entries(d.sourceHashes))if(!recordedInputMatches(p,h)){const archived='data/anatomical-arm-v1/audit/contact-missed-soft-v3/'+p;if(!fs.existsSync(root+archived)||hash(archived)!==h)throw Error('Missing failed execution source '+p);};
 const x=Float64Array.from(d.candidateCoordinatesM),old=d.oldState,p=arm.parameters,h=d.hS,a=d.requestedEffort+(old.activation-d.requestedEffort)*Math.exp(-h/p.activationTimeS),c=anatomicalConfiguration(arm,x,a,{hessian:false}),j=arm.model.jointIndex,q=x[j]/JOINT_SCALE_M,grip=attachmentMap(arm.gripM,arm.model.frame,q),com=attachmentMap(arm.comM,arm.model.frame,q),I=arm.baseInertiaKgM2+old.massKg*arm.gripRadiusSquaredM2,stop=q<p.minimumAngleRad?q-p.minimumAngleRad:q>p.maximumAngleRad?q-p.maximumAngleRad:0;
 c.gradient[j]+=(p.gMPerS2*(p.segmentMassKg*com.B[2]+old.massKg*grip.B[2])+p.stopStiffnessNmPerRad*stop+I/h**2*(q-old.qRad-h*old.omegaRadPerS)+p.jointDampingNmS/h*(q-old.qRad))/JOINT_SCALE_M;
 const residual=Math.max(...c.gradient.map(Math.abs));if(!(Number.isFinite(residual)&&residual>p.stationarityToleranceN))throw Error('Failed unassisted residual not reproduced');
 if(d.sourceHashes&&Math.abs(residual-d.residualN)>1e-9)throw Error('Current-source rejected residual differs');
 rows.push({input:path,inputSHA256:hash('data/anatomical-arm-v1/'+path),candidateAccepted:false,recordedResidualN:d.residualN,residualN:residual,toleranceN:p.stationarityToleranceN,surfaceAudit:finitePoseAudit(arm.model,c.positions,q),routingAudit:finiteRoutingAudit(arm.model,x),contact:c.contact,minimumJ:Math.min(...c.headResults.map(h=>h.minJ))});
}
const files=[...Object.keys(rest.sourceHashes),'web/anatomical-contact-refinement.mjs','tools/verify-anatomical-cold-candidate.mjs'],payload={schema:1,result:'PASS',candidateAccepted:false,claim:'The current operator rejects both saved unassisted candidates. Failed starting guesses never advance state.',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),rows};
fs.writeFileSync(base+'audit/contact-cold-start-recheck.json',JSON.stringify(payload,null,2)+'\n');console.log(JSON.stringify({result:'PASS',rows:rows.map(r=>({input:r.input,residualN:r.residualN}))}));
