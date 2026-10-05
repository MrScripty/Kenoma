/** Exact-sign orientation certificates for the stored accepted P2 geometries. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm} from '../web/anatomical-arm.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';
import {prepareModalBody as enrichedBody} from './enriched/anatomical-modal.mjs';
import {exactElementOrientation} from './anatomical-bernstein-orientation.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),read=p=>JSON.parse(fs.readFileSync(base+p)),coarse=read('audit/anatomical-dense-trajectory.json'),replay=read('audit/anatomical-dense-trajectory-recheck.json'),enriched=read('audit/anatomical-enriched-step.json'),enrichedReplay=read('audit/anatomical-enriched-step-recheck.json');
if(replay.result!=='PASS_DENSE_TRAJECTORY'||replay.executionReceiptSHA256!==hash('data/anatomical-arm-v1/audit/anatomical-dense-trajectory.json')||enrichedReplay.result!=='PASS_ACCEPTED_ENRICHED_COMPARISON'||enrichedReplay.executionReceiptSHA256!==hash('data/anatomical-arm-v1/audit/anatomical-enriched-step.json'))throw Error('Fresh accepted replay required');
for(const run of [coarse,enriched])for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed accepted source '+p);
const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:coarse.parameters,contactParameters:coarse.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),extra=enrichedBody(arm.model.bodies.find(b=>b.id==='FJ1512').modal.source),rows=[];
const ratio=(a,b)=>Number(BigInt(a.minimumNumerator))/Number(BigInt(b.maximumNumerator))*2**(b.denominatorPowerOfTwo-a.denominatorPowerOfTwo);
function audit(state,kind){
 const heads=[];
 for(const b of arm.model.bodies){
  const body=kind==='enriched'&&b.id==='FJ1512'?extra:b.modal,offset=b.offset+(kind==='enriched'&&b.offset>=126?6:0),positions=modalPositions(body,state.coordinatesM.slice(offset,offset+body.ndof)),elements=[];
  for(const [i,nodes] of body.source.elements_ten_node.entries()){
   const certificate=exactElementOrientation(nodes.map(n=>body.source.nodes_m[n]),nodes.map(n=>positions[n]));
   elements.push({elementIndex:i,orientationCertified:certificate.orientationCertified,lowerJApprox:ratio(certificate.current,certificate.reference),...certificate});
  }
  heads.push({elementId:b.id,elementCount:elements.length,certifiedCount:elements.filter(e=>e.orientationCertified).length,allElementsCertified:elements.every(e=>e.orientationCertified),minimumCertifiedLowerJApprox:Math.min(...elements.filter(e=>e.orientationCertified).map(e=>e.lowerJApprox)),elements});
 }
 rows.push({kind,timeS:state.timeS,allElementsCertified:heads.every(h=>h.allElementsCertified),heads});console.log('POSE',kind,state.timeS,rows.at(-1).allElementsCertified,heads.map(h=>({id:h.elementId,certified:h.certifiedCount,total:h.elementCount,lowerJApprox:h.minimumCertifiedLowerJApprox})));
}
audit(coarse.held.state,'dense-held');for(const state of coarse.snapshots)audit(state,'dense');audit(enriched.candidate,'enriched');
const files=[...new Set([...Object.keys(coarse.sourceHashes),...Object.keys(enriched.sourceHashes),'tools/anatomical-bernstein-orientation.mjs','tools/anatomical-trajectory-orientation-audit.mjs','data/anatomical-arm-v1/audit/anatomical-dense-trajectory.json','data/anatomical-arm-v1/audit/anatomical-dense-trajectory-recheck.json','data/anatomical-arm-v1/audit/anatomical-enriched-step.json','data/anatomical-arm-v1/audit/anatomical-enriched-step-recheck.json'])];
const result={schema:1,result:rows.every(r=>r.allElementsCertified)?'PASS_EXACT_STORED_P2_ORIENTATION':'UNRESOLVED_STORED_P2_ORIENTATION',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),method:'All 20 degree-three tetrahedral Bernstein coefficients of each reference/current P2 Jacobian determinant are strictly positive by exact BigInt arithmetic. Binary64 nodal positions are treated as exact dyadic numbers.',rows,limits:['Exact signs certify positive orientation throughout each stored P2 element interpolant. Reported numeric lower-J approximations are not outward-rounded bounds.','This geometric certificate does not establish stationarity outside the retained coordinates, incompressibility, contact completeness or continuous-motion validity.','The exact nodal interpolant is the stored binary64 nodal geometry; floating quadrature evaluation and physiological calibration remain separate. No Lean proof claim or constitutive change is made.']};
fs.writeFileSync(base+'audit/anatomical-trajectory-orientation.json',JSON.stringify(result)+'\n');console.log('RESULT',result.result);
