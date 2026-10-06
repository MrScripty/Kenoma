/** Compare accepted states at actual equal times. No interpolation or solve. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm} from '../web/anatomical-arm.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),inputs={};
function read(name){const p=fileURLToPath(new URL('audit/'+name,'file://'+base));inputs['data/anatomical-arm-v1/'+p.slice(base.length)]=hash(p);return JSON.parse(fs.readFileSync(p));}
function pair(stem){
 const name=stem==='contact-lift-release'?stem+'-results.json':stem+'.json',execution=read(name),replay=read(stem+'-recheck.json');
 if(replay.executionReceiptSHA256!==inputs['data/anatomical-arm-v1/audit/'+name]||!['PASS','PASS_DENSE_TRAJECTORY','PASS_PRESERVED_REJECTION','PASS_PRESERVED_BEHAVIOR_REJECTION'].includes(replay.result)||replay.rows.length!==execution.snapshots.length)throw Error('Fresh complete replay required: '+stem);
 return {stem,execution,replay};
}
const coarse=pair('anatomical-dense-trajectory'),baseline=pair('contact-lift-release'),others=['anatomical-dense-fine-trajectory','anatomical-dense-interpolated-trajectory','anatomical-dense-release-refinement'].map(pair);
const arm=prepareAnatomicalArm(read('../generated/arm-reference.json'),read('../config/attachments-apparatus.json'),read('modal-fixed-end-results.json'),{parameters:coarse.execution.parameters,contactParameters:coarse.execution.contactParameters,routingRecipe:read('../config/apparatus-routing.json')});
const positions=s=>arm.model.bodies.map(b=>modalPositions(b.modal,s.coordinatesM.slice(b.offset,b.offset+63)));
function compare(other,reference=coarse){
 const rows=[];
 for(const [i,a] of reference.execution.snapshots.entries()){
  const k=other.execution.snapshots.findIndex(b=>Math.abs(a.timeS-b.timeS)<1e-12);if(k<0)continue;
  const b=other.execution.snapshots[k],pa=positions(a),pb=positions(b);let maximumNodalDifferenceM=0,maximumCoordinateDifferenceM=0;
  for(let d=0;d<a.coordinatesM.length;d++)if(d!==arm.model.jointIndex)maximumCoordinateDifferenceM=Math.max(maximumCoordinateDifferenceM,Math.abs(a.coordinatesM[d]-b.coordinatesM[d]));
  for(let h=0;h<pa.length;h++)for(let n=0;n<pa[h].length;n++)maximumNodalDifferenceM=Math.max(maximumNodalDifferenceM,Math.hypot(...pa[h][n].map((v,d)=>v-pb[h][n][d])));
  if(Math.abs(a.activation-b.activation)>1e-13||a.massKg!==b.massKg)throw Error('Changed matched-time activation or load');
  rows.push({timeS:a.timeS,referenceStep:i+1,otherStep:k+1,referenceAngleDeg:a.qRad*180/Math.PI,otherAngleDeg:b.qRad*180/Math.PI,angleDifferenceDeg:(b.qRad-a.qRad)*180/Math.PI,maximumCoordinateDifferenceM,maximumNodalDifferenceM,referenceIndependentResidualN:reference.replay.rows[i].independentResidualN,otherIndependentResidualN:other.replay.rows[k].independentResidualN??other.replay.rows[k].residualN});
 }
 const release=rows.filter(r=>r.timeS>.13+1e-12),max=(xs,key)=>xs.length?Math.max(...xs.map(r=>Math.abs(r[key]))):null;
 return {reference:reference.stem,comparedWith:other.stem,executionResult:other.execution.result,verifiedSteps:other.replay.rows.length,lastAcceptedTimeS:other.execution.snapshots.at(-1)?.timeS??0,rows,matchedCount:rows.length,maximumAbsoluteAngleDifferenceDeg:max(rows,'angleDifferenceDeg'),maximumNodalDifferenceM:max(rows,'maximumNodalDifferenceM'),releaseMatchedCount:release.length,maximumReleaseAngleDifferenceDeg:max(release,'angleDifferenceDeg'),rejection:other.replay.rejected??null};
}
// Frozen prefixes must remain exactly the states from the originating run.
const prefixes=[['anatomical-dense-loading-prefix.json',4],['anatomical-dense-release-base.json',5]];
for(const [name,n] of prefixes){const prefix=read(name);if(JSON.stringify(prefix.held)!==JSON.stringify(coarse.execution.held)||JSON.stringify(prefix.snapshots)!==JSON.stringify(coarse.execution.snapshots.slice(0,n)))throw Error('Changed frozen dense prefix '+name);}
const output={schema:1,result:'PASS_ACCEPTED_MATCHED_TIME_COMPARISON',coarseResult:coarse.execution.result,coarseVerifiedSteps:coarse.replay.rows.length,coarseLastTimeS:coarse.execution.snapshots.at(-1)?.timeS??0,comparisons:[baseline,...others].map(other=>compare(other)),seedComparison:compare(others[1],others[0]),sourceHashes:{...inputs,'tools/anatomical-dense-matched-times.mjs':hash(fileURLToPath(import.meta.url))},limits:['Only independently replayed accepted states at equal times are compared; rejected candidates never advance the trajectory.','Release-only refinement shares five identical dense loading increments. All-half refinements have their own held and accepted old states.','Reported nodal differences are actual P2 tissue node positions, not mesh/full nodal convergence. No tolerance was relaxed.','A nonzero difference or a short accepted prefix does not qualify timestep or quadrature convergence.']};
output.workSummaries=[coarse,...others].map(({stem,replay})=>({trajectory:stem,acceptedSteps:replay.rows.length,lastAcceptedTimeS:replay.rows.at(-1)?.timeS??0,maximumAbsoluteNonlinearWorkDefectJ:Math.max(...replay.rows.map(r=>Math.abs(r.nonlinearWorkDefectJ))),sumNonlinearWorkDefectJ:replay.rows.reduce((s,r)=>s+r.nonlinearWorkDefectJ,0),sumReferenceQuadratureUpdateJ:replay.rows.reduce((s,r)=>s+r.referenceQuadratureUpdateJ,0)}));
output.limits.push('Ledger arithmetic replay is not energy conservation; nonlinear work defects include quasistatic relaxation and nonlinear joint sampling, and contact-rule energy events remain separate.');
output.limits.push('Maximum coordinate differences exclude the scaled joint coordinate; joint differences are angles and nodal differences are physical tissue node distances.');
fs.writeFileSync(base+'audit/anatomical-dense-matched-times.json',JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output));
